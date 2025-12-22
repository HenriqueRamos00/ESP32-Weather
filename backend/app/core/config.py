from typing import Any
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Device Management API"

    ADMIN_USER: str
    ADMIN_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MINUTES: str
    SECRET_KEY: str
    API_KEY_HASH_SECRET: str
    ALGORITHM: str = 'HS256'
    
    DATABASE_URL: PostgresDsn
    
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    
    ENVIRONMENT: str = "development"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def docs_url(self) -> str | None:
        """Return docs URL or None if in production."""
        return None if self.is_production else "/docs"
    
    @property
    def redoc_url(self) -> str | None:
        """Return redoc URL or None if in production."""
        return None if self.is_production else "/redoc"
    
    @property
    def openapi_url(self) -> str | None:
        """Return OpenAPI schema URL or None if in production."""
        return None if self.is_production else f"{self.API_V1_STR}/openapi.json"


settings = Settings()  # pyright: ignore[reportCallIssue]