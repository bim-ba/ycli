"""DataLensClient — composition root over the DataLens resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.yandex.core.session import SyncSession

from ycli.yandex.base import DomainClient
from ycli.yandex.datalens import SERVICE
from ycli.yandex.datalens.tenant.client import TenantClient


class DataLensClient(DomainClient):
    """Holds the per-resource DataLens clients, all sharing one httpx2 core session.

    Examples:
        >>> datalens.tenant.details_get().tenant_id
        'org_bpf00000000000000000'
    """

    profile = SERVICE.profile

    def probe(self) -> None:
        """One cheap authenticated read: the details of the DataLens instance."""
        self.tenant.details_get()

    def _wire(self, session: SyncSession) -> None:
        self.tenant = TenantClient(session=session)
