---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/createConnection
title: "Yandex DataLens | DataLens API: Create connection"
author: "Yandex Cloud"
extracted: "2026-07-09T13:28:11Z"
---

```
POST https://api.datalens.tech/rpc/createConnection
```

```
{
  "<oneOf>": [
    {
      "accuracy": "number | null",
      "counter_id": "string",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "token": "string",
      "type": "appmetrica_api",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "created_at": "string",
      "credentials": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "project_id": "string",
      "raw_sql_level": "string",
      "type": "bigquery",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "portal": "string",
      "token": "string",
      "type": "bitrix24",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "type": "ch_billing_analytics",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "type": "ch_frozen_bumpy_roads",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "type": "ch_frozen_covid",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "type": "ch_frozen_demo",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "type": "ch_frozen_dtp",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "type": "ch_frozen_gkh",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "type": "ch_frozen_horeca",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "type": "ch_frozen_samples",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "type": "ch_frozen_transparency",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "type": "ch_frozen_weather",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "mp_product_id": "string",
      "name": "string",
      "type": "ch_geo_filtered",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "token": "string",
      "type": "ch_ya_music_podcast_stats",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "alias": "string",
      "cache_ttl_sec": "integer | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "description": "string | null",
      "dir_path": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "port": "integer",
      "raw_sql_level": "string",
      "secure": "boolean",
      "token": "string",
      "type": "chyt",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "connection_manager_cloud_id": "string | null",
      "connection_manager_connection_id": "string | null",
      "connection_manager_delegation_is_set": "boolean | null",
      "connection_manager_folder_id": "string | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_name": "string | null",
      "description": "string | null",
      "dir_path": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "mdb_cluster_id": "string | null",
      "mdb_folder_id": "string | null",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "password": "string | null",
      "port": "integer",
      "raw_sql_level": "string",
      "readonly": "integer",
      "secure": "unknown",
      "ssl_ca": "unknown",
      "type": "clickhouse",
      "updated_at": "string",
      "username": "string | null",
      "workbook_id": "string | null"
    },
    {
      "access_token": "string",
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "type": "equeo",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "access_token": "string",
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "type": "extractor1c",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_name": "string | null",
      "description": "string | null",
      "dir_path": "string",
      "enforce_collate": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "mdb_cluster_id": "string | null",
      "mdb_folder_id": "string | null",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "password": "string",
      "port": "integer",
      "raw_sql_level": "string",
      "ssl_ca": "unknown",
      "ssl_enable": "unknown",
      "type": "greenplum",
      "updated_at": "string",
      "username": "string",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "type": "gsheets",
      "updated_at": "string",
      "url": "string",
      "workbook_id": "string | null"
    },
    {
      "allowed_methods": [
        "string"
      ],
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "path": "string | null",
      "plain_headers": "object | null",
      "port": "integer",
      "secret_headers": "object | null",
      "secure": "boolean",
      "type": "json_api",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "access_token": "string",
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "type": "kontur_market",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "accuracy": "number | null",
      "counter_id": "string",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "token": "string",
      "type": "metrika_api",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "cloud_id": "string | null",
      "created_at": "string",
      "delegation_is_set": "boolean | null",
      "description": "string | null",
      "dir_path": "string",
      "folder_id": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "service_account_id": "string",
      "type": "monitoring",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "access_token": "string",
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "type": "moysklad",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_name": "string | null",
      "description": "string | null",
      "dir_path": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "password": "string",
      "port": "integer",
      "raw_sql_level": "string",
      "type": "mssql",
      "updated_at": "string",
      "username": "string",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "connection_manager_cloud_id": "string | null",
      "connection_manager_connection_id": "string | null",
      "connection_manager_delegation_is_set": "boolean | null",
      "connection_manager_folder_id": "string | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_name": "string | null",
      "description": "string | null",
      "dir_path": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "mdb_cluster_id": "string | null",
      "mdb_folder_id": "string | null",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "password": "string | null",
      "port": "integer",
      "raw_sql_level": "string",
      "ssl_ca": "unknown",
      "ssl_enable": "unknown",
      "type": "mysql",
      "updated_at": "string",
      "username": "string | null",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_connect_method": "string",
      "db_name": "string | null",
      "description": "string | null",
      "dir_path": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "password": "string",
      "port": "integer",
      "raw_sql_level": "string",
      "ssl_ca": "unknown",
      "ssl_enable": "unknown",
      "type": "oracle",
      "updated_at": "string",
      "username": "string",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "connection_manager_cloud_id": "string | null",
      "connection_manager_connection_id": "string | null",
      "connection_manager_delegation_is_set": "boolean | null",
      "connection_manager_folder_id": "string | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_name": "string | null",
      "description": "string | null",
      "dir_path": "string",
      "enforce_collate": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "mdb_cluster_id": "string | null",
      "mdb_folder_id": "string | null",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "password": "string | null",
      "port": "integer",
      "raw_sql_level": "string",
      "ssl_ca": "unknown",
      "ssl_enable": "unknown",
      "type": "postgres",
      "updated_at": "string",
      "username": "string | null",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_name": "string | null",
      "description": "string | null",
      "dir_path": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "password": "string | null",
      "path": "string | null",
      "port": "integer",
      "secure": "boolean",
      "type": "promql",
      "updated_at": "string",
      "username": "string | null",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "token": "string",
      "type": "smb_heatmaps",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "account_name": "string",
      "client_id": "string",
      "client_secret": "string",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_name": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "refresh_token": "string",
      "refresh_token_expire_time": "string | null",
      "schema": "string",
      "type": "snowflake",
      "updated_at": "string",
      "user_name": "string",
      "user_role": "string | null",
      "warehouse": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "project_id": "string",
      "type": "speechsense",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "auth_type": "unknown",
      "cache_ttl_sec": "integer | null",
      "cloud_id": "string | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_name": "string | null",
      "delegation_is_set": "boolean | null",
      "description": "string | null",
      "dir_path": "string",
      "folder_id": "string | null",
      "host": "string",
      "id": "string",
      "jwt": "string | null",
      "key": "string",
      "listing_sources": "unknown",
      "mdb_cluster_id": "string | null",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "password": "string | null",
      "port": "integer | null",
      "raw_sql_level": "string",
      "service_account_id": "string | null",
      "ssl_ca": "unknown",
      "ssl_enable": "unknown",
      "type": "trino",
      "updated_at": "string",
      "username": "string | null",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "type": "usage_analytics_detailed",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "created_at": "string",
      "description": "string | null",
      "dir_path": "string",
      "id": "string",
      "key": "string",
      "meta": {
        "string": "unknown"
      },
      "name": "string",
      "type": "usage_analytics_light",
      "updated_at": "string",
      "workbook_id": "string | null"
    },
    {
      "auth_type": "string | null",
      "cache_ttl_sec": "integer | null",
      "cloud_id": "string | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "db_name": "string",
      "delegation_is_set": "boolean | null",
      "description": "string | null",
      "dir_path": "string",
      "folder_id": "string",
      "host": "string",
      "id": "string",
      "key": "string",
      "mdb_cluster_id": "string | null",
      "mdb_folder_id": "string | null",
      "name": "string",
      "port": "integer",
      "raw_sql_level": "string",
      "service_account_id": "string",
      "ssl_ca": "unknown",
      "ssl_enable": "unknown",
      "token": "string | null",
      "type": "ydb",
      "updated_at": "string",
      "username": "string | null",
      "workbook_id": "string | null"
    },
    {
      "cache_ttl_sec": "integer | null",
      "cloud_id": "string | null",
      "created_at": "string",
      "data_export_forbidden": "unknown",
      "delegation_is_set": "boolean | null",
      "description": "string | null",
      "dir_path": "string",
      "folder_id": "string",
      "id": "string",
      "key": "string",
      "name": "string",
      "raw_sql_level": "string",
      "service_account_id": "string",
      "type": "yq",
      "updated_at": "string",
      "workbook_id": "string | null"
    }
  ]
}
```
