"""Env-driven configuration — parsed once into refined, immutable types.

Split deliberately: app config must be constructible WITHOUT credentials (the root CLI
callback configures logging on every invocation, including ``--help``), while credentials
are required only when an API call is made. ``Credentials`` has no defaults, so pydantic
enforces presence — no hand-written validation.

App settings are grouped, one model per concern, and read from ``YCLI__<GROUP>__<SETTING>``
(``YCLI__HTTP__TIMEOUT_SECONDS``, ``YCLI__LOGGING__LEVEL``). Keyword arguments use the same
shape: ``AppConfig(http={"timeout_seconds": 5})``. Credentials keep Yandex's own names
(``YANDEX_ID_OAUTH_TOKEN``) with a ``YCLI__AUTH__*`` fallback.

A named profile (``--profile`` / ``YCLI_PROFILE``) is a dotenv file with the same credential
variables under :func:`profiles_directory`. Once one is named it is the only source of the
token and the organization: the environment and ``.env`` are not read for them.

Examples:
    >>> AppConfig(http={"timeout_seconds": 5}).http.timeout_seconds
    5.0
"""

import enum
import os
import re
from pathlib import Path
from typing import Annotated, Self

from dotenv import dotenv_values
from platformdirs import user_config_path
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
    PrivateAttr,
    SecretStr,
    ValidationError,
    ValidationInfo,
    field_validator,
)
from pydantic_core import ErrorDetails, PydanticCustomError
from pydantic_settings import BaseSettings, SettingsConfigDict

from ycli.log import LogFormat, LogLevel

# Yandex's own names for the credential variables; everything that names them imports these.
OAUTH_TOKEN_ENV = "YANDEX_ID_OAUTH_TOKEN"
ORGANIZATION_ID_ENV = "YANDEX_ID_ORGANIZATION_ID"
# A ready IAM token (`yc iam create-token`), used in place of the OAuth token.
IAM_TOKEN_ENV = "YANDEX_CLOUD_IAM_TOKEN"
# A service account's authorized key (`yc iam key create`): the file, or its JSON itself.
SERVICE_ACCOUNT_KEY_FILE_ENV = "YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_FILE"
SERVICE_ACCOUNT_KEY_ENV = "YANDEX_CLOUD_SERVICE_ACCOUNT_KEY"
# A Yandex Cloud organization, where a service does not live in a Yandex 360 one.
CLOUD_ORGANIZATION_ID_ENV = "YANDEX_CLOUD_ORGANIZATION_ID"
# The profile to use when ``--profile`` is not given.
PROFILE_ENV = "YCLI_PROFILE"
# Every name a credential is read under: Yandex's own first, then ycli's fallback.
_OAUTH_TOKEN_NAMES = (OAUTH_TOKEN_ENV, "YCLI__AUTH__OAUTH_TOKEN")
_ORGANIZATION_ID_NAMES = (ORGANIZATION_ID_ENV, "YCLI__AUTH__ORGANIZATION_ID")
# A profile's name is a file name: nothing in it can leave the profiles directory.
_PROFILE_NAME_RE = re.compile(r"[a-z0-9][a-z0-9_-]*")
_PROFILE_SUFFIX = ".env"

# pydantic-settings reports a missing field under its validation alias (the env var name), so a
# ``ValidationError`` loc is already one of these strings.
_CREDENTIAL_ENV_NAMES = frozenset({OAUTH_TOKEN_ENV, ORGANIZATION_ID_ENV})
# Every credential variable, in the order a report names them: the ways to sign in, then the
# organizations.
_CREDENTIAL_NAMES = (
    OAUTH_TOKEN_ENV,
    IAM_TOKEN_ENV,
    SERVICE_ACCOUNT_KEY_FILE_ENV,
    SERVICE_ACCOUNT_KEY_ENV,
    ORGANIZATION_ID_ENV,
    CLOUD_ORGANIZATION_ID_ENV,
)
# The ways to sign in, by the variable that carries each: exactly one is set.
_SIGN_IN_ENV_NAMES = {
    "oauth_token": OAUTH_TOKEN_ENV,
    "iam_token": IAM_TOKEN_ENV,
    "service_account_key_file": SERVICE_ACCOUNT_KEY_FILE_ENV,
    "service_account_key": SERVICE_ACCOUNT_KEY_ENV,
}
NOT_SET = "not set"
# The error type of credentials with no token at all (the OAuth token is the one asked for).
NO_TOKEN = "no_token"
# The error type of credentials that name no organization of either kind.
NO_ORGANIZATION = "no_organization"


