"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "SchemaForge"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = "postgresql://schemaforge:schemaforge@localhost:5432/schemaforge"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Authentication
    JWT_SECRET: str = "change-me-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440  # 24 hours

    # AI Providers
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    AI_PROVIDER: str = "openai"
    AI_MAX_RETRIES: int = 3
    AI_MAX_TOKENS_PER_CHUNK: int = 8000
    AI_PIPELINE_BUDGET_USD: float = 50.0

    # Validation
    AZURE_SQL_CONNECTION_STRING: str | None = None

    # Workers
    WORKER_HEARTBEAT_INTERVAL: int = 30
    WORKER_ORPHAN_TIMEOUT: int = 120
    WORKER_TASK_TIMEOUT: int = 600
    WORKER_GRACEFUL_SHUTDOWN_TIMEOUT: int = 60

    # Storage
    STORAGE_ROOT: str = "./storage"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


# Singleton settings instance
settings = Settings()
