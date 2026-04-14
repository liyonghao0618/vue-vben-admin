from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="守护桑榆后端服务", alias="APP_NAME")
    app_env: Literal["development", "testing", "production"] = Field(
        default="development",
        alias="APP_ENV",
    )
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_api_prefix: str = Field(default="/api/v1", alias="APP_API_PREFIX")
    app_allowed_origins: list[str] = Field(default_factory=list, alias="APP_ALLOWED_ORIGINS")
    app_jwt_secret: str = Field(
        default="change-this-secret-at-least-32-chars",
        alias="APP_JWT_SECRET",
    )
    app_jwt_algorithm: str = Field(default="HS256", alias="APP_JWT_ALGORITHM")
    app_access_token_expire_minutes: int = Field(
        default=120,
        alias="APP_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    app_database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@127.0.0.1:5432/guard_silver",
        alias="APP_DATABASE_URL",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
