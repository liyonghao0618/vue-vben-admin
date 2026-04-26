from functools import lru_cache
from pathlib import Path
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

    app_name: str = Field(default="桑榆智盾后端服务", alias="APP_NAME")
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
    chat_message_rate_limit_count: int = Field(default=20, alias="CHAT_MESSAGE_RATE_LIMIT_COUNT")
    chat_message_rate_limit_window_seconds: int = Field(default=60, alias="CHAT_MESSAGE_RATE_LIMIT_WINDOW_SECONDS")
    chat_audit_enabled: bool = Field(default=True, alias="CHAT_AUDIT_ENABLED")
    call_session_invite_timeout_seconds: int = Field(
        default=45,
        alias="CALL_SESSION_INVITE_TIMEOUT_SECONDS",
    )
    call_stun_servers: list[str] = Field(
        default_factory=lambda: ["stun:stun.l.google.com:19302"],
        alias="CALL_STUN_SERVERS",
    )
    call_turn_url: str | None = Field(default=None, alias="CALL_TURN_URL")
    call_turn_username: str | None = Field(default=None, alias="CALL_TURN_USERNAME")
    call_turn_password: str | None = Field(default=None, alias="CALL_TURN_PASSWORD")
    audio_guard_enabled: bool = Field(default=True, alias="AUDIO_GUARD_ENABLED")
    audio_guard_script_path: str = Field(
        default=str(Path(__file__).resolve().parents[4] / "read_audio_guard_improved.sh"),
        alias="AUDIO_GUARD_SCRIPT_PATH",
    )
    audio_guard_timeout_seconds: int = Field(default=180, alias="AUDIO_GUARD_TIMEOUT_SECONDS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
