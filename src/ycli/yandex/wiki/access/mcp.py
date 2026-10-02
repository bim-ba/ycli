"""Wiki /pages/{id}/access FastMCP tools."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack
from ycli.yandex.wiki.access.models import PageAccess, PageAccessCreate, PageAccessUpdate
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import (
    DESTRUCTIVE,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    wiki_client,
)

mcp = FastMCP("wiki-access")

_PAGE_ID = Field(description="Numeric id of the page.")
_ACCESS_ID = Field(description="Id of the access entry, from the page's ``access_lists``.")
_PREVENT_SELFLOCK = Field(
    description="Refuse the change if it would leave you without read access or the right to "
    "change accesses. Set it unless you mean to lock yourself out."
)


@mcp.tool(
    name="access_create", annotations={**WRITE, "title": "Grant Wiki page access"}, tags=WRITE_TAGS
)
def create(
    page_id: Annotated[int, _PAGE_ID],
    body: Annotated[
        PageAccessCreate,
        Field(
            description="The grant: exactly one of ``user`` (uid / cloud_uid) and ``group`` "
            "(src + id), the ``role``, and optionally ``inheritance``."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> PageAccess:
    """Grant a user or a group a role on a wiki page; returns the new access entry.

    A user who already holds a personal access is refused: change it with ``access_update``.
    Read the current accesses with ``pages_get_by_id`` and
    ``fields="access_policy,access_lists"``.
    """
    return client.access.create(page_id=page_id, body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="access_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Wiki page access"},
    tags=WRITE_TAGS,
)
def update(
    page_id: Annotated[int, _PAGE_ID],
    access_id: Annotated[str, _ACCESS_ID],
    body: Annotated[
        PageAccessUpdate,
        Field(description="The new ``role`` and/or ``inheritance`` (one at least)."),
    ],
    prevent_selflock: Annotated[bool, _PREVENT_SELFLOCK] = False,
    client: WikiClient = Depends(wiki_client),
) -> PageAccess:
    """Change the role or reach of one access entry on a wiki page.

    The page owner's own entry cannot be changed.
    """
    return client.access.update(
        page_id=page_id,
        access_id=access_id,
        body=body.model_dump(exclude_none=True),
        prevent_selflock=prevent_selflock,
    )


@mcp.tool(
    name="access_delete",
    annotations={**DESTRUCTIVE, "title": "Revoke Wiki page access"},
    tags=WRITE_TAGS,
)
def delete(
    page_id: Annotated[int, _PAGE_ID],
    access_id: Annotated[str, _ACCESS_ID],
    prevent_selflock: Annotated[bool, _PREVENT_SELFLOCK] = False,
    client: WikiClient = Depends(wiki_client),
) -> Ack:
    """Revoke one access entry on a wiki page — the holder loses that grant at once.

    The page owner's own entry cannot be revoked.
    """
    client.access.delete(page_id=page_id, access_id=access_id, prevent_selflock=prevent_selflock)
    return Ack.deleted("access", access_id, from_=f"page {page_id}")


@mcp.tool(
    name="access_clear",
    annotations={**DESTRUCTIVE, "title": "Clear Wiki page accesses"},
    tags=WRITE_TAGS,
)
def clear(
    page_id: Annotated[int, _PAGE_ID],
    prevent_selflock: Annotated[bool, _PREVENT_SELFLOCK] = False,
    client: WikiClient = Depends(wiki_client),
) -> Ack:
    """Revoke every personal access on a wiki page except the owner's.

    Everyone but the owner falls back to the page's access policy. Irreversible: the revoked
    entries are not kept.
    """
    client.access.clear(page_id=page_id, prevent_selflock=prevent_selflock)
    return Ack.cleared(f"personal accesses on page {page_id}")
