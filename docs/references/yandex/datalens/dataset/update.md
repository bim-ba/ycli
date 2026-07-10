---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset
title: "Yandex DataLens | DataLens API: Update dataset"
author: "Yandex Cloud"
extracted: "2026-07-09T13:29:34Z"
---

# HTTP request

```
POST https://api.datalens.tech/rpc/updateDataset
```

# Body parameters

**Request schema: application/json**

```
{
  "datasetId": "string",
  "data": {
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
    }
  }
}
```

| Field | Description |
| --- | --- |
| datasetId | **string** Required field. |
| data | **[DatasetUpdate](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#DatasetUpdate)** Required field. |

# DatasetUpdate

# DatasetContentInternal

| Field | Description |
| --- | --- |
| avatar_relations[] | **[AvatarRelation](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#AvatarRelation)** Required field. |
| component_errors | **[ComponentErrorList](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ComponentErrorList)** |
| data_export_forbidden | **boolean** |
| description | **string \| null** |
| load_preview_by_default | **boolean** |
| obligatory_filters[] | **[ObligatoryFilter](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ObligatoryFilter)** Required field. |
| preview_enabled | **boolean** |
| result_schema[] | **[ResultSchemaSchemaGeneric](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ResultSchemaSchemaGeneric)** |
| result_schema_aux | **[ResultSchemaAux](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ResultSchemaAux)** |
| revision_id | **string \| null** |
| rls | **object** (map<**string**, **unknown**>) |
| rls2 | **[RLS2ConfigEntry](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#RLS2ConfigEntry)** Required field. |
| source_avatars[] | **[SourceAvatarStrict](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SourceAvatarStrict)** Required field. |
| sources[] | **[DataSourceStrict](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#DataSourceStrict)** |
| template_enabled | **boolean** |

# AvatarRelation

| Field | Description |
| --- | --- |
| conditions[] | **[JoinCondition](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#JoinCondition)** Required field. |
| id | **string** Required field. |
| join_type | **enum** `inner`, `left`, `right`, `full` |
| left_avatar_id | **string** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| required | **boolean** |
| right_avatar_id | **string** |
| virtual | **unknown** |

# JoinCondition

# direct

| Field | Description |
| --- | --- |
| calc_mode | **enum** Required field. `direct`, `formula`, `result_field` |
| source | **string** Required field. |

# formula

| Field | Description |
| --- | --- |
| calc_mode | **enum** Required field. `direct`, `formula`, `result_field` |
| formula | **string** Required field. |

# result\_field

| Field | Description |
| --- | --- |
| calc_mode | **enum** Required field. `direct`, `formula`, `result_field` |
| field_id | **string** Required field. |

# ComponentErrorList

# ComponentErrorPack

| Field | Description |
| --- | --- |
| errors[] | **[ComponentError](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ComponentError)** |
| id | **string** |
| type | **enum** `data_source`, `source_avatar`, `avatar_relation`, `field`, `obligatory_filter`, `result_schema` |

# ComponentError

| Field | Description |
| --- | --- |
| code | **unknown** |
| details | **object** (map<**string**, **unknown**>) |
| level | **enum** `error`, `warning` |
| message | **string** |

# ObligatoryFilter

| Field | Description |
| --- | --- |
| default_filters[] | **[Where](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Where)** Required field. |
| field_guid | **string** |
| id | **string** Required field. |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| valid | **boolean** |

# Where

| Field | Description |
| --- | --- |
| column | **string** Required field. |
| operation | **enum** Required field. `ISNULL`, `ISNOTNULL`, `GT`, `LT`, `GTE`, `LTE`, `EQ`, `NE`, `STARTSWITH`, `ISTARTSWITH`, `ENDSWITH`, `IENDSWITH`, `CONTAINS`, `ICONTAINS`, `NOTCONTAINS`, `NOTICONTAINS`, `LENEQ`, `LENNE`, `LENGT`, `LENGTE`, `LENLT`, `LENLTE`, `IN`, `NIN`, `BETWEEN` |
| values | **array \| null** Required field. |

# ResultSchemaSchemaGeneric

One of:

| Field | Description |
| --- | --- |
| aggregation | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| aggregation_locked | **boolean \| null** |
| autoaggregated | **boolean \| null** |
| avatar_id | **string \| null** |
| cast | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| description | **string** |
| guid | **string** |
| has_auto_aggregation | **boolean \| null** |
| hidden | **boolean** |
| initial_data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| lock_aggregation | **boolean \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| source | **string** |
| title | **string** Required field. |
| type | **enum** `DIMENSION`, `MEASURE` |
| ui_settings | **string** |
| valid | **boolean \| null** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| aggregation | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| aggregation_locked | **boolean \| null** |
| autoaggregated | **boolean \| null** |
| cast | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| description | **string** |
| formula | **string** |
| guid | **string** |
| guid_formula | **string** |
| has_auto_aggregation | **boolean \| null** |
| hidden | **boolean** |
| initial_data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| lock_aggregation | **boolean \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| title | **string** Required field. |
| type | **enum** `DIMENSION`, `MEASURE` |
| ui_settings | **string** |
| valid | **boolean \| null** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| aggregation | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| aggregation_locked | **boolean \| null** |
| autoaggregated | **boolean \| null** |
| cast | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| default_value | **string \| null** |
| description | **string** |
| guid | **string** |
| has_auto_aggregation | **boolean \| null** |
| hidden | **boolean** |
| initial_data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| lock_aggregation | **boolean \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| template_enabled | **boolean** |
| title | **string** Required field. |
| type | **enum** `DIMENSION`, `MEASURE` |
| ui_settings | **string** |
| valid | **boolean \| null** |
| value_constraint | Any of **[ParameterValueConstraint](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ParameterValueConstraint)** \| **null** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| Empty |  |

# ParameterValueConstraint

One of:

| Field | Description |
| --- | --- |
| pattern | **string** |
| type | **regex** (const) |

| Field | Description |
| --- | --- |
| type | **default** (const) |

| Field | Description |
| --- | --- |
| Empty |  |

# ResultSchemaAux

# FieldInterDependencyInfo

# FieldInterDependencyItem

| Field | Description |
| --- | --- |
| dep_field_id | **string** |
| ref_field_ids[] | **string** |

# RLS2ConfigEntry

| Field | Description |
| --- | --- |
| allowed_value | **string \| null** |
| field_guid | **string \| null** |
| pattern_type | **enum** `value`, `all`, `userid` |
| subject | **[RLSSubject](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#RLSSubject)** Required field. |

# RLSSubject

| Field | Description |
| --- | --- |
| subject_id | **string** Required field. |
| subject_name | **string \| null** |
| subject_type | **enum** `user`, `group`, `all`, `userid`, `unknown`, `notfound` |

# SourceAvatarStrict

| Field | Description |
| --- | --- |
| id | **string** Required field. |
| is_root | **boolean** |
| managed_by | **enum** Required field. `user`, `feature`, `compiler_runtime`, `null` |
| source_id | **string** |
| title | **string** |
| valid | **boolean** |
| virtual | **unknown** |

# DataSourceStrict

One of:

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **APPMETRICA_API** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[BigQueryTableParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#BigQueryTableParameters)** |
| raw_schema | **array \| null** |
| source_type | **BIGQUERY_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **BIGQUERY_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **BITRIX_GDS** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_BILLING_ANALYTICS_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_FROZEN_SOURCE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_FROZEN_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_GEO_FILTERED_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_YA_MUSIC_PODCAST_STATS_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **CHYT_YTSAURUS_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[CHYTTableListParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#CHYTTableListParameters)** |
| raw_schema | **array \| null** |
| source_type | **CHYT_YTSAURUS_TABLE_LIST** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[CHYTTableRangeParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#CHYTTableRangeParameters)** |
| raw_schema | **array \| null** |
| source_type | **CHYT_YTSAURUS_TABLE_RANGE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **CHYT_YTSAURUS_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **EQUEO_CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **EXTRACTOR_1C_CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters)** |
| raw_schema | **array \| null** |
| source_type | **GP_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **GP_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SimpleParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SimpleParameters)** |
| raw_schema | **array \| null** |
| source_type | **GSHEETS** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SimpleParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SimpleParameters)** |
| raw_schema | **array \| null** |
| source_type | **JSON_API** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **KONTUR_MARKET_CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **METRIKA_API** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SimpleParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SimpleParameters)** |
| raw_schema | **array \| null** |
| source_type | **MONITORING** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **MOYSKLAD_CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters)** |
| raw_schema | **array \| null** |
| source_type | **MSSQL_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **MSSQL_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **MYSQL_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **MYSQL_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters)** |
| raw_schema | **array \| null** |
| source_type | **ORACLE_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **ORACLE_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters)** |
| raw_schema | **array \| null** |
| source_type | **PG_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **PG_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SimpleParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SimpleParameters)** |
| raw_schema | **array \| null** |
| source_type | **PROMQL** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_SMB_HEATMAPS_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SnowFlakeTableParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SnowFlakeTableParameters)** |
| raw_schema | **array \| null** |
| source_type | **SNOWFLAKE_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **SPEECHSENSE_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters)** |
| raw_schema | **array \| null** |
| source_type | **TRINO_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **TRINO_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_USAGE_TRACKING_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **CH_USAGE_TRACKING_AGG_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **YDB_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **YDB_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters)** |
| raw_schema | **array \| null** |
| source_type | **YQ_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters)** |
| raw_schema | **array \| null** |
| source_type | **YQ_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| Empty |  |

