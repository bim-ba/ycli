"""Wiki /pages/{id}/resources FastMCP tool."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import ItemList
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, app_config, wiki_client
from ycli.yandex.wiki.resources.models import ResourceItem

mcp = FastMCP("wiki-resources")


@mcp.tool(name="resources_list", annotations={**RO, "title": "List Wiki page resources"})
def list_(
    page_id: Annotated[int, Field(description="Numeric page id whose resources to list.")],
    limit: Annotated[
        int | None, Field(ge=1, description="Max resources (omitted: the configured cap).")
    ] = None,
    q: Annotated[str | None, Field(description="Optional title search filter.")] = None,
    types: Annotated[
        str | None, Field(description="Comma-separated kinds to include: ``attachment,grid``.")
    ] = None,
    order_by: Annotated[
        str | None, Field(description="Sort field: ``name_title`` or ``created_at``.")
    ] = None,
    order_direction: Annotated[
        str | None, Field(description="Sort direction for ``order_by``: ``asc`` or ``desc``.")
    ] = None,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[ResourceItem]:
    """A page's resources — attachments AND grids — as ``{type, item}`` envelopes, auto-paginated.

    The unified single-pass listing over what ``attachments_list`` and ``pages_grids_list``
    expose separately (drains ``next_cursor`` internally). Capped at the configured item cap
    unless ``limit`` is given; narrow with ``q`` (title) or ``types`` (``attachment,grid``).
    """
    cap = config.http.cap(limit)
    return client.resources.list(
        page_id=page_id,
        limit=cap,
        q=q,
        types=types,
        order_by=order_by,
        order_direction=order_direction,
    )
