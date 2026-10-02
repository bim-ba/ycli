"""Models for `ycli auth status` and the `status_get` MCP tool."""

from __future__ import annotations

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
