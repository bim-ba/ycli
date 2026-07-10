"""Wiki /grids FastMCP tools — reads only (ARCH-3); grid writes ship on SDK + CLI."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, TAGS, wiki_client
from ycli.yandex.wiki.grids.models import Grid

mcp = FastMCP("wiki-grids")


@mcp.tool(name="grids_get", annotations={**RO, "title": "Get Wiki grid"}, tags=TAGS)
def get(
    grid_id: Annotated[str, Field(description="The grid's permanent UUID4 id.")],
    fields: Annotated[
        str | None,
        Field(description="Extra blocks to include (CSV), e.g. ``attributes,user_permissions``."),
    ] = None,
    row_filter: Annotated[
        str | None, Field(description="Server-side row filter, e.g. ``[slug] ~ wiki``.")
    ] = None,
    only_cols: Annotated[
        str | None, Field(description="Return only these column slugs (CSV).")
    ] = None,
    only_rows: Annotated[str | None, Field(description="Return only these row ids (CSV).")] = None,
    sort: Annotated[str | None, Field(description="Row sort, e.g. ``slug,-slug2``.")] = None,
    client: WikiClient = Depends(wiki_client),
) -> Grid:
    """A single dynamic table (grid) by its UUID, with structure, rows and revision.

    Grids are the modern dynamic tables attached to a page; find a grid's id with
    ``pages_grids_list``. Use ``filter``/``only_cols``/``only_rows``/``sort`` to narrow large
    grids server-side, and ``fields=attributes,user_permissions`` for extra blocks. The returned
    ``revision`` is the optimistic-lock token any subsequent write (via the CLI/SDK) must echo.

    Example:
        >>> grids_get(grid_id="g-uuid", only_cols="name,owner")  # doctest: +SKIP
    """
    return client.grids.get(
        grid_id,
        fields=fields,
        row_filter=row_filter,
        only_cols=only_cols,
        only_rows=only_rows,
        sort=sort,
    )
