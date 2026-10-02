"""Wiki ``/pages/{id}/resources`` client on the httpx2 core."""

from __future__ import annotations

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.resources import endpoints
from ycli.yandex.wiki.resources.models import ResourceItemList


class ResourcesClient(Resource):
    """The unified listing of a page's attachments and grids."""

    def list(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        q: str | None = None,
        types: str | None = None,
        order_by: str | None = None,
    ) -> ResourceItemList:
        """``GET /pages/{id}/resources`` → flat :class:`ResourceItemList`, draining ``next_cursor``.

        The unified listing of everything attached to a page — attachments AND grids — as
        ``{type, item}`` envelopes. Capped at ``limit`` (``None`` = every resource); narrow
        with ``q`` (title search), ``types`` (comma-separated ``attachment,grid``), and
        ``order_by`` (``name_title`` or ``created_at``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.resources.list(12345, types="attachment").root[0].type  # doctest: +SKIP
            'attachment'
        """
        paged = endpoints.list_resources(page_id, q=q, types=types, order_by=order_by)
        return ResourceItemList(list(self._session.iterate(paged, limit=limit)))
