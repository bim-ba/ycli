# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class GetSqlQueryArgs(RequestBody):
    sql_query_id: str = Field(
        ..., alias="sqlQueryId", description="ID of the SQL query to retrieve."
    )
    rev_id: str | None = Field(
        default=None,
        alias="revId",
        description="ID of the SQL query revision to retrieve.",
    )
    include_permissions: bool | None = Field(
        default=None,
        alias="includePermissions",
        description="Whether to include SQL query permissions.",
    )
    include_favorite: bool | None = Field(
        default=None,
        alias="includeFavorite",
        description="Whether to include the favorite status.",
    )


class DeleteSqlQueryArgs(RequestBody):
    sql_query_id: str = Field(..., alias="sqlQueryId", description="ID of the SQL query to delete.")


class DeleteSqlQueryResponse(APIModel):
    pass


class SqlQueryDataParamsItemVariant1DefaultValue(APIModel):
    """Default value of the parameter."""

    from_: str | None = Field(default=None, alias="from", description="Start of the interval.")
    to: str | None = Field(default=None, description="End of the interval.")


class SqlQueryDataParamsItemVariant2(APIModel):
    name: str | None = None
    type: Literal["date"] | Literal["datetime"] | None = Field(
        default=None, description="Type of the parameter."
    )
    default_value: str | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class SqlQueryDataParamsItemVariant3(APIModel):
    name: str | None = None
    type: Literal["string"] | Literal["number"] | Literal["boolean"] | None = Field(
        default=None, description="Type of the parameter."
    )
    default_value: str | int | float | bool | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class SqlQueryAnnotation(APIModel):
    """Annotation of the SQL query."""

    description: str | None = Field(default=None, description="Description of the entry.")


class GetSqlQueryResultPermissions(APIModel):
    """Permissions for the SQL query."""

    execute: bool | None = Field(
        default=None, description="Indicates if there are permissions to execute."
    )
    read: bool | None = Field(
        default=None, description="Indicates if there are permissions to read."
    )
    edit: bool | None = Field(
        default=None, description="Indicates if there are permissions to edit."
    )
    admin: bool | None = Field(
        default=None, description="Indicates if there are permissions for admin."
    )


class CreateSqlQueryArgsParamsItemVariant1DefaultValue(APIModel):
    """Default value of the parameter."""

    from_: str | None = Field(default=None, alias="from", description="Start of the interval.")
    to: str | None = Field(default=None, description="End of the interval.")


class CreateSqlQueryArgsParamsItemVariant2(APIModel):
    name: str | None = None
    type: Literal["date"] | Literal["datetime"] | None = Field(
        default=None, description="Type of the parameter."
    )
    default_value: str | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class CreateSqlQueryArgsParamsItemVariant3(APIModel):
    name: str | None = None
    type: Literal["string"] | Literal["number"] | Literal["boolean"] | None = Field(
        default=None, description="Type of the parameter."
    )
    default_value: str | int | float | bool | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class UpdateSqlQueryArgsParamsItemVariant1DefaultValue(APIModel):
    """Default value of the parameter."""

    from_: str | None = Field(default=None, alias="from", description="Start of the interval.")
    to: str | None = Field(default=None, description="End of the interval.")


class UpdateSqlQueryArgsParamsItemVariant2(APIModel):
    name: str | None = None
    type: Literal["date"] | Literal["datetime"] | None = Field(
        default=None, description="Type of the parameter."
    )
    default_value: str | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class UpdateSqlQueryArgsParamsItemVariant3(APIModel):
    name: str | None = None
    type: Literal["string"] | Literal["number"] | Literal["boolean"] | None = Field(
        default=None, description="Type of the parameter."
    )
    default_value: str | int | float | bool | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class RunSqlQueryResultResultsItemVariant1ColumnsItem(APIModel):
    name: str | None = Field(default=None, description="Name of the column.")


