"""DataLens connection operations, declared once (sans-IO).

Examples:
    >>> get("c1", workbook_id=None, binded_dataset_id=None, rev_id=None).body
    {'connectionId': 'c1'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.connections.models import (
    Connection,
    ConnectionCreate,
    ConnectionCreated,
    ConnectionUpdate,
)
from ycli.yandex.datalens.schemas.connection import (
    DeleteConnectionRequest,
    GetConnectionRequest,
    UpdateConnectionRequest,
)


def get(
    connection_id: str,
    *,
    workbook_id: str | None,
    binded_dataset_id: str | None,
    rev_id: str | None,
) -> Endpoint[Connection]:
    body = GetConnectionRequest(
        connectionId=connection_id,
        workbookId=workbook_id,
        bindedDatasetId=binded_dataset_id,
        rev_id=rev_id,
    )
    return RPC("getConnection", Connection, json=body, effect=Effect.READ)


def create(connection: ConnectionCreate) -> Endpoint[ConnectionCreated]:
    # The request is the connection itself, a union by ``type``: there is no envelope.
    return RPC("createConnection", ConnectionCreated, json=connection, effect=Effect.WRITE)


def update(connection_id: str, *, data: ConnectionUpdate) -> Endpoint[None]:
    # Measured: DataLens answers 200 with no body at all, so the reply is not read.
    body = UpdateConnectionRequest(connectionId=connection_id, data=data)
    return RPC("updateConnection", json=body, effect=Effect.IDEMPOTENT_WRITE)


def delete(connection_id: str) -> Endpoint[None]:
    # Measured: 200 with no body, as for an update.
    body = DeleteConnectionRequest(connectionId=connection_id)
    return RPC("deleteConnection", json=body, effect=Effect.DESTRUCTIVE)
