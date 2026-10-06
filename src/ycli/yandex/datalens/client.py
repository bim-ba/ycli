"""DataLensClient — composition root over the DataLens resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.yandex.core.session import SyncSession

from ycli.yandex.base import DomainClient
from ycli.yandex.datalens import SERVICE
from ycli.yandex.datalens.charts.client import ChartsClient
from ycli.yandex.datalens.collections.client import CollectionsClient
from ycli.yandex.datalens.connections.client import ConnectionsClient
from ycli.yandex.datalens.datasets.client import DatasetsClient
from ycli.yandex.datalens.embeddingsecrets.client import EmbeddingSecretsClient
from ycli.yandex.datalens.embeds.client import EmbedsClient
from ycli.yandex.datalens.entries.client import EntriesClient
from ycli.yandex.datalens.entrylocks.client import EntryLocksClient
from ycli.yandex.datalens.members.client import MembersClient
from ycli.yandex.datalens.permissions.client import PermissionsClient
from ycli.yandex.datalens.reports.client import ReportsClient
from ycli.yandex.datalens.tenant.client import TenantClient
from ycli.yandex.datalens.workbookexports.client import WorkbookExportsClient
from ycli.yandex.datalens.workbookimports.client import WorkbookImportsClient
from ycli.yandex.datalens.workbooks.client import WorkbooksClient


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
        self.collections = CollectionsClient(session=session)
        self.workbooks = WorkbooksClient(session=session)
        self.entrylocks = EntryLocksClient(session=session)
        self.members = MembersClient(session=session)
        self.entries = EntriesClient(session=session)
        self.permissions = PermissionsClient(session=session)
        self.connections = ConnectionsClient(session=session)
        self.datasets = DatasetsClient(session=session)
        self.charts = ChartsClient(session=session)
        self.reports = ReportsClient(session=session)
        self.workbookexports = WorkbookExportsClient(session=session)
        self.workbookimports = WorkbookImportsClient(session=session)
        self.embeds = EmbedsClient(session=session)
        self.embeddingsecrets = EmbeddingSecretsClient(session=session)