class RunSqlQueryResultResultsItemVariant2(APIModel):
    status: Literal["error"] = Field(..., description="Status of the statement.")
    code: str | None = Field(default=None, description="Error code.")
    message: str | None = Field(default=None, description="Error message.")
    database_message: str | None = Field(
        default=None,
        alias="databaseMessage",
        description="Message returned by the database.",
    )


class RunSqlQueryArgsParamsValueVariant5(APIModel):
    from_: str | None = Field(default=None, alias="from", description="Start of the interval.")
    to: str | None = Field(default=None, description="End of the interval.")


class RunSqlQueryArgs(RequestBody):
    sql_query_id: str = Field(..., alias="sqlQueryId", description="ID of the SQL query to run.")
    params: (
        dict[
            str,
            str
            | int
            | float
            | bool
            | list[str | int | float | bool]
            | RunSqlQueryArgsParamsValueVariant5,
        ]
        | None
    ) = Field(
        default=None,
        description="Values of the query parameters, keyed by name. A parameter left out here falls back to its default value.",
    )


class SqlQueryDataParamsItemVariant1(APIModel):
    name: str | None = None
    type: Literal["date-interval"] | Literal["datetime-interval"] | None = Field(
        default=None, description="Type of the parameter."
    )
    default_value: SqlQueryDataParamsItemVariant1DefaultValue | None = Field(
        default=None, alias="defaultValue"
    )


class CreateSqlQueryArgsParamsItemVariant1(APIModel):
    name: str | None = None
    type: Literal["date-interval"] | Literal["datetime-interval"] | None = Field(
        default=None, description="Type of the parameter."
    )
    default_value: CreateSqlQueryArgsParamsItemVariant1DefaultValue | None = Field(
        default=None, alias="defaultValue"
    )


class UpdateSqlQueryArgsParamsItemVariant1(APIModel):
    name: str | None = None
    type: Literal["date-interval"] | Literal["datetime-interval"] | None = Field(
        default=None, description="Type of the parameter."
    )
    default_value: UpdateSqlQueryArgsParamsItemVariant1DefaultValue | None = Field(
        default=None, alias="defaultValue"
    )


class RunSqlQueryResultResultsItemVariant1(APIModel):
    status: Literal["success"] = Field(..., description="Status of the statement.")
    columns: list[RunSqlQueryResultResultsItemVariant1ColumnsItem] | None = Field(
        default=None,
        description="Columns of the statement result. Empty for statements that return no rows.",
    )
    rows: list[list[str | int | float | bool | None]] | None = Field(
        default=None,
        description="Rows of the statement result, with values in the order of the columns.",
    )
    affected_rows: int | float | None = Field(
        default=None,
        alias="affectedRows",
        description="Number of rows affected by the statement.",
    )


class CreateSqlQueryArgs(RequestBody):
    workbook_id: str = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook where the SQL query should be created.",
    )
    name: str = Field(..., description="Name of the SQL query in the workbook.")
    description: str | None = Field(default=None, description="Description of the SQL query.")
    connection_id: str = Field(
        ...,
        alias="connectionId",
        description="ID of the connection. Supported connection types: PostgreSQL, ClickHouse, MySQL, Greenplum, Trino.",
    )
    query: str = Field(..., description="Text of the SQL query.")
    params: (
        list[
            CreateSqlQueryArgsParamsItemVariant1
            | CreateSqlQueryArgsParamsItemVariant2
            | CreateSqlQueryArgsParamsItemVariant3
        ]
        | None
    ) = Field(default=None, description="Parameters of the SQL query.")


