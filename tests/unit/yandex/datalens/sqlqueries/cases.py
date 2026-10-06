"""Contract cases for DataLens saved SQL queries (see tests/contract/).

Written from the document DataLens publishes: the section is experimental there, and the
owner's organization answers 403 ``SQL_EDITOR_NOT_ALLOWED``, so no reply here was measured.
"""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.schemas.sql_queries import (
    CreateSqlQueryArgsParamsItemVariant2,
    UpdateSqlQueryArgsParamsItemVariant3,
)

SINCE = {"name": "since", "type": "date", "defaultValue": "2026-01-01"}
LIMIT = {"name": "top", "type": "number", "defaultValue": 10}
QUERY = {
    "entryId": "sq00000000001",
    "scope": "sql_query",
    "type": "",
    "key": "Sales/Orders a day",
    "workbookId": "wb000000000001",
    "revId": "rev1",
    "savedId": "rev1",
    "publishedId": None,
    "data": {
        "connectionId": "con00000000001",
        "query": "select count(*) from orders where day >= {{since}}",
        "statementPositions": [[0, 49]],
        "params": [SINCE],
    },
    "annotation": {"description": "Orders since a day"},
    "createdBy": "user-1",
    "createdAt": "2026-10-01T10:00:00.000Z",
    "updatedBy": "user-1",
    "updatedAt": "2026-10-01T10:00:00.000Z",
}
RAN = {
    "id": "run0000000001",
    "connectionId": "con00000000001",
    "status": "success",
    "query": "select count(*) from orders where day >= '2026-10-01'",
    "statementPositions": [[0, 52]],
    "results": [{"status": "success", "columns": [{"name": "count"}], "rows": [[42]]}],
    "createdBy": "user-1",
    "createdAt": "2026-10-02T10:00:00.000Z",
}