class CredentialKind(enum.StrEnum):
    """Which token the credentials hold."""

    OAUTH = "oauth"
    IAM = "iam"
    SERVICE_ACCOUNT = "service_account"


class OrganizationKind(enum.StrEnum):
    """Where an organization lives: Yandex 360 or Yandex Cloud."""

    YANDEX_360 = "360"
    CLOUD = "cloud"


# `YCLI__LOGGING__LEVEL=debug` is read as DEBUG.
type AnyCaseLogLevel = Annotated[
    LogLevel,
    BeforeValidator(lambda value: value.upper() if isinstance(value, str) else value),
]


class HTTPConfig(BaseModel):
    """How ycli talks to the Yandex APIs (``YCLI__HTTP__*``)."""

    model_config = ConfigDict(frozen=True)

    timeout_seconds: PositiveFloat = 30.0
    retries: NonNegativeInt = 3
    max_items: PositiveInt = 500
    # What a tool gives when no `limit` is asked: its answer is read whole into a context.
    max_tool_items: PositiveInt = 50
    # A listing that never ends by itself stops after this many pages.
    max_pages: PositiveInt = 1000
    # The longest `next` token read: a caller far away sends it, so it is bounded before decoding.
    max_token_length: PositiveInt = 16_384
    # The longest pause a 429's Retry-After may ask for; a longer one fails at once.
    max_retry_after_seconds: PositiveFloat = 60.0
    # How long `--wait` polls a long operation (an export, a clone, a bulk change) before giving up.
    max_wait_seconds: PositiveFloat = 1380.0

    def cap(self, limit: int | None, *, all_: bool = False) -> int | None:
        """A listing's item cap from ``limit`` and "everything", on the CLI.

        "Everything" uncaps (``None``); a given ``limit`` wins; otherwise ``max_items``.

        Args:
            limit: The ``--limit`` option; ``None`` when not given.
            all_: The ``--all`` flag.

        Returns:
            The most items to fetch, or ``None`` for no cap.

        Examples:
            >>> (
            ...     HTTPConfig(max_items=500).cap(None),
            ...     HTTPConfig().cap(10),
            ...     HTTPConfig().cap(10, all_=True),
            ... )
            (500, 10, None)
        """
        return None if all_ else (self.max_items if limit is None else limit)

    def tool_cap(self, limit: int | None, *, all_: bool = False) -> int | None:
        """:meth:`cap` for a tool of the MCP server: ``max_tool_items`` where no limit is given.

        Args:
            limit: The tool's ``limit``; ``None`` when not given.
            all_: The tool's ``all``.

        Returns:
            The most items to fetch, or ``None`` for no cap.

        Examples:
            >>> tools = HTTPConfig()
            >>> tools.tool_cap(None), tools.tool_cap(10), tools.tool_cap(1, all_=True)
            (50, 10, None)
        """
        return None if all_ else (self.max_tool_items if limit is None else limit)


# `ycli doctor` asks PyPI for the latest release: one short attempt, so it never holds the report.
RELEASE_CHECK_HTTP = HTTPConfig(timeout_seconds=3.0, retries=0)


class LoggingConfig(BaseModel):
    """Diagnostic output on stderr (``YCLI__LOGGING__*``)."""

    model_config = ConfigDict(frozen=True)

    level: AnyCaseLogLevel = LogLevel.WARNING
    format: LogFormat = LogFormat.TEXT


