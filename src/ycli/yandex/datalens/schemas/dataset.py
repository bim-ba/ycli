# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import AwareDatetime, Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class AvatarBase(APIModel):
    id: str | None = None


class AvatarsSourceListItem(APIModel):
    id: str | None = None
    schema_update_enabled: bool | None = None


class BigQueryTableParameters(APIModel):
    dataset_name: str | None = None
    db_version: str | None = None
    manual: bool | None = None
    table_name: str | None = None


class CHYTTableListParameters(APIModel):
    manual: bool | None = None
    table_names: str | None = None


class CHYTTableRangeParameters(APIModel):
    directory_path: str | None = None
    manual: bool | None = None
    range_from: str | None = None
    range_to: str | None = None


class CacheInvalidationError(APIModel):
    level: Literal["info", "warning", "critical"] | str | None = None
    locator: str | None = None
    message: str | None = None
    title: str | None = None


class CloneField(APIModel):
    aggregation: (
        Literal["none", "sum", "avg", "min", "max", "count", "countunique"] | str | None
    ) = None
    cast: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    from_guid: str | None = None
    guid: str | None = None
    strict: bool | None = None
    title: str | None = None


class CompatConnectionTypeListItem(APIModel):
    conn_type: (
        Literal[
            "appmetrica_api",
            "bigquery",
            "bitrix24",
            "ch_billing_analytics",
            "ch_ya_music_podcast_stats",
            "chyt",
            "clickhouse",
            "equeo",
            "extractor1c",
            "greenplum",
            "gsheets",
            "json_api",
            "kontur_market",
            "metrika_api",
            "monitoring",
            "moysklad",
            "mssql",
            "mysql",
            "oracle",
            "postgres",
            "promql",
            "smb_heatmaps",
            "snowflake",
            "speechsense",
            "trino",
            "unknown",
            "usage_analytics_detailed",
            "usage_analytics_light",
            "ydb",
            "yq",
        ]
        | str
        | None
    ) = None


class CompatSourceTypeListItem(APIModel):
    source_type: (
        Literal[
            "APPMETRICA_API",
            "BIGQUERY_SUBSELECT",
            "BIGQUERY_TABLE",
            "BITRIX_GDS",
            "CHYT_YTSAURUS_SUBSELECT",
            "CHYT_YTSAURUS_TABLE",
            "CHYT_YTSAURUS_TABLE_LIST",
            "CHYT_YTSAURUS_TABLE_RANGE",
            "CH_BILLING_ANALYTICS_TABLE",
            "CH_SMB_HEATMAPS_TABLE",
            "CH_SUBSELECT",
            "CH_TABLE",
            "CH_USAGE_TRACKING_AGG_TABLE",
            "CH_USAGE_TRACKING_TABLE",
            "CH_YA_MUSIC_PODCAST_STATS_TABLE",
            "EQUEO_CH_TABLE",
            "EXTRACTOR_1C_CH_TABLE",
            "GP_SUBSELECT",
            "GP_TABLE",
            "GSHEETS",
            "JSON_API",
            "KONTUR_MARKET_CH_TABLE",
            "METRIKA_API",
            "MONITORING",
            "MOYSKLAD_CH_TABLE",
            "MSSQL_SUBSELECT",
            "MSSQL_TABLE",
            "MYSQL_SUBSELECT",
            "MYSQL_TABLE",
            "ORACLE_SUBSELECT",
            "ORACLE_TABLE",
            "PG_SUBSELECT",
            "PG_TABLE",
            "PROMQL",
            "SNOWFLAKE_SUBSELECT",
            "SNOWFLAKE_TABLE",
            "SPEECHSENSE_TABLE",
            "TRINO_SUBSELECT",
            "TRINO_TABLE",
            "YDB_SUBSELECT",
            "YDB_TABLE",
            "YQ_SUBSELECT",
            "YQ_TABLE",
        ]
        | str
        | None
    ) = None


class ComponentError(APIModel):
    code: str | None = None
    details: dict[str, Any] | None = None
    level: Literal["error", "warning"] | str | None = None
    message: str | None = None


class ComponentErrorPack(APIModel):
    errors: list[ComponentError] | None = None
    id: str | None = None
    type: (
        Literal[
            "data_source",
            "source_avatar",
            "avatar_relation",
            "field",
            "obligatory_filter",
            "result_schema",
        ]
        | str
        | None
    ) = None


class ConnectionListItem(APIModel):
    id: str | None = None
    replacement_types: list[CompatConnectionTypeListItem] | None = None


class Connections(APIModel):
    compatible_types: list[CompatConnectionTypeListItem] | None = None
    items: list[ConnectionListItem] | None = None
    max: int | None = None


