"""TrackerClient — composition root over the tracker resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.yandex.core.session import SyncSession

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
from ycli.yandex.tracker.gaps.client import GapsClient
from ycli.yandex.tracker.issues.client import IssuesClient
from ycli.yandex.tracker.issuetypes.client import IssueTypesClient
from ycli.yandex.tracker.links.client import LinksClient
from ycli.yandex.tracker.linktypes.client import LinkTypesClient
from ycli.yandex.tracker.localfields.client import LocalFieldsClient
from ycli.yandex.tracker.macros.client import MacrosClient
from ycli.yandex.tracker.me.client import MeClient
from ycli.yandex.tracker.priorities.client import PrioritiesClient
from ycli.yandex.tracker.projects.client import ProjectsClient
from ycli.yandex.tracker.queues.client import QueuesClient
from ycli.yandex.tracker.remotelinks.client import RemoteLinksClient
from ycli.yandex.tracker.resolutions.client import ResolutionsClient
from ycli.yandex.tracker.sprints.client import SprintsClient
from ycli.yandex.tracker.statuses.client import StatusesClient
from ycli.yandex.tracker.transitions.client import TransitionsClient
from ycli.yandex.tracker.triggers.client import TriggersClient
from ycli.yandex.tracker.users.client import UsersClient
from ycli.yandex.tracker.workflows.client import WorkflowsClient
from ycli.yandex.tracker.worklog.client import WorklogClient


class TrackerClient(DomainClient):
    """Holds the per-resource tracker clients, all sharing one httpx2 core session.

    Examples:
        >>> tracker.me.get().login
        'alice'
    """

    profile = SERVICE.profile

    def probe(self) -> None:
        """One cheap authenticated read: the current user."""
        self.me.get()

    def _wire(self, session: SyncSession) -> None:
        self.me = MeClient(session=session)
        self.issues = IssuesClient(session=session)
        self.comments = CommentsClient(session=session)
        self.links = LinksClient(session=session)
        self.transitions = TransitionsClient(session=session)
        self.worklog = WorklogClient(session=session)
        self.changelog = ChangelogClient(session=session)
        self.checklists = ChecklistsClient(session=session)
        self.columns = ColumnsClient(session=session)
        self.priorities = PrioritiesClient(session=session)
        self.issuetypes = IssueTypesClient(session=session)
        self.linktypes = LinkTypesClient(session=session)
        self.users = UsersClient(session=session)
        self.statuses = StatusesClient(session=session)
        self.resolutions = ResolutionsClient(session=session)
        self.queues = QueuesClient(session=session)
        self.localfields = LocalFieldsClient(session=session)
        self.fields = FieldsClient(session=session)
        self.components = ComponentsClient(session=session)
        self.filters = FiltersClient(session=session)
        self.applications = ApplicationsClient(session=session)
        self.boards = BoardsClient(session=session)
        self.sprints = SprintsClient(session=session)
        self.attachments = AttachmentsClient(session=session)
        self.macros = MacrosClient(session=session)
        self.triggers = TriggersClient(session=session)
        self.autoactions = AutoactionsClient(session=session)
        self.bulk = BulkClient(session=session)
        self.remotelinks = RemoteLinksClient(session=session)
        self.dashboards = DashboardsClient(session=session)
        self.entities = EntitiesClient(session=session)
        self.workflows = WorkflowsClient(session=session)
        self.projects = ProjectsClient(session=session)
        self.gaps = GapsClient(session=session)