class _EnvSettings(BaseSettings):
    """What every settings model shares: read ``.env`` too, and stay immutable.

    ``env_ignore_empty``: an exported-but-empty variable reads as "not set", so the CLI routes
    it to the same "run `ycli auth login`" hint as a missing one. ``hide_input_in_errors``: a
    value that fails validation here may be a token, and the text of a ``ValidationError``
    would quote it.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        validate_by_name=True,
        frozen=True,
        hide_input_in_errors=True,
    )


class AppConfig(_EnvSettings):
    """Process-wide app configuration — always constructible, never needs credentials."""

    model_config = SettingsConfigDict(
        env_prefix="YCLI__", env_nested_delimiter="__", env_nested_max_split=1
    )

    http: HTTPConfig = HTTPConfig()
    logging: LoggingConfig = LoggingConfig()


class ProfileError(ValueError):
    """A named profile cannot be used: a bad name, no such profile, or a file missing a value."""


class _ProfileSelection(_EnvSettings):
    """The profile named outside the command line: ``YCLI_PROFILE``, environment or ``.env``."""

    name: str | None = Field(default=None, validation_alias=PROFILE_ENV)


def profiles_directory() -> Path:
    """Where profiles live: ``profiles`` under the user's configuration directory for ycli."""
    return user_config_path("ycli") / "profiles"


def profile_path(name: str) -> Path:
    """The dotenv file of the profile ``name``, whether it exists or not.

    Args:
        name: The profile's name: lowercase letters, digits, ``-`` and ``_``.

    Returns:
        The file's path under :func:`profiles_directory`.

    Raises:
        ProfileError: ``name`` is not a valid profile name.

    Examples:
        >>> profile_path("work").name
        'work.env'
    """
    if not _PROFILE_NAME_RE.fullmatch(name):
        raise ProfileError(
            f"{name!r} is not a profile name: use lowercase letters, digits, '-' and '_'"
        )
    return profiles_directory() / f"{name}{_PROFILE_SUFFIX}"


def profile_names() -> list[str]:
    """The names of the saved profiles, sorted; empty when there is no profiles directory."""
    return sorted(
        path.name.removesuffix(_PROFILE_SUFFIX)
        for path in profiles_directory().glob(f"*{_PROFILE_SUFFIX}")
    )


def active_profile(named: str | None = None) -> str | None:
    """The profile in use: ``named`` (``--profile``), else ``YCLI_PROFILE``, else ``None``."""
    return named or _ProfileSelection().name


def name_profile(name: str) -> None:
    """Make ``name`` the profile of this process, as ``YCLI_PROFILE`` would.

    For ``ycli mcp start --profile``: the server's providers read the credentials on every
    tool call, long after the command line was parsed.
    """
    os.environ[PROFILE_ENV] = name


