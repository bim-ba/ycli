"""DataLens embeds FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    datalens_client,
)
from ycli.yandex.datalens.embeds.models import Embed, EmbedDeleted, EmbedSettings
from ycli.yandex.models import ItemList

mcp = FastMCP("datalens-embeds")

EmbedID = Annotated[str, Field(description="Embed id, from ``embeds_list``.")]
Title = Annotated[str, Field(description="The name of the embed.")]
SigningSecretID = Annotated[str, Field(description="The key for embedding that signs its links.")]
PublicParamsMode = Annotated[
    bool, Field(description="Whether the default mode of parameters is on.")
]
Settings = Annotated[
    EmbedSettings, Field(description="The settings of the embed; an empty object is valid.")
]
DepsIDs = Annotated[list[str] | None, Field(description="The entries the embedded one depends on.")]
UnsignedParams = Annotated[
    list[str] | None, Field(description="The parameters a link may carry unsigned.")
]
PrivateParams = Annotated[
    list[str] | None, Field(description="The parameters that go signed, inside the token.")
]


@mcp.tool(name="embeds_list", annotations={**RO, "title": "List DataLens embeds"})
def list_(
    entry_id: Annotated[str, Field(description="The id of the entry that is embedded.")],
    client: DataLensClient = Depends(datalens_client),
) -> ItemList[Embed]:
    """The embeds of one entry: where a chart or a dashboard is shown on another site."""
    return client.embeds.list(entry_id)


@mcp.tool(name="embeds_create", annotations={**WRITE, "title": "Create DataLens embed"})
def create(
    title: Title,
    embedding_secret_id: SigningSecretID,
    entry_id: Annotated[str, Field(description="The entry to embed.")],
    public_params_mode: PublicParamsMode,
    settings: Settings,
    deps_ids: DepsIDs = None,
    unsigned_params: UnsignedParams = None,
    private_params: PrivateParams = None,
    client: DataLensClient = Depends(datalens_client),
) -> Embed:
    """Embed an entry and return the embed.

    The key for embedding is one of the workbook the entry lies in (``embeddingsecrets_list``).
    """
    return client.embeds.create(
        title=title,
        embedding_secret_id=embedding_secret_id,
        entry_id=entry_id,
        public_params_mode=public_params_mode,
        settings=settings,
        deps_ids=deps_ids or (),
        unsigned_params=unsigned_params or (),
        private_params=private_params or (),
    )


@mcp.tool(name="embeds_update", annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens embed"})
def update(
    embed_id: EmbedID,
    title: Title,
    embedding_secret_id: SigningSecretID,
    public_params_mode: PublicParamsMode,
    settings: Settings,
    deps_ids: DepsIDs = None,
    unsigned_params: UnsignedParams = None,
    private_params: PrivateParams = None,
    client: DataLensClient = Depends(datalens_client),
) -> Embed:
    """Save an embed as given and return it.

    The embed is replaced whole: read it with ``embeds_list`` and send back what is to stay; a
    list left out is saved empty.
    """
    return client.embeds.update(
        embed_id,
        title=title,
        embedding_secret_id=embedding_secret_id,
        public_params_mode=public_params_mode,
        settings=settings,
        deps_ids=deps_ids or (),
        unsigned_params=unsigned_params or (),
        private_params=private_params or (),
    )


@mcp.tool(name="embeds_delete", annotations={**DESTRUCTIVE, "title": "Delete DataLens embed"})
def delete(embed_id: EmbedID, client: DataLensClient = Depends(datalens_client)) -> EmbedDeleted:
    """Delete an embed; its links stop working. Deleting again answers 404."""
    return client.embeds.delete(embed_id)
