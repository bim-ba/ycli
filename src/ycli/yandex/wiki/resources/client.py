"""Wiki ``/pages/{id}/resources`` client on the httpx2 core."""

from ycli.yandex.core.listing import Listing
from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.resources import endpoints
from ycli.yandex.wiki.resources.models import ResourceItem


class ResourcesClient(Resource):
    """The unified listing of a page's attachments and grids."""

    def list(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        next: str | None = None,
        q: str | None = None,
        types: str | None = None,
        order_by: str | None = None,
        order_direction: str | None = None,
    ) -> Listing[ResourceItem]:
        """``GET /pages/{id}/resources`` → ``ItemList[ResourceItem]``, draining ``next_cursor``.

        The unified listing of everything attached to a page — attachments AND grids — as
        ``{type, item}`` envelopes. Capped at ``limit`` (``None`` = every resource); narrow
        with ``q`` (title search), ``types`` (comma-separated ``attachment,grid``), and
        ``order_by`` (``name_title`` or ``created_at``).

        Args:
            page_id: The page's id.
            limit: The most resources to return; ``None`` returns every resource.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.
            q: The title search.
            types: The comma-separated kinds to list: ``attachment``, ``grid``.
            order_by: The sort field: ``name_title`` or ``created_at``.
            order_direction: The sort direction for ``order_by``: ``asc`` or ``desc``.

        Returns:
            The page's attachments and grids.

        Examples:
            >>> found = wiki.resources.list(5401, limit=25, q="plan", types="attachment,grid")
            >>> [resource.type for resource in found]
            ['attachment', 'grid']
        """
        paged = endpoints.list_(
            page_id, q=q, types=types, order_by=order_by, order_direction=order_direction
        )
        return self._session.iterate(paged, limit=limit, next=next)