class Credentials(_EnvSettings):
    """Yandex credentials: one way to sign in and an organization; pydantic raises without them.

    The way to sign in is an OAuth token, a ready IAM token or a service account's key, exactly
    one: two would leave it to chance which a request carries. The organization is a Yandex 360
    one, a Yandex Cloud one, or both: a service takes the kind it lives in
    (:meth:`ycli.yandex.core.profile.ServiceProfile.headers_for`). :attr:`kind` is the parsed
    result.

    Examples:
        >>> Credentials(oauth_token=None, iam_token="t1.x", organization_id="1").kind
        <CredentialKind.IAM: 'iam'>
    """

    iam_token: SecretStr | None = Field(default=None, min_length=1, validation_alias=IAM_TOKEN_ENV)
    service_account_key_file: Path | None = Field(
        default=None, validation_alias=SERVICE_ACCOUNT_KEY_FILE_ENV
    )
    service_account_key: SecretStr | None = Field(
        default=None, min_length=1, validation_alias=SERVICE_ACCOUNT_KEY_ENV
    )
    cloud_organization_id: str | None = Field(
        default=None, min_length=1, validation_alias=CLOUD_ORGANIZATION_ID_ENV
    )
    oauth_token: SecretStr | None = Field(
        default=None,
        min_length=1,
        validate_default=True,  # so that no token at all is reported beside a missing organization
        validation_alias=AliasChoices(*_OAUTH_TOKEN_NAMES),
    )
    organization_id: str | None = Field(
        default=None,
        min_length=1,
        validate_default=True,  # so that no organization at all is reported
        validation_alias=AliasChoices(*_ORGANIZATION_ID_NAMES),
    )

    _profile: str | None = PrivateAttr(default=None)

    @field_validator("oauth_token", mode="after")
    @classmethod
    def _exactly_one_way_to_sign_in(
        cls, oauth_token: SecretStr | None, info: ValidationInfo
    ) -> SecretStr | None:
        # The other three are declared first, so they are already parsed.
        given = {**info.data, "oauth_token": oauth_token}
        names = [env for field, env in _SIGN_IN_ENV_NAMES.items() if given.get(field) is not None]
        if not names:
            raise PydanticCustomError(NO_TOKEN, f"{OAUTH_TOKEN_ENV} is not set")
        if len(names) > 1:
            raise PydanticCustomError(
                "two_tokens",
                "{names} are both set: keep one of them",
                {"names": " and ".join(names)},
            )
        return oauth_token

    @field_validator("organization_id", mode="after")
    @classmethod
    def _an_organization(cls, organization_id: str | None, info: ValidationInfo) -> str | None:
        if organization_id is None and info.data.get("cloud_organization_id") is None:
            raise PydanticCustomError(NO_ORGANIZATION, f"{ORGANIZATION_ID_ENV} is not set")
        return organization_id

    @classmethod
    def load(cls, profile: str | None = None) -> Self:
        """The credentials of this invocation: the active profile's, else the environment's.

        Args:
            profile: The ``--profile`` option; ``None`` leaves the choice to ``YCLI_PROFILE``.

        Returns:
            The credentials of the active profile, or of the environment when none is named.
        """
        name = active_profile(profile)
        return cls() if name is None else cls.from_profile(name)

    @classmethod
    def from_profile(cls, name: str) -> Self:
        """The credentials saved as the profile ``name``; the environment is not consulted.

        Args:
            name: The profile's name.

        Returns:
            The profile's credentials, with :attr:`profile` set.

        Raises:
            ProfileError: There is no such profile, or its file does not hold one token and
                the organization.

        Examples:
            >>> Credentials.from_profile("work").profile  # doctest: +SKIP
            'work'
        """
        path = profile_path(name)
        if not path.is_file():
            saved = ", ".join(profile_names()) or "none"
            raise ProfileError(
                f"profile {name!r} not found in {path.parent} (saved profiles: {saved})"
            )
        saved_values = dotenv_values(path)

        def secret(name: str) -> SecretStr | None:
            value = saved_values.get(name)
            return SecretStr(value) if value else None

        key_file = saved_values.get(SERVICE_ACCOUNT_KEY_FILE_ENV)
        try:
            # Every field is passed, so nothing falls through to the environment.
            credentials = cls(
                oauth_token=secret(OAUTH_TOKEN_ENV),
                iam_token=secret(IAM_TOKEN_ENV),
                service_account_key_file=Path(key_file) if key_file else None,
                service_account_key=secret(SERVICE_ACCOUNT_KEY_ENV),
                organization_id=saved_values.get(ORGANIZATION_ID_ENV) or None,
                cloud_organization_id=saved_values.get(CLOUD_ORGANIZATION_ID_ENV) or None,
            )
        except ValidationError as exc:
            problems = "; ".join(
                f"{ORGANIZATION_ID_ENV} is not set"
                if error["loc"] == ("organization_id",)
                else error["msg"]
                for error in exc.errors()
            )
            raise ProfileError(f"profile {name!r} ({path}): {problems}") from exc
        credentials._profile = name
        return credentials

    @property
    def profile(self) -> str | None:
        """The profile these credentials were read from; ``None`` for the environment."""
        return self._profile

    @property
    def kind(self) -> CredentialKind:
        """Which way to sign in this is: ``oauth``, ``iam`` or ``service_account``."""
        if self.oauth_token is not None:
            return CredentialKind.OAUTH
        return CredentialKind.IAM if self.iam_token is not None else CredentialKind.SERVICE_ACCOUNT

    @property
    def organization(self) -> tuple[str, OrganizationKind]:
        """The organization to show first: the Yandex 360 one when set, else the Cloud one."""
        if self.organization_id is not None:
            return self.organization_id, OrganizationKind.YANDEX_360
        assert self.cloud_organization_id is not None  # _an_organization
        return self.cloud_organization_id, OrganizationKind.CLOUD

    @property
    def token(self) -> SecretStr:
        """The OAuth or IAM token; a service account has a key instead (see :attr:`kind`)."""
        token = self.oauth_token or self.iam_token
        assert token is not None  # the caller asks only for the token kinds
        return token


