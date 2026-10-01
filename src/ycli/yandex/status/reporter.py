"""Probe each service's identity endpoint and assemble an AuthReport (shared by CLI + MCP)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.factory import build_client
from ycli.yandex.registry import SERVICES
from ycli.yandex.status.models import AuthReport, ServiceAuthStatus

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ycli.settings import AppConfig, Credentials
    from ycli.yandex.account import Account


class MeModel(Protocol):
    """A service's ``me`` payload that can say whose token it is."""

    def account(self) -> Account: ...


class MeProbe(Protocol):
    """A domain ``me`` client: a zero-argument ``get()``."""

    def get(self) -> MeModel: ...


class StatusReporter:
    """Given each service's `me` client, probe identity and build a per-service AuthReport."""

    def __init__(self, me_clients: Mapping[str, MeProbe]) -> None:
        self._me_clients = me_clients

    @classmethod
    def for_credentials(cls, credentials: Credentials, config: AppConfig) -> StatusReporter:
        """A reporter over every registered service, each client built from ``credentials``."""
        return cls(
            {
                # Every domain client has a `me` probe, but DomainClient does not declare it.
                service.name: build_client(  # ty: ignore[unresolved-attribute]
                    service.client_class(), credentials, config
                ).me
                for service in SERVICES
            }
        )

    def report(self, *, configured: bool, organization_id: str) -> AuthReport:
        services = [self._probe(name, client) for name, client in self._me_clients.items()]
        return AuthReport(configured=configured, organization_id=organization_id, services=services)

    @staticmethod
    def _probe(name: str, me_client: MeProbe) -> ServiceAuthStatus:
        try:
            me = me_client.get()
        except YandexAuthError:
            return ServiceAuthStatus(service=name, detail="token invalid or expired")
        except YandexError as exc:
            return ServiceAuthStatus(service=name, detail=str(exc))
        return ServiceAuthStatus(service=name, valid=True, account=me.account())