class DataTypeListItem(APIModel):
    aggregations: (
        list[Literal["none", "sum", "avg", "min", "max", "count", "countunique"] | str] | None
    ) = None
    casts: (
        list[
            Literal[
                "string",
                "integer",
                "float",
                "date",
                "datetime",
                "boolean",
                "geopoint",
                "geopolygon",
                "uuid",
                "markup",
                "datetimetz",
                "unsupported",
                "array_str",
                "array_int",
                "array_float",
                "tree_str",
                "genericdatetime",
            ]
            | str
        ]
        | None
    ) = None
    filter_operations: (
        list[
            Literal[
                "ISNULL",
                "ISNOTNULL",
                "GT",
                "LT",
                "GTE",
                "LTE",
                "EQ",
                "NE",
                "STARTSWITH",
                "ISTARTSWITH",
                "ENDSWITH",
                "IENDSWITH",
                "CONTAINS",
                "ICONTAINS",
                "NOTCONTAINS",
                "NOTICONTAINS",
                "LENEQ",
                "LENNE",
                "LENGT",
                "LENGTE",
                "LENLT",
                "LENLTE",
                "IN",
                "NIN",
                "BETWEEN",
            ]
            | str
        ]
        | None
    ) = None
    type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None


class DataTypes(APIModel):
    items: list[DataTypeListItem] | None = None


class DeleteField(APIModel):
    guid: str | None = None
    strict: bool | None = None


class DeleteObligatoryFilter(APIModel):
    id: str | None = None


class FieldInterDependencyItem(APIModel):
    dep_field_id: str | None = None
    ref_field_ids: list[str] | None = None


class FieldListItem(APIModel):
    aggregations: (
        list[Literal["none", "sum", "avg", "min", "max", "count", "countunique"] | str] | None
    ) = None
    casts: (
        list[
            Literal[
                "string",
                "integer",
                "float",
                "date",
                "datetime",
                "boolean",
                "geopoint",
                "geopolygon",
                "uuid",
                "markup",
                "datetimetz",
                "unsupported",
                "array_str",
                "array_int",
                "array_float",
                "tree_str",
                "genericdatetime",
            ]
            | str
        ]
        | None
    ) = None
    guid: str | None = None


class Fields(APIModel):
    items: list[FieldListItem] | None = None


class FormulaCalculationSpec(APIModel):
    formula: str | None = None
    guid_formula: str | None = None


class IndexInfo(APIModel):
    columns: list[str] | None = None
    kind: Literal["table_sorting"] | None = None


class Join(APIModel):
    operators: list[Literal["gt", "lt", "gte", "lte", "eq", "ne"] | str] | None = None
    types: list[Literal["inner", "left", "right", "full"] | str] | None = None


class Preview(APIModel):
    enabled: bool | None = None


class RLSSubject(APIModel):
    subject_id: str | None = None
    subject_name: str | None = None
    subject_type: Literal["user", "group", "all", "userid", "unknown", "notfound"] | str | None = (
        None
    )


class RefreshSource(APIModel):
    force_update_fields: bool | None = None
    id: str | None = None


class RelationBase(APIModel):
    id: str | None = None


class ReplaceConnection(APIModel):
    id: str | None = None
    new_id: str | None = None


class SQLParameters(APIModel):
    db_name: str | None = None
    db_version: str | None = None
    manual: bool | None = None
    table_name: str | None = None


class SchematizedParameters(APIModel):
    db_name: str | None = None
    db_version: str | None = None
    manual: bool | None = None
    schema_name: str | None = None
    table_name: str | None = None


class Setting(APIModel):
    name: (
        Literal["load_preview_by_default", "template_enabled", "data_export_forbidden"] | str | None
    ) = None
    value: bool | None = None


class SimpleParameters(APIModel):
    manual: bool | None = None


class SnowFlakeTableParameters(APIModel):
    db_name: str | None = None
    manual: bool | None = None
    schema_: str | None = Field(default=None, alias="schema")
    table_name: str | None = None


class SourceAvatar(APIModel):
    id: str | None = None
    is_root: bool | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    source_id: str | None = None
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class SourceAvatarStrict(APIModel):
    id: str | None = None
    is_root: bool | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    source_id: str | None = None
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class SourceBase(APIModel):
    id: str | None = None


class SourceListing(APIModel):
    db_name_label: str | None = None
    db_name_required_for_search: bool | None = None
    supports_db_name_listing: bool | None = None
    supports_query_pagination: bool | None = None
    supports_source_pagination: bool | None = None
    supports_source_search: bool | None = None


class SourcesSourceListItem(APIModel):
    id: str | None = None
    schema_update_enabled: bool | None = None


class SubselectParameters(APIModel):
    manual: bool | None = None
    subsql: str | None = None


class Where(APIModel):
    column: str | None = None
    operation: (
        Literal[
            "ISNULL",
            "ISNOTNULL",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "EQ",
            "NE",
            "STARTSWITH",
            "ISTARTSWITH",
            "ENDSWITH",
            "IENDSWITH",
            "CONTAINS",
            "ICONTAINS",
            "NOTCONTAINS",
            "NOTICONTAINS",
            "LENEQ",
            "LENNE",
            "LENGT",
            "LENGTE",
            "LENLT",
            "LENLTE",
            "IN",
            "NIN",
            "BETWEEN",
        ]
        | str
        | None
    ) = None
    values: list[Any] | None = None


class AddSourceAvatar(APIModel):
    action: Literal["add_source_avatar"]
    disable_fields_update: bool | None = None
    order_index: int | None = None
    source_avatar: SourceAvatar | None = None


class ArrayFloat(APIModel):
    type: Literal["array_float"]
    value: list[float] | None = None


class ArrayInt(APIModel):
    type: Literal["array_int"]
    value: list[int] | None = None


