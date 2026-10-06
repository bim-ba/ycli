"""DataLens saved SQL query operations, declared once (sans-IO).

Every one of them is marked experimental in the document DataLens publishes.

Examples:
    >>> run("sq1", params=None).body
    {'sqlQueryId': 'sq1'}
"""

from collections.abc import Mapping, Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.schemas.sql_queries import (
    CreateSqlQueryArgs,
    DeleteSqlQueryArgs,
    GetSqlQueryArgs,
    RunSqlQueryArgs,
    UpdateSqlQueryArgs,
)
from ycli.yandex.datalens.sqlqueries.models import (
    SqlQueryCreated,
    SqlQueryDetails,
    SqlQueryNewParam,
    SqlQueryRun,
    SqlQuerySaved,
    SqlQuerySavedParam,
    SqlQueryValue,
)


def get(
    sql_query_id: str,
    *,
    rev_id: str | None,
    include_permissions: bool | None,
    include_favorite: bool | None,
) -> Endpoint[SqlQueryDetails]:
    body = GetSqlQueryArgs(
        sqlQueryId=sql_query_id,
        revId=rev_id,
        includePermissions=include_permissions,
        includeFavorite=include_favorite,
    )
    return RPC("getSqlQuery", SqlQueryDetails, json=body, effect=Effect.READ)


def create(
    *,
    workbook_id: str,
    name: str,
    connection_id: str,
    query: str,
    description: str | None,
    params: Sequence[SqlQueryNewParam] | None,
) -> Endpoint[SqlQueryCreated]:
    body = CreateSqlQueryArgs(
        workbookId=workbook_id,
        name=name,
        connectionId=connection_id,
        query=query,
        description=description,
        params=None if params is None else list(params),
    )
    return RPC("createSqlQuery", SqlQueryCreated, json=body, effect=Effect.WRITE)


def update(
    sql_query_id: str,
    *,
    connection_id: str,
    query: str,
    description: str | None,
    params: Sequence[SqlQuerySavedParam] | None,
) -> Endpoint[SqlQuerySaved]:
    body = UpdateSqlQueryArgs(
        sqlQueryId=sql_query_id,
        connectionId=connection_id,
        query=query,
        description=description,
        params=None if params is None else list(params),
    )
    return RPC("updateSqlQuery", SqlQuerySaved, json=body, effect=Effect.IDEMPOTENT_WRITE)


def delete(sql_query_id: str) -> Endpoint[None]:
    # The document describes an empty object for a reply: nothing in it to read.
    body = DeleteSqlQueryArgs(sqlQueryId=sql_query_id)
    return RPC("deleteSqlQuery", json=body, effect=Effect.DESTRUCTIVE)


def run(sql_query_id: str, *, params: Mapping[str, SqlQueryValue] | None) -> Endpoint[SqlQueryRun]:
    # A write: the saved text may be any statement the connection lets through.
    body = RunSqlQueryArgs(sqlQueryId=sql_query_id, params=None if params is None else dict(params))
    return RPC("runSqlQuery", SqlQueryRun, json=body, effect=Effect.WRITE)
