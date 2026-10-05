"""Probe the services and read the token's owner and organization (shared by CLI + MCP)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ycli.settings import OrganizationKind
from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.factory import build_client, not_configured
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
# The detail of a probe whose service rejected the token (401/403), as opposed to any other failure.
TOKEN_REJECTED = "token invalid or expired"
IAM_ORGANIZATION = "name unknown: API 360 names an organization for an OAuth token only"
CLOUD_ORGANIZATION = "name unknown: API 360 names Yandex 360 organizations only"


def probe_service(name: str, client: DomainClient) -> ServiceAuthStatus:
    """Whether ``client``'s token works for its service: its own ``probe()``, as a status.

    A 401 gives ``valid=False, detail="token invalid or expired"``; any other failure keeps its
    message in ``detail``.
    """
    error = probe_error(client)
    if error is None:
        return ServiceAuthStatus(service=name, valid=True)
    detail = TOKEN_REJECTED if isinstance(error, YandexAuthError) else str(error)
    return ServiceAuthStatus(service=name, detail=detail)


def probe_error(client: DomainClient) -> YandexError | None:
    """What ``client``'s own ``probe()`` raised, or ``None`` when the service accepts the token."""
    try:
        client.probe()
    except YandexError as error:
        return error
    return None


def build_report(credentials: Credentials, config: AppConfig) -> AuthReport:
    """The full report: owner (Yandex ID), organization (API 360) and one probe per service.

    The owner and the organization are context, not a verdict: when either read fails the report
    still carries every service's probe. A service the credentials cannot reach is listed as
    not configured, with what it needs, and is not probed.
    """
    identity, organization = owner_and_organization(credentials, config)
    services = []
    for service in SERVICES:
        reason = not_configured(service.profile, credentials)
        if reason:
            services.append(
                ServiceAuthStatus(service=service.name, configured=False, detail=reason)
            )
            continue
        with build_client(service.client_class(), credentials, config) as client:
            services.append(probe_service(service.name, client))
    return AuthReport(
        configured=True,
        credential=credentials.kind,
        profile=credentials.profile,
        identity=identity,
        organization=organization,
        cloud_organization=_cloud_beside(credentials),
        services=services,
    )


def owner_and_organization(
    credentials: Credentials, config: AppConfig
) -> tuple[Identity | None, OrganizationStatus]:
    """The token's owner and the organization's name, where the token can tell.

    Yandex ID and API 360 take an OAuth token only (measured: both answer an IAM token with
    401), so with an IAM token neither is asked and the organization keeps its id alone.
    """
    organization_id, kind = credentials.organization
    if credentials.oauth_token is None:
        detail = IAM_ORGANIZATION if kind is OrganizationKind.YANDEX_360 else CLOUD_ORGANIZATION
        return None, OrganizationStatus(id=organization_id, kind=kind, detail=detail)
    token = credentials.oauth_token.get_secret_value()
    with TokenClient(oauth_token=token, http=config.http) as token_client:
        identity = _identity(token_client)
        if kind is OrganizationKind.CLOUD:
            return identity, OrganizationStatus(
                id=organization_id, kind=kind, detail=CLOUD_ORGANIZATION
            )
        return identity, organization_status(token_client, organization_id)


def _cloud_beside(credentials: Credentials) -> OrganizationStatus | None:
    """The Cloud organization as a second row, when a Yandex 360 one is the first."""
    if credentials.organization_id is None or credentials.cloud_organization_id is None:
        return None
    return OrganizationStatus(
        id=credentials.cloud_organization_id,
        kind=OrganizationKind.CLOUD,
        detail=CLOUD_ORGANIZATION,
    )


def _identity(token_client: TokenClient) -> Identity | None:
    """The token's owner; ``None`` when Yandex ID would not say (the service probes say why)."""
    try:
        return token_client.identity()
    except YandexError as exc:
        logger.warning("could not read the token's owner from Yandex ID: %s", exc)
        return None


def organization_status(token_client: TokenClient, organization_id: str) -> OrganizationStatus:
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
