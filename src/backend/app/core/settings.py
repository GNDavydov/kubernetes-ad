from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kubernetes Anomaly Detector"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    database_url: str = "sqlite+aiosqlite:///./anomaly.db"
    db_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20

    jwt_secret_key: str = "change-me-please-use-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    admin_email: str = "admin@example.com"
    admin_password: str = "admin12345"

    redis_blacklist_url: str = "redis://localhost:6379/2"
    redis_blacklist_key_prefix: str = "auth:blacklist:"

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    opensearch_timeout_seconds: int = 30
    opensearch_verify_ssl: bool = False
    opensearch_timestamp_field: str = "requestReceivedTimestamp"
    worker_fetch_size: int = 100000
    detect_default_lookback_minutes: int = 60
    train_batch_size: int = 64
    train_learning_rate: float = 0.001
    train_val_split_ratio: float = 0.2
    random_seed: int = 42
    train_threshold_percentile: float = 99.0

    lstm_hidden_dim: int = 64
    lstm_latent_dim: int = 32
    lstm_num_layers: int = 1
    lstm_dropout: float = 0.0

    # CORS: use ["*"] for dev; restrict in production (comma-separated in env not supported — override in code or extend settings).
    cors_origins: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
