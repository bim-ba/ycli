"""Env-driven configuration — parsed once into refined, immutable types.

Split deliberately: app config must be constructible WITHOUT credentials (the root CLI
callback configures logging on every invocation, including ``--help``), while credentials
are required only when an API call is made. ``Credentials`` has no defaults, so pydantic
enforces presence — no hand-written validation.

App settings are grouped, one model per concern, and read from ``YCLI__<GROUP>__<SETTING>``
(``YCLI__HTTP__TIMEOUT_SECONDS``, ``YCLI__LOGGING__LEVEL``). Keyword arguments use the same
shape: ``AppConfig(http={"timeout_seconds": 5})``. Credentials keep Yandex's own names
(``YANDEX_ID_OAUTH_TOKEN``) with a ``YCLI__AUTH__*`` fallback.

Examples:
    >>> AppConfig(http={"timeout_seconds": 5}).http.timeout_seconds
    5.0
"""

from __future__ import annotations

import os
from typing import Annotated, Literal

from dotenv import dotenv_values
from pydantic import (
    AliasChoices,
    AnyHttpUrl,
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
    # A listing that never ends by itself stops after this many pages.
    max_pages: PositiveInt = 1000
    # The longest pause a 429's Retry-After may ask for; a longer one fails at once.
    max_retry_after_seconds: PositiveFloat = 60.0

    def cap(self, limit: int, *, all_: bool = False) -> int | None:
        """A listing's item cap from a ``limit`` option and the CLI's ``--all`` flag.

        ``--all`` uncaps (``None``); a positive ``limit`` wins; otherwise ``max_items``. The MCP
        surface has no ``--all``, so it is always capped.

        Args:
            limit: The ``--limit`` option; zero or less means not given.
            all_: The CLI's ``--all`` flag.

        Returns:
            The most items to fetch, or ``None`` for no cap.

        Examples:
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


class MCPHTTPConfig(BaseSettings):
    """``ycli mcp start --transport http`` (``YCLI__MCP__*``): the server's address and signing key.

    ``base_url`` is the public HTTPS address MCP clients reach (the Yandex OAuth app's redirect
    URI is ``<base_url>/auth/callback``); ``host``/``port`` are where the process listens,
    behind the TLS proxy. ``organization_id`` is the one organization every caller works in.
    ``jwt_signing_key`` signs the server's own tokens (derived from the OAuth app's secret when
    unset); a verified Yandex token is trusted for ``token_cache_seconds`` before Yandex ID is
    asked again, so a revoked token keeps working at most that long.

    Examples:
        >>> MCPHTTPConfig(base_url="https://mcp.example.com", organization_id="1").port
        8000
    """

    model_config = SettingsConfigDict(
        env_prefix="YCLI__MCP__",
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        validate_by_name=True,
        frozen=True,
    )

    base_url: AnyHttpUrl
    organization_id: str = Field(
        min_length=1,
        validation_alias=AliasChoices(ORGANIZATION_ID_ENV, "YCLI__AUTH__ORGANIZATION_ID"),
    )
    host: str = "127.0.0.1"
    port: PositiveInt = 8000
    jwt_signing_key: SecretStr | None = None
    token_cache_seconds: NonNegativeInt = 300


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


def credential_sources() -> dict[str, str]:
    """Where each credential variable is set: ``environment``, ``.env file`` or ``not set``.

    Names only, never a value. A variable set but empty counts as not set, as it does for
    :class:`Credentials`.

    Returns:
        The source of each credential variable, by its name.
    """
    in_file = dotenv_values(".env")
    names = {
        OAUTH_TOKEN_ENV: (OAUTH_TOKEN_ENV, "YCLI__AUTH__OAUTH_TOKEN"),
        ORGANIZATION_ID_ENV: (ORGANIZATION_ID_ENV, "YCLI__AUTH__ORGANIZATION_ID"),
    }
    return {
        name: "environment"
        if any(os.environ.get(alias) for alias in aliases)
        else ".env file"
        if any(in_file.get(alias) for alias in aliases)
        else "not set"
        for name, aliases in names.items()
    }


def proxy_variables() -> list[str]:
    """The names of the proxy variables that are set: they change where a request goes.

    Returns:
        The names, as spelled in the environment.
    """
    known = ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "NO_PROXY")
    return [
        name
        for known_name in known
        for name in (known_name, known_name.lower())
        if os.environ.get(name)
    ]
