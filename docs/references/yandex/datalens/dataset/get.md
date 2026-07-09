---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getDataset
title: "Yandex DataLens | DataLens API: Get dataset"
author: "Yandex Cloud"
extracted: "2026-07-09T13:29:12Z"
---

```
POST https://api.datalens.tech/rpc/getDataset
```

```
{
  "datasetId": "string",
  "workbookId": "string | null",
  "rev_id": "string"
}
```

```
{
  "dataset": {
    "avatar_relations": [
      {
        "conditions": [
          {
            "left": {
              "<oneOf>": [
                {
                  "calc_mode": "string",
                  "source": "string"
                },
                {
                  "calc_mode": "string",
                  "formula": "string"
                },
                {
                  "calc_mode": "string",
                  "field_id": "string"
                }
              ]
            },
            "operator": "string",
            "right": {
              "<oneOf>": [
                {
                  "calc_mode": "string",
                  "source": "string"
                },
                {
                  "calc_mode": "string",
                  "formula": "string"
                },
                {
                  "calc_mode": "string",
                  "field_id": "string"
                }
              ]
            },
            "type": "string"
          }
        ],
        "id": "string",
        "join_type": "string",
        "left_avatar_id": "string",
        "managed_by": "string | null",
        "required": "boolean",
        "right_avatar_id": "string",
        "virtual": "unknown"
      }
    ],
    "component_errors": {
      "items": [
        {
          "errors": [
            {
              "code": "unknown",
              "details": {
                "string": "unknown"
              },
              "level": "string",
              "message": "string"
            }
          ],
          "id": "string",
          "type": "string"
        }
      ]
    },
    "data_export_forbidden": "boolean",
    "description": "string | null",
    "load_preview_by_default": "boolean",
    "obligatory_filters": [
      {
        "default_filters": [
          {
            "column": "string",
            "operation": "string",
            "values": "array | null"
          }
        ],
        "field_guid": "string",
        "id": "string",
        "managed_by": "string | null",
        "valid": "boolean"
      }
    ],
    "preview_enabled": "boolean",
    "result_schema": [
      {
        "<oneOf>": [
          {
            "aggregation": "string",
            "aggregation_locked": "boolean | null",
            "autoaggregated": "boolean | null",
            "avatar_id": "string | null",
            "cast": "string",
            "data_type": "string | null",
            "description": "string",
            "guid": "string",
            "has_auto_aggregation": "boolean | null",
            "hidden": "boolean",
            "initial_data_type": "string | null",
            "lock_aggregation": "boolean | null",
            "managed_by": "string | null",
            "source": "string",
            "title": "string",
            "type": "string",
            "ui_settings": "string",
            "valid": "boolean | null",
            "virtual": "unknown"
          },
          {
            "aggregation": "string",
            "aggregation_locked": "boolean | null",
            "autoaggregated": "boolean | null",
            "cast": "string",
            "data_type": "string | null",
            "description": "string",
            "formula": "string",
            "guid": "string",
            "guid_formula": "string",
            "has_auto_aggregation": "boolean | null",
            "hidden": "boolean",
            "initial_data_type": "string | null",
            "lock_aggregation": "boolean | null",
            "managed_by": "string | null",
            "title": "string",
            "type": "string",
            "ui_settings": "string",
            "valid": "boolean | null",
            "virtual": "unknown"
          },
          {
            "aggregation": "string",
            "aggregation_locked": "boolean | null",
            "autoaggregated": "boolean | null",
            "cast": "string",
            "data_type": "string | null",
            "default_value": "string | null",
            "description": "string",
            "guid": "string",
            "has_auto_aggregation": "boolean | null",
            "hidden": "boolean",
            "initial_data_type": "string | null",
            "lock_aggregation": "boolean | null",
            "managed_by": "string | null",
            "template_enabled": "boolean",
            "title": "string",
            "type": "string",
            "ui_settings": "string",
            "valid": "boolean | null",
            "value_constraint": "unknown",
            "virtual": "unknown"
          }
        ]
      }
    ],
    "result_schema_aux": {
      "inter_dependencies": {
        "deps": [
          {
            "dep_field_id": "string",
            "ref_field_ids": [
              "string"
            ]
          }
        ]
      }
    },
    "revision_id": "string | null",
    "rls": {
      "string": "unknown"
    },
    "rls2": {
      "string": "array"
    },
    "source_avatars": [
      {
        "id": "string",
        "is_root": "boolean",
        "managed_by": "string | null",
        "source_id": "string",
        "title": "string",
        "valid": "boolean",
        "virtual": "unknown"
      }
    ],
    "sources": [
      {
        "<oneOf>": [
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "APPMETRICA_API",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "dataset_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "BIGQUERY_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "BIGQUERY_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "BITRIX_GDS",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "CH_BILLING_ANALYTICS_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "CH_FROZEN_SOURCE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "CH_FROZEN_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "CH_GEO_FILTERED_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "CH_YA_MUSIC_PODCAST_STATS_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "CHYT_YTSAURUS_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "table_names": "string"
            },
            "raw_schema": "array | null",
            "source_type": "CHYT_YTSAURUS_TABLE_LIST",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "directory_path": "string",
              "range_from": "string",
              "range_to": "string"
            },
            "raw_schema": "array | null",
            "source_type": "CHYT_YTSAURUS_TABLE_RANGE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "CHYT_YTSAURUS_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "CH_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "CH_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "EQUEO_CH_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "EXTRACTOR_1C_CH_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "schema_name": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "GP_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "GP_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {},
            "raw_schema": "array | null",
            "source_type": "GSHEETS",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {},
            "raw_schema": "array | null",
            "source_type": "JSON_API",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "KONTUR_MARKET_CH_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "METRIKA_API",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {},
            "raw_schema": "array | null",
            "source_type": "MONITORING",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "MOYSKLAD_CH_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "schema_name": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "MSSQL_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "MSSQL_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "MYSQL_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "MYSQL_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "schema_name": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "ORACLE_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "ORACLE_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "schema_name": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "PG_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "PG_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {},
            "raw_schema": "array | null",
            "source_type": "PROMQL",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "CH_SMB_HEATMAPS_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "schema": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "SNOWFLAKE_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "SPEECHSENSE_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "schema_name": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "TRINO_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "TRINO_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "CH_USAGE_TRACKING_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "CH_USAGE_TRACKING_AGG_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "YDB_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "YDB_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "db_name": "string | null",
              "db_version": "string | null",
              "table_name": "string | null"
            },
            "raw_schema": "array | null",
            "source_type": "YQ_TABLE",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          },
          {
            "connection_id": "string | null",
            "id": "string",
            "index_info_set": "array | null",
            "managed_by": "string | null",
            "parameter_hash": "string",
            "parameters": {
              "subsql": "string"
            },
            "raw_schema": "array | null",
            "source_type": "YQ_SUBSELECT",
            "title": "string",
            "valid": "boolean",
            "virtual": "unknown"
          }
        ]
      }
    ],
    "template_enabled": "boolean"
  },
  "id": "string",
  "is_favorite": "boolean",
  "key": "string",
  "options": {
    "connections": {
      "compatible_types": [
        {
          "conn_type": "unknown"
        }
      ],
      "items": [
        {
          "id": "string",
          "replacement_types": [
            {
              "conn_type": "unknown"
            }
          ]
        }
      ],
      "max": "integer"
    },
    "data_types": {
      "items": [
        {
          "aggregations": [
            "string"
          ],
          "casts": [
            "string"
          ],
          "filter_operations": [
            "string"
          ],
          "type": "string"
        }
      ]
    },
    "fields": {
      "items": [
        {
          "aggregations": [
            "string"
          ],
          "casts": [
            "string"
          ],
          "guid": "string"
        }
      ]
    },
    "join": {
      "operators": [
        "string"
      ],
      "types": [
        "string"
      ]
    },
    "preview": {
      "enabled": "boolean"
    },
    "schema_update_enabled": "boolean",
    "source_avatars": {
      "items": [
        {
          "id": "string",
          "schema_update_enabled": "boolean"
        }
      ],
      "max": "integer"
    },
    "source_listing": {
      "db_name_label": "string",
      "db_name_required_for_search": "boolean",
      "supports_db_name_listing": "boolean",
      "supports_source_pagination": "boolean",
      "supports_source_search": "boolean"
    },
    "sources": {
      "compatible_types": [
        {
          "source_type": "unknown"
        }
      ],
      "items": [
        {
          "id": "string",
          "schema_update_enabled": "boolean"
        }
      ],
      "max": "integer"
    },
    "supported_functions": [
      "string"
    ],
    "supports_offset": "boolean"
  },
  "permissions": {
    "string": "boolean"
  }
}
```
