"""Tracker issue ``/changelog`` client on the httpx2 core."""

from __future__ import annotations

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.changelog import endpoints
from ycli.yandex.tracker.changelog.models import ChangelogList


class ChangelogClient(Resource):
    """The change history of an issue (relative-paginated)."""

    def list(self, key: str, *, limit: int | None = None) -> ChangelogList:
        """All changelog events on an issue, draining the ``id=<last change id>`` cursor.

        ``GET /issues/{key}/changelog`` returns one page at a time; each next page repeats
        with ``id=<id of the last change seen>`` until a page comes back empty. Capped at
        ``limit`` (``None`` = the full history); a small cap narrows the page to ``limit`` rows.

        Args:
            key: The issue key.
            limit: The most events to return; ``None`` returns the full history.

        Returns:
            The changelog events.

        Examples:
            >>> [change.id for change in tracker.changelog.list("DE-21", limit=500).root]
            ['ch1', 'ch2', 'ch3']
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_changelog(key, page_size=page_size)
        return ChangelogList(list(self._session.iterate(paged, limit=limit)))
