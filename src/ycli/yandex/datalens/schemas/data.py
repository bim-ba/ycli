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
    name: str
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
    )


class GetQLChartDataResultResultsItemSchemaItem(APIModel):
    name: str
    type: str = Field(
        ...,
        description='QL value type, for example "number" or "string". Numeric values may be returned as strings.',
    )


class GetEditorChartDataResultResultsItemSchemaItem(APIModel):
    name: str


class GetDatasetDataRequestFiltersItem(APIModel):
    guid: str = Field(..., description="Dataset field GUID.")
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
    ) = Field(..., description="Filter operation.")
    values: list[str | float | bool] | None = Field(
        default=None,
        description="Filter values; the required count depends on the operation.",
    )


class GetDatasetDataRequestParamsItem(APIModel):
    guid: str = Field(..., description="Dataset parameter GUID.")
    value: str | float | bool = Field(..., description="Parameter value.")


class GetDatasetDataRequestSortItem(APIModel):
    guid: str = Field(..., description="Dataset field GUID.")
    direction: Literal["asc", "desc"] | str = Field(..., description="Sort direction.")


class GetDatasetDataResponseSchemaItem(APIModel):
    name: str = Field(..., description="Dataset field name.")
    guid: str = Field(..., description="Dataset field GUID.")
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
    ) = Field(..., description="Dataset field data type.")


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
    schema_: list[GetDatasetDataResponseSchemaItem] = Field(
        ..., alias="schema", description="Returned columns in row value order."
    )
    rows: list[list[Any]] = Field(..., description="Rows with values ordered according to schema.")


class GetWizardChartDataResultResultsItem(APIModel):
    schema_: list[GetWizardChartDataResultResultsItemSchemaItem] = Field(
        ..., alias="schema", description="Columns in row value order."
    )
    rows: list[list[Any]] = Field(..., description="Values ordered according to schema.")


class GetQLChartDataResultResultsItem(APIModel):
    schema_: list[GetQLChartDataResultResultsItemSchemaItem] = Field(
        ..., alias="schema", description="Columns in row value order."
    )
    rows: list[list[Any]] = Field(..., description="Values ordered according to schema.")


class GetEditorChartDataResultResultsItem(APIModel):
    schema_: list[GetEditorChartDataResultResultsItemSchemaItem] = Field(
        ..., alias="schema", description="Columns in row value order."
    )
    rows: list[list[Any]] = Field(..., description="Values ordered according to schema.")


class GetWizardChartDataResult(APIModel):
    chart_type: Literal["wizard"] = Field(..., alias="chartType")
    results: list[GetWizardChartDataResultResultsItem] = Field(
        ...,
        description="Tables in query and block order. Results with different schemas are returned separately.",
    )


class GetQLChartDataResult(APIModel):
    chart_type: Literal["ql"] = Field(..., alias="chartType")
    results: list[GetQLChartDataResultResultsItem] = Field(
        ...,
        description="Tables in query and block order. Results with different schemas are returned separately.",
    )


class GetEditorChartDataResult(APIModel):
    chart_type: Literal["editor"] = Field(..., alias="chartType")
    results: list[GetEditorChartDataResultResultsItem] = Field(
        ...,
        description="Tables in query and block order. Results with different schemas are returned separately.",
    )


class GetChartDataResult(
    RootModel[GetWizardChartDataResult | GetQLChartDataResult | GetEditorChartDataResult]
):
    root: GetWizardChartDataResult | GetQLChartDataResult | GetEditorChartDataResult = Field(
        ..., discriminator="chart_type"
    )
