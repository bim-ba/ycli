# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class DefaultValue(APIModel):
    """Default value of the parameter."""

    from_: str = Field(..., alias="from", description="Start of the interval.")
    to: str = Field(..., description="End of the interval.")


class Param(APIModel):
    type: Literal["date-interval"] | Literal["datetime-interval"] = Field(
        ..., description="Type of the parameter."
    )
    default_value: DefaultValue | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class ParamModel(APIModel):
    type: Literal["date"] | Literal["datetime"] = Field(..., description="Type of the parameter.")
    default_value: str | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class ParamModel1(APIModel):
    type: Literal["string"] | Literal["number"] | Literal["boolean"] = Field(
        ..., description="Type of the parameter."
    )
    default_value: str | float | bool | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class ParamModel2(APIModel):
    name: str


class ParamModel3(Param, ParamModel2):
    pass


class ParamModel4(ParamModel, ParamModel2):
    pass


class ParamModel5(ParamModel1, ParamModel2):
    pass


class ParamModel6(RootModel[ParamModel3 | ParamModel4 | ParamModel5]):
    root: ParamModel3 | ParamModel4 | ParamModel5


class Data(APIModel):
    """Data of the SQL query entry."""

    connection_id: str = Field(..., alias="connectionId", description="ID of the connection.")
    query: str = Field(..., description="Text of the SQL query.")
    statement_positions: list[list[Any]] = Field(
        ...,
        alias="statementPositions",
        description="Start and end indexes of the query statements.",
    )
    params: list[ParamModel6] | None = Field(
        default=None, description="Parameters of the SQL query."
    )


class Annotation(APIModel):
    """Annotation of the SQL query."""

    description: str | None = Field(default=None, description="Description of the entry.")


