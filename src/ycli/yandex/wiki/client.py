"""WikiClient — composition root over the wiki resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

from ycli.yandex.base import DomainClient
from ycli.yandex.wiki import SERVICE
from ycli.yandex.wiki.attachments.client import AttachmentsClient
from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.grids.client import GridsClient
from ycli.yandex.wiki.me.client import MeClient
from ycli.yandex.wiki.operations.client import OperationsClient
from ycli.yandex.wiki.pages.client import PagesClient
from ycli.yandex.wiki.recovery.client import RecoveryClient
from ycli.yandex.wiki.resources.client import ResourcesClient
from ycli.yandex.wiki.uploadsessions.client import UploadSessionsClient


class WikiClient(DomainClient):
    """Holds the per-resource wiki clients, all sharing one httpx2 core session.

    Example:
        >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
    """

    def _wire(self, transport: requests.Session) -> None:
        session = self._connect(SERVICE.profile)
        self.me = MeClient(session=session)
        self.pages = PagesClient(session=session)
        self.comments = CommentsClient(session=session)
        self.attachments = AttachmentsClient(session=session)
        self.resources = ResourcesClient(session=session)
        self.recovery = RecoveryClient(session=session)
        self.grids = GridsClient(session=session)
        self.operations = OperationsClient(session=session)
        self.uploadsessions = UploadSessionsClient(session=session)
