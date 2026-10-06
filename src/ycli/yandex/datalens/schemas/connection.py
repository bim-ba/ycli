# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from typing import Annotated, Any, Literal

from pydantic import AwareDatetime, Field, RootModel, SecretStr

from ycli.yandex.models import APIModel, NoDropNull, RequestBody

from . import shared


class ConnectionCreateResponse(APIModel):
    id: str | None = None
    operation: dict[str, Any] | None = None


class RequiredParameterInfo(APIModel):
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
    name: str | None = None


class AppmetricaApi(APIModel):
    accuracy: int | float | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    counter_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    token: SecretStr | None = None
    type: Literal["appmetrica_api"]
    updated_at: str | None = None
    workbook_id: str | None = None


class AppmetricaApi2(APIModel):
    accuracy: int | float | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    counter_id: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    token: SecretStr | None = None


class Bigquery(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    credentials: SecretStr | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    project_id: str | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    type: Literal["bigquery"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Bigquery2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    credentials: SecretStr | None = None
    description: str | None = None
    project_id: str | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )


class Bitrix24(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    portal: str | None = None
    token: SecretStr | None = None
    type: Literal["bitrix24"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Bitrix242(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    portal: str | None = None
    token: SecretStr | None = None


class ChBillingAnalytics(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    type: Literal["ch_billing_analytics"]
    updated_at: str | None = None
    workbook_id: str | None = None


class ChBillingAnalytics2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    description: str | None = None


class ChYaMusicPodcastStats(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    token: SecretStr | None = None
    type: Literal["ch_ya_music_podcast_stats"]
    updated_at: str | None = None
    workbook_id: str | None = None


class ChYaMusicPodcastStats2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    description: str | None = None
    token: SecretStr | None = None


class Chyt(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    alias: str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    dir_path: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    secure: bool | None = None
    token: SecretStr | None = None
    type: Literal["chyt"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Chyt2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    alias: str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    host: str | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    secure: bool | None = None
    token: SecretStr | None = None


class Clickhouse(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    connection_manager_cloud_id: str | None = None
    connection_manager_connection_id: str | None = None
    connection_manager_delegation_is_set: bool | None = None
    connection_manager_folder_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dir_path: str | None = None
    dlp_managed_cloud_id: str | None = None
    dlp_managed_cluster_id: str | None = None
    dlp_managed_connection_manager_connection_id: str | None = None
    dlp_managed_connection_manager_delegation_is_set: bool | None = None
    dlp_managed_connection_manager_delegation_is_set_current: bool | None = None
    dlp_managed_folder_id: str | None = None
    experimental_features: Literal["on", "off"] | str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    mode: Literal["onpremise", "managed"] | str | None = None
    name: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    readonly: int | None = None
    secure: Literal["on", "off"] | str | None = None
    ssl_ca: str | None = None
    ssl_ca_verify: Literal["on", "off"] | str | None = None
    type: Literal["clickhouse"]
    updated_at: str | None = None
    username: str | None = None
    variant: Literal["default", "dlp"] | str | None = None
    workbook_id: str | None = None


class Clickhouse2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    connection_manager_cloud_id: str | None = None
    connection_manager_connection_id: str | None = None
    connection_manager_delegation_is_set: bool | None = None
    connection_manager_folder_id: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dlp_managed_cloud_id: str | None = None
    dlp_managed_cluster_id: str | None = None
    dlp_managed_connection_manager_connection_id: str | None = None
    dlp_managed_connection_manager_delegation_is_set: bool | None = None
    dlp_managed_folder_id: str | None = None
    experimental_features: Literal["on", "off"] | str | None = None
    host: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    mode: Literal["onpremise", "managed"] | str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    readonly: int | None = None
    secure: Literal["on", "off"] | str | None = None
    ssl_ca: str | None = None
    ssl_ca_verify: Literal["on", "off"] | str | None = None
    username: str | None = None
    variant: Literal["default", "dlp"] | str | None = None


class Equeo(APIModel):
    access_token: SecretStr | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    type: Literal["equeo"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Equeo2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    description: str | None = None


class Extractor1c(APIModel):
    access_token: SecretStr | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    type: Literal["extractor1c"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Extractor1c2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    description: str | None = None


class Greenplum(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dir_path: str | None = None
    enforce_collate: Literal["auto", "on", "off"] | str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["greenplum"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Greenplum2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    enforce_collate: Literal["auto", "on", "off"] | str | None = None
    host: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    username: str | None = None


class Gsheets(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    type: Literal["gsheets"]
    updated_at: str | None = None
    url: str | None = None
    workbook_id: str | None = None


class Gsheets2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    url: str | None = None


class JsonApi(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    allowed_methods: list[Literal["GET", "POST", "PUT", "PATCH", "DELETE"] | str] | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    path: str | None = None
    plain_headers: dict[str, Any] | None = None
    port: int | None = None
    secret_headers: dict[str, SecretStr] | None = None
    secure: bool | None = None
    type: Literal["json_api"]
    updated_at: str | None = None
    workbook_id: str | None = None


class JsonApi2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    allowed_methods: list[Literal["GET", "POST", "PUT", "PATCH", "DELETE"] | str] | None = None
    description: str | None = None
    host: str | None = None
    path: str | None = None
    plain_headers: dict[str, Any] | None = None
    port: int | None = None
    secret_headers: dict[str, SecretStr] | None = None
    secure: bool | None = None


class KonturMarket(APIModel):
    access_token: SecretStr | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    type: Literal["kontur_market"]
    updated_at: str | None = None
    workbook_id: str | None = None


class KonturMarket2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    description: str | None = None


class MetrikaApi(APIModel):
    accuracy: int | float | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    counter_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    token: SecretStr | None = None
    type: Literal["metrika_api"]
    updated_at: str | None = None
    workbook_id: str | None = None


class MetrikaApi2(APIModel):
    accuracy: int | float | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    counter_id: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    token: SecretStr | None = None


class Monitoring(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: Annotated[str | None, NoDropNull()] = None
    collection_id: str | None = None
    created_at: str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    dir_path: str | None = None
    folder_id: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    service_account_id: str | None = None
    type: Literal["monitoring"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Monitoring2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    folder_id: str | None = None
    service_account_id: str | None = None


class Moysklad(APIModel):
    access_token: SecretStr | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    type: Literal["moysklad"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Moysklad2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    description: str | None = None


class Mssql(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dir_path: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    type: Literal["mssql"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Mssql2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    host: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    username: str | None = None


class Mysql(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    connection_manager_cloud_id: str | None = None
    connection_manager_connection_id: str | None = None
    connection_manager_delegation_is_set: bool | None = None
    connection_manager_folder_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dir_path: str | None = None
    dlp_managed_cloud_id: str | None = None
    dlp_managed_cluster_id: str | None = None
    dlp_managed_connection_manager_connection_id: str | None = None
    dlp_managed_connection_manager_delegation_is_set: bool | None = None
    dlp_managed_connection_manager_delegation_is_set_current: bool | None = None
    dlp_managed_folder_id: str | None = None
    enforce_collate: Literal["auto", "on", "off"] | str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    mode: Literal["onpremise", "managed"] | str | None = None
    name: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["mysql"]
    updated_at: str | None = None
    username: str | None = None
    variant: Literal["default", "dlp"] | str | None = None
    workbook_id: str | None = None


class Mysql2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    connection_manager_cloud_id: str | None = None
    connection_manager_connection_id: str | None = None
    connection_manager_delegation_is_set: bool | None = None
    connection_manager_folder_id: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dlp_managed_cloud_id: str | None = None
    dlp_managed_cluster_id: str | None = None
    dlp_managed_connection_manager_connection_id: str | None = None
    dlp_managed_connection_manager_delegation_is_set: bool | None = None
    dlp_managed_folder_id: str | None = None
    enforce_collate: Literal["auto", "on", "off"] | str | None = None
    host: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    mode: Literal["onpremise", "managed"] | str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    username: str | None = None
    variant: Literal["default", "dlp"] | str | None = None


class Oracle(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_connect_method: Literal["sid", "service_name"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dir_path: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["oracle"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Oracle2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_connect_method: Literal["sid", "service_name"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    host: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    username: str | None = None


class Postgres(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    connection_manager_cloud_id: str | None = None
    connection_manager_connection_id: str | None = None
    connection_manager_delegation_is_set: bool | None = None
    connection_manager_folder_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dir_path: str | None = None
    dlp_managed_cloud_id: str | None = None
    dlp_managed_cluster_id: str | None = None
    dlp_managed_connection_manager_connection_id: str | None = None
    dlp_managed_connection_manager_delegation_is_set: bool | None = None
    dlp_managed_connection_manager_delegation_is_set_current: bool | None = None
    dlp_managed_folder_id: str | None = None
    enforce_collate: Literal["auto", "on", "off"] | str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    mode: Literal["onpremise", "managed"] | str | None = None
    name: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["postgres"]
    updated_at: str | None = None
    username: str | None = None
    variant: Literal["default", "dlp"] | str | None = None
    workbook_id: str | None = None


class Postgres2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    connection_manager_cloud_id: str | None = None
    connection_manager_connection_id: str | None = None
    connection_manager_delegation_is_set: bool | None = None
    connection_manager_folder_id: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dlp_managed_cloud_id: str | None = None
    dlp_managed_cluster_id: str | None = None
    dlp_managed_connection_manager_connection_id: str | None = None
    dlp_managed_connection_manager_delegation_is_set: bool | None = None
    dlp_managed_folder_id: str | None = None
    enforce_collate: Literal["auto", "on", "off"] | str | None = None
    host: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    mode: Literal["onpremise", "managed"] | str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    username: str | None = None
    variant: Literal["default", "dlp"] | str | None = None


class Promql(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_header: SecretStr | None = None
    auth_type: Literal["header", "password"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dir_path: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    password: SecretStr | None = None
    path: str | None = None
    port: int | None = None
    secure: bool | None = None
    type: Literal["promql"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Promql2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_header: SecretStr | None = None
    auth_type: Literal["header", "password"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    host: str | None = None
    password: SecretStr | None = None
    path: str | None = None
    port: int | None = None
    secure: bool | None = None
    username: str | None = None


class SmbHeatmaps(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    token: SecretStr | None = None
    type: Literal["smb_heatmaps"]
    updated_at: str | None = None
    workbook_id: str | None = None


class SmbHeatmaps2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    description: str | None = None
    token: SecretStr | None = None


class Snowflake(APIModel):
    account_name: str | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    client_id: str | None = None
    client_secret: SecretStr | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    refresh_token: SecretStr | None = None
    refresh_token_expire_time: AwareDatetime | None = None
    schema_: str | None = Field(default=None, alias="schema")
    type: Literal["snowflake"]
    updated_at: str | None = None
    user_name: str | None = None
    user_role: str | None = None
    warehouse: str | None = None
    workbook_id: str | None = None


class Snowflake2(APIModel):
    account_name: str | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    client_id: str | None = None
    client_secret: SecretStr | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    refresh_token: SecretStr | None = None
    refresh_token_expire_time: AwareDatetime | None = None
    schema_: str | None = Field(default=None, alias="schema")
    user_name: str | None = None
    user_role: str | None = None
    warehouse: str | None = None


class Speechsense(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_type: Literal["service_account", "user_credentials"] | str | None = None
    cloud_id: str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    dir_path: str | None = None
    folder_id: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    project_id: str | None = None
    service_account_id: str | None = None
    type: Literal["speechsense"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Speechsense2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_type: Literal["service_account", "user_credentials"] | str | None = None
    cloud_id: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    folder_id: str | None = None
    project_id: str | None = None
    service_account_id: str | None = None


class Trino(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_type: (
        Literal["certificate", "header", "jwt", "kerberos", "none", "oauth2", "password"]
        | str
        | None
    ) = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: str | None = None
    cluster_entry_id: str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    dir_path: str | None = None
    extra_credentials: dict[str, SecretStr] | None = None
    folder_id: str | None = None
    form_fill_mode: Literal["cloud", "manually", "platform"] | str | None = None
    host: str | None = None
    id: str | None = None
    jwt: SecretStr | None = None
    key: str | None = None
    listing_sources: Literal["on", "off"] | str | None = None
    mdb_cluster_id: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    service_account_id: str | None = None
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["trino"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Trino2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_type: (
        Literal["certificate", "header", "jwt", "kerberos", "none", "oauth2", "password"]
        | str
        | None
    ) = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: str | None = None
    cluster_entry_id: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    extra_credentials: dict[str, SecretStr] | None = None
    folder_id: str | None = None
    form_fill_mode: Literal["cloud", "manually", "platform"] | str | None = None
    host: str | None = None
    jwt: SecretStr | None = None
    listing_sources: Literal["on", "off"] | str | None = None
    mdb_cluster_id: str | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    service_account_id: str | None = None
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    username: str | None = None


class UsageAnalyticsDetailed(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    type: Literal["usage_analytics_detailed"]
    updated_at: str | None = None
    workbook_id: str | None = None


class UsageAnalyticsDetailed2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    description: str | None = None


class UsageAnalyticsLight(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    dir_path: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    type: Literal["usage_analytics_light"]
    updated_at: str | None = None
    workbook_id: str | None = None


class UsageAnalyticsLight2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    description: str | None = None


class Ydb(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_type: Literal["anonymous", "password", "oauth"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: Annotated[str | None, NoDropNull()] = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    dir_path: str | None = None
    folder_id: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    service_account_id: str | None = None
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    token: SecretStr | None = None
    type: Literal["ydb"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Ydb2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_type: Literal["anonymous", "password", "oauth"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    folder_id: str | None = None
    host: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    service_account_id: str | None = None
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    token: SecretStr | None = None
    username: str | None = None


class Yq(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: Annotated[str | None, NoDropNull()] = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    dir_path: str | None = None
    folder_id: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    service_account_id: str | None = None
    type: Literal["yq"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Yq2(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    folder_id: str | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    service_account_id: str | None = None


class GetConnectionRequest(RequestBody):
    connection_id: str = Field(..., alias="connectionId")
    workbook_id: str | None = Field(default=None, alias="workbookId")
    binded_dataset_id: str | None = Field(default=None, alias="bindedDatasetId")
    rev_id: str | None = None


class DeleteConnectionRequest(RequestBody):
    connection_id: str = Field(..., alias="connectionId")


class ConnectionCreate(
    RootModel[
        AppmetricaApi
        | Bigquery
        | Bitrix24
        | ChBillingAnalytics
        | ChYaMusicPodcastStats
        | Chyt
        | Clickhouse
        | Equeo
        | Extractor1c
        | Greenplum
        | Gsheets
        | JsonApi
        | KonturMarket
        | MetrikaApi
        | Monitoring
        | Moysklad
        | Mssql
        | Mysql
        | Oracle
        | Postgres
        | Promql
        | SmbHeatmaps
        | Snowflake
        | Speechsense
        | Trino
        | UsageAnalyticsDetailed
        | UsageAnalyticsLight
        | Ydb
        | Yq
        | shared.OtherKind
    ],
    hide_input_in_errors=True,
):
    root: (
        AppmetricaApi
        | Bigquery
        | Bitrix24
        | ChBillingAnalytics
        | ChYaMusicPodcastStats
        | Chyt
        | Clickhouse
        | Equeo
        | Extractor1c
        | Greenplum
        | Gsheets
        | JsonApi
        | KonturMarket
        | MetrikaApi
        | Monitoring
        | Moysklad
        | Mssql
        | Mysql
        | Oracle
        | Postgres
        | Promql
        | SmbHeatmaps
        | Snowflake
        | Speechsense
        | Trino
        | UsageAnalyticsDetailed
        | UsageAnalyticsLight
        | Ydb
        | Yq
        | shared.OtherKind
    )


class ConnectionUpdate(
    RootModel[
        AppmetricaApi2
        | Bigquery2
        | Bitrix242
        | ChBillingAnalytics2
        | ChYaMusicPodcastStats2
        | Chyt2
        | Clickhouse2
        | Equeo2
        | Extractor1c2
        | Greenplum2
        | Gsheets2
        | JsonApi2
        | KonturMarket2
        | MetrikaApi2
        | Monitoring2
        | Moysklad2
        | Mssql2
        | Mysql2
        | Oracle2
        | Postgres2
        | Promql2
        | SmbHeatmaps2
        | Snowflake2
        | Speechsense2
        | Trino2
        | UsageAnalyticsDetailed2
        | UsageAnalyticsLight2
        | Ydb2
        | Yq2
    ],
    hide_input_in_errors=True,
):
    root: (
        AppmetricaApi2
        | Bigquery2
        | Bitrix242
        | ChBillingAnalytics2
        | ChYaMusicPodcastStats2
        | Chyt2
        | Clickhouse2
        | Equeo2
        | Extractor1c2
        | Greenplum2
        | Gsheets2
        | JsonApi2
        | KonturMarket2
        | MetrikaApi2
        | Monitoring2
        | Moysklad2
        | Mssql2
        | Mysql2
        | Oracle2
        | Postgres2
        | Promql2
        | SmbHeatmaps2
        | Snowflake2
        | Speechsense2
        | Trino2
        | UsageAnalyticsDetailed2
        | UsageAnalyticsLight2
        | Ydb2
        | Yq2
    )


class QueryTypeInfo(APIModel):
    allow_selector: bool | None = None
    query_type: (
        Literal[
            "generic_distinct",
            "generic_label_names",
            "generic_label_values",
            "generic_query",
            "raw_query",
        ]
        | str
        | None
    ) = None
    query_type_label: str | None = None
    required_parameters: list[RequiredParameterInfo] | None = None


class UpdateConnectionRequest(RequestBody):
    connection_id: str = Field(..., alias="connectionId")
    data: ConnectionUpdate | None = None


class ConnectionOptions(APIModel):
    allow_dashsql_usage: bool | None = None
    allow_dataset_usage: bool | None = None
    allow_pagination_usage: bool | None = None
    allow_typed_query_usage: bool | None = None
    query_types: list[QueryTypeInfo] | None = None


class AppmetricaApi1(APIModel):
    accuracy: int | float | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    counter_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    token: SecretStr | None = None
    type: Literal["appmetrica_api"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Bigquery1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    credentials: SecretStr | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    project_id: str | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    type: Literal["bigquery"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Bitrix241(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    portal: str | None = None
    token: SecretStr | None = None
    type: Literal["bitrix24"]
    updated_at: str | None = None
    workbook_id: str | None = None


class ChBillingAnalytics1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    type: Literal["ch_billing_analytics"]
    updated_at: str | None = None
    workbook_id: str | None = None


class ChYaMusicPodcastStats1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    token: SecretStr | None = None
    type: Literal["ch_ya_music_podcast_stats"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Chyt1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    alias: str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    secure: bool | None = None
    token: SecretStr | None = None
    type: Literal["chyt"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Clickhouse1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    connection_manager_cloud_id: str | None = None
    connection_manager_connection_id: str | None = None
    connection_manager_delegation_is_set: bool | None = None
    connection_manager_folder_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dlp_managed_cloud_id: str | None = None
    dlp_managed_cluster_id: str | None = None
    dlp_managed_connection_manager_connection_id: str | None = None
    dlp_managed_connection_manager_delegation_is_set: bool | None = None
    dlp_managed_connection_manager_delegation_is_set_current: bool | None = None
    dlp_managed_folder_id: str | None = None
    experimental_features: Literal["on", "off"] | str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    mode: Literal["onpremise", "managed"] | str | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    readonly: int | None = None
    secure: Literal["on", "off"] | str | None = None
    ssl_ca: str | None = None
    ssl_ca_verify: Literal["on", "off"] | str | None = None
    type: Literal["clickhouse"]
    updated_at: str | None = None
    username: str | None = None
    variant: Literal["default", "dlp"] | str | None = None
    workbook_id: str | None = None


class Equeo1(APIModel):
    access_token: SecretStr | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    type: Literal["equeo"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Extractor1c1(APIModel):
    access_token: SecretStr | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    type: Literal["extractor1c"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Greenplum1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    enforce_collate: Literal["auto", "on", "off"] | str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["greenplum"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Gsheets1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    type: Literal["gsheets"]
    updated_at: str | None = None
    url: str | None = None
    workbook_id: str | None = None


class JsonApi1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    allowed_methods: list[Literal["GET", "POST", "PUT", "PATCH", "DELETE"] | str] | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    path: str | None = None
    plain_headers: dict[str, Any] | None = None
    port: int | None = None
    secret_headers: dict[str, SecretStr] | None = None
    secure: bool | None = None
    type: Literal["json_api"]
    updated_at: str | None = None
    workbook_id: str | None = None


class KonturMarket1(APIModel):
    access_token: SecretStr | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    type: Literal["kontur_market"]
    updated_at: str | None = None
    workbook_id: str | None = None


class MetrikaApi1(APIModel):
    accuracy: int | float | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    counter_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    token: SecretStr | None = None
    type: Literal["metrika_api"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Monitoring1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: Annotated[str | None, NoDropNull()] = None
    collection_id: str | None = None
    created_at: str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    folder_id: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    service_account_id: str | None = None
    type: Literal["monitoring"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Moysklad1(APIModel):
    access_token: SecretStr | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    type: Literal["moysklad"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Mssql1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    type: Literal["mssql"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Mysql1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    connection_manager_cloud_id: str | None = None
    connection_manager_connection_id: str | None = None
    connection_manager_delegation_is_set: bool | None = None
    connection_manager_folder_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dlp_managed_cloud_id: str | None = None
    dlp_managed_cluster_id: str | None = None
    dlp_managed_connection_manager_connection_id: str | None = None
    dlp_managed_connection_manager_delegation_is_set: bool | None = None
    dlp_managed_connection_manager_delegation_is_set_current: bool | None = None
    dlp_managed_folder_id: str | None = None
    enforce_collate: Literal["auto", "on", "off"] | str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    mode: Literal["onpremise", "managed"] | str | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["mysql"]
    updated_at: str | None = None
    username: str | None = None
    variant: Literal["default", "dlp"] | str | None = None
    workbook_id: str | None = None


class Oracle1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_connect_method: Literal["sid", "service_name"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["oracle"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Postgres1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    connection_manager_cloud_id: str | None = None
    connection_manager_connection_id: str | None = None
    connection_manager_delegation_is_set: bool | None = None
    connection_manager_folder_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    dlp_managed_cloud_id: str | None = None
    dlp_managed_cluster_id: str | None = None
    dlp_managed_connection_manager_connection_id: str | None = None
    dlp_managed_connection_manager_delegation_is_set: bool | None = None
    dlp_managed_connection_manager_delegation_is_set_current: bool | None = None
    dlp_managed_folder_id: str | None = None
    enforce_collate: Literal["auto", "on", "off"] | str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    mode: Literal["onpremise", "managed"] | str | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["postgres"]
    updated_at: str | None = None
    username: str | None = None
    variant: Literal["default", "dlp"] | str | None = None
    workbook_id: str | None = None


class Promql1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_header: SecretStr | None = None
    auth_type: Literal["header", "password"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    password: SecretStr | None = None
    path: str | None = None
    port: int | None = None
    secure: bool | None = None
    type: Literal["promql"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class SmbHeatmaps1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    token: SecretStr | None = None
    type: Literal["smb_heatmaps"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Snowflake1(APIModel):
    account_name: str | None = None
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    client_id: str | None = None
    client_secret: SecretStr | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    refresh_token: SecretStr | None = None
    refresh_token_expire_time: AwareDatetime | None = None
    schema_: str | None = Field(default=None, alias="schema")
    type: Literal["snowflake"]
    updated_at: str | None = None
    user_name: str | None = None
    user_role: str | None = None
    warehouse: str | None = None
    workbook_id: str | None = None


class Speechsense1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_type: Literal["service_account", "user_credentials"] | str | None = None
    cloud_id: str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    folder_id: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    project_id: str | None = None
    service_account_id: str | None = None
    type: Literal["speechsense"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Trino1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_type: (
        Literal["certificate", "header", "jwt", "kerberos", "none", "oauth2", "password"]
        | str
        | None
    ) = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: str | None = None
    cluster_entry_id: str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    extra_credentials: dict[str, SecretStr] | None = None
    folder_id: str | None = None
    form_fill_mode: Literal["cloud", "manually", "platform"] | str | None = None
    host: str | None = None
    id: str | None = None
    jwt: SecretStr | None = None
    key: str | None = None
    listing_sources: Literal["on", "off"] | str | None = None
    mdb_cluster_id: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    password: SecretStr | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    service_account_id: str | None = None
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    type: Literal["trino"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class UsageAnalyticsDetailed1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    type: Literal["usage_analytics_detailed"]
    updated_at: str | None = None
    workbook_id: str | None = None


class UsageAnalyticsLight1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    collection_id: str | None = None
    created_at: str | None = None
    description: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    type: Literal["usage_analytics_light"]
    updated_at: str | None = None
    workbook_id: str | None = None


class Ydb1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    auth_type: Literal["anonymous", "password", "oauth"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: Annotated[str | None, NoDropNull()] = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    db_name: str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    folder_id: str | None = None
    host: str | None = None
    id: str | None = None
    key: str | None = None
    mdb_cluster_id: str | None = None
    mdb_folder_id: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    port: int | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    service_account_id: str | None = None
    ssl_ca: str | None = None
    ssl_enable: Literal["on", "off"] | str | None = None
    token: SecretStr | None = None
    type: Literal["ydb"]
    updated_at: str | None = None
    username: str | None = None
    workbook_id: str | None = None


class Yq1(APIModel):
    ai_access_level: Literal["allow", "allow_trusted", "deny"] | str | None = None
    cache_invalidation_throttling_interval_sec: int | None = None
    cache_ttl_sec: int | None = None
    cloud_id: Annotated[str | None, NoDropNull()] = None
    collection_id: str | None = None
    created_at: str | None = None
    data_export_forbidden: Literal["on", "off"] | str | None = None
    delegation_is_set: bool | None = None
    description: str | None = None
    folder_id: str | None = None
    id: str | None = None
    key: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    options: ConnectionOptions | None = None
    raw_sql_level: Literal["off", "subselect", "template", "dashsql", "readwrite"] | str | None = (
        None
    )
    service_account_id: str | None = None
    type: Literal["yq"]
    updated_at: str | None = None
    workbook_id: str | None = None


class ConnectionRead(
    RootModel[
        AppmetricaApi1
        | Bigquery1
        | Bitrix241
        | ChBillingAnalytics1
        | ChYaMusicPodcastStats1
        | Chyt1
        | Clickhouse1
        | Equeo1
        | Extractor1c1
        | Greenplum1
        | Gsheets1
        | JsonApi1
        | KonturMarket1
        | MetrikaApi1
        | Monitoring1
        | Moysklad1
        | Mssql1
        | Mysql1
        | Oracle1
        | Postgres1
        | Promql1
        | SmbHeatmaps1
        | Snowflake1
        | Speechsense1
        | Trino1
        | UsageAnalyticsDetailed1
        | UsageAnalyticsLight1
        | Ydb1
        | Yq1
        | shared.OtherKind
    ],
    hide_input_in_errors=True,
):
    root: (
        AppmetricaApi1
        | Bigquery1
        | Bitrix241
        | ChBillingAnalytics1
        | ChYaMusicPodcastStats1
        | Chyt1
        | Clickhouse1
        | Equeo1
        | Extractor1c1
        | Greenplum1
        | Gsheets1
        | JsonApi1
        | KonturMarket1
        | MetrikaApi1
        | Monitoring1
        | Moysklad1
        | Mssql1
        | Mysql1
        | Oracle1
        | Postgres1
        | Promql1
        | SmbHeatmaps1
        | Snowflake1
        | Speechsense1
        | Trino1
        | UsageAnalyticsDetailed1
        | UsageAnalyticsLight1
        | Ydb1
        | Yq1
        | shared.OtherKind
    )
