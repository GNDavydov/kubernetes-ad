import asyncio
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import torch

from app.domain.entities.detect_metric import DetectMetric
from app.domain.entities.model import Model
from app.domain.enums.model_status import ModelStatus
from app.domain.enums.task_status import TaskStatus
from app.domain.enums.task_type import TaskType
from app.domain.interfaces.create_sequences import CreateSequences
from app.domain.interfaces.encode_pipeline import EncodePipeline
from app.infrastructure.db.database import Database
from app.infrastructure.db.repositories.detect_metric_repository_impl import (
    DetectMetricRepositoryImpl,
)
from app.infrastructure.db.repositories.integration_repository_impl import (
    IntegrationRepositoryImpl,
)
from app.infrastructure.db.repositories.model_repository_impl import ModelRepositoryImpl
from app.infrastructure.db.repositories.task_repository_impl import TaskRepositoryImpl
from app.infrastructure.ml.lstm_ae import LSTMAutoencoder
from app.infrastructure.opensearch.opensearch_log_provider import OpenSearchLogProvider


class DetectUseCase:
    def __init__(
        self,
        database: Database,
        encode_pipeline: EncodePipeline,
        sequence_pipeline: CreateSequences,
        opensearch_timeout_seconds: int,
        opensearch_verify_ssl: bool,
        opensearch_timestamp_field: str,
        fetch_size: int,
        detect_default_lookback_minutes: int,
        detect_batch_size: int,
    ) -> None:
        self._database = database
        self._encode_pipeline = encode_pipeline
        self._sequence_pipeline = sequence_pipeline
        self._opensearch_timeout_seconds = opensearch_timeout_seconds
        self._opensearch_verify_ssl = opensearch_verify_ssl
        self._opensearch_timestamp_field = opensearch_timestamp_field
        self._fetch_size = fetch_size
        self._detect_default_lookback_minutes = detect_default_lookback_minutes
        self._detect_batch_size = detect_batch_size

    def __call__(self, task_id: UUID | str) -> None:
        asyncio.run(self.execute(task_id=task_id))

    async def execute(self, task_id: UUID | str) -> None:
        task_uuid = UUID(str(task_id))
        t_wall0 = time.perf_counter()

        async with self._database.session_factory() as session:
            task_repository = TaskRepositoryImpl(session)
            model_repository = ModelRepositoryImpl(session)
            integration_repository = IntegrationRepositoryImpl(session)
            detect_metric_repository = DetectMetricRepositoryImpl(session)

            task = await task_repository.get_by_id(task_uuid)
            if task is None:
                return

            model = await model_repository.get_by_id(task.model_id)
            integration = await integration_repository.get_by_id(task.integration_id)
            if model is None or model.id is None or integration is None:
                await task_repository.update_status(task_uuid, TaskStatus.FAILED)
                return

            if task.type != TaskType.DETECT:
                await task_repository.update_status(task_uuid, TaskStatus.FAILED)
                raise RuntimeError("Invalid task type: expected DETECT.")

            if model.status != ModelStatus.READY:
                await task_repository.update_status(task_uuid, TaskStatus.FAILED)
                raise RuntimeError(
                    f"Model must be READY for detection, got {model.status}."
                )

            model_id = model.id

            try:
                if not Path(model.model_path).is_file():
                    raise FileNotFoundError(
                        f"Model weights not found at {model.model_path}"
                    )

                await task_repository.update_status(task_uuid, TaskStatus.RUNNING)

                end_ts = datetime.now(timezone.utc)
                if model.last_processed_at is not None:
                    start_ts = model.last_processed_at
                    if start_ts.tzinfo is None:
                        start_ts = start_ts.replace(tzinfo=timezone.utc)
                else:
                    start_ts = end_ts - timedelta(
                        minutes=self._detect_default_lookback_minutes
                    )

                provider = OpenSearchLogProvider(
                    base_url=integration.url,
                    source_index=integration.log_source_name,
                    anomaly_index=integration.anomaly_name,
                    username=integration.username,
                    password=integration.password,
                    timeout_seconds=self._opensearch_timeout_seconds,
                    verify_ssl=self._opensearch_verify_ssl,
                    timestamp_field=self._opensearch_timestamp_field,
                )
                events = provider.fetch_audit_events(
                    start_ts=start_ts,
                    end_ts=end_ts,
                    size=self._fetch_size,
                )
                processed_events = len(events)
                if not events:
                    duration = time.perf_counter() - t_wall0
                    await detect_metric_repository.create(
                        DetectMetric(
                            id=None,
                            task_id=task_uuid,
                            processed_events=0,
                            anomalies_count=0,
                            duration=duration,
                            created_at=None,
                            start_timestamp=start_ts,
                            end_timestamp=end_ts,
                        )
                    )
                    updated = Model(
                        id=model_id,
                        user_id=model.user_id,
                        name=model.name,
                        status=ModelStatus.READY,
                        seq_len=model.seq_len,
                        threshold=model.threshold,
                        model_path=model.model_path,
                        last_processed_at=end_ts,
                        created_at=model.created_at,
                    )
                    await model_repository.update(updated)
                    await task_repository.update_status(task_uuid, TaskStatus.DONE)
                    return

                sequences, descriptors = self._sequence_pipeline.transform(
                    events, model.seq_len
                )

                device = torch.device("cpu")
                net = LSTMAutoencoder.load(model.model_path, device=device)
                net.eval()

                threshold = float(model.threshold)
                anomaly_docs: list[dict] = []
                n = len(sequences)
                anomalies_count = 0

                with torch.no_grad():
                    for batch_start in range(0, n, self._detect_batch_size):
                        batch_end = min(
                            batch_start + self._detect_batch_size, n)
                        batch = torch.from_numpy(
                            sequences[batch_start:batch_end]
                        ).float().to(device)
                        scores = net.predict(batch).cpu().numpy()
                        for i, score in enumerate(scores):
                            idx = batch_start + i
                            desc = descriptors[idx]
                            if float(score) > threshold:
                                anomalies_count += 1
                                anomaly_docs.append(
                                    {
                                        "timestamp": desc.end_timestamp.isoformat(),
                                        "user_username": desc.user_username,
                                        "anomaly_score": float(score),
                                        "threshold": threshold,
                                        "task_id": str(task_uuid),
                                        "model_id": str(model_id),
                                        "window_start": desc.start_timestamp.isoformat(),
                                        "window_end": desc.end_timestamp.isoformat(),
                                    }
                                )

                provider.save_anomalies(anomaly_docs)

                duration = time.perf_counter() - t_wall0
                await detect_metric_repository.create(
                    DetectMetric(
                        id=None,
                        task_id=task_uuid,
                        processed_events=processed_events,
                        anomalies_count=anomalies_count,
                        duration=duration,
                        created_at=None,
                        start_timestamp=start_ts,
                        end_timestamp=end_ts,
                    )
                )

                updated = Model(
                    id=model_id,
                    user_id=model.user_id,
                    name=model.name,
                    status=ModelStatus.READY,
                    seq_len=model.seq_len,
                    threshold=model.threshold,
                    model_path=model.model_path,
                    last_processed_at=end_ts,
                    created_at=model.created_at,
                )
                await model_repository.update(updated)
                await task_repository.update_status(task_uuid, TaskStatus.DONE)

            except Exception:
                await task_repository.update_status(task_uuid, TaskStatus.FAILED)
                raise
