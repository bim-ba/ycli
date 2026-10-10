"""DataLens licensing FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    All,
    Next,
    app_config,
    datalens_client,
    new_server,
)
from ycli.yandex.datalens.licensing.models import (
    License,
    LicenseLimits,
    LicenseListed,
    LicenseSortField,
    LicenseStatus,
)
from ycli.yandex.models import ItemList, Listed, SortDirection

mcp = new_server("datalens-licensing")


@mcp.tool(name="licensing_licenses_list", annotations={**RO, "title": "List DataLens licences"})
def licenses_list(
    user_ids: Annotated[
        list[str] | None, Field(description="Only the licences of these users.")
    ] = None,
    status: Annotated[
        LicenseStatus | None, Field(description="Only the licences in this state.")
    ] = None,
    sort_by: Annotated[LicenseSortField | None, Field(description="The field to sort by.")] = None,
    order: Annotated[SortDirection | None, Field(description="The order of the sort.")] = None,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max licences to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[LicenseListed]:
    """The licences (seats) of the DataLens instance, auto-paginated.

    Each says whose it is, its type (``creator`` or ``viewer``), whether it is active, and when
    its holder last signed in.
    """
    return client.licensing.licenses_list(
        user_ids=user_ids,
        status=status,
        sort_by=sort_by,
        order=order,
        limit=config.http.tool_cap(limit, all_=all),
        next=next,
    ).collect()


@mcp.tool(
    name="licensing_licenses_assign", annotations={**WRITE, "title": "Assign DataLens licences"}
)
def licenses_assign(
    user_ids: Annotated[list[str], Field(description="The users to give a licence to.")],
    client: DataLensClient = Depends(datalens_client),
) -> ItemList[License]:
    """Give each of these users a licence and return the licences given.

    A licence is a seat DataLens bills for: ask the person before calling. Written from the
    DataLens document and never called: not measured.
    """
    return client.licensing.licenses_assign(user_ids)


@mcp.tool(name="licensing_limit_get", annotations={**RO, "title": "Get DataLens licence limit"})
def limit_get(client: DataLensClient = Depends(datalens_client)) -> LicenseLimits:
    """How many licences the instance may hold: the limit in force and the one that takes over.

    ``current`` carries the count of active licences; ``next`` is null when no change is set.
    """
    return client.licensing.limit_get()


@mcp.tool(
    name="licensing_limit_set",
    annotations={**WRITE_IDEMPOTENT, "title": "Set DataLens licence limit"},
)
def limit_set(
    value: Annotated[int, Field(description="The most licences the instance may hold.")],
    client: DataLensClient = Depends(datalens_client),
) -> LicenseLimits:
    """Set how many licences the instance may hold and return the limits.

    The limit is the number of seats DataLens bills for: ask the person before calling. Written
    from the DataLens document and never called: not measured.
    """
    return client.licensing.limit_set(value)