class SqlQuery(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the SQL query.")
    scope: Literal["sql_query"] = Field(..., description="Scope of the SQL query entry.")
    type: str = Field(..., description="Type of the SQL query entry.")
    key: str = Field(..., description="Key of the SQL query entry.")
    workbook_id: str = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook containing the SQL query.",
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection containing the SQL query.",
    )
    rev_id: str = Field(..., alias="revId", description="ID of the current SQL query revision.")
    saved_id: str = Field(..., alias="savedId", description="ID of the saved SQL query revision.")
    published_id: str | None = Field(
        ..., alias="publishedId", description="ID of the published SQL query revision."
    )
    data: Data = Field(..., description="Data of the SQL query entry.")
    annotation: Annotation | None = Field(..., description="Annotation of the SQL query.")
    created_by: str = Field(
        ..., alias="createdBy", description="ID of the user who created the SQL query."
    )
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="Date and time when the SQL query was created.",
    )
    updated_by: str = Field(
        ...,
        alias="updatedBy",
        description="ID of the user who last updated the SQL query.",
    )
    updated_at: str = Field(
        ...,
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
    tenant_id: str = Field(
        ..., alias="tenantId", description="ID of the tenant that owns the SQL query."
    )
    hidden: bool = Field(..., description="Whether the SQL query is hidden.")
    version: float | None = Field(..., description="Schema version of the SQL query.")
    links: dict[str, Any] | None = Field(
        default=None, description="Links to the entries the SQL query depends on."
    )


class Permissions(APIModel):
    """Permissions for the SQL query."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class GetSqlQueryResult(APIModel):
    entry: SqlQuery
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Whether the SQL query is a favorite.",
    )
    permissions: Permissions | None = Field(
        default=None, description="Permissions for the SQL query."
    )


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


class CreateSqlQueryResult(APIModel):
    entry: SqlQuery


class ParamModel7(APIModel):
    type: Literal["date-interval"] | Literal["datetime-interval"] = Field(
        ..., description="Type of the parameter."
    )
    default_value: DefaultValue | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class ParamModel8(APIModel):
    type: Literal["date"] | Literal["datetime"] = Field(..., description="Type of the parameter.")
    default_value: str | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class ParamModel9(APIModel):
    type: Literal["string"] | Literal["number"] | Literal["boolean"] = Field(
        ..., description="Type of the parameter."
    )
    default_value: str | float | bool | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class ParamModel10(APIModel):
    name: str


class ParamModel11(ParamModel7, ParamModel10):
    pass


class ParamModel12(ParamModel8, ParamModel10):
    pass


class ParamModel13(ParamModel9, ParamModel10):
    pass


class ParamModel14(RootModel[ParamModel11 | ParamModel12 | ParamModel13]):
    root: ParamModel11 | ParamModel12 | ParamModel13


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
    params: list[ParamModel14] | None = Field(
        default=None, description="Parameters of the SQL query."
    )


class UpdateSqlQueryResult(APIModel):
    entry: SqlQuery


class ParamModel15(APIModel):
    type: Literal["date-interval"] | Literal["datetime-interval"] = Field(
        ..., description="Type of the parameter."
    )
    default_value: DefaultValue | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class ParamModel16(APIModel):
    type: Literal["date"] | Literal["datetime"] = Field(..., description="Type of the parameter.")
    default_value: str | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class ParamModel17(APIModel):
    type: Literal["string"] | Literal["number"] | Literal["boolean"] = Field(
        ..., description="Type of the parameter."
    )
    default_value: str | float | bool | None = Field(
        default=None,
        alias="defaultValue",
        description="Default value of the parameter.",
    )


class ParamModel18(APIModel):
    name: str


class ParamModel19(ParamModel15, ParamModel18):
    pass


class ParamModel20(ParamModel16, ParamModel18):
    pass


class ParamModel21(ParamModel17, ParamModel18):
    pass


class ParamModel22(RootModel[ParamModel19 | ParamModel20 | ParamModel21]):
    root: ParamModel19 | ParamModel20 | ParamModel21


class UpdateSqlQueryArgs(RequestBody):
    sql_query_id: str = Field(..., alias="sqlQueryId", description="ID of the SQL query to update.")
    description: str | None = Field(default=None, description="New description of the SQL query.")
    connection_id: str = Field(
        ...,
        alias="connectionId",
        description="ID of the connection. Supported connection types: PostgreSQL, ClickHouse, MySQL, Greenplum, Trino.",
    )
    query: str = Field(..., description="Text of the SQL query.")
    params: list[ParamModel22] | None = Field(
        default=None, description="Parameters of the SQL query."
    )


class DeleteSqlQueryArgs(RequestBody):
    sql_query_id: str = Field(..., alias="sqlQueryId", description="ID of the SQL query to delete.")


class Column(APIModel):
    name: str = Field(..., description="Name of the column.")


class Results(APIModel):
    status: Literal["success"] = Field(..., description="Status of the statement.")
    columns: list[Column] = Field(
        ...,
        description="Columns of the statement result. Empty for statements that return no rows.",
    )
    rows: list[list[str | float | bool | None]] = Field(
        ...,
        description="Rows of the statement result, with values in the order of the columns.",
    )
    affected_rows: float | None = Field(
        default=None,
        alias="affectedRows",
        description="Number of rows affected by the statement.",
    )


class ResultsModel(APIModel):
    status: Literal["error"] = Field(..., description="Status of the statement.")
    code: str = Field(..., description="Error code.")
    message: str = Field(..., description="Error message.")
    database_message: str | None = Field(
        default=None,
        alias="databaseMessage",
        description="Message returned by the database.",
    )


class RunSqlQueryResult(APIModel):
    id: str = Field(..., description="ID of the query run.")
    connection_id: str = Field(
        ...,
        alias="connectionId",
        description="ID of the connection the query was executed on.",
    )
    tenant_id: str = Field(..., alias="tenantId", description="ID of the DataLens tenant.")
    status: Literal["success", "error", "pending", "partial_success"] | str = Field(
        ..., description="Status of the query run."
    )
    query: str = Field(..., description="Text of the executed query.")
    statement_positions: list[list[Any]] = Field(
        ...,
        alias="statementPositions",
        description="Start and end indexes of the executed statements.",
    )
    results: list[Results | ResultsModel] = Field(
        ...,
        description="Results of the executed statements, in the order of the statements.",
    )
    created_by: str = Field(..., alias="createdBy", description="ID of the user who ran the query.")
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="Date and time when the query run was created.",
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="Date and time when the query run was updated.",
    )


class Params(APIModel):
    from_: str = Field(..., alias="from", description="Start of the interval.")
    to: str = Field(..., description="End of the interval.")


class RunSqlQueryArgs(RequestBody):
    sql_query_id: str = Field(..., alias="sqlQueryId", description="ID of the SQL query to run.")
    params: dict[str, str | float | bool | list[str | float | bool] | Params] | None = Field(
        default=None,
        description="Values of the query parameters, keyed by name. A parameter left out here falls back to its default value.",
    )


class DeleteSqlQueryResponse(APIModel):
    pass
