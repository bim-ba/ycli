"""`datalens sqlqueries` commands."""

import json
from typing import Annotated

import typer
from pydantic import TypeAdapter

from ycli.cli.body_fields import CallerFields
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.schemas.sql_queries import CreateSqlQueryArgs, UpdateSqlQueryArgs
from ycli.yandex.datalens.sqlqueries.models import (
    SqlQueryCreated,
    SqlQueryDetails,
    SqlQueryRun,
    SqlQuerySaved,
    SqlQueryValue,
)
from ycli.yandex.models import Ack

EXPERIMENTAL = (
    "Experimental in the DataLens API and written from its document: not measured. An "
    "organization whose SQL editor is off answers 403 SQL_EDITOR_NOT_ALLOWED."
)
app = typer.Typer(
    name="sqlqueries",
    help="DataLens saved SQL queries (experimental in the API).",
    no_args_is_help=True,
)

SqlQueryIDArg = Annotated[str, typer.Argument(metavar="SQL_QUERY_ID", help="SQL query id.")]
ConnectionOption = Annotated[
    str | None,
    typer.Option(
        "--connection-id",
        help="The connection it runs over: PostgreSQL, ClickHouse, MySQL, Greenplum or Trino.",
    ),
]
QueryOption = Annotated[str | None, typer.Option("--query", help="The text of the query.")]
DescriptionOption = Annotated[str | None, typer.Option("--description", help="A description.")]
ParamsOption = Annotated[
    str | None,
    typer.Option(
        "--params",
        help="The parameters the text takes, as a JSON array: "
        '[{"name": "since", "type": "date", "defaultValue": "2026-01-01"}].',
    ),
]
_VALUES: TypeAdapter[dict[str, SqlQueryValue]] = TypeAdapter(dict[str, SqlQueryValue])


@app.command(epilog=EXPERIMENTAL)
def get(
    sql_query_id: SqlQueryIDArg,
    rev_id: Annotated[
        str | None, typer.Option("--rev-id", help="The revision to read; the current if not.")
    ] = None,
    include_permissions: Annotated[
        bool | None,
        typer.Option(
            "--include-permissions/--no-include-permissions",
            help="Also say what you may do with the query.",
        ),
    ] = None,
    include_favorite: Annotated[
        bool | None,
        typer.Option(
            "--include-favorite/--no-include-favorite",
            help="Also say whether the query is a favourite.",
        ),
    ] = None,
    *,
    datalens: DataLensClient,
) -> SqlQueryDetails:
    """Print one saved SQL query: its text, its connection and its parameters."""
    return datalens.sqlqueries.get(
        sql_query_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_favorite=include_favorite,
    )


@app.command(epilog=EXPERIMENTAL)
def create(
    workbook_id: Annotated[
        str | None, typer.Option("--workbook-id", help="The workbook to keep it in.")
    ] = None,
    name: Annotated[
        str | None, typer.Option("--name", help="The query's name in the workbook.")
    ] = None,
    connection_id: ConnectionOption = None,
    query: QueryOption = None,
    description: DescriptionOption = None,
    params: ParamsOption = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> SqlQueryCreated:
    """Save a SQL query in a workbook.

    The workbook, the name, the connection and the text are required.
    """
    given = {
        "workbookId": workbook_id,
        "name": name,
        "connectionId": connection_id,
        "query": query,
        "description": description,
        "params": None if params is None else json.loads(params),
    }
    # The text of a query usually comes from --body-file: merge before the model is built.
    flags = {key: value for key, value in given.items() if value is not None}
    body = CreateSqlQueryArgs.model_validate(caller.over(flags))
    return datalens.sqlqueries.create(
        workbook_id=body.workbook_id,
        name=body.name,
        connection_id=body.connection_id,
        query=body.query,
        description=body.description,
        params=body.params,
    )


@app.command(epilog=EXPERIMENTAL)
def update(
    sql_query_id: SqlQueryIDArg,
    connection_id: ConnectionOption = None,
    query: QueryOption = None,
    description: DescriptionOption = None,
    params: ParamsOption = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> SqlQuerySaved:
    """Save a SQL query anew; the connection and the text are required every time."""
    given = {
        "sqlQueryId": sql_query_id,
        "connectionId": connection_id,
        "query": query,
        "description": description,
        "params": None if params is None else json.loads(params),
    }
    flags = {key: value for key, value in given.items() if value is not None}
    body = UpdateSqlQueryArgs.model_validate(caller.over(flags))
    return datalens.sqlqueries.update(
        body.sql_query_id,
        connection_id=body.connection_id,
        query=body.query,
        description=body.description,
        params=body.params,
    )


@app.command(epilog=EXPERIMENTAL)
def delete(sql_query_id: SqlQueryIDArg, *, datalens: DataLensClient) -> Ack:
    """Delete a saved SQL query."""
    datalens.sqlqueries.delete(sql_query_id)
    return Ack.deleted("SQL query", sql_query_id)


@app.command(epilog=EXPERIMENTAL)
def run(
    sql_query_id: SqlQueryIDArg,
    params: Annotated[
        str | None,
        typer.Option(
            "--params",
            help='The values of the parameters, as a JSON object: {"since": "2026-10-01"}. '
            "A parameter left out takes its default.",
        ),
    ] = None,
    *,
    datalens: DataLensClient,
) -> SqlQueryRun:
    """Run a saved SQL query on its connection; a text that changes data changes it."""
    values = None if params is None else _VALUES.validate_json(params)
    return datalens.sqlqueries.run(sql_query_id, params=values)
