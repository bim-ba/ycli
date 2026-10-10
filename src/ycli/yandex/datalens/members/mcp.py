"""DataLens members FastMCP tools (read-only) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
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
from ycli.yandex.datalens.members.models import Member, MemberKind, MemberLanguage
from ycli.yandex.models import Listed

mcp = new_server("datalens-members")


@mcp.tool(name="members_list", annotations={**RO, "title": "List DataLens members"})
def list_(
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max members to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    language: Annotated[MemberLanguage | None, Field(description="Language of the names.")] = None,
    search: Annotated[
        str | None, Field(description="Keep the members whose name or address has this text.")
    ] = None,
    tab_id: Annotated[MemberKind | None, Field(description="Keep one kind of subject.")] = None,
    filter: Annotated[  # noqa: A002  # the API's own name for it
        str | None, Field(description="A filter expression of the API.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[Member]:
    """The users, groups and service accounts of the organization, auto-paginated.

    The ``sub`` of a member is the subject id a role is given to: find it here before
    ``collections_access_bindings_update`` or ``workbooks_access_bindings_update``. Capped at
    the configured item cap unless ``limit`` is given.
    """
    return client.members.list(
        limit=config.http.cap(limit, all_=all),
        next=next,
        language=language,
        search=search,
        tab_id=tab_id,
        filter=filter,
    ).collect()
