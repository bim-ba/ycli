"""TrackerClient — composition root over the tracker resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

from ycli.yandex.base import DomainClient
from ycli.yandex.tracker import SERVICE
from ycli.yandex.tracker.applications.client import ApplicationsClient
from ycli.yandex.tracker.attachments.client import AttachmentsClient
from ycli.yandex.tracker.autoactions.client import AutoactionsClient
from ycli.yandex.tracker.boards.client import BoardsClient
from ycli.yandex.tracker.bulk.client import BulkClient
from ycli.yandex.tracker.changelog.client import ChangelogClient
from ycli.yandex.tracker.checklists.client import ChecklistsClient
from ycli.yandex.tracker.columns.client import ColumnsClient
from ycli.yandex.tracker.comments.client import CommentsClient
from ycli.yandex.tracker.components.client import ComponentsClient
from ycli.yandex.tracker.dashboards.client import DashboardsClient
from ycli.yandex.tracker.entities.client import EntitiesClient
from ycli.yandex.tracker.fields.client import FieldsClient
from ycli.yandex.tracker.filters.client import FiltersClient
from ycli.yandex.tracker.import_.client import ImportClient
from ycli.yandex.tracker.issues.client import IssuesClient
from ycli.yandex.tracker.issuetypes.client import IssueTypesClient
from ycli.yandex.tracker.links.client import LinksClient
from ycli.yandex.tracker.linktypes.client import LinkTypesClient
from ycli.yandex.tracker.localfields.client import LocalFieldsClient
from ycli.yandex.tracker.macros.client import MacrosClient
from ycli.yandex.tracker.me.client import MeClient
from ycli.yandex.tracker.priorities.client import PrioritiesClient
from ycli.yandex.tracker.queues.client import QueuesClient
from ycli.yandex.tracker.remotelinks.client import RemoteLinksClient
from ycli.yandex.tracker.resolutions.client import ResolutionsClient
from ycli.yandex.tracker.sprints.client import SprintsClient
from ycli.yandex.tracker.statuses.client import StatusesClient
from ycli.yandex.tracker.transitions.client import TransitionsClient
from ycli.yandex.tracker.triggers.client import TriggersClient
from ycli.yandex.tracker.users.client import UsersClient
from ycli.yandex.tracker.worklog.client import WorklogClient


class TrackerClient(DomainClient):
    """Holds the per-resource tracker clients, all sharing one authed ``requests.Session``.

    Example:
        >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
    """

    def _wire(self, transport: requests.Session) -> None:
        core = self._connect(SERVICE.profile)
        self.me = MeClient(session=core)
        self.issues = IssuesClient(session=core)
        self.comments = CommentsClient(session=core)
        self.links = LinksClient(session=core)
        self.transitions = TransitionsClient(session=core)
        self.worklog = WorklogClient(session=core)
        self.changelog = ChangelogClient(session=core)
        self.checklists = ChecklistsClient(session=core)
        self.columns = ColumnsClient(session=core)
        self.priorities = PrioritiesClient(session=core)
        self.issuetypes = IssueTypesClient(session=core)
        self.linktypes = LinkTypesClient(session=core)
        self.users = UsersClient(session=core)
        self.statuses = StatusesClient(session=core)
        self.resolutions = ResolutionsClient(session=core)
        self.queues = QueuesClient(session=core)
        self.localfields = LocalFieldsClient(session=core)
        self.fields = FieldsClient(session=core)
        self.components = ComponentsClient(session=core)
        self.filters = FiltersClient(session=core)
        self.applications = ApplicationsClient(session=core)
        self.boards = BoardsClient(session=core)
        self.sprints = SprintsClient(session=core)
        self.attachments = AttachmentsClient(session=core)
        self.macros = MacrosClient(session=core)
        self.triggers = TriggersClient(session=core)
        self.autoactions = AutoactionsClient(session=core)
        self.bulk = BulkClient(session=core)
        self.remotelinks = RemoteLinksClient(session=core)
        self.import_ = ImportClient(session=core)
        self.dashboards = DashboardsClient(session=core)
        self.entities = EntitiesClient(session=core)
