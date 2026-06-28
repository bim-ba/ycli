"""Env-driven configuration — two single-purpose pydantic-settings models.

Split deliberately: app config must be constructible WITHOUT credentials (the root CLI
callback configures logging on every invocation, including ``--help``), while credentials
are required only when an API call is made. ``Credentials`` has no defaults, so pydantic
enforces presence — no hand-written validation.
"""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Process-wide app configuration — always constructible, never needs credentials."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    timeout_seconds: float = Field(default=30.0, validation_alias="YCLI_TIMEOUT_SECONDS")
    retries: int = Field(default=3, validation_alias="YCLI_RETRIES")
    log_level: str = Field(default="INFO", validation_alias="YCLI_LOG_LEVEL")


class Credentials(BaseSettings):
    """Yandex 360 credentials — required; pydantic raises if either env var is absent."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    oauth_token: str = Field(validation_alias="YANDEX_ID_OAUTH_TOKEN")
    organization_id: str = Field(validation_alias="YANDEX_ID_ORGANIZATION_ID")