class UpdateSqlQueryArgs(RequestBody):
    sql_query_id: str = Field(..., alias="sqlQueryId", description="ID of the SQL query to update.")
    description: str | None = Field(default=None, description="New description of the SQL query.")
    connection_id: str = Field(
        ...,
        alias="connectionId",
        description="ID of the connection. Supported connection types: PostgreSQL, ClickHouse, MySQL, Greenplum, Trino.",
    )
    query: str = Field(..., description="Text of the SQL query.")
    params: (
        list[
            UpdateSqlQueryArgsParamsItemVariant1
            | UpdateSqlQueryArgsParamsItemVariant2
            | UpdateSqlQueryArgsParamsItemVariant3
        ]
        | None
    ) = Field(default=None, description="Parameters of the SQL query.")


class RunSqlQueryResult(APIModel):
    id: str | None = Field(default=None, description="ID of the query run.")
    connection_id: str | None = Field(
        default=None,
        alias="connectionId",
        description="ID of the connection the query was executed on.",
    )
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="ID of the DataLens tenant."
    )
    status: Literal["success", "error", "pending", "partial_success"] | str | None = Field(
        default=None, description="Status of the query run."
    )
    query: str | None = Field(default=None, description="Text of the executed query.")
    statement_positions: list[list[Any]] | None = Field(
        default=None,
        alias="statementPositions",
        description="Start and end indexes of the executed statements.",
    )
    results: (
        list[RunSqlQueryResultResultsItemVariant1 | RunSqlQueryResultResultsItemVariant2] | None
    ) = Field(
        default=None,
        description="Results of the executed statements, in the order of the statements.",
    )
    created_by: str | None = Field(
        default=None, alias="createdBy", description="ID of the user who ran the query."
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the query run was created.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the query run was updated.",
    )


class SqlQueryData(APIModel):
    """Data of the SQL query entry."""

    connection_id: str | None = Field(
        default=None, alias="connectionId", description="ID of the connection."
    )
    query: str | None = Field(default=None, description="Text of the SQL query.")
    statement_positions: list[list[Any]] | None = Field(
        default=None,
        alias="statementPositions",
        description="Start and end indexes of the query statements.",
    )
    params: (
        list[
            SqlQueryDataParamsItemVariant1
            | SqlQueryDataParamsItemVariant2
            | SqlQueryDataParamsItemVariant3
        ]
        | None
    ) = Field(default=None, description="Parameters of the SQL query.")


class SqlQuery(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the SQL query."
    )
    scope: Literal["sql_query"] = Field(..., description="Scope of the SQL query entry.")
    type: str | None = Field(default=None, description="Type of the SQL query entry.")
    key: str | None = Field(default=None, description="Key of the SQL query entry.")
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook containing the SQL query.",
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the collection containing the SQL query.",
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="ID of the current SQL query revision."
    )
    saved_id: str | None = Field(
        default=None, alias="savedId", description="ID of the saved SQL query revision."
    )
    published_id: str | None = Field(
        default=None,
        alias="publishedId",
        description="ID of the published SQL query revision.",
    )
    data: SqlQueryData | None = None
    annotation: SqlQueryAnnotation | None = None
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the SQL query.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the SQL query was created.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the SQL query.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the SQL query was last updated.",
    )
    rev_updated_by: str | None = Field(
        default=None,
        alias="revUpdatedBy",
        description="ID of the user who last updated the current revision.",
    )
    rev_updated_at: str | None = Field(
        default=None,
        alias="revUpdatedAt",
        description="Date and time when the current revision was last updated.",
    )
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="ID of the tenant that owns the SQL query.",
    )
    hidden: bool | None = Field(default=None, description="Whether the SQL query is hidden.")
    version: int | float | None = Field(
        default=None, description="Schema version of the SQL query."
    )
    links: dict[str, Any] | None = Field(
        default=None, description="Links to the entries the SQL query depends on."
    )


class GetSqlQueryResult(APIModel):
    entry: SqlQuery | None = None
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Whether the SQL query is a favorite.",
    )
    permissions: GetSqlQueryResultPermissions | None = None


class CreateSqlQueryResult(APIModel):
    entry: SqlQuery | None = None


class UpdateSqlQueryResult(APIModel):
    entry: SqlQuery | None = None
