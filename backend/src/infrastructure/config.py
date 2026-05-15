from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/arxiv_db"
    secret_key: str = "your-secret-key-change-in-production-min-32-chars"
    access_token_expire_minutes: int = 480
    upload_dir: str = "uploads"
    cors_origins: str = "http://localhost:3000,http://192.168.20.247:3000"
    redis_url: str = "redis://localhost:6379/0"
    elasticsearch_url: str = "http://localhost:9200"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
