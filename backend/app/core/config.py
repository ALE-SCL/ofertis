import os
from typing import List
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field
except ImportError:
    class BaseSettings:
        pass
    def SettingsConfigDict(**kwargs):
        return kwargs
    def Field(default=None, **kwargs):
        return default


class Settings(BaseSettings):
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    # PostgreSQL Database
    POSTGRES_USER: str = Field(default="ofertis_user")
    POSTGRES_PASSWORD: str = Field(default="ofertis_dev_secret_2026")
    POSTGRES_DB: str = Field(default="ofertis_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://ofertis_user:ofertis_dev_secret_2026@localhost:5432/ofertis_db"
    )

    # Redis
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Server API
    BACKEND_HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    )

    # Embeddings & Vector DB
    EMBEDDING_MODEL_NAME: str = Field(default="paraphrase-multilingual-MiniLM-L12-v2")
    EMBEDDING_DIMENSION: int = Field(default=384)
    USE_LOCAL_SENTENCE_TRANSFORMER: bool = Field(default=False) # En Render (512MB RAM) debe ser False para evitar OOM

    # Scraping Configuration
    DEFAULT_CHILE_COMMUNE: str = Field(default="santiago_centro")
    SCRAPER_USER_AGENT: str = Field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    SCRAPER_RATE_LIMIT_DELAY_SECONDS: float = Field(default=2.0)

    # WhatsApp Channel
    WHATSAPP_PROVIDER: str = Field(default="mock") # 'mock', 'twilio_sandbox', 'meta_cloud'
    TWILIO_ACCOUNT_SID: str = Field(default="")
    TWILIO_AUTH_TOKEN: str = Field(default="")
    TWILIO_WHATSAPP_FROM: str = Field(default="whatsapp:+14155238886")
    ADMIN_ALERT_PHONE: str = Field(default="+56912345678")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
