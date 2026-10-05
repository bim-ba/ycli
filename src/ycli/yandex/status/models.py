"""Models for `ycli auth status` and the `status_get` MCP tool."""

from typing import Literal

from pydantic import Field

from ycli.settings import CredentialKind, OrganizationKind
from ycli.yandex.models import APIModel


class Identity(APIModel):
    """Who owns the token — Yandex ID's ``GET https://login.yandex.ru/info`` answer.

    Any valid token returns ``id``, ``login`` and ``client_id`` (the OAuth app it was issued to);
    the rest needs the ``login:*`` scopes (``login:info`` for the names, ``login:email`` for the
    address).

    Examples:
        >>> Identity.model_validate({"id": "1000034426", "login": "ivan", "psuid": "x"}).login
        'ivan'
    """

    id: str = Field(description="Yandex ID of the user.")
    login: str = Field(description="Yandex login of the user.")
    client_id: str | None = Field(
        default=None, description="Id of the OAuth app the token was issued to."
    )
    display_name: str | None = Field(
        default=None, description="Name to show for the user (needs `login:info`)."
    )
    real_name: str | None = Field(
        default=None, description="Real name of the user (needs `login:info`)."
    )
    default_email: str | None = Field(
        default=None, description="Default email address of the user (needs `login:email`)."
    )


class OrganizationStatus(APIModel):
    """The configured organization: its id, and its name when API 360 could say.

    ``detail`` says why the name is unknown (the token lacks ``directory:read_organization``).
    """

    id: str = Field(description="Id of the organization.")
    kind: OrganizationKind = Field(
        default=OrganizationKind.YANDEX_360,
        description="Where the organization lives: Yandex 360 or Yandex Cloud.",
    )
    name: str | None = Field(
        default=None, description="Name of the organization; `null` when it could not be read."
    )
    detail: str = Field(default="", description="Why the name is unknown; empty when it was read.")


class ServiceAuthStatus(APIModel):
    """One service's probe: whether the token works there, or why not.

    A service the credentials cannot reach as they are (no organization of its kind, or a
    token it does not take) is not probed: ``configured`` is ``False`` and ``detail`` says
    what to set. That is not a failure of the others.
    """

    service: str = Field(description="Service probed, e.g. `tracker`.")
    valid: bool = Field(default=False, description="Whether the token works in the service.")
    configured: bool = Field(
        default=True,
        description="`false` when the credentials cannot reach the service as they are: "
        "it was not probed, and `detail` says what to set.",
    )
    detail: str = Field(
        default="",
        description="Why the probe failed, or what a service that is not configured needs; "
        "empty when it passed.",
    )


class AuthReport(APIModel):
    """Whether the credentials are set, whose they are, and which services accept them."""

    configured: bool = Field(description="Whether a credential is set.")
    credential: CredentialKind | None = Field(
        default=None, description="Which token is in use; never its value."
    )
    profile: str | None = Field(
        default=None, description="The named profile the credentials come from, if any."
    )
    identity: Identity | None = Field(
        default=None, description="Who owns the token; `null` when it could not be read."
    )
    organization: OrganizationStatus | None = Field(
        default=None, description="The configured organization."
    )
    cloud_organization: OrganizationStatus | None = Field(
        default=None,
        description="The Yandex Cloud organization, when configured beside a Yandex 360 one.",
    )
    services: list[ServiceAuthStatus] = Field(
        default_factory=list, description="One probe per service, in the order they ran."
    )


class SavedProfile(APIModel):
    """One saved profile, as ``ycli auth profiles`` lists it: never the token itself.

    Examples:
        >>> SavedProfile(name="work", organization_id="1", credential="oauth").active
        False
    """

    name: str = Field(description="Name of the profile.")
    organization_id: str | None = Field(
        default=None, description="`null` when the profile's file cannot be used."
    )
    organization_kind: OrganizationKind | None = Field(
        default=None, description="Where that organization lives: Yandex 360 or Yandex Cloud."
    )
    credential: CredentialKind | None = Field(
        default=None, description="Which token the profile holds; never its value."
    )
    active: bool = Field(
        default=False, description="Whether `--profile` or `YCLI_PROFILE` names this profile."
    )


class Check(APIModel):
    """One thing ``ycli doctor`` checked: what it found and, when it is wrong, what to do."""

    check: str = Field(description="What was checked: `token`, `service:tracker`, `extra:mcp`.")
    status: Literal["ok", "warn", "fail", "skipped"] = Field(
        description="`fail` breaks a call, `warn` does not, `skipped` could not run."
    )
    detail: str = Field(default="", description="What was found, or why the check was skipped.")
    fix: str | None = Field(default=None, description="What to do about a `warn` or a `fail`.")


class DoctorReport(APIModel):
    """Every check of ``ycli doctor`` in the order it ran.

    Examples:
        >>> DoctorReport(ok=True, checks=[Check(check="token", status="ok")]).checks[0].status
        'ok'
    """

    ok: bool = Field(description="`false` when a check failed.")
    checks: list[Check] = Field(default_factory=list, description="The checks, in order.")