# SQLParameters

| Field | Description |
| --- | --- |
| db_name | **string \| null** |
| db_version | **string \| null** |
| table_name | **string \| null** |

# BigQueryTableParameters

| Field | Description |
| --- | --- |
| dataset_name | **string \| null** |
| db_version | **string \| null** |
| table_name | **string \| null** |

# SubselectParameters

| Field | Description |
| --- | --- |
| subsql | **string** |

# CHYTTableListParameters

| Field | Description |
| --- | --- |
| table_names | **string** |

# CHYTTableRangeParameters

| Field | Description |
| --- | --- |
| directory_path | **string** |
| range_from | **string** |
| range_to | **string** |

# SchematizedParameters

| Field | Description |
| --- | --- |
| db_name | **string \| null** |
| db_version | **string \| null** |
| schema_name | **string \| null** |
| table_name | **string \| null** |

# SimpleParameters

| Field | Description |
| --- | --- |
| Empty |  |

# SnowFlakeTableParameters

| Field | Description |
| --- | --- |
| db_name | **string \| null** |
| schema | **string \| null** |
| table_name | **string \| null** |

# Options

| Field | Description |
| --- | --- |
| connections | **[Connections](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Connections)** |
| data_types | **[DataTypes](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#DataTypes)** |
| fields | **[Fields](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Fields)** |
| join | **[Join](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Join)** |
| preview | **[Preview](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Preview)** |
| schema_update_enabled | **boolean** |
| source_avatars | **[Avatars](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Avatars)** |
| source_listing | **[SourceListing](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SourceListing)** |
| sources | **[Sources](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Sources)** |
| supported_functions[] | **string** |
| supports_offset | **boolean** |

# Connections

# CompatConnectionTypeListItem

| Field | Description |
| --- | --- |
| conn_type | **unknown** |

# ConnectionListItem

# DataTypes

# DataTypeListItem

| Field | Description |
| --- | --- |
| aggregations[] | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| casts[] | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| filter_operations[] | **enum** `ISNULL`, `ISNOTNULL`, `GT`, `LT`, `GTE`, `LTE`, `EQ`, `NE`, `STARTSWITH`, `ISTARTSWITH`, `ENDSWITH`, `IENDSWITH`, `CONTAINS`, `ICONTAINS`, `NOTCONTAINS`, `NOTICONTAINS`, `LENEQ`, `LENNE`, `LENGT`, `LENGTE`, `LENLT`, `LENLTE`, `IN`, `NIN`, `BETWEEN` |
| type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |

# Fields

# FieldListItem

| Field | Description |
| --- | --- |
| aggregations[] | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| casts[] | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| guid | **string** |

# Join

| Field | Description |
| --- | --- |
| operators[] | **enum** `gt`, `lt`, `gte`, `lte`, `eq`, `ne` |
| types[] | **enum** `inner`, `left`, `right`, `full` |

# Preview

| Field | Description |
| --- | --- |
| enabled | **boolean** |

# Avatars

# SourceListItem

| Field | Description |
| --- | --- |
| id | **string** |
| schema_update_enabled | **boolean** |

# SourceListing

| Field | Description |
| --- | --- |
| db_name_label | **string** |
| db_name_required_for_search | **boolean** |
| supports_db_name_listing | **boolean** |
| supports_source_pagination | **boolean** |
| supports_source_search | **boolean** |

# Sources

# CompatSourceTypeListItem

| Field | Description |
| --- | --- |
| source_type | **unknown** |

# SourceListItem1

| Field | Description |
| --- | --- |
| id | **string** |
| schema_update_enabled | **boolean** |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

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

| Field | Description |
| --- | --- |
| dataset | **[DatasetContentInternal](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#DatasetContentInternal2)** Required field. |
| id | **string** |
| is_favorite | **boolean** |
| key | **string** |
| options | **[Options](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Options2)** |
| permissions | **object** (map<**string**, **boolean**>) |

# DatasetContentInternal

| Field | Description |
| --- | --- |
| avatar_relations[] | **[AvatarRelation](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#AvatarRelation2)** Required field. |
| component_errors | **[ComponentErrorList](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ComponentErrorList2)** |
| data_export_forbidden | **boolean** |
| description | **string \| null** |
| load_preview_by_default | **boolean** |
| obligatory_filters[] | **[ObligatoryFilter](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ObligatoryFilter2)** Required field. |
| preview_enabled | **boolean** |
| result_schema[] | **[ResultSchemaSchemaGeneric](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ResultSchemaSchemaGeneric2)** |
| result_schema_aux | **[ResultSchemaAux](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ResultSchemaAux2)** |
| revision_id | **string \| null** |
| rls | **object** (map<**string**, **unknown**>) |
| rls2 | **[RLS2ConfigEntry](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#RLS2ConfigEntry2)** Required field. |
| source_avatars[] | **[SourceAvatarStrict](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SourceAvatarStrict2)** Required field. |
| sources[] | **[DataSourceStrict](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#DataSourceStrict2)** |
| template_enabled | **boolean** |

# AvatarRelation

| Field | Description |
| --- | --- |
| conditions[] | **[JoinCondition](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#JoinCondition2)** Required field. |
| id | **string** Required field. |
| join_type | **enum** `inner`, `left`, `right`, `full` |
| left_avatar_id | **string** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| required | **boolean** |
| right_avatar_id | **string** |
| virtual | **unknown** |

# JoinCondition

# direct

| Field | Description |
| --- | --- |
| calc_mode | **enum** Required field. `direct`, `formula`, `result_field` |
| source | **string** Required field. |

# formula

| Field | Description |
| --- | --- |
| calc_mode | **enum** Required field. `direct`, `formula`, `result_field` |
| formula | **string** Required field. |

# result\_field

| Field | Description |
| --- | --- |
| calc_mode | **enum** Required field. `direct`, `formula`, `result_field` |
| field_id | **string** Required field. |

# ComponentErrorList

# ComponentErrorPack

| Field | Description |
| --- | --- |
| errors[] | **[ComponentError](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ComponentError2)** |
| id | **string** |
| type | **enum** `data_source`, `source_avatar`, `avatar_relation`, `field`, `obligatory_filter`, `result_schema` |

# ComponentError

| Field | Description |
| --- | --- |
| code | **unknown** |
| details | **object** (map<**string**, **unknown**>) |
| level | **enum** `error`, `warning` |
| message | **string** |

# ObligatoryFilter

| Field | Description |
| --- | --- |
| default_filters[] | **[Where](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Where2)** Required field. |
| field_guid | **string** |
| id | **string** Required field. |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| valid | **boolean** |

# Where

| Field | Description |
| --- | --- |
| column | **string** Required field. |
| operation | **enum** Required field. `ISNULL`, `ISNOTNULL`, `GT`, `LT`, `GTE`, `LTE`, `EQ`, `NE`, `STARTSWITH`, `ISTARTSWITH`, `ENDSWITH`, `IENDSWITH`, `CONTAINS`, `ICONTAINS`, `NOTCONTAINS`, `NOTICONTAINS`, `LENEQ`, `LENNE`, `LENGT`, `LENGTE`, `LENLT`, `LENLTE`, `IN`, `NIN`, `BETWEEN` |
| values | **array \| null** Required field. |

# ResultSchemaSchemaGeneric

One of:

| Field | Description |
| --- | --- |
| aggregation | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| aggregation_locked | **boolean \| null** |
| autoaggregated | **boolean \| null** |
| avatar_id | **string \| null** |
| cast | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| description | **string** |
| guid | **string** |
| has_auto_aggregation | **boolean \| null** |
| hidden | **boolean** |
| initial_data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| lock_aggregation | **boolean \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| source | **string** |
| title | **string** Required field. |
| type | **enum** `DIMENSION`, `MEASURE` |
| ui_settings | **string** |
| valid | **boolean \| null** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| aggregation | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| aggregation_locked | **boolean \| null** |
| autoaggregated | **boolean \| null** |
| cast | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| description | **string** |
| formula | **string** |
| guid | **string** |
| guid_formula | **string** |
| has_auto_aggregation | **boolean \| null** |
| hidden | **boolean** |
| initial_data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| lock_aggregation | **boolean \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| title | **string** Required field. |
| type | **enum** `DIMENSION`, `MEASURE` |
| ui_settings | **string** |
| valid | **boolean \| null** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| aggregation | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| aggregation_locked | **boolean \| null** |
| autoaggregated | **boolean \| null** |
| cast | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| default_value | **string \| null** |
| description | **string** |
| guid | **string** |
| has_auto_aggregation | **boolean \| null** |
| hidden | **boolean** |
| initial_data_type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime`, `null` |
| lock_aggregation | **boolean \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| template_enabled | **boolean** |
| title | **string** Required field. |
| type | **enum** `DIMENSION`, `MEASURE` |
| ui_settings | **string** |
| valid | **boolean \| null** |
| value_constraint | Any of **[ParameterValueConstraint](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#ParameterValueConstraint2)** \| **null** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| Empty |  |

# ParameterValueConstraint

One of:

| Field | Description |
| --- | --- |
| pattern | **string** |
| type | **regex** (const) |

| Field | Description |
| --- | --- |
| type | **default** (const) |

| Field | Description |
| --- | --- |
| Empty |  |

# ResultSchemaAux

# FieldInterDependencyInfo

# FieldInterDependencyItem

| Field | Description |
| --- | --- |
| dep_field_id | **string** |
| ref_field_ids[] | **string** |

# RLS2ConfigEntry

| Field | Description |
| --- | --- |
| allowed_value | **string \| null** |
| field_guid | **string \| null** |
| pattern_type | **enum** `value`, `all`, `userid` |
| subject | **[RLSSubject](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#RLSSubject2)** Required field. |

# RLSSubject

| Field | Description |
| --- | --- |
| subject_id | **string** Required field. |
| subject_name | **string \| null** |
| subject_type | **enum** `user`, `group`, `all`, `userid`, `unknown`, `notfound` |

# SourceAvatarStrict

| Field | Description |
| --- | --- |
| id | **string** Required field. |
| is_root | **boolean** |
| managed_by | **enum** Required field. `user`, `feature`, `compiler_runtime`, `null` |
| source_id | **string** |
| title | **string** |
| valid | **boolean** |
| virtual | **unknown** |

# DataSourceStrict

One of:

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **APPMETRICA_API** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[BigQueryTableParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#BigQueryTableParameters2)** |
| raw_schema | **array \| null** |
| source_type | **BIGQUERY_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **BIGQUERY_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **BITRIX_GDS** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_BILLING_ANALYTICS_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_FROZEN_SOURCE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_FROZEN_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_GEO_FILTERED_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_YA_MUSIC_PODCAST_STATS_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CHYT_YTSAURUS_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[CHYTTableListParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#CHYTTableListParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CHYT_YTSAURUS_TABLE_LIST** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[CHYTTableRangeParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#CHYTTableRangeParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CHYT_YTSAURUS_TABLE_RANGE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CHYT_YTSAURUS_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **EQUEO_CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **EXTRACTOR_1C_CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters2)** |
| raw_schema | **array \| null** |
| source_type | **GP_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **GP_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SimpleParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SimpleParameters2)** |
| raw_schema | **array \| null** |
| source_type | **GSHEETS** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SimpleParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SimpleParameters2)** |
| raw_schema | **array \| null** |
| source_type | **JSON_API** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **KONTUR_MARKET_CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **METRIKA_API** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SimpleParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SimpleParameters2)** |
| raw_schema | **array \| null** |
| source_type | **MONITORING** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **MOYSKLAD_CH_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters2)** |
| raw_schema | **array \| null** |
| source_type | **MSSQL_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **MSSQL_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **MYSQL_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **MYSQL_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters2)** |
| raw_schema | **array \| null** |
| source_type | **ORACLE_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **ORACLE_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters2)** |
| raw_schema | **array \| null** |
| source_type | **PG_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **PG_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SimpleParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SimpleParameters2)** |
| raw_schema | **array \| null** |
| source_type | **PROMQL** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_SMB_HEATMAPS_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SnowFlakeTableParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SnowFlakeTableParameters2)** |
| raw_schema | **array \| null** |
| source_type | **SNOWFLAKE_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **SPEECHSENSE_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SchematizedParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SchematizedParameters2)** |
| raw_schema | **array \| null** |
| source_type | **TRINO_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **TRINO_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_USAGE_TRACKING_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **CH_USAGE_TRACKING_AGG_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **YDB_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **YDB_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SQLParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SQLParameters2)** |
| raw_schema | **array \| null** |
| source_type | **YQ_TABLE** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| connection_id | **string \| null** |
| id | **string** Required field. |
| index_info_set | **array \| null** |
| managed_by | **enum** `user`, `feature`, `compiler_runtime`, `null` |
| parameter_hash | **string** |
| parameters | **[SubselectParameters](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SubselectParameters2)** |
| raw_schema | **array \| null** |
| source_type | **YQ_SUBSELECT** (const) |
| title | **string** Required field. |
| valid | **boolean** |
| virtual | **unknown** |

| Field | Description |
| --- | --- |
| Empty |  |

# SQLParameters

| Field | Description |
| --- | --- |
| db_name | **string \| null** |
| db_version | **string \| null** |
| table_name | **string \| null** |

# BigQueryTableParameters

| Field | Description |
| --- | --- |
| dataset_name | **string \| null** |
| db_version | **string \| null** |
| table_name | **string \| null** |

# SubselectParameters

| Field | Description |
| --- | --- |
| subsql | **string** |

# CHYTTableListParameters

| Field | Description |
| --- | --- |
| table_names | **string** |

# CHYTTableRangeParameters

| Field | Description |
| --- | --- |
| directory_path | **string** |
| range_from | **string** |
| range_to | **string** |

# SchematizedParameters

| Field | Description |
| --- | --- |
| db_name | **string \| null** |
| db_version | **string \| null** |
| schema_name | **string \| null** |
| table_name | **string \| null** |

# SimpleParameters

| Field | Description |
| --- | --- |
| Empty |  |

# SnowFlakeTableParameters

| Field | Description |
| --- | --- |
| db_name | **string \| null** |
| schema | **string \| null** |
| table_name | **string \| null** |

# Options

| Field | Description |
| --- | --- |
| connections | **[Connections](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Connections2)** |
| data_types | **[DataTypes](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#DataTypes2)** |
| fields | **[Fields](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Fields2)** |
| join | **[Join](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Join2)** |
| preview | **[Preview](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Preview2)** |
| schema_update_enabled | **boolean** |
| source_avatars | **[Avatars](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Avatars2)** |
| source_listing | **[SourceListing](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#SourceListing2)** |
| sources | **[Sources](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateDataset#Sources2)** |
| supported_functions[] | **string** |
| supports_offset | **boolean** |

# Connections

# CompatConnectionTypeListItem

| Field | Description |
| --- | --- |
| conn_type | **unknown** |

# ConnectionListItem

# DataTypes

# DataTypeListItem

| Field | Description |
| --- | --- |
| aggregations[] | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| casts[] | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| filter_operations[] | **enum** `ISNULL`, `ISNOTNULL`, `GT`, `LT`, `GTE`, `LTE`, `EQ`, `NE`, `STARTSWITH`, `ISTARTSWITH`, `ENDSWITH`, `IENDSWITH`, `CONTAINS`, `ICONTAINS`, `NOTCONTAINS`, `NOTICONTAINS`, `LENEQ`, `LENNE`, `LENGT`, `LENGTE`, `LENLT`, `LENLTE`, `IN`, `NIN`, `BETWEEN` |
| type | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |

# Fields

# FieldListItem

| Field | Description |
| --- | --- |
| aggregations[] | **enum** `none`, `sum`, `avg`, `min`, `max`, `count`, `countunique` |
| casts[] | **enum** `string`, `integer`, `float`, `date`, `datetime`, `boolean`, `geopoint`, `geopolygon`, `uuid`, `markup`, `datetimetz`, `unsupported`, `array_str`, `array_int`, `array_float`, `tree_str`, `genericdatetime` |
| guid | **string** |

# Join

| Field | Description |
| --- | --- |
| operators[] | **enum** `gt`, `lt`, `gte`, `lte`, `eq`, `ne` |
| types[] | **enum** `inner`, `left`, `right`, `full` |

# Preview

| Field | Description |
| --- | --- |
| enabled | **boolean** |

# Avatars

# SourceListItem

| Field | Description |
| --- | --- |
| id | **string** |
| schema_update_enabled | **boolean** |

# SourceListing

| Field | Description |
| --- | --- |
| db_name_label | **string** |
| db_name_required_for_search | **boolean** |
| supports_db_name_listing | **boolean** |
| supports_source_pagination | **boolean** |
| supports_source_search | **boolean** |

# Sources

# CompatSourceTypeListItem

| Field | Description |
| --- | --- |
| source_type | **unknown** |

# SourceListItem1

| Field | Description |
| --- | --- |
| id | **string** |
| schema_update_enabled | **boolean** |
