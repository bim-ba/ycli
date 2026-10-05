"""Tracker issue ``/changelog`` client on the httpx2 core."""

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.changelog import endpoints
from ycli.yandex.tracker.changelog.models import ChangelogEntry


class ChangelogClient(Resource):
    """The change history of an issue (relative-paginated)."""

    def list(
        self,
        issue_key: str,
        *,
        limit: int | None = None,
        field: str | None = None,
        change_type: str | None = None,
        sort: str | None = None,
    ) -> ItemList[ChangelogEntry]:
        """All changelog events on an issue, draining the ``id=<last change id>`` cursor.

        ``GET /issues/{key}/changelog`` returns one page at a time; each next page repeats
        with ``id=<id of the last change seen>`` until a page comes back empty. Capped at
        ``limit`` (``None`` = the full history); a small cap narrows the page to ``limit`` rows.

        Args:
            issue_key: The issue key.
            limit: The most events to return; ``None`` returns the full history.
            field: Keep the changes of this field, e.g. ``status`` or ``checklistItems``.
            change_type: Keep the changes of this type, e.g. ``IssueWorkflow``.
            sort: The order of the changes: ``asc`` or ``desc``.

        Returns:
            The changelog events.

        Examples:
            >>> [change.id for change in tracker.changelog.list("DE-21", limit=500).root]
            ['ch1', 'ch2', 'ch3']
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_(
            issue_key, page_size=page_size, field=field, change_type=change_type, sort=sort
        )
        return ItemList[ChangelogEntry](list(self._session.iterate(paged, limit=limit)))
