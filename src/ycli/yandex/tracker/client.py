"""TrackerClient — composition root over the tracker resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

from ycli.yandex.base import DomainClient
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
        self.me = MeClient(session=transport)
        self.issues = IssuesClient(session=transport)
        self.comments = CommentsClient(session=transport)
        self.links = LinksClient(session=transport)
        self.transitions = TransitionsClient(session=transport)
        self.worklog = WorklogClient(session=transport)
        self.changelog = ChangelogClient(session=transport)
        self.checklists = ChecklistsClient(session=transport)
        self.columns = ColumnsClient(session=transport)
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
        self.macros = MacrosClient(session=transport)
        self.triggers = TriggersClient(session=transport)
        self.autoactions = AutoactionsClient(session=transport)
        self.bulk = BulkClient(session=transport)
        self.remotelinks = RemoteLinksClient(session=transport)
        self.import_ = ImportClient(session=transport)
        self.dashboards = DashboardsClient(session=transport)
        self.entities = EntitiesClient(session=transport)
    supports_service_account_iam = True
