"""TrackerClient — composition root over the tracker resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

from ycli.yandex.tracker.applications.client import ApplicationsClient
from ycli.yandex.tracker.attachments.client import AttachmentsClient
from ycli.yandex.tracker.boards.client import BoardsClient
from ycli.yandex.tracker.changelog.client import ChangelogClient
from ycli.yandex.tracker.comments.client import CommentsClient
from ycli.yandex.tracker.components.client import ComponentsClient
from ycli.yandex.tracker.fields.client import FieldsClient
from ycli.yandex.tracker.filters.client import FiltersClient
from ycli.yandex.tracker.issues.client import IssuesClient
from ycli.yandex.tracker.issuetypes.client import IssueTypesClient
from ycli.yandex.tracker.links.client import LinksClient
from ycli.yandex.tracker.linktypes.client import LinkTypesClient
from ycli.yandex.tracker.localfields.client import LocalFieldsClient
from ycli.yandex.tracker.me.client import MeClient
from ycli.yandex.tracker.priorities.client import PrioritiesClient
from ycli.yandex.tracker.queues.client import QueuesClient
from ycli.yandex.tracker.resolutions.client import ResolutionsClient
from ycli.yandex.tracker.sprints.client import SprintsClient
from ycli.yandex.tracker.statuses.client import StatusesClient
from ycli.yandex.tracker.transitions.client import TransitionsClient
from ycli.yandex.tracker.users.client import UsersClient
from ycli.yandex.tracker.worklog.client import WorklogClient
from ycli.yandex.transport import Transport


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
        self.users = UsersClient(session=transport)
        self.statuses = StatusesClient(session=transport)
        self.resolutions = ResolutionsClient(session=transport)
        self.queues = QueuesClient(session=transport)
        self.localfields = LocalFieldsClient(session=transport)
        self.fields = FieldsClient(session=transport)
        self.components = ComponentsClient(session=transport)
        self.filters = FiltersClient(session=transport)
        self.applications = ApplicationsClient(session=transport)
        self.boards = BoardsClient(session=transport)
        self.sprints = SprintsClient(session=transport)
        self.attachments = AttachmentsClient(session=transport)
