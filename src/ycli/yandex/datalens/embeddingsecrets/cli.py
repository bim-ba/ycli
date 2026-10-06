"""`datalens embeddingsecrets` commands."""

from typing import Annotated

import typer

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.embeddingsecrets.models import (
    EmbeddingSecret,
    EmbeddingSecretCreated,
    EmbeddingSecretDeleted,
)
from ycli.yandex.models import ItemList

app = typer.Typer(
    name="embeddingsecrets", help="DataLens keys for embedding.", no_args_is_help=True
)

SecretIDArg = Annotated[
    str, typer.Argument(metavar="EMBEDDING_SECRET_ID", help="Id of the key for embedding.")
]


@app.command()
def get(embedding_secret_id: SecretIDArg, *, datalens: DataLensClient) -> EmbeddingSecret:
    """Print one key for embedding: its name and workbook, never its private key."""
    return datalens.embeddingsecrets.get(embedding_secret_id)


@app.command("list")
def list_(
    workbook_id: Annotated[str, typer.Argument(metavar="WORKBOOK_ID", help="Workbook id.")],
    *,
    datalens: DataLensClient,
) -> ItemList[EmbeddingSecret]:
    """List the keys for embedding of a workbook, without their private keys."""
    return datalens.embeddingsecrets.list(workbook_id)


@app.command()
def create(
    title: Annotated[str, typer.Option("--title", help="The name of the key.")],
    workbook_id: Annotated[
        str, typer.Option("--workbook-id", help="The workbook the key belongs to.")
    ],
    *,
    datalens: DataLensClient,
) -> EmbeddingSecretCreated:
    """Make a key for embedding; prints its id and its private key.

    The private key is given once: `get` and `list` do not return it. Keep it at once, in a
    file nobody else reads: `ycli -o json datalens embeddingsecrets create … > secret.json`.
    """
    return datalens.embeddingsecrets.create(title=title, workbook_id=workbook_id)


@app.command()
def delete(embedding_secret_id: SecretIDArg, *, datalens: DataLensClient) -> EmbeddingSecretDeleted:
    """Delete a key for embedding."""
    return datalens.embeddingsecrets.delete(embedding_secret_id)