class ArrayStr(APIModel):
    type: Literal["array_str"]
    value: list[str] | None = None


class Boolean(APIModel):
    type: Literal["boolean"]
    value: bool | None = None


class ClickhouseDatetime64NativeType(APIModel):
    lowcardinality: bool | None = None
    name: str | None = None
    nullable: bool | None = None
    precision: int | None = None
    native_type_class_name: Literal["clickhouse_datetime64_native_type"]


class ClickhouseDatetime64withtzNativeType(APIModel):
    explicit_timezone: bool | None = None
    lowcardinality: bool | None = None
    name: str | None = None
    nullable: bool | None = None
    precision: int | None = None
    timezone_name: str | None = None
    native_type_class_name: Literal["clickhouse_datetime64withtz_native_type"]


class ClickhouseDatetimewithtzNativeType(APIModel):
    explicit_timezone: bool | None = None
    lowcardinality: bool | None = None
    name: str | None = None
    nullable: bool | None = None
    timezone_name: str | None = None
    native_type_class_name: Literal["clickhouse_datetimewithtz_native_type"]


class ClickhouseNativeType(APIModel):
    lowcardinality: bool | None = None
    name: str | None = None
    nullable: bool | None = None
    native_type_class_name: Literal["clickhouse_native_type"]


class CloneFieldModel(APIModel):
    action: Literal["clone_field"]
    field: CloneField | None = None
    order_index: int | None = None


class CommonNativeType(APIModel):
    name: str | None = None
    nullable: bool | None = None
    native_type_class_name: Literal["common_native_type"]


class Date(APIModel):
    type: Literal["date"]
    value: date | None = None


class Datetime(APIModel):
    type: Literal["datetime"]
    value: AwareDatetime | None = None


class Datetimetz(APIModel):
    type: Literal["datetimetz"]
    value: AwareDatetime | None = None


class Default(APIModel):
    type: Literal["default"]


class DeleteAvatarRelation(APIModel):
    action: Literal["delete_avatar_relation"]
    avatar_relation: RelationBase | None = None
    order_index: int | None = None


class DeleteFieldModel(APIModel):
    action: Literal["delete_field"]
    field: DeleteField | None = None
    order_index: int | None = None


class DeleteObligatoryFilterModel(APIModel):
    action: Literal["delete_obligatory_filter"]
    obligatory_filter: DeleteObligatoryFilter | None = None
    order_index: int | None = None


class DeleteSource(APIModel):
    action: Literal["delete_source"]
    order_index: int | None = None
    source: SourceBase | None = None


class DeleteSourceAvatar(APIModel):
    action: Literal["delete_source_avatar"]
    disable_fields_update: bool | None = None
    order_index: int | None = None
    source_avatar: AvatarBase | None = None


class Direct(APIModel):
    calc_mode: Literal["direct"]
    source: str | None = None


class Direct1(APIModel):
    aggregation: (
        Literal["none", "sum", "avg", "min", "max", "count", "countunique"] | str | None
    ) = None
    aggregation_locked: bool | None = None
    autoaggregated: bool | None = None
    avatar_id: str | None = None
    cast: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    data_type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    description: str | None = None
    guid: str | None = None
    has_auto_aggregation: bool | None = None
    hidden: bool | None = None
    initial_data_type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    lock_aggregation: bool | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    source: str | None = None
    title: str | None = None
    type: Literal["DIMENSION", "MEASURE"] | str | None = None
    ui_settings: str | None = None
    valid: bool | None = None
    virtual: Any | None = None
    calc_mode: Literal["direct"]


class Float(APIModel):
    type: Literal["float"]
    value: float | None = None


class Formula(APIModel):
    calc_mode: Literal["formula"]
    formula: str | None = None


class Formula2(APIModel):
    aggregation: (
        Literal["none", "sum", "avg", "min", "max", "count", "countunique"] | str | None
    ) = None
    aggregation_locked: bool | None = None
    autoaggregated: bool | None = None
    cast: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    data_type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    description: str | None = None
    formula: str | None = None
    guid: str | None = None
    guid_formula: str | None = None
    has_auto_aggregation: bool | None = None
    hidden: bool | None = None
    initial_data_type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    lock_aggregation: bool | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    title: str | None = None
    type: Literal["DIMENSION", "MEASURE"] | str | None = None
    ui_settings: str | None = None
    valid: bool | None = None
    virtual: Any | None = None
    calc_mode: Literal["formula"]


class GenericNativeType(APIModel):
    name: str | None = None
    native_type_class_name: Literal["generic_native_type"]


class Genericdatetime(APIModel):
    type: Literal["genericdatetime"]
    value: AwareDatetime | None = None


class Geopoint(APIModel):
    type: Literal["geopoint"]
    value: list[float] | None = None


class Geopolygon(APIModel):
    type: Literal["geopolygon"]
    value: list[list[list[float]]] | None = None


class Integer(APIModel):
    type: Literal["integer"]
    value: int | None = None


class LengthedNativeType(APIModel):
    length: int | None = None
    name: str | None = None
    nullable: bool | None = None
    native_type_class_name: Literal["lengthed_native_type"]


class Markup(APIModel):
    type: Literal["markup"]
    value: str | None = None


