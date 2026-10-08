"""`datalens connections` commands."""

import json
from typing import Annotated

import typer

from ycli.cli.body_fields import CallerFields
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.connections.models import (
    Connection,
    ConnectionCreate,
    ConnectionCreated,
    ConnectionUpdate,
)
from ycli.yandex.datalens.schemas.connection import UpdateConnectionRequest
from ycli.yandex.models import Ack

app = typer.Typer(name="connections", help="DataLens connections.", no_args_is_help=True)

ConnectionIDArg = Annotated[str, typer.Argument(metavar="CONNECTION_ID", help="Connection id.")]
SECRET_IN_A_FILE = (
    "Give a password or a token from a file outside the repository, mode 600: in --body-file, "
    "or as one field with -F password=@FILE. Typed on a command line it stays in the shell "
    "history. Write the file of one field with no line break at its end "
    "(printf %s 'secret' > file), or the break goes out with the secret. --dry-run prints a "
    "secret as ***."
)


@app.command()
def get(
    connection_id: ConnectionIDArg,
    workbook_id: Annotated[
        str | None, typer.Option("--workbook-id", help="The workbook the connection lies in.")
    ] = None,
    binded_dataset_id: Annotated[
        str | None,
        typer.Option("--binded-dataset-id", help="A dataset bound to it, to read it through."),
    ] = None,
    rev_id: Annotated[
        str | None, typer.Option("--rev-id", help="The revision to read; the current by default.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> Connection:
    """Print one connection; its kind comes in `db_type`, its password or token never."""
    return datalens.connections.get(
        connection_id, workbook_id=workbook_id, binded_dataset_id=binded_dataset_id, rev_id=rev_id
    )


@app.command(epilog=SECRET_IN_A_FILE)
def create(*, caller: CallerFields, datalens: DataLensClient) -> ConnectionCreated:
    """Create a connection from --body-file (JSON or YAML) and -F over it.

    The body is the connection itself: `type` says which kind it is and which fields it takes
    (`ycli datalens connections create --body-file conn.yaml --dry-run` shows what would go).
    """
    # The body is a union that picks its class by ``type``: it comes from --body-file and -F.
    return datalens.connections.create(ConnectionCreate.model_validate(caller.over({})))


@app.command(epilog=SECRET_IN_A_FILE)
def update(
    connection_id: ConnectionIDArg,
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            help='The fields to change, as a JSON object: {"host": "db2.example.net"}. '
            "--body-file and -F give them under `data` (-F 'data[port]=8443').",
        ),
    ] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> Ack:
    """Change the fields given of a connection; the others stay as they are."""
    given = caller.over({"data": json.loads(data)} if data is not None else {})
    # The request whole: a field that is not of it is refused, not dropped.
    body = UpdateConnectionRequest.model_validate({"connectionId": connection_id, **given})
    datalens.connections.update(
        body.connection_id, data=ConnectionUpdate.model_validate(given.get("data"))
    )
    return Ack.updated("connection", connection_id)


@app.command()
def delete(connection_id: ConnectionIDArg, *, datalens: DataLensClient) -> Ack:
    """Delete a connection; the datasets on it lose their source.

    The API has no way to bring it back, and a chart that reads through it keeps naming its id
    (measured).

    The interface lists what was deleted under Service settings, Deleted objects, with a
    Restore button (measured: the entry appears there; restoring was not tried).
    """
    datalens.connections.delete(connection_id)
    return Ack.deleted("connection", connection_id)
