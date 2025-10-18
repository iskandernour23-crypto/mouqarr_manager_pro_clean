from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration for Mouqarr Manager Pro services."""

    app_name: str = Field(default="Mouqarr Manager Pro", env="APP_NAME")
    app_lang: str = Field(default="ar", env="APP_LANG")
    frontend_url: str = Field(default="http://localhost:5173", env="FRONTEND_URL")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    ai_rpm: int = Field(default=60, env="AI_RPM")
    ai_max_tokens: int = Field(default=1500, env="AI_MAX_TOKENS")
    ai_lang_default: str = Field(default="ar", env="AI_LANG_DEFAULT")
    vector_db: str = Field(default="sqlite", env="VECTOR_DB")
    pgvector_enabled: bool = Field(default=False, env="PGVECTOR_ENABLED")
    database_url: str = Field(default="sqlite+aiosqlite:///./app.db", env="DATABASE_URL")
    sqlite_url: str = Field(default="sqlite:///./dev.db", env="SQLITE_URL")
    jwt_secret: str = Field(default="secret", env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=43200, env="JWT_EXPIRE_MINUTES")
    rate_limit_per_user: int = Field(default=30, env="AI_CHAT_MAX_REQUESTS")
    rate_limit_period: int = Field(default=600, env="AI_CHAT_PERIOD_SECONDS")
    reminder_hour_utc: int = Field(default=8, env="REMINDER_HOUR_UTC")
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: Optional[int] = Field(default=None, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_pass: Optional[str] = Field(default=None, env="SMTP_PASS")
    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, env="TELEGRAM_CHAT_ID")

    class Config:
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings(_env_file=os.getenv("ENV_FILE", ".env"), _env_file_encoding="utf-8")


settings = get_settings()