class RefreshSourceModel(APIModel):
    action: Literal["refresh_source"]
    order_index: int | None = None
    source: RefreshSource | None = None


class Regex(APIModel):
    pattern: str | None = None
    type: Literal["regex"]


class ReplaceConnectionModel(APIModel):
    action: Literal["replace_connection"]
    connection: ReplaceConnection | None = None
    order_index: int | None = None


class ResultField(APIModel):
    calc_mode: Literal["result_field"]
    field_id: str | None = None


class String(APIModel):
    type: Literal["string"]
    value: str | None = None


class TreeStr(APIModel):
    type: Literal["tree_str"]
    value: list[str] | None = None


class UpdateDescription(APIModel):
    action: Literal["update_description"]
    description: str | None = None
    order_index: int | None = None


class UpdateSetting(APIModel):
    action: Literal["update_setting"]
    order_index: int | None = None
    setting: Setting | None = None


class UpdateSourceAvatar(APIModel):
    action: Literal["update_source_avatar"]
    disable_fields_update: bool | None = None
    order_index: int | None = None
    source_avatar: SourceAvatar | None = None


class Uuid(APIModel):
    type: Literal["uuid"]
    value: str | None = None


class GetDatasetRequest(RequestBody):
    dataset_id: str = Field(..., alias="datasetId")
    workbook_id: str | None = Field(default=None, alias="workbookId")
    rev_id: str | None = None


class DeleteDatasetRequest(RequestBody):
    dataset_id: str = Field(..., alias="datasetId")


class Avatars(APIModel):
    items: list[AvatarsSourceListItem] | None = None
    max: int | None = None


class CacheInvalidationField(APIModel):
    aggregation: (
        Literal["none", "sum", "avg", "min", "max", "count", "countunique"] | str | None
    ) = None
    aggregation_locked: bool | None = None
    autoaggregated: bool | None = None
    calc_spec: FormulaCalculationSpec | None = None
    cast: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    data_type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    description: str | None = None
    guid: str | None = None
    has_auto_aggregation: bool | None = None
    hidden: bool | None = None
    initial_data_type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    lock_aggregation: bool | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    title: str | None = None
    type: Literal["DIMENSION", "MEASURE"] | str | None = None
    ui_settings: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class ComponentErrorList(APIModel):
    items: list[ComponentErrorPack] | None = None


class ConditionPartGeneric(RootModel[Direct | Formula | ResultField]):
    root: Direct | Formula | ResultField = Field(..., discriminator="calc_mode")


class FieldInterDependencyInfo(APIModel):
    deps: list[FieldInterDependencyItem] | None = None


class JoinCondition(APIModel):
    left: ConditionPartGeneric | None = None
    operator: Literal["gt", "lt", "gte", "lte", "eq", "ne"] | str | None = None
    right: ConditionPartGeneric | None = None
    type: Literal["binary"]


class ObligatoryFilter(APIModel):
    default_filters: list[Where] | None = None
    field_guid: str | None = None
    id: str | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    valid: bool | None = None


class OneOfNativeType(
    RootModel[
        GenericNativeType
        | CommonNativeType
        | LengthedNativeType
        | ClickhouseNativeType
        | ClickhouseDatetimewithtzNativeType
        | ClickhouseDatetime64NativeType
        | ClickhouseDatetime64withtzNativeType
    ]
):
    root: (
        GenericNativeType
        | CommonNativeType
        | LengthedNativeType
        | ClickhouseNativeType
        | ClickhouseDatetimewithtzNativeType
        | ClickhouseDatetime64NativeType
        | ClickhouseDatetime64withtzNativeType
    ) = Field(..., discriminator="native_type_class_name")


class ParameterValueConstraint(RootModel[Regex | Default]):
    root: Regex | Default = Field(..., discriminator="type")


class RLS2ConfigEntry(APIModel):
    allowed_value: str | None = None
    field_guid: str | None = None
    pattern_type: Literal["value", "all", "userid"] | str | None = None
    subject: RLSSubject | None = None


class RawSchemaColumn(APIModel):
    description: str | None = None
    has_auto_aggregation: bool | None = None
    lock_aggregation: bool | None = None
    name: str | None = None
    native_type: OneOfNativeType | None = None
    nullable: bool | None = None
    title: str | None = None
    user_type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None


class ResultSchemaAux(APIModel):
    inter_dependencies: FieldInterDependencyInfo | None = None


class SNOWFLAKETABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SnowFlakeTableParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["SNOWFLAKE_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class SNOWFLAKETABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SnowFlakeTableParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["SNOWFLAKE_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class SPEECHSENSETABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["SPEECHSENSE_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class SPEECHSENSETABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["SPEECHSENSE_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class Sources(APIModel):
    compatible_types: list[CompatSourceTypeListItem] | None = None
    items: list[SourcesSourceListItem] | None = None
    max: int | None = None


class TRINOSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["TRINO_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class TRINOSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["TRINO_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class TRINOTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["TRINO_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class TRINOTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["TRINO_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class Value(
    RootModel[
        String
        | Integer
        | Float
        | Date
        | Datetime
        | Datetimetz
        | Genericdatetime
        | Boolean
        | Geopoint
        | Geopolygon
        | Uuid
        | Markup
        | ArrayStr
        | ArrayInt
        | ArrayFloat
        | TreeStr
    ]
):
    root: (
        String
        | Integer
        | Float
        | Date
        | Datetime
        | Datetimetz
        | Genericdatetime
        | Boolean
        | Geopoint
        | Geopolygon
        | Uuid
        | Markup
        | ArrayStr
        | ArrayInt
        | ArrayFloat
        | TreeStr
    ) = Field(..., discriminator="type")


class YDBSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["YDB_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class YDBSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["YDB_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class YDBTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["YDB_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class YDBTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["YDB_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class YQSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["YQ_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class YQSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["YQ_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class YQTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["YQ_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class YQTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["YQ_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class AddObligatoryFilter(APIModel):
    action: Literal["add_obligatory_filter"]
    obligatory_filter: ObligatoryFilter | None = None
    order_index: int | None = None


class Parameter1(APIModel):
    aggregation: (
        Literal["none", "sum", "avg", "min", "max", "count", "countunique"] | str | None
    ) = None
    aggregation_locked: bool | None = None
    autoaggregated: bool | None = None
    cast: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    data_type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    default_value: str | None = None
    description: str | None = None
    guid: str | None = None
    has_auto_aggregation: bool | None = None
    hidden: bool | None = None
    initial_data_type: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    lock_aggregation: bool | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    template_enabled: bool | None = None
    title: str | None = None
    type: Literal["DIMENSION", "MEASURE"] | str | None = None
    ui_settings: str | None = None
    valid: bool | None = None
    value_constraint: ParameterValueConstraint | None = None
    virtual: Any | None = None
    calc_mode: Literal["parameter"]


class UpdateObligatoryFilter(APIModel):
    action: Literal["update_obligatory_filter"]
    obligatory_filter: ObligatoryFilter | None = None
    order_index: int | None = None


class APPMETRICAAPI(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["APPMETRICA_API"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class APPMETRICAAPI1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["APPMETRICA_API"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class AddField(APIModel):
    aggregation: (
        Literal["none", "sum", "avg", "min", "max", "count", "countunique"] | str | None
    ) = None
    avatar_id: str | None = None
    calc_mode: Literal["direct", "formula", "parameter"] | str | None = None
    cast: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    default_value: Value | None = None
    description: str | None = None
    formula: str | None = None
    guid: str | None = None
    guid_formula: str | None = None
    hidden: bool | None = None
    new_id: str | None = None
    source: str | None = None
    strict: bool | None = None
    template_enabled: bool | None = None
    title: str | None = None
    ui_settings: str | None = None
    value_constraint: ParameterValueConstraint | None = None


class AvatarRelation(APIModel):
    conditions: list[JoinCondition] | None = None
    id: str | None = None
    join_type: Literal["inner", "left", "right", "full"] | str | None = None
    left_avatar_id: str | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    required: bool | None = None
    right_avatar_id: str | None = None
    virtual: Any | None = None


class BIGQUERYSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["BIGQUERY_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class BIGQUERYSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["BIGQUERY_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class BIGQUERYTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: BigQueryTableParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["BIGQUERY_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class BIGQUERYTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: BigQueryTableParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["BIGQUERY_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class BITRIXGDS(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["BITRIX_GDS"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class BITRIXGDS1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["BITRIX_GDS"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYTYTSAURUSSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CHYT_YTSAURUS_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYTYTSAURUSSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CHYT_YTSAURUS_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYTYTSAURUSTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CHYT_YTSAURUS_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYTYTSAURUSTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CHYT_YTSAURUS_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYTYTSAURUSTABLELIST(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: CHYTTableListParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CHYT_YTSAURUS_TABLE_LIST"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYTYTSAURUSTABLELIST1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: CHYTTableListParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CHYT_YTSAURUS_TABLE_LIST"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYTYTSAURUSTABLERANGE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: CHYTTableRangeParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CHYT_YTSAURUS_TABLE_RANGE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYTYTSAURUSTABLERANGE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: CHYTTableRangeParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CHYT_YTSAURUS_TABLE_RANGE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHBILLINGANALYTICSTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_BILLING_ANALYTICS_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHBILLINGANALYTICSTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_BILLING_ANALYTICS_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHSMBHEATMAPSTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_SMB_HEATMAPS_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHSMBHEATMAPSTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_SMB_HEATMAPS_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHUSAGETRACKINGAGGTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_USAGE_TRACKING_AGG_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHUSAGETRACKINGAGGTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_USAGE_TRACKING_AGG_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHUSAGETRACKINGTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_USAGE_TRACKING_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHUSAGETRACKINGTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_USAGE_TRACKING_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYAMUSICPODCASTSTATSTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_YA_MUSIC_PODCAST_STATS_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CHYAMUSICPODCASTSTATSTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["CH_YA_MUSIC_PODCAST_STATS_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class CacheInvalidationSource(APIModel):
    cache_invalidation_error: CacheInvalidationError | None = None
    field: CacheInvalidationField | None = None
    filters: list[ObligatoryFilter] | None = None
    mode: Literal["sql", "formula", "off"] | str | None = None
    sql: str | None = None


class EQUEOCHTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["EQUEO_CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class EQUEOCHTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["EQUEO_CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class EXTRACTOR1CCHTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["EXTRACTOR_1C_CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class EXTRACTOR1CCHTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["EXTRACTOR_1C_CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class GPSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["GP_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class GPSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["GP_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class GPTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["GP_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class GPTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["GP_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class GSHEETS(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SimpleParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["GSHEETS"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class GSHEETS1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SimpleParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["GSHEETS"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class JSONAPI(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SimpleParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["JSON_API"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class JSONAPI1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SimpleParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["JSON_API"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class KONTURMARKETCHTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["KONTUR_MARKET_CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class KONTURMARKETCHTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["KONTUR_MARKET_CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class METRIKAAPI(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["METRIKA_API"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class METRIKAAPI1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["METRIKA_API"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MONITORING(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SimpleParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MONITORING"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MONITORING1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SimpleParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MONITORING"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MOYSKLADCHTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MOYSKLAD_CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MOYSKLADCHTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MOYSKLAD_CH_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MSSQLSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MSSQL_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MSSQLSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MSSQL_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MSSQLTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MSSQL_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MSSQLTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MSSQL_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MYSQLSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MYSQL_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MYSQLSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MYSQL_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MYSQLTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MYSQL_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class MYSQLTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SQLParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["MYSQL_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class ORACLESUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["ORACLE_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class ORACLESUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["ORACLE_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class ORACLETABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["ORACLE_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class ORACLETABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["ORACLE_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class Options(APIModel):
    connections: Connections | None = None
    data_types: DataTypes | None = None
    fields: Fields | None = None
    is_cache_invalidation_enabled_in_conn: bool | None = None
    join: Join | None = None
    preview: Preview | None = None
    schema_update_enabled: bool | None = None
    source_avatars: Avatars | None = None
    source_listing: SourceListing | None = None
    sources: Sources | None = None
    supported_functions: list[str] | None = None
    supports_offset: bool | None = None


class PGSUBSELECT(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["PG_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class PGSUBSELECT1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SubselectParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["PG_SUBSELECT"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class PGTABLE(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["PG_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class PGTABLE1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SchematizedParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["PG_TABLE"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class PROMQL(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SimpleParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["PROMQL"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class PROMQL1(APIModel):
    connection_id: str | None = None
    id: str | None = None
    index_info_set: list[IndexInfo] | None = None
    managed_by: Literal["user", "feature", "compiler_runtime"] | str | None = None
    parameter_hash: str | None = None
    parameters: SimpleParameters | None = None
    raw_schema: list[RawSchemaColumn] | None = None
    source_type: Literal["PROMQL"]
    title: str | None = None
    valid: bool | None = None
    virtual: Any | None = None


class ResultSchemaSchemaGeneric(RootModel[Direct1 | Formula2 | Parameter1]):
    root: Direct1 | Formula2 | Parameter1 = Field(..., discriminator="calc_mode")


class UpdateField(APIModel):
    aggregation: (
        Literal["none", "sum", "avg", "min", "max", "count", "countunique"] | str | None
    ) = None
    avatar_id: str | None = None
    calc_mode: Literal["direct", "formula", "parameter"] | str | None = None
    cast: (
        Literal[
            "string",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
            "geopoint",
            "geopolygon",
            "uuid",
            "markup",
            "datetimetz",
            "unsupported",
            "array_str",
            "array_int",
            "array_float",
            "tree_str",
            "genericdatetime",
        ]
        | str
        | None
    ) = None
    default_value: Value | None = None
    description: str | None = None
    formula: str | None = None
    guid: str | None = None
    guid_formula: str | None = None
    hidden: bool | None = None
    new_id: str | None = None
    source: str | None = None
    strict: bool | None = None
    template_enabled: bool | None = None
    title: str | None = None
    ui_settings: str | None = None
    value_constraint: ParameterValueConstraint | None = None


class AddAvatarRelation(APIModel):
    action: Literal["add_avatar_relation"]
    avatar_relation: AvatarRelation | None = None
    order_index: int | None = None


class AddFieldModel(APIModel):
    action: Literal["add_field"]
    field: AddField | None = None
    order_index: int | None = None


class UpdateAvatarRelation(APIModel):
    action: Literal["update_avatar_relation"]
    avatar_relation: AvatarRelation | None = None
    order_index: int | None = None


class UpdateCacheInvalidationSource(APIModel):
    action: Literal["update_cache_invalidation_source"]
    cache_invalidation_source: CacheInvalidationSource | None = None
    order_index: int | None = None


class UpdateFieldModel(APIModel):
    action: Literal["update_field"]
    field: UpdateField | None = None
    order_index: int | None = None


class DataSource(
    RootModel[
        APPMETRICAAPI1
        | BIGQUERYTABLE1
        | BIGQUERYSUBSELECT1
        | BITRIXGDS1
        | CHBILLINGANALYTICSTABLE1
        | CHYAMUSICPODCASTSTATSTABLE1
        | CHYTYTSAURUSTABLE1
        | CHYTYTSAURUSTABLELIST1
        | CHYTYTSAURUSTABLERANGE1
        | CHYTYTSAURUSSUBSELECT1
        | CHTABLE1
        | CHSUBSELECT1
        | EQUEOCHTABLE1
        | EXTRACTOR1CCHTABLE1
        | GPTABLE1
        | GPSUBSELECT1
        | GSHEETS1
        | JSONAPI1
        | KONTURMARKETCHTABLE1
        | METRIKAAPI1
        | MONITORING1
        | MOYSKLADCHTABLE1
        | MSSQLTABLE1
        | MSSQLSUBSELECT1
        | MYSQLTABLE1
        | MYSQLSUBSELECT1
        | ORACLETABLE1
        | ORACLESUBSELECT1
        | PGTABLE1
        | PGSUBSELECT1
        | PROMQL1
        | CHSMBHEATMAPSTABLE1
        | SNOWFLAKETABLE1
        | SPEECHSENSETABLE1
        | TRINOTABLE1
        | TRINOSUBSELECT1
        | CHUSAGETRACKINGTABLE1
        | CHUSAGETRACKINGAGGTABLE1
        | YDBTABLE1
        | YDBSUBSELECT1
        | YQTABLE1
        | YQSUBSELECT1
    ]
):
    root: (
        APPMETRICAAPI1
        | BIGQUERYTABLE1
        | BIGQUERYSUBSELECT1
        | BITRIXGDS1
        | CHBILLINGANALYTICSTABLE1
        | CHYAMUSICPODCASTSTATSTABLE1
        | CHYTYTSAURUSTABLE1
        | CHYTYTSAURUSTABLELIST1
        | CHYTYTSAURUSTABLERANGE1
        | CHYTYTSAURUSSUBSELECT1
        | CHTABLE1
        | CHSUBSELECT1
        | EQUEOCHTABLE1
        | EXTRACTOR1CCHTABLE1
        | GPTABLE1
        | GPSUBSELECT1
        | GSHEETS1
        | JSONAPI1
        | KONTURMARKETCHTABLE1
        | METRIKAAPI1
        | MONITORING1
        | MOYSKLADCHTABLE1
        | MSSQLTABLE1
        | MSSQLSUBSELECT1
        | MYSQLTABLE1
        | MYSQLSUBSELECT1
        | ORACLETABLE1
        | ORACLESUBSELECT1
        | PGTABLE1
        | PGSUBSELECT1
        | PROMQL1
        | CHSMBHEATMAPSTABLE1
        | SNOWFLAKETABLE1
        | SPEECHSENSETABLE1
        | TRINOTABLE1
        | TRINOSUBSELECT1
        | CHUSAGETRACKINGTABLE1
        | CHUSAGETRACKINGAGGTABLE1
        | YDBTABLE1
        | YDBSUBSELECT1
        | YQTABLE1
        | YQSUBSELECT1
    ) = Field(..., discriminator="source_type")


class DataSourceStrict(
    RootModel[
        APPMETRICAAPI
        | BIGQUERYTABLE
        | BIGQUERYSUBSELECT
        | BITRIXGDS
        | CHBILLINGANALYTICSTABLE
        | CHYAMUSICPODCASTSTATSTABLE
        | CHYTYTSAURUSTABLE
        | CHYTYTSAURUSTABLELIST
        | CHYTYTSAURUSTABLERANGE
        | CHYTYTSAURUSSUBSELECT
        | CHTABLE
        | CHSUBSELECT
        | EQUEOCHTABLE
        | EXTRACTOR1CCHTABLE
        | GPTABLE
        | GPSUBSELECT
        | GSHEETS
        | JSONAPI
        | KONTURMARKETCHTABLE
        | METRIKAAPI
        | MONITORING
        | MOYSKLADCHTABLE
        | MSSQLTABLE
        | MSSQLSUBSELECT
        | MYSQLTABLE
        | MYSQLSUBSELECT
        | ORACLETABLE
        | ORACLESUBSELECT
        | PGTABLE
        | PGSUBSELECT
        | PROMQL
        | CHSMBHEATMAPSTABLE
        | SNOWFLAKETABLE
        | SPEECHSENSETABLE
        | TRINOTABLE
        | TRINOSUBSELECT
        | CHUSAGETRACKINGTABLE
        | CHUSAGETRACKINGAGGTABLE
        | YDBTABLE
        | YDBSUBSELECT
        | YQTABLE
        | YQSUBSELECT
    ]
):
    root: (
        APPMETRICAAPI
        | BIGQUERYTABLE
        | BIGQUERYSUBSELECT
        | BITRIXGDS
        | CHBILLINGANALYTICSTABLE
        | CHYAMUSICPODCASTSTATSTABLE
        | CHYTYTSAURUSTABLE
        | CHYTYTSAURUSTABLELIST
        | CHYTYTSAURUSTABLERANGE
        | CHYTYTSAURUSSUBSELECT
        | CHTABLE
        | CHSUBSELECT
        | EQUEOCHTABLE
        | EXTRACTOR1CCHTABLE
        | GPTABLE
        | GPSUBSELECT
        | GSHEETS
        | JSONAPI
        | KONTURMARKETCHTABLE
        | METRIKAAPI
        | MONITORING
        | MOYSKLADCHTABLE
        | MSSQLTABLE
        | MSSQLSUBSELECT
        | MYSQLTABLE
        | MYSQLSUBSELECT
        | ORACLETABLE
        | ORACLESUBSELECT
        | PGTABLE
        | PGSUBSELECT
        | PROMQL
        | CHSMBHEATMAPSTABLE
        | SNOWFLAKETABLE
        | SPEECHSENSETABLE
        | TRINOTABLE
        | TRINOSUBSELECT
        | CHUSAGETRACKINGTABLE
        | CHUSAGETRACKINGAGGTABLE
        | YDBTABLE
        | YDBSUBSELECT
        | YQTABLE
        | YQSUBSELECT
    ) = Field(..., discriminator="source_type")


class DatasetContentInternal(APIModel):
    avatar_relations: list[AvatarRelation] | None = None
    cache_invalidation_source: CacheInvalidationSource | None = None
    component_errors: ComponentErrorList | None = None
    data_export_forbidden: bool | None = None
    description: str | None = None
    load_preview_by_default: bool | None = None
    obligatory_filters: list[ObligatoryFilter] | None = None
    preview_enabled: bool | None = None
    result_schema: list[ResultSchemaSchemaGeneric] | None = None
    result_schema_aux: ResultSchemaAux | None = None
    revision_id: str | None = None
    rls: dict[str, Any] | None = None
    rls2: dict[str, list[RLS2ConfigEntry]] | None = None
    source_avatars: list[SourceAvatarStrict] | None = None
    sources: list[DataSourceStrict] | None = None
    template_enabled: bool | None = None


class DatasetCreate(RequestBody):
    collection_id: str | None = None
    created_via: Literal["user", "workbook_copy"] | str | None = None
    dataset: DatasetContentInternal
    dir_path: str | None = None
    name: str | None = None
    options: Options | None = None
    preview: bool | None = None
    published_id: str | None = Field(default=None, alias="publishedId")
    rev_id: str | None = Field(default=None, alias="revId")
    saved_id: str | None = Field(default=None, alias="savedId")
    workbook_id: str | None = None


class DatasetRead(APIModel):
    collection_id: str | None = None
    ctime: str | None = None
    dataset: DatasetContentInternal | None = None
    full_permissions: dict[str, bool] | None = None
    id: str | None = None
    is_favorite: bool | None = None
    key: str | None = None
    mtime: str | None = None
    name: str | None = None
    options: Options | None = None
    permissions: dict[str, bool] | None = None
    pub_operation_id: str | None = None
    published_id: str | None = Field(default=None, alias="publishedId")
    rev_id: str | None = Field(default=None, alias="revId")
    row_count: int | None = None
    saved_id: str | None = Field(default=None, alias="savedId")
    workbook_id: str | None = None


class DatasetUpdate(APIModel):
    dataset: DatasetContentInternal | None = None
    mode: Literal["publish", "save"] | str | None = None
    options: Options | None = None
    published_id: str | None = Field(default=None, alias="publishedId")
    rev_id: str | None = Field(default=None, alias="revId")
    saved_id: str | None = Field(default=None, alias="savedId")


class AddSource(APIModel):
    action: Literal["add_source"]
    order_index: int | None = None
    source: DataSource | None = None


class UpdateSource(APIModel):
    action: Literal["update_source"]
    order_index: int | None = None
    source: DataSource | None = None


class UpdateDatasetRequest(RequestBody):
    dataset_id: str = Field(..., alias="datasetId")
    data: DatasetUpdate | None = None
    workbook_id: str | None = Field(default=None, alias="workbookId")


class Action(
    RootModel[
        AddFieldModel
        | UpdateFieldModel
        | DeleteFieldModel
        | CloneFieldModel
        | AddSource
        | UpdateSource
        | DeleteSource
        | RefreshSourceModel
        | AddSourceAvatar
        | UpdateSourceAvatar
        | DeleteSourceAvatar
        | AddAvatarRelation
        | UpdateAvatarRelation
        | DeleteAvatarRelation
        | ReplaceConnectionModel
        | AddObligatoryFilter
        | UpdateObligatoryFilter
        | DeleteObligatoryFilterModel
        | UpdateSetting
        | UpdateDescription
        | UpdateCacheInvalidationSource
    ]
):
    root: (
        AddFieldModel
        | UpdateFieldModel
        | DeleteFieldModel
        | CloneFieldModel
        | AddSource
        | UpdateSource
        | DeleteSource
        | RefreshSourceModel
        | AddSourceAvatar
        | UpdateSourceAvatar
        | DeleteSourceAvatar
        | AddAvatarRelation
        | UpdateAvatarRelation
        | DeleteAvatarRelation
        | ReplaceConnectionModel
        | AddObligatoryFilter
        | UpdateObligatoryFilter
        | DeleteObligatoryFilterModel
        | UpdateSetting
        | UpdateDescription
        | UpdateCacheInvalidationSource
    ) = Field(..., discriminator="action")


class DatasetValidate(APIModel):
    dataset: DatasetContentInternal | None = None
    updates: list[Action] | None = None


class ValidateDatasetRequest(RequestBody):
    dataset_id: str = Field(..., alias="datasetId")
    workbook_id: str | None = Field(default=None, alias="workbookId")
    binded_dataset_id: str | None = Field(default=None, alias="bindedDatasetId")
    data: DatasetValidate | None = None
