"""DataLens entry locks FastMCP tools (writes) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    WRITE,
    WRITE_IDEMPOTENT,
    datalens_client,
)
from ycli.yandex.datalens.entrylocks.models import (
    Lock,
    LockCreated,
    LockExtension,
    LockRelease,
    LockTerms,
)

mcp = FastMCP("datalens-entrylocks")

EntryID = Annotated[str, Field(description="Entry id.")]


@mcp.tool(name="entrylocks_create", annotations={**WRITE, "title": "Lock a DataLens entry"})
def create(
    entry_id: EntryID,
    data: Annotated[LockTerms, Field(description="How long to hold the lock, in milliseconds.")],
    client: DataLensClient = Depends(datalens_client),
) -> LockCreated:
    """Lock an entry (a dataset, a chart, a dashboard) for editing.

    The reply holds the token of the lock and nothing else: keep it, extending and releasing
    the lock take it. An entry that is already locked answers 423 with who holds the lock
    and until when.
    """
    return client.entrylocks.create(entry_id, data=data)


@mcp.tool(
    name="entrylocks_extend",
    annotations={**WRITE_IDEMPOTENT, "title": "Extend the lock of a DataLens entry"},
)
def extend(
    entry_id: EntryID,
    data: Annotated[LockExtension, Field(description="The token of the lock and its new terms.")],
    client: DataLensClient = Depends(datalens_client),
) -> Lock:
    """Hold a lock longer; the reply says when it expires now."""
    return client.entrylocks.extend(entry_id, data=data)


@mcp.tool(
    name="entrylocks_delete",
    annotations={**DESTRUCTIVE, "title": "Release the lock of a DataLens entry"},
)
def delete(
    entry_id: EntryID,
    params: Annotated[
        LockRelease, Field(description="The token of the lock, or `force` for another's lock.")
    ],
    client: DataLensClient = Depends(datalens_client),
) -> Lock:
    """Release a lock; with ``force`` it releases a lock another editor holds.

    An entry that is not locked answers 404.
    """
    return client.entrylocks.delete(entry_id, params=params)
