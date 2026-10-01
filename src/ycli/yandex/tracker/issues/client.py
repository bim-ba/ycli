"""Tracker ``/issues`` client on the httpx2 core — the first resource off ``uplink``.

Every method sends one declaration from :mod:`ycli.yandex.tracker.issues.endpoints`.
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.issues import endpoints
from ycli.yandex.tracker.issues.models import Issue, IssueList


class IssuesClient(Resource):
    """Get, search (paginated), count, create, update, move and suggest Tracker issues."""

    def get(self, key: str) -> Issue:
        """``GET /issues/{key}`` → a single ``Issue``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issues.get("DATAENGINEERING-1").status  # doctest: +SKIP
            'inProgress'
        """
        return self._session.send(endpoints.get_issue(key))

    def search(self, body: dict[str, Any], *, limit: int | None = None) -> IssueList:
        """``POST /issues/_search`` → every matching issue, page by page, at most ``limit``.

        ``body`` is ``{"filter": …}`` or ``{"query": …}``. ``limit=None`` fetches every page (up
        to Tracker's 10 000 results); when the cap leaves issues behind, a warning is logged to
        ``ycli.http``.

        Example:
            >>> client.issues.search({"query": "Queue: DE"}, limit=10).root[0].key  # doctest: +SKIP
            'DE-1'
        """
        if limit is not None and limit < 1:
            raise ValueError(f"limit must be a positive number of issues or None, got {limit}")
        # A small cap needs no 100-issue page.
        page_size = min(limit, endpoints.SEARCH_PAGE_SIZE) if limit else endpoints.SEARCH_PAGE_SIZE
        paged = endpoints.search_issues(body, page_size=page_size)
        return IssueList(list(self._session.iterate(paged, limit=limit)))

    def count(self, body: dict[str, Any]) -> int:
        """``POST /issues/_count`` → the number of matching issues."""
        return self._session.send(endpoints.count_issues(body))

    def create(self, body: dict[str, Any]) -> Issue:
        """``POST /issues/`` — create from a ready body; returns the created ``Issue``."""
        return self._session.send(endpoints.create_issue(body))

    def update(self, key: str, body: dict[str, Any]) -> Issue:
        """``PATCH /issues/{key}`` — update fields; returns the updated ``Issue``."""
        return self._session.send(endpoints.update_issue(key, body))

    def move(self, key: str, queue: str) -> Issue:
        """``POST /issues/{key}/_move?queue=<key>`` — returns the moved ``Issue`` (new key)."""
        return self._session.send(endpoints.move_issue(key, queue))

    def suggest(self, text: str) -> IssueList:
        """``GET /issues/_suggest?input=<text>`` → issues whose summary contains ``text``."""
        return self._session.send(endpoints.suggest_issues(text))

    def scroll_clear(self, body: dict[str, str]) -> None:
        """Release a search scroll's server resources (``POST …/scroll/_clear``)."""
        self._session.send(endpoints.clear_scroll(body))
