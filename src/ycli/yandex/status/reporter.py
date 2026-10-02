"""Probe the services and read the token's owner and organization (shared by CLI + MCP)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.factory import build_client
from ycli.yandex.registry import SERVICES
from ycli.yandex.status.models import (
    AuthReport,
    Identity,
    OrganizationStatus,
    ServiceAuthStatus,
)
from ycli.yandex.status.token_client import TokenClient

if TYPE_CHECKING:
    from ycli.settings import AppConfig, Credentials
    from ycli.yandex.base import DomainClient

logger = logging.getLogger("ycli.status")

ORGANIZATION_SCOPE = "directory:read_organization"


def probe_service(name: str, client: DomainClient) -> ServiceAuthStatus:
    """Whether ``client``'s token works for its service: its own ``probe()``, as a status.

    A 401 gives ``valid=False, detail="token invalid or expired"``; any other failure keeps its
    message in ``detail``.
    """
    try:
        client.probe()
    except YandexAuthError:
        return ServiceAuthStatus(service=name, detail="token invalid or expired")
    except YandexError as exc:
        return ServiceAuthStatus(service=name, detail=str(exc))
    return ServiceAuthStatus(service=name, valid=True)


def build_report(credentials: Credentials, config: AppConfig) -> AuthReport:
    """The full report: owner (Yandex ID), organization (API 360) and one probe per service.

    The owner and the organization are context, not a verdict: when either read fails the report
    still carries every service's probe.
    """
    token = credentials.oauth_token.get_secret_value()
    with TokenClient(oauth_token=token, http=config.http) as token_client:
        identity = _identity(token_client)
        organization = _organization(token_client, credentials.organization_id)
    services = []
    for service in SERVICES:
        with build_client(service.client_class(), credentials, config) as client:
            services.append(probe_service(service.name, client))
    return AuthReport(
        configured=True, identity=identity, organization=organization, services=services
    )


def _identity(token_client: TokenClient) -> Identity | None:
    """The token's owner; ``None`` when Yandex ID would not say (the service probes say why)."""
    try:
        return token_client.identity()
    except YandexError as exc:
        logger.warning("could not read the token's owner from Yandex ID: %s", exc)
        return None


def _organization(token_client: TokenClient, organization_id: str) -> OrganizationStatus:
    """The configured organization with its name, or its id alone and a note saying why."""
    try:
        organizations = token_client.organizations()
    except YandexAuthError:
        return OrganizationStatus(
            id=organization_id,
            detail=f"name unknown: the token lacks the {ORGANIZATION_SCOPE} scope",
        )
    except YandexError as exc:
        return OrganizationStatus(id=organization_id, detail=f"name unknown: {exc}")
    listed = next((org for org in organizations if str(org.id) == organization_id), None)
    if listed is None:
        return OrganizationStatus(
            id=organization_id, detail="name unknown: the token's organizations do not list it"
        )
    return OrganizationStatus(id=organization_id, name=listed.name)
