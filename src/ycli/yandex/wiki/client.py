"""WikiClient — composition root over the wiki resource clients (one shared session)."""
from __future__ import annotations

import requests

from ycli.yandex.base import FromEnvSession
from ycli.yandex.wiki.attachments.client import AttachmentsClient
from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.pages.client import PagesClient


class WikiClient(FromEnvSession):
    """Holds the per-resource wiki clients, all sharing one ``requests.Session``.

    Example:
        >>> WikiClient.from_env().pages.get(slug="data/x")  # doctest: +SKIP
    """

    def __init__(self, *, session: requests.Session) -> None:
        self.pages = PagesClient(session=session)
        self.comments = CommentsClient(session=session)
        self.attachments = AttachmentsClient(session=session)
