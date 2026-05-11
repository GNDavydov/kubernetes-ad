from uuid import UUID

from app.application.use_cases.detect import DetectUseCase
from app.application.use_cases.train import TrainUseCase
from app.core.settings import get_settings
from app.infrastructure.db.database import Database
from app.infrastructure.ml.create_sequences_impl import CreateSequencesImpl
from app.infrastructure.ml.encode_pipeline_impl import EncodePipelineImpl
from app.infrastructure.task_queue.celery_app import CeleryTaskQueue

settings = get_settings()

if __name__ == "__main__":
    database = Database(
        database_url=settings.database_url,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )
    encode_pipeline = EncodePipelineImpl()
    sequence_pipeline = CreateSequencesImpl(encode_pipeline)

    train_use_case = TrainUseCase(
        database=database,
        encode_pipeline=encode_pipeline,
        sequence_pipeline=sequence_pipeline,
        opensearch_timeout_seconds=settings.opensearch_timeout_seconds,
        opensearch_verify_ssl=settings.opensearch_verify_ssl,
        opensearch_timestamp_field=settings.opensearch_timestamp_field,
        fetch_size=settings.worker_fetch_size,
        train_batch_size=settings.train_batch_size,
        train_learning_rate=settings.train_learning_rate,
        train_val_split_ratio=settings.train_val_split_ratio,
        random_seed=settings.random_seed,
        train_threshold_percentile=settings.train_threshold_percentile,
        lstm_hidden_dim=settings.lstm_hidden_dim,
        lstm_latent_dim=settings.lstm_latent_dim,
        lstm_num_layers=settings.lstm_num_layers,
        lstm_dropout=settings.lstm_dropout,
    )
    detect_use_case = DetectUseCase(
        database=database,
        encode_pipeline=encode_pipeline,
        sequence_pipeline=sequence_pipeline,
        opensearch_timeout_seconds=settings.opensearch_timeout_seconds,
        opensearch_verify_ssl=settings.opensearch_verify_ssl,
        opensearch_timestamp_field=settings.opensearch_timestamp_field,
        fetch_size=settings.worker_fetch_size,
        detect_default_lookback_minutes=settings.detect_default_lookback_minutes,
        detect_batch_size=settings.train_batch_size,
    )

    task_queue = CeleryTaskQueue(
        app_name=settings.app_name,
        broker_url=settings.celery_broker_url,
        backend_url=settings.celery_result_backend,
    )

    # Celery expects a real function object (with __name__), not a class instance.
    def run_train_task(task_id: UUID | str) -> None:
        train_use_case(task_id)

    def run_detect_task(task_id: UUID | str) -> None:
        detect_use_case(task_id)

    task_queue.register_train_task(run_train_task)
    task_queue.register_detect_task(run_detect_task)

    argv: list[str] = [
        "worker",
        "--loglevel=info",
        "--pool=solo",
    ]
    task_queue.app.worker_main(argv)
