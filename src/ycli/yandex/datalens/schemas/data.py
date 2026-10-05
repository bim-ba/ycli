# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class GetChartDataArgs(RequestBody):
    chart_id: str = Field(..., alias="chartId", description="Saved chart ID.")
    params: dict[str, str | list[str]] | None = Field(
        default=None,
        description="Chart parameters, including table pagination. Saved chart settings apply.",
    )


class GetWizardChartDataResultResultsItemSchemaItem(APIModel):
    name: str | None = None
    guid: str | None = Field(default=None, description="Field GUID, when provided by the source.")
    type: (
        Literal[
            "date",
            "genericdatetime",
            "datetimetz",
            "integer",
            "uinteger",
            "string",
            "float",
            "boolean",
            "geopoint",
            "geopolygon",
            "markup",
            "heatmap",
            "array_int",
            "array_float",
            "array_str",
            "unsupported",
            "hierarchy",
            "tree_str",
            "tree_int",
            "tree_float",
        ]
        | str
        | None
    ) = None


class GetQLChartDataResultResultsItemSchemaItem(APIModel):
    name: str | None = None
    type: str | None = Field(
        default=None,
        description='QL value type, for example "number" or "string". Numeric values may be returned as strings.',
    )


class GetEditorChartDataResultResultsItemSchemaItem(APIModel):
    name: str | None = None


class GetDatasetDataRequestFiltersItem(APIModel):
    guid: str | None = Field(default=None, description="Dataset field GUID.")
    operation: (
        Literal[
            "in",
            "nin",
            "isnull",
            "isnotnull",
            "between",
            "eq",
            "ne",
            "gt",
            "lt",
            "gte",
            "lte",
            "istartswith",
            "startswith",
            "iendswith",
            "endswith",
            "icontains",
            "contains",
            "noticontains",
            "notcontains",
            "leneq",
            "lenne",
            "lengt",
            "lengte",
            "lenlt",
            "lenlte",
        ]
        | str
        | None
    ) = Field(default=None, description="Filter operation.")
    values: list[str | float | bool] | None = Field(
        default=None,
        description="Filter values; the required count depends on the operation.",
    )


class GetDatasetDataRequestParamsItem(APIModel):
    guid: str | None = Field(default=None, description="Dataset parameter GUID.")
    value: str | float | bool | None = Field(default=None, description="Parameter value.")


class GetDatasetDataRequestSortItem(APIModel):
    guid: str | None = Field(default=None, description="Dataset field GUID.")
    direction: Literal["asc", "desc"] | str | None = Field(
        default=None, description="Sort direction."
    )


class GetDatasetDataResponseSchemaItem(APIModel):
    name: str | None = Field(default=None, description="Dataset field name.")
    guid: str | None = Field(default=None, description="Dataset field GUID.")
    type: (
        Literal[
            "date",
            "genericdatetime",
            "datetimetz",
            "integer",
            "uinteger",
            "string",
            "float",
            "boolean",
            "geopoint",
            "geopolygon",
            "markup",
            "heatmap",
            "array_int",
            "array_float",
            "array_str",
            "unsupported",
            "hierarchy",
            "tree_str",
            "tree_int",
            "tree_float",
        ]
        | str
        | None
    ) = Field(default=None, description="Dataset field data type.")


class GetDatasetDataRequest(RequestBody):
    dataset_id: str = Field(..., alias="datasetId", description="Dataset ID.")
    workbook_id: str | None = Field(default=None, alias="workbookId", description="Workbook ID.")
    columns: list[str] = Field(..., description="Dataset field GUIDs to return.")
    filters: list[GetDatasetDataRequestFiltersItem] | None = Field(
        default=None, description="Filters to apply."
    )
    params: list[GetDatasetDataRequestParamsItem] | None = Field(
        default=None, description="Dataset parameter values."
    )
    sort: list[GetDatasetDataRequestSortItem] | None = Field(
        default=None,
        description="Sorting rules. Use a unique tie-breaking field to make pagination deterministic.",
    )
    limit: int | None = Field(
        default=None,
        description="Maximum number of rows to return. Defaults to 100. Without sort, the selected rows and their order are not guaranteed.",
    )
    offset: int | None = Field(
        default=None,
        description="Number of rows to skip. Values greater than zero require a non-empty sort.",
    )


class GetDatasetDataResponse(APIModel):
    schema_: list[GetDatasetDataResponseSchemaItem] | None = Field(
        default=None, alias="schema", description="Returned columns in row value order."
    )
    rows: list[list[Any]] | None = Field(
        default=None, description="Rows with values ordered according to schema."
    )


class GetWizardChartDataResultResultsItem(APIModel):
    schema_: list[GetWizardChartDataResultResultsItemSchemaItem] | None = Field(
        default=None, alias="schema", description="Columns in row value order."
    )
    rows: list[list[Any]] | None = Field(
        default=None, description="Values ordered according to schema."
    )


class GetQLChartDataResultResultsItem(APIModel):
    schema_: list[GetQLChartDataResultResultsItemSchemaItem] | None = Field(
        default=None, alias="schema", description="Columns in row value order."
    )
    rows: list[list[Any]] | None = Field(
        default=None, description="Values ordered according to schema."
    )


class GetEditorChartDataResultResultsItem(APIModel):
    schema_: list[GetEditorChartDataResultResultsItemSchemaItem] | None = Field(
        default=None, alias="schema", description="Columns in row value order."
    )
    rows: list[list[Any]] | None = Field(
        default=None, description="Values ordered according to schema."
    )


class GetWizardChartDataResult(APIModel):
    chart_type: Literal["wizard"] = Field(..., alias="chartType")
    results: list[GetWizardChartDataResultResultsItem] | None = Field(
        default=None,
        description="Tables in query and block order. Results with different schemas are returned separately.",
    )


class GetQLChartDataResult(APIModel):
    chart_type: Literal["ql"] = Field(..., alias="chartType")
    results: list[GetQLChartDataResultResultsItem] | None = Field(
        default=None,
        description="Tables in query and block order. Results with different schemas are returned separately.",
    )


class GetEditorChartDataResult(APIModel):
    chart_type: Literal["editor"] = Field(..., alias="chartType")
    results: list[GetEditorChartDataResultResultsItem] | None = Field(
        default=None,
        description="Tables in query and block order. Results with different schemas are returned separately.",
    )


class GetChartDataResult(
    RootModel[GetWizardChartDataResult | GetQLChartDataResult | GetEditorChartDataResult]
):
    root: GetWizardChartDataResult | GetQLChartDataResult | GetEditorChartDataResult = Field(
        ..., discriminator="chart_type"
    )
