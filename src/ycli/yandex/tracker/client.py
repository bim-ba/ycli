"""TrackerClient — composition root over the tracker resource clients (one shared session)."""
from __future__ import annotations

import requests

from ycli.yandex.transport import Transport
from ycli.yandex.tracker.changelog.client import ChangelogClient
from ycli.yandex.tracker.comments.client import CommentsClient
from ycli.yandex.tracker.issues.client import IssuesClient
from ycli.yandex.tracker.issuetypes.client import IssueTypesClient
from ycli.yandex.tracker.links.client import LinksClient
from ycli.yandex.tracker.linktypes.client import LinkTypesClient
from ycli.yandex.tracker.me.client import MeClient
from ycli.yandex.tracker.priorities.client import PrioritiesClient
from ycli.yandex.tracker.transitions.client import TransitionsClient
from ycli.yandex.tracker.worklog.client import WorklogClient


class TrackerClient:
    """Holds the per-resource tracker clients, all sharing one authed ``requests.Session``.

    Example:
        >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
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
        self.issues = IssuesClient(session=transport)
        self.comments = CommentsClient(session=transport)
        self.links = LinksClient(session=transport)
        self.transitions = TransitionsClient(session=transport)
        self.worklog = WorklogClient(session=transport)
        self.changelog = ChangelogClient(session=transport)
        self.priorities = PrioritiesClient(session=transport)
        self.issuetypes = IssueTypesClient(session=transport)
        self.linktypes = LinkTypesClient(session=transport)
