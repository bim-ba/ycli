"""Probe each service's identity endpoint and assemble an AuthReport (shared by CLI + MCP)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from pydantic import TypeAdapter

from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.forms.me.models import (
    User as FormsMe,  # noqa: TC001  # used in the MeProbe protocol annotation
)
from ycli.yandex.status.models import AuthReport, ServiceAuthStatus
from ycli.yandex.tracker.me.models import (
    Me as TrackerMe,  # noqa: TC001  # used in the MeProbe protocol annotation
)
from ycli.yandex.wiki.me.models import (
    Me as WikiMe,  # noqa: TC001  # used in the MeProbe protocol annotation
)

if TYPE_CHECKING:
    from collections.abc import Mapping

# Routes a probe result to the right discriminated `ServiceAuthStatus` member by `service`
# tag — the single source of truth for service→model is the Literal discriminator itself.
_STATUS = TypeAdapter(ServiceAuthStatus)


class MeProbe(Protocol):
    """Structural type for a domain `me` client: a zero-arg `get()` returning an API model."""

    def get(self) -> TrackerMe | WikiMe | FormsMe: ...


class StatusReporter:
    """Given each service's `me` client, probe identity and build a per-service AuthReport."""

    def __init__(self, me_clients: Mapping[str, MeProbe]) -> None:
        self._me_clients = me_clients

    def report(self, *, configured: bool, organization_id: str) -> AuthReport:
        services = [self._probe(name, client) for name, client in self._me_clients.items()]
        return AuthReport(configured=configured, organization_id=organization_id, services=services)

    @staticmethod
    def _probe(name: str, me_client: MeProbe) -> ServiceAuthStatus:
        try:
            me = me_client.get()
        except YandexAuthError:
            return _STATUS.validate_python(
                {"service": name, "valid": False, "detail": "token invalid or expired"}
            )
        except YandexError as exc:
            return _STATUS.validate_python({"service": name, "valid": False, "detail": str(exc)})
        return _STATUS.validate_python({"service": name, "valid": True, "me": me})
