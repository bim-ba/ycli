"""DataLens embedding secrets FastMCP tools (read + write) — Depends DI, native errors."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    GRANTS_ACCESS,
    RO,
    WRITE,
    datalens_client,
    new_server,
)
from ycli.yandex.datalens.embeddingsecrets.models import (
    EmbeddingSecret,
    EmbeddingSecretCreated,
    EmbeddingSecretDeleted,
)
from ycli.yandex.models import ItemList

mcp = new_server("datalens-embeddingsecrets")

SecretID = Annotated[str, Field(description="Id of the key for embedding.")]


@mcp.tool(
    name="embeddingsecrets_get", annotations={**RO, "title": "Get DataLens key for embedding"}
)
def get(
    embedding_secret_id: SecretID, client: DataLensClient = Depends(datalens_client)
) -> EmbeddingSecret:
    """One key for embedding: its name, its workbook, who made it. Never its private key."""
    return client.embeddingsecrets.get(embedding_secret_id)


@mcp.tool(
    name="embeddingsecrets_list",
    annotations={**RO, "title": "List DataLens keys for embedding"},
)
def list_(
    workbook_id: Annotated[str, Field(description="Workbook id.")],
    client: DataLensClient = Depends(datalens_client),
) -> ItemList[EmbeddingSecret]:
    """The keys for embedding of a workbook, without their private keys."""
    return client.embeddingsecrets.list(workbook_id)


@mcp.tool(
    name="embeddingsecrets_create",
    annotations={**WRITE, "title": "Create DataLens key for embedding"},
    meta=GRANTS_ACCESS,
)
def create(
    title: Annotated[str, Field(description="The name of the key.")],
    workbook_id: Annotated[str, Field(description="The workbook the key belongs to.")],
    client: DataLensClient = Depends(datalens_client),
) -> EmbeddingSecretCreated:
    """Make a key for embedding and return its id and its private key.

    The private key is given once: ``embeddingsecrets_get`` and ``embeddingsecrets_list`` do not
    return it. It comes in this tool's result, so it enters your context: hand it to the person
    at once, and do not repeat it in later messages.
    """
    return client.embeddingsecrets.create(title=title, workbook_id=workbook_id)


@mcp.tool(
    name="embeddingsecrets_delete",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens key for embedding"},
)
def delete(
    embedding_secret_id: SecretID, client: DataLensClient = Depends(datalens_client)
) -> EmbeddingSecretDeleted:
    """Delete a key for embedding. Deleting again answers 404."""
    return client.embeddingsecrets.delete(embedding_secret_id)
