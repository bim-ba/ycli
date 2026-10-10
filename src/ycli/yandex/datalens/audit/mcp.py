"""DataLens audit FastMCP tools (read-only) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.audit.models import AuditEntry, UserEntryPermissions
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    LIMIT_CAP,
    RO,
    All,
    Next,
    app_config,
    datalens_client,
    new_server,
)
from ycli.yandex.models import Listed

mcp = new_server("datalens-audit")


@mcp.tool(
    name="audit_entries_updates_list",
    annotations={**RO, "title": "List DataLens entries changed in a period"},
)
def entries_updates_list(
    from_: Annotated[
        str, Field(description="The start of the period: an ISO-8601 time with its zone.")
    ],
    to: Annotated[str | None, Field(description="The end of the period.")] = None,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max entries to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[AuditEntry]:
    """The entries changed in a period, auto-paginated: what, when and by whom.

    A deleted entry is listed too, with ``isDeleted``.
    """
    return client.audit.entries_updates_list(
        from_, to=to, limit=config.http.cap(limit, all_=all), next=next
    ).collect()


@mcp.tool(
    name="audit_entry_permissions_get",
    annotations={**RO, "title": "Get a user's permissions on DataLens entries"},
)
def entry_permissions_get(
    entry_ids: Annotated[list[str], Field(description="The ids of the entries to ask about.")],
    user_id: Annotated[
        str, Field(description="The user's id, as ``createdBy`` of an entry gives it.")
    ],
    client: DataLensClient = Depends(datalens_client),
) -> UserEntryPermissions:
    """What one user may do with each entry: execute, read, edit, admin, by entry id."""
    return client.audit.entry_permissions_get(entry_ids, user_id=user_id)
