"""Models for `ycli auth status` and the `status_get` MCP tool."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

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

    id: str
    login: str
    client_id: str | None = None
    display_name: str | None = None
    real_name: str | None = None
    default_email: str | None = None


class OrganizationStatus(APIModel):
    """The configured organization: its id, and its name when API 360 could say.

    ``detail`` says why the name is unknown (the token lacks ``directory:read_organization``).
    """

    id: str
    name: str | None = None
    detail: str = ""


class ServiceAuthStatus(APIModel):
    """One service's probe: whether the token works there, or why not."""

    service: str
    valid: bool = False
    detail: str = ""


class AuthReport(APIModel):
    """Whether the credentials are set, whose they are, and which services accept them."""

    configured: bool
    identity: Identity | None = None
    organization: OrganizationStatus | None = None
    services: list[ServiceAuthStatus] = Field(default_factory=list)


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
