"""WikiClient — composition root over the wiki resource clients (one shared session)."""
from __future__ import annotations

import requests

from ycli.yandex.settings import AppConfig, Credentials
from ycli.yandex.transport import Transport
from ycli.yandex.wiki.attachments.client import AttachmentsClient
from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.me.client import MeClient
from ycli.yandex.wiki.pages.client import PagesClient


class WikiClient:
    """Holds the per-resource wiki clients, all sharing one authed ``requests.Session``."""

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

    @classmethod
    def from_env(cls) -> "WikiClient":
        """TEMPORARY shim for the MCP _deps.py — removed in Task 6."""
        credentials, config = Credentials(), AppConfig()
        return cls(
            oauth_token=credentials.oauth_token,
            organization_id=credentials.organization_id,
            timeout_seconds=int(config.timeout_seconds),
            retries=config.retries,
        )
