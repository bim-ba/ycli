"""Env-driven configuration — two single-purpose pydantic-settings models.

Split deliberately: app config must be constructible WITHOUT credentials (the root CLI
callback configures logging on every invocation, including ``--help``), while credentials
are required only when an API call is made. ``Credentials`` has no defaults, so pydantic
enforces presence — no hand-written validation.
"""

from __future__ import annotations

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ycli.yandex.auth import ServiceAccountCredentials


class AppConfig(BaseSettings):
    """Process-wide app configuration — always constructible, never needs credentials."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    timeout_seconds: float = Field(default=30.0, validation_alias="YCLI_TIMEOUT_SECONDS")
    retries: int = Field(default=3, validation_alias="YCLI_RETRIES")
    log_level: str = Field(default="INFO", validation_alias="YCLI_LOG_LEVEL")
    max_items: int = Field(default=500, validation_alias="YCLI_MAX_ITEMS")


class Credentials(BaseSettings):
    """OAuth, static IAM, or service-account IAM credentials plus one organization ID."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    oauth_token: str | None = Field(default=None, validation_alias="YANDEX_ID_OAUTH_TOKEN")
    organization_id: str | None = Field(
        default=None, validation_alias="YANDEX_ID_ORGANIZATION_ID"
    )
    iam_token: str | None = Field(default=None, validation_alias="YANDEX_CLOUD_IAM_TOKEN")
    cloud_organization_id: str | None = Field(
        default=None, validation_alias="YANDEX_CLOUD_ORGANIZATION_ID"
    )
    service_account_key_id: str | None = Field(
        default=None, validation_alias="YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_ID"
    )
    service_account_id: str | None = Field(
        default=None, validation_alias="YANDEX_CLOUD_SERVICE_ACCOUNT_ID"
    )
    service_account_private_key: str | None = Field(
        default=None, validation_alias="YANDEX_CLOUD_SERVICE_ACCOUNT_PRIVATE_KEY"
    )

    @field_validator("*", mode="before")
    @classmethod
    def _empty_is_absent(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def _validate_authentication(self) -> Credentials:
        service_account_values = (
            self.service_account_key_id,
            self.service_account_id,
            self.service_account_private_key,
        )
        configured_service_account_values = sum(
            value is not None for value in service_account_values
        )
        if (
            configured_service_account_values not in (0, 3)
            and not self.oauth_token
            and not self.iam_token
        ):
            raise ValueError(
                "YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_ID, YANDEX_CLOUD_SERVICE_ACCOUNT_ID, and "
                "YANDEX_CLOUD_SERVICE_ACCOUNT_PRIVATE_KEY must be set together"
            )
        if not self.oauth_token and not self.iam_token and configured_service_account_values == 0:
            raise ValueError(
                "set YANDEX_ID_OAUTH_TOKEN, YANDEX_CLOUD_IAM_TOKEN, or all Yandex Cloud "
                "service-account credentials"
            )
        if bool(self.organization_id) == bool(self.cloud_organization_id):
            raise ValueError(
                "set exactly one of YANDEX_ID_ORGANIZATION_ID or "
                "YANDEX_CLOUD_ORGANIZATION_ID"
            )
        if not self.oauth_token and not self.cloud_organization_id:
            raise ValueError("IAM authentication requires YANDEX_CLOUD_ORGANIZATION_ID")
        return self

    @property
    def service_account(self) -> ServiceAccountCredentials | None:
        if not all(
            (
                self.service_account_key_id,
                self.service_account_id,
                self.service_account_private_key,
            )
        ):
            return None
        assert self.service_account_key_id is not None
        assert self.service_account_id is not None
        assert self.service_account_private_key is not None
        return ServiceAccountCredentials(
            key_id=self.service_account_key_id,
            service_account_id=self.service_account_id,
            private_key=self.service_account_private_key,
        )

    @property
    def uses_service_account_iam(self) -> bool:
        return not self.oauth_token and not self.iam_token and self.service_account is not None


class OAuthAppConfig(BaseSettings):
    """The user's OWN Yandex OAuth application, used by ``ycli auth login``.

    Both are optional: with only ``client_id`` the browser (implicit) flow is used;
    adding ``client_secret`` enables the headless device flow. Nothing is baked in —
    the caller registers their app at https://oauth.yandex.ru.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    client_id: str | None = Field(default=None, validation_alias="YANDEX_OAUTH_CLIENT_ID")
    client_secret: str | None = Field(default=None, validation_alias="YANDEX_OAUTH_CLIENT_SECRET")
