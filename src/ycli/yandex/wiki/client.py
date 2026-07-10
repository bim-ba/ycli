"""WikiClient — composition root over the wiki resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

from ycli.yandex.transport import Transport
from ycli.yandex.wiki.attachments.client import AttachmentsClient
from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.grids.client import GridsClient
from ycli.yandex.wiki.me.client import MeClient
from ycli.yandex.wiki.operations.client import OperationsClient
from ycli.yandex.wiki.pages.client import PagesClient
from ycli.yandex.wiki.recovery.client import RecoveryClient
from ycli.yandex.wiki.resources.client import ResourcesClient
from ycli.yandex.wiki.uploadsessions.client import UploadSessionsClient


class WikiClient:
    """Holds the per-resource wiki clients, all sharing one authed ``requests.Session``.

    Example:
        >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
    """

    def __init__(
        self,
        *,
        oauth_token: str,
        organization_id: str,
        timeout_seconds: int = 30,
        retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        transport = Transport.session(
            oauth_token=oauth_token,
            organization_id=organization_id,
            timeout_seconds=timeout_seconds,
            retries=retries,
            base=session,
        )
        self.me = MeClient(session=transport)
        self.pages = PagesClient(session=transport)
        self.comments = CommentsClient(session=transport)
        self.attachments = AttachmentsClient(session=transport)
        self.resources = ResourcesClient(session=transport)
        self.recovery = RecoveryClient(session=transport)
        self.grids = GridsClient(session=transport)
        self.operations = OperationsClient(session=transport)
        self.uploadsessions = UploadSessionsClient(session=transport)
