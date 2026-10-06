"""DataLens connections FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.connections.models import (
    Connection,
    ConnectionCreate,
    ConnectionCreated,
    ConnectionUpdate,
)
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    OverBudget,
    datalens_client,
)
from ycli.yandex.models import Ack

mcp = FastMCP("datalens-connections")

ConnectionID = Annotated[str, Field(description="Connection id.")]
MODELS = "ycli.yandex.datalens.connections.models"


@mcp.tool(name="connections_get", annotations={**RO, "title": "Get DataLens connection"})
def get(
    connection_id: ConnectionID,
    workbook_id: Annotated[
        str | None, Field(description="The workbook the connection lies in.")
    ] = None,
    binded_dataset_id: Annotated[
        str | None, Field(description="A dataset bound to the connection, to read it through.")
    ] = None,
    rev_id: Annotated[
        str | None, Field(description="The revision to read; the current one when left out.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Connection:
    """One connection by id: its name, its kind and the settings of that kind.

    The kind comes in ``db_type``: the reply has no ``type``, though creating one takes it.

    A password or a token is never in the reply. ``workbooks_entries_list`` with the scope
    ``connection`` finds the connections of a workbook.
    """
    return client.connections.get(
        connection_id, workbook_id=workbook_id, binded_dataset_id=binded_dataset_id, rev_id=rev_id
    )


@mcp.tool(name="connections_create", annotations={**WRITE, "title": "Create DataLens connection"})
def create(
    connection: Annotated[
        ConnectionCreate,
        OverBudget(
            f"{MODELS}:ConnectionCreate",
            "The new connection; ``type`` says which kind it is and selects its schema.",
        ),
    ],
    client: DataLensClient = Depends(datalens_client),
) -> ConnectionCreated:
    """Create a connection and return its id.

    Give ``workbook_id`` (or ``dir_path``) for where it lies. The password or the token you
    give is stored by DataLens and never returned by ``connections_get``. A connection to
    Google Sheets (``gsheets``) cannot be created here: the API answers that the type is not
    editable; it is made in the DataLens interface and then read like any other.
    """
    return client.connections.create(connection)


@mcp.tool(
    name="connections_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens connection"},
)
def update(
    connection_id: ConnectionID,
    data: Annotated[
        ConnectionUpdate,
        OverBudget(
            f"{MODELS}:ConnectionUpdate",
            "The fields to change, of the connection's own kind; the others stay as they are.",
        ),
    ],
    client: DataLensClient = Depends(datalens_client),
) -> Ack:
    """Change the fields given of a connection; returns an acknowledgement."""
    client.connections.update(connection_id, data=data)
    return Ack.updated("connection", connection_id)


@mcp.tool(
    name="connections_delete", annotations={**DESTRUCTIVE, "title": "Delete DataLens connection"}
)
def delete(connection_id: ConnectionID, client: DataLensClient = Depends(datalens_client)) -> Ack:
    """Delete a connection; the datasets built on it lose their source."""
    client.connections.delete(connection_id)
    return Ack.deleted("connection", connection_id)
