"""Wiki /pages/{id}/resources FastMCP tool."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, TAGS, app_config, wiki_client
from ycli.yandex.wiki.resources.models import ResourceItemList

mcp = FastMCP("wiki-resources")


@mcp.tool(name="resources_list", annotations={**RO, "title": "List Wiki page resources"}, tags=TAGS)
def list_(
    page_id: Annotated[int, Field(description="Numeric page id whose resources to list.")],
    limit: Annotated[int, Field(description="Max resources (0 = YCLI_MAX_ITEMS cap).")] = 0,
    q: Annotated[str, Field(description="Optional title search filter.")] = "",
    types: Annotated[
        str, Field(description="Comma-separated kinds to include: ``attachment,grid``.")
    ] = "",
    client: WikiClient = Depends(wiki_client),
    cfg: AppConfig = Depends(app_config),
) -> ResourceItemList:
    """A page's resources — attachments AND grids — as ``{type, item}`` envelopes, auto-paginated.

    The unified single-pass listing over what ``attachments_list`` and ``pages_grids_list``
    expose separately (drains ``next_cursor`` internally). Capped at YCLI_MAX_ITEMS (default
    500) unless ``limit`` is given; narrow with ``q`` (title) or ``types`` (``attachment,grid``).

    Example:
        >>> list_(page_id=12345, types="attachment")  # doctest: +SKIP
    """
    cap = resolve_cap(limit, cfg.max_items)
    return client.resources.list(page_id=page_id, limit=cap, q=q or None, types=types or None)
