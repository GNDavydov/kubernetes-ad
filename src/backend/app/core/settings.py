from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kubernetes Anomaly Detector"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    database_url: str = "sqlite+aiosqlite:///./anomaly.db"
    db_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
