"""Contract cases for DataLens connections (see tests/contract/)."""

import json
from pathlib import Path

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.connections.models import ConnectionCreate, ConnectionUpdate

NEW_FILE = str(Path(__file__).parent / "clickhouse.json")
NEW = json.loads(Path(NEW_FILE).read_text(encoding="utf-8"))
CHANGE = {"host": "db2.example.net", "port": 9440}

# The keys of a live ClickHouse reply (2026-10-06): no `type`, the kind in `db_type`, no secret.
SALES_DB = {
    "id": "con00000000001",
    "name": "Sales DB",
    "db_type": "clickhouse",
    "description": "",
    "key": "Sales/Sales DB",
    "workbook_id": "wb000000000001",
    "created_at": "2026-09-01T10:00:00.000Z",
    "updated_at": "2026-09-02T10:00:00.000Z",
    "meta": {},
    "host": "db.example.net",
    "port": 8443,
    "username": "reader",
    "secure": True,
}

CASES = [
    Case(
        "datalens.connections.get",
        args=("con00000000001",),
        cli=["datalens", "connections", "get", "con00000000001"],
        mcp=("datalens_connections_get", {"connection_id": "con00000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getConnection", json={"connectionId": "con00000000001"}),
                Reply(json=SALES_DB),
            )
        ],
    ),
    Case(
        "datalens.connections.get",
        args=("con00000000001",),
        kwargs={
            "workbook_id": "wb000000000001",
            "binded_dataset_id": "ds000000000001",
            "rev_id": "rev1",
        },
        cli=[
            *("datalens", "connections", "get", "con00000000001"),
            *("--workbook-id", "wb000000000001", "--binded-dataset-id", "ds000000000001"),
            *("--rev-id", "rev1"),
        ],
        mcp=(
            "datalens_connections_get",
            {
                "connection_id": "con00000000001",
                "workbook_id": "wb000000000001",
                "binded_dataset_id": "ds000000000001",
                "rev_id": "rev1",
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getConnection",
                    json={
                        "connectionId": "con00000000001",
                        "workbookId": "wb000000000001",
                        "bindedDatasetId": "ds000000000001",
                        "rev_id": "rev1",
                    },
                ),
                Reply(json=SALES_DB),
            )
        ],
    ),
    Case(
        "datalens.connections.create",
        args=(ConnectionCreate.model_validate(NEW),),
        cli=["datalens", "connections", "create", "--body-file", NEW_FILE],
        mcp=("datalens_connections_create", {"connection": NEW}),
        exchanges=[
            (
                Sent("POST", "rpc/createConnection", json=NEW),
                Reply(json={"id": "con00000000001"}),
            )
        ],
    ),
    Case(
        "datalens.connections.update",
        args=("con00000000001",),
        kwargs={"data": ConnectionUpdate.model_validate(CHANGE)},
        cli=["datalens", "connections", "update", "con00000000001", "--data", json.dumps(CHANGE)],
        mcp=("datalens_connections_update", {"connection_id": "con00000000001", "data": CHANGE}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateConnection",
                    json={"connectionId": "con00000000001", "data": CHANGE},
                ),
                Reply(),  # measured: 200 with no body
            )
        ],
    ),
    Case(
        "datalens.connections.delete",
        args=("con00000000001",),
        cli=["datalens", "connections", "delete", "con00000000001"],
        mcp=("datalens_connections_delete", {"connection_id": "con00000000001"}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent("POST", "rpc/deleteConnection", json={"connectionId": "con00000000001"}),
                Reply(),  # measured: 200 with no body
            )
        ],
    ),
]