class OAuthAppConfig(_EnvSettings):
    """The user's OWN Yandex OAuth application, used by ``ycli auth login``.

    Both are optional: with only ``client_id`` the browser (implicit) flow is used;
    adding ``client_secret`` enables the headless device flow. Nothing is baked in —
    the caller registers their app at https://oauth.yandex.ru.
    """

    client_id: str | None = Field(default=None, validation_alias="YANDEX_OAUTH_CLIENT_ID")
    client_secret: SecretStr | None = Field(
        default=None, validation_alias="YANDEX_OAUTH_CLIENT_SECRET"
    )


class MCPHTTPConfig(_EnvSettings):
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

    model_config = SettingsConfigDict(env_prefix="YCLI__MCP__")

    base_url: AnyHttpUrl
    organization_id: str = Field(
        min_length=1,
        validation_alias=AliasChoices(*_ORGANIZATION_ID_NAMES),
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
        name for error in exc.errors() if (name := _missing_name(error)) in _CREDENTIAL_ENV_NAMES
    ]


def _missing_name(error: ErrorDetails) -> str:
    """The credential variable ``error`` reports missing, or ``""``."""
    if error.get("type") == NO_TOKEN:
        return OAUTH_TOKEN_ENV
    if error.get("type") == NO_ORGANIZATION:
        return ORGANIZATION_ID_ENV
    return str(error["loc"][0]) if error.get("type") == "missing" and error["loc"] else ""


def credential_sources(profile: str | None = None) -> dict[str, str]:
    """Where each credential variable is set: ``environment``, ``.env file`` or ``not set``.

    Names only, never a value. A variable set but empty counts as not set, as it does for
    :class:`Credentials`. With a profile it is ``profile <name>`` or ``not set``: nothing else
    is read.

    Args:
        profile: The active profile, or ``None``.

    Returns:
        The source of each credential variable, by its name.
    """
    if profile is not None:
        return _profile_sources(profile)
    in_file = dotenv_values(".env")
    aliases_of = {OAUTH_TOKEN_ENV: _OAUTH_TOKEN_NAMES, ORGANIZATION_ID_ENV: _ORGANIZATION_ID_NAMES}
    names = {name: aliases_of.get(name, (name,)) for name in _CREDENTIAL_NAMES}
    sources = {
        name: "environment"
        if any(os.environ.get(alias) for alias in aliases)
        else ".env file"
        if any(in_file.get(alias) for alias in aliases)
        else NOT_SET
        for name, aliases in names.items()
    }
    return _named_once(sources)


def _profile_sources(profile: str) -> dict[str, str]:
    """:func:`credential_sources` of a named profile; a profile that cannot be read sets nothing."""
    try:
        saved_values = dotenv_values(profile_path(profile))
    except ProfileError:
        saved_values = {}
    return _named_once(
        {
            name: f"profile {profile}" if saved_values.get(name) else NOT_SET
            for name in _CREDENTIAL_NAMES
        }
    )


def _named_once(sources: dict[str, str]) -> dict[str, str]:
    """One way to sign in and one organization are enough: an unset alternative is left out.

    ``YANDEX_ID_OAUTH_TOKEN`` and ``YANDEX_ID_ORGANIZATION_ID`` stand for their groups when
    nothing of the group is set, so that the report always says what is missing.
    """
    for group in (_CREDENTIAL_NAMES[:4], _CREDENTIAL_NAMES[4:]):
        some_set = any(sources[name] != NOT_SET for name in group)
        for name in group[1:] if not some_set else group:
            if sources[name] == NOT_SET:
                del sources[name]
    return sources


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
