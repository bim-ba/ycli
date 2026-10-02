"""Env-driven configuration — parsed once into refined, immutable types.

Split deliberately: app config must be constructible WITHOUT credentials (the root CLI
callback configures logging on every invocation, including ``--help``), while credentials
are required only when an API call is made. ``Credentials`` has no defaults, so pydantic
enforces presence — no hand-written validation.

App settings are grouped, one model per concern, and read from ``YCLI__<GROUP>__<SETTING>``
(``YCLI__HTTP__TIMEOUT_SECONDS``, ``YCLI__LOGGING__LEVEL``). Keyword arguments use the same
shape: ``AppConfig(http={"timeout_seconds": 5})``. Credentials keep Yandex's own names
(``YANDEX_ID_OAUTH_TOKEN``) with a ``YCLI__AUTH__*`` fallback.

Example:
    >>> AppConfig(http={"timeout_seconds": 5}).http.timeout_seconds
    5.0
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
    SecretStr,
    ValidationError,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# Yandex's own names for the credential variables; everything that names them imports these.
OAUTH_TOKEN_ENV = "YANDEX_ID_OAUTH_TOKEN"
ORGANIZATION_ID_ENV = "YANDEX_ID_ORGANIZATION_ID"

# pydantic-settings reports a missing field under its validation alias (the env var name), so a
# ``ValidationError`` loc is already one of these strings.
_CREDENTIAL_ENV_NAMES = frozenset({OAUTH_TOKEN_ENV, ORGANIZATION_ID_ENV})

type LogLevel = Annotated[
    Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    BeforeValidator(lambda value: value.upper() if isinstance(value, str) else value),
]


class HTTPConfig(BaseModel):
    """How ycli talks to the Yandex APIs (``YCLI__HTTP__*``)."""

    model_config = ConfigDict(frozen=True)

    timeout_seconds: PositiveFloat = 30.0
    retries: NonNegativeInt = 3
    max_items: PositiveInt = 500

    def cap(self, limit: int, *, all_: bool = False) -> int | None:
        """A listing's item cap from a ``limit`` option and the CLI's ``--all`` flag.

        ``--all`` uncaps (``None``); a positive ``limit`` wins; otherwise ``max_items``. The MCP
        surface has no ``--all``, so it is always capped.

        Example:
            >>> (
            ...     HTTPConfig(max_items=500).cap(0),
            ...     HTTPConfig().cap(10),
            ...     HTTPConfig().cap(10, all_=True),
            ... )
            (500, 10, None)
        """
        return None if all_ else (limit if limit > 0 else self.max_items)


class LoggingConfig(BaseModel):
    """Diagnostic output on stderr (``YCLI__LOGGING__*``)."""

    model_config = ConfigDict(frozen=True)

    level: LogLevel = "WARNING"
    format: Literal["text", "json"] = "text"


class AppConfig(BaseSettings):
    """Process-wide app configuration — always constructible, never needs credentials."""

    model_config = SettingsConfigDict(
        env_prefix="YCLI__",
        env_nested_delimiter="__",
        env_nested_max_split=1,
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    http: HTTPConfig = HTTPConfig()
    logging: LoggingConfig = LoggingConfig()


class Credentials(BaseSettings):
    """Yandex 360 credentials — required; pydantic raises if either is absent or empty."""

    # env_ignore_empty: an exported-but-empty variable reads as "not set", so the CLI routes it
    # to the same "run `ycli auth login`" hint as a missing one.
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore", validate_by_name=True, frozen=True
    )

    oauth_token: SecretStr = Field(
        min_length=1,
        validation_alias=AliasChoices(OAUTH_TOKEN_ENV, "YCLI__AUTH__OAUTH_TOKEN"),
    )
    organization_id: str = Field(
        min_length=1,
        validation_alias=AliasChoices(ORGANIZATION_ID_ENV, "YCLI__AUTH__ORGANIZATION_ID"),
    )


class OAuthAppConfig(BaseSettings):
    """The user's OWN Yandex OAuth application, used by ``ycli auth login``.

    Both are optional: with only ``client_id`` the browser (implicit) flow is used;
    adding ``client_secret`` enables the headless device flow. Nothing is baked in —
    the caller registers their app at https://oauth.yandex.ru.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore", validate_by_name=True, frozen=True
    )

    client_id: str | None = Field(default=None, validation_alias="YANDEX_OAUTH_CLIENT_ID")
    client_secret: SecretStr | None = Field(
        default=None, validation_alias="YANDEX_OAUTH_CLIENT_SECRET"
    )


def missing_credentials(exc: Exception) -> list[str]:
    """The credential variables a ``ValidationError`` from :class:`Credentials` reports missing.

    Both unset gives ``["YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID"]``; any other
    exception, or an error about another field, gives ``[]``.
    """
    if not isinstance(exc, ValidationError):
        return []
    return [
        name
        for error in exc.errors()
        if error.get("type") == "missing"
        and error["loc"]
        and (name := str(error["loc"][0])) in _CREDENTIAL_ENV_NAMES
    ]
