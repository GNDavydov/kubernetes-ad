import asyncio
import time
from uuid import UUID

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from app.domain.entities.model import Model
from app.domain.entities.train_metric import TrainMetric
from app.domain.enums.model_status import ModelStatus
from app.domain.enums.task_status import TaskStatus
from app.domain.enums.task_type import TaskType
from app.domain.interfaces.create_sequences import CreateSequences
from app.infrastructure.db.database import Database
from app.infrastructure.db.repositories.integration_repository_impl import (
    IntegrationRepositoryImpl,
)
from app.infrastructure.db.repositories.model_repository_impl import ModelRepositoryImpl
from app.infrastructure.db.repositories.task_repository_impl import TaskRepositoryImpl
from app.infrastructure.db.repositories.train_metric_repository_impl import (
    TrainMetricRepositoryImpl,
)
from app.infrastructure.ml.lstm_ae import LSTMAutoencoder
from app.infrastructure.opensearch.opensearch_log_provider import OpenSearchLogProvider


class TrainUseCase:
    def __init__(
        self,
        database: Database,
        sequence_pipeline: CreateSequences,
        opensearch_timeout_seconds: int,
        opensearch_verify_ssl: bool,
        opensearch_timestamp_field: str,
        opensearch_fetch_size: int,
        train_batch_size: int,
        train_learning_rate: float,
        train_val_split_ratio: float,
        train_threshold_percentile: float,
    ) -> None:
        self._database = database
        self._sequence_pipeline = sequence_pipeline

        self._opensearch_timeout_seconds = opensearch_timeout_seconds
        self._opensearch_verify_ssl = opensearch_verify_ssl
        self._opensearch_timestamp_field = opensearch_timestamp_field
        self._opensearch_fetch_size = opensearch_fetch_size

        self._train_batch_size = train_batch_size
        self._train_learning_rate = train_learning_rate
        self._train_val_split_ratio = train_val_split_ratio
        self._train_threshold_percentile = train_threshold_percentile

    def __call__(self, task_id: UUID | str) -> None:
        asyncio.run(self.execute(task_id=task_id))

    async def execute(self, task_id: UUID | str) -> None:
        task_uuid = UUID(str(task_id))

        async with self._database.session_factory() as session:
            task_repository = TaskRepositoryImpl(session)
            model_repository = ModelRepositoryImpl(session)
            integration_repository = IntegrationRepositoryImpl(session)
            train_metric_repository = TrainMetricRepositoryImpl(session)

            task = await task_repository.get_by_id(task_uuid)
            if task is None:
                return

            model = await model_repository.get_by_id(task.model_id)
            integration = await integration_repository.get_by_id(task.integration_id)
            if model is None or model.id is None or integration is None:
                await task_repository.update_status(task_uuid, TaskStatus.FAILED)
                return

            if task.type != TaskType.TRAIN or task.epochs is None or task.epochs < 1:
                await task_repository.update_status(task_uuid, TaskStatus.FAILED)
                await model_repository.update_status(model.id, ModelStatus.FAILED)
                raise RuntimeError(
                    "Invalid train task: missing epochs or wrong type.")

            await task_repository.update_status(task_uuid, TaskStatus.RUNNING)
            await model_repository.update_status(model.id, ModelStatus.TRAINING)

            model_id = model.id

            try:
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
                    size=self._opensearch_fetch_size)
                if not events:
                    raise RuntimeError("No audit events fetched for training.")

                sequences = self._sequence_pipeline.transform(
                    events, model.seq_len)
                sequences = np.asarray(sequences, dtype=np.float32)

                if sequences.ndim != 3:
                    raise ValueError(
                        f"Expected sequences with shape (n, seq_len, feature_dim), got {sequences.shape}"
                    )

                processed_events = len(events)

                train_x, val_x = self._split_train_val(
                    sequences=sequences,
                    val_split_ratio=self._train_val_split_ratio,
                    seed=42,
                )

                if len(train_x) == 0:
                    raise RuntimeError("Not enough sequences for training.")

                train_loader = DataLoader(
                    TensorDataset(torch.from_numpy(train_x).float()),
                    batch_size=self._train_batch_size,
                    shuffle=True,
                )
                val_loader = DataLoader(
                    TensorDataset(torch.from_numpy(val_x).float()),
                    batch_size=self._train_batch_size,
                    shuffle=False,
                )

                input_dim = sequences.shape[-1]
                device = torch.device("cpu")

                net: LSTMAutoencoder = LSTMAutoencoder(
                    input_dim=input_dim,
                    hidden_dim=64,
                    latent_dim=32,
                    num_layers=1,
                ).to(device)

                optimizer = torch.optim.Adam(
                    net.parameters(),
                    lr=self._train_learning_rate,
                )
                criterion = nn.MSELoss(reduction="mean")

                for epoch in range(1, task.epochs + 1):
                    t0 = time.perf_counter()

                    net.train()
                    running_loss = 0.0
                    n_samples = 0

                    for (x,) in train_loader:
                        x = x.to(device)

                        optimizer.zero_grad()
                        xhat = net(x)
                        loss = criterion(xhat, x)
                        loss.backward()
                        optimizer.step()

                        bs = x.size(0)
                        running_loss += loss.item() * bs
                        n_samples += bs

                    train_loss = running_loss / \
                        n_samples if n_samples else float("nan")

                    net.eval()
                    running_val_loss = 0.0
                    n_val = 0

                    with torch.no_grad():
                        for (x,) in val_loader:
                            x = x.to(device)
                            xhat = net(x)
                            loss = criterion(xhat, x)

                            bs = x.size(0)
                            running_val_loss += loss.item() * bs
                            n_val += bs

                    val_loss = running_val_loss / \
                        n_val if n_val else float("nan")
                    duration = time.perf_counter() - t0

                    await train_metric_repository.create(
                        TrainMetric(
                            id=None,
                            task_id=task_uuid,
                            processed_events=processed_events,
                            epoch=epoch,
                            loss=train_loss,
                            val_loss=val_loss,
                            duration=duration,
                            created_at=None,
                        )
                    )

                net.eval()
                val_scores: list[float] = []

                with torch.no_grad():
                    for (x,) in val_loader:
                        x = x.to(device)
                        val_scores.extend(net.predict(
                            x).cpu().numpy().tolist())

                if not val_scores:
                    with torch.no_grad():
                        for (x,) in train_loader:
                            x = x.to(device)
                            val_scores.extend(net.predict(
                                x).cpu().numpy().tolist())

                threshold = float(
                    np.percentile(np.asarray(
                        val_scores, dtype=np.float32), self._train_threshold_percentile)
                )

                net.save(model.model_path)

                updated = Model(
                    id=model_id,
                    user_id=model.user_id,
                    name=model.name,
                    status=ModelStatus.READY,
                    seq_len=model.seq_len,
                    threshold=threshold,
                    model_path=model.model_path,
                    last_processed_at=model.last_processed_at,
                    created_at=model.created_at,
                )
                await model_repository.update(updated)
                await task_repository.update_status(task_uuid, TaskStatus.DONE)

            except Exception:
                await task_repository.update_status(task_uuid, TaskStatus.FAILED)
                await model_repository.update_status(model_id, ModelStatus.FAILED)
                raise

    def _split_train_val(
        self,
        sequences: np.ndarray,
        val_ratio: float,
        seed: int | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(seed)
        n = len(sequences)
        if n < 2:
            return sequences, sequences
        n_val = min(max(1, int(round(n * val_ratio))), n - 1)
        perm = rng.permutation(n)
        val_idx = perm[:n_val]
        train_idx = perm[n_val:]
        return sequences[train_idx], sequences[val_idx]