CASES = [
    Case(
        "datalens.sqlqueries.get",
        args=("sq00000000001",),
        cli=["datalens", "sqlqueries", "get", "sq00000000001"],
        mcp=("datalens_sqlqueries_get", {"sql_query_id": "sq00000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getSqlQuery", json={"sqlQueryId": "sq00000000001"}),
                Reply(json={"entry": QUERY}),
            )
        ],
    ),
    Case(
        "datalens.sqlqueries.get",
        args=("sq00000000002",),
        kwargs={"rev_id": "rev7", "include_permissions": True, "include_favorite": False},
        cli=[
            *("datalens", "sqlqueries", "get", "sq00000000002", "--rev-id", "rev7"),
            *("--include-permissions", "--no-include-favorite"),
        ],
        mcp=(
            "datalens_sqlqueries_get",
            {
                "sql_query_id": "sq00000000002",
                "rev_id": "rev7",
                "include_permissions": True,
                "include_favorite": False,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getSqlQuery",
                    json={
                        "sqlQueryId": "sq00000000002",
                        "revId": "rev7",
                        "includePermissions": True,
                        "includeFavorite": False,
                    },
                ),
                Reply(
                    json={
                        "entry": {**QUERY, "entryId": "sq00000000002", "revId": "rev7"},
                        "isFavorite": False,
                        "permissions": {
                            "execute": True,
                            "read": True,
                            "edit": False,
                            "admin": False,
                        },
                    }
                ),
            )
        ],
    ),
    Case(
        "datalens.sqlqueries.create",
        kwargs={
            "workbook_id": "wb000000000001",
            "name": "Orders a day",
            "connection_id": "con00000000001",
            "query": "select count(*) from orders",
        },
        cli=[
            *("datalens", "sqlqueries", "create", "--workbook-id", "wb000000000001"),
            *("--name", "Orders a day", "--connection-id", "con00000000001"),
            *("--query", "select count(*) from orders"),
        ],
        mcp=(
            "datalens_sqlqueries_create",
            {
                "workbook_id": "wb000000000001",
                "name": "Orders a day",
                "connection_id": "con00000000001",
                "query": "select count(*) from orders",
            },
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createSqlQuery",
                    json={
                        "workbookId": "wb000000000001",
                        "name": "Orders a day",
                        "connectionId": "con00000000001",
                        "query": "select count(*) from orders",
                    },
                ),
                Reply(json={"entry": QUERY}),
            )
        ],
    ),
    Case(
        "datalens.sqlqueries.create",
        kwargs={
            "workbook_id": "wb000000000002",
            "name": "Orders since",
            "connection_id": "con00000000002",
            "query": "select count(*) from orders where day >= {{since}}",
            "description": "Orders since a day",
            "params": [CreateSqlQueryArgsParamsItemVariant2.model_validate(SINCE)],
        },
        cli=[
            *("datalens", "sqlqueries", "create", "--workbook-id", "wb000000000002"),
            *("--name", "Orders since", "--connection-id", "con00000000002"),
            *("--query", "select count(*) from orders where day >= {{since}}"),
            *("--description", "Orders since a day", "--params", json.dumps([SINCE])),
        ],
        mcp=(
            "datalens_sqlqueries_create",
            {
                "workbook_id": "wb000000000002",
                "name": "Orders since",
                "connection_id": "con00000000002",
                "query": "select count(*) from orders where day >= {{since}}",
                "description": "Orders since a day",
                "params": [SINCE],
            },
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createSqlQuery",
                    json={
                        "workbookId": "wb000000000002",
                        "name": "Orders since",
                        "connectionId": "con00000000002",
                        "query": "select count(*) from orders where day >= {{since}}",
                        "description": "Orders since a day",
                        "params": [SINCE],
                    },
                ),
                Reply(json={"entry": {**QUERY, "entryId": "sq00000000002"}}),
            )
        ],
    ),
    Case(
        "datalens.sqlqueries.update",
        args=("sq00000000001",),
        kwargs={
            "connection_id": "con00000000001",
            "query": "select count(*) from orders where paid",
        },
        cli=[
            *("datalens", "sqlqueries", "update", "sq00000000001"),
            *("--connection-id", "con00000000001"),
            *("--query", "select count(*) from orders where paid"),
        ],
        mcp=(
            "datalens_sqlqueries_update",
            {
                "sql_query_id": "sq00000000001",
                "connection_id": "con00000000001",
                "query": "select count(*) from orders where paid",
            },
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateSqlQuery",
                    json={
                        "sqlQueryId": "sq00000000001",
                        "connectionId": "con00000000001",
                        "query": "select count(*) from orders where paid",
                    },
                ),
                Reply(
                    json={
                        "entry": {
                            **QUERY,
                            "data": {
                                "connectionId": "con00000000001",
                                "query": "select count(*) from orders where paid",
                            },
                        }
                    }
                ),
            )
        ],
    ),
    Case(
        "datalens.sqlqueries.update",
        args=("sq00000000003",),
        kwargs={
            "connection_id": "con00000000003",
            "query": "select * from orders limit {{top}}",
            "description": "The first orders",
            "params": [UpdateSqlQueryArgsParamsItemVariant3.model_validate(LIMIT)],
        },
        cli=[
            *("datalens", "sqlqueries", "update", "sq00000000003"),
            *("--connection-id", "con00000000003"),
            *("--query", "select * from orders limit {{top}}"),
            *("--description", "The first orders", "--params", json.dumps([LIMIT])),
        ],
        mcp=(
            "datalens_sqlqueries_update",
            {
                "sql_query_id": "sq00000000003",
                "connection_id": "con00000000003",
                "query": "select * from orders limit {{top}}",
                "description": "The first orders",
                "params": [LIMIT],
            },
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateSqlQuery",
                    json={
                        "sqlQueryId": "sq00000000003",
                        "connectionId": "con00000000003",
                        "query": "select * from orders limit {{top}}",
                        "description": "The first orders",
                        "params": [LIMIT],
                    },
                ),
                Reply(json={"entry": {**QUERY, "entryId": "sq00000000003"}}),
            )
        ],
    ),
    Case(
        "datalens.sqlqueries.delete",
        args=("sq00000000001",),
        cli=["datalens", "sqlqueries", "delete", "sq00000000001"],
        mcp=("datalens_sqlqueries_delete", {"sql_query_id": "sq00000000001"}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent("POST", "rpc/deleteSqlQuery", json={"sqlQueryId": "sq00000000001"}),
                Reply(json={}),
            )
        ],
    ),
    Case(
        "datalens.sqlqueries.run",
        args=("sq00000000001",),
        kwargs={"params": {"since": "2026-10-01"}},
        cli=[
            *("datalens", "sqlqueries", "run", "sq00000000001"),
            *("--params", json.dumps({"since": "2026-10-01"})),
        ],
        mcp=(
            "datalens_sqlqueries_run",
            {"sql_query_id": "sq00000000001", "params": {"since": "2026-10-01"}},
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/runSqlQuery",
                    json={"sqlQueryId": "sq00000000001", "params": {"since": "2026-10-01"}},
                ),
                Reply(json=RAN),
            )
        ],
    ),
    # With the defaults of its parameters; one statement of two fails.
    Case(
        "datalens.sqlqueries.run",
        args=("sq00000000004",),
        cli=["datalens", "sqlqueries", "run", "sq00000000004"],
        mcp=("datalens_sqlqueries_run", {"sql_query_id": "sq00000000004"}),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/runSqlQuery", json={"sqlQueryId": "sq00000000004"}),
                Reply(
                    json={
                        **RAN,
                        "id": "run0000000002",
                        "status": "partial_success",
                        "results": [
                            RAN["results"][0],
                            {
                                "status": "error",
                                "code": "ERR.QUERY",
                                "message": "The statement failed",
                                "databaseMessage": "relation does not exist",
                            },
                        ],
                    }
                ),
            )
        ],
    ),
]
