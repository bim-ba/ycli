"""TrackerClient — composition root over the tracker resource clients (one shared session)."""
from __future__ import annotations

import requests

from ycli.yandex.base import session_from_env
from ycli.yandex.tracker.changelog.client import ChangelogClient
from ycli.yandex.tracker.comments.client import CommentsClient
from ycli.yandex.tracker.issues.client import IssuesClient
from ycli.yandex.tracker.issuetypes.client import IssueTypesClient
from ycli.yandex.tracker.links.client import LinksClient
from ycli.yandex.tracker.linktypes.client import LinkTypesClient
from ycli.yandex.tracker.priorities.client import PrioritiesClient
from ycli.yandex.tracker.transitions.client import TransitionsClient
from ycli.yandex.tracker.worklog.client import WorklogClient


class TrackerClient:
    """Holds the per-resource tracker clients, all sharing one ``requests.Session``.

    Example:
        >>> TrackerClient.from_env().issues.get("DATAENGINEERING-1")  # doctest: +SKIP
    """

    def __init__(self, *, session: requests.Session) -> None:
        self.issues = IssuesClient(session=session)
        self.comments = CommentsClient(session=session)
        self.links = LinksClient(session=session)
        self.transitions = TransitionsClient(session=session)
        self.worklog = WorklogClient(session=session)
        self.changelog = ChangelogClient(session=session)
        self.priorities = PrioritiesClient(session=session)
        self.issuetypes = IssueTypesClient(session=session)
        self.linktypes = LinkTypesClient(session=session)

    @classmethod
    def from_env(cls) -> TrackerClient:
        """Build all sub-clients from one env-resolved session."""
        return cls(session=session_from_env())
