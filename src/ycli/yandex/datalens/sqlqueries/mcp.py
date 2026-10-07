"""DataLens saved SQL queries FastMCP tools (read + write) — Depends DI, native errors."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    datalens_client,
    new_server,
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
from ycli.yandex.models import Ack

mcp = new_server("datalens-sqlqueries")

SqlQueryID = Annotated[str, Field(description="SQL query id.")]
Connection = Annotated[
    str,
    Field(
        description="The connection it runs over: PostgreSQL, ClickHouse, MySQL, Greenplum, Trino."
    ),
]
Query = Annotated[str, Field(description="The text of the query.")]
Description = Annotated[str | None, Field(description="A description.")]


@mcp.tool(name="sqlqueries_get", annotations={**RO, "title": "Get DataLens saved SQL query"})
def get(
    sql_query_id: SqlQueryID,
    rev_id: Annotated[
        str | None, Field(description="The revision to read; the current one when left out.")
    ] = None,
    include_permissions: Annotated[
        bool | None, Field(description="Also say what the caller may do with it.")
    ] = None,
    include_favorite: Annotated[
        bool | None, Field(description="Also say whether it is a favourite.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> SqlQueryDetails:
    """One saved SQL query: its text, its connection and its parameters.

    Experimental in the DataLens API and written from its document: not measured. An
    organization whose SQL editor is off answers 403 ``SQL_EDITOR_NOT_ALLOWED``.
    """
    return client.sqlqueries.get(
        sql_query_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_favorite=include_favorite,
    )


@mcp.tool(
    name="sqlqueries_create", annotations={**WRITE, "title": "Create DataLens saved SQL query"}
)
def create(
    workbook_id: Annotated[str, Field(description="The workbook to keep it in.")],
    name: Annotated[str, Field(description="The query's name in the workbook.")],
    connection_id: Connection,
    query: Query,
    description: Description = None,
    params: Annotated[
        list[SqlQueryNewParam] | None,
        Field(description="The parameters the text takes: a name, a type and a default each."),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> SqlQueryCreated:
    """Save a SQL query in a workbook and return it.

    Experimental in the DataLens API and written from its document: not measured. An
    organization whose SQL editor is off answers 403 ``SQL_EDITOR_NOT_ALLOWED``.
    """
    return client.sqlqueries.create(
        workbook_id=workbook_id,
        name=name,
        connection_id=connection_id,
        query=query,
        description=description,
        params=params,
    )


@mcp.tool(
    name="sqlqueries_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens saved SQL query"},
)
def update(
    sql_query_id: SqlQueryID,
    connection_id: Connection,
    query: Query,
    description: Description = None,
    params: Annotated[
        list[SqlQuerySavedParam] | None, Field(description="The parameters the text takes.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> SqlQuerySaved:
    """Save a SQL query anew and return it; the connection and the text go every time.

    Experimental in the DataLens API and written from its document: not measured.
    """
    return client.sqlqueries.update(
        sql_query_id,
        connection_id=connection_id,
        query=query,
        description=description,
        params=params,
    )


@mcp.tool(
    name="sqlqueries_delete",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens saved SQL query"},
)
def delete(sql_query_id: SqlQueryID, client: DataLensClient = Depends(datalens_client)) -> Ack:
    """Delete a saved SQL query.

    Experimental in the DataLens API and written from its document: not measured.
    """
    client.sqlqueries.delete(sql_query_id)
    return Ack.deleted("SQL query", sql_query_id)


@mcp.tool(name="sqlqueries_run", annotations={**WRITE, "title": "Run DataLens saved SQL query"})
def run(
    sql_query_id: SqlQueryID,
    params: Annotated[
        dict[str, SqlQueryValue] | None,
        Field(description="The values of the parameters, by name; one left out takes its default."),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> SqlQueryRun:
    """Run a saved SQL query on its connection and return the result of each statement.

    The text runs as it is saved: one that changes data changes it. Experimental in the DataLens
    API and written from its document: not measured.
    """
    return client.sqlqueries.run(sql_query_id, params=params)
