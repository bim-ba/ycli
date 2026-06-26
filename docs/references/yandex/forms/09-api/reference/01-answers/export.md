---
source: https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_export_answers_view
title: "Export answers - Answers |"
word_count: 271
token_estimate: 1965
extracted: "2026-05-22T18:07:37Z"
mode: quality
---

Starts a background process to export answers.

Parameters:

-   **survey\_id**: form ID

# Request

POST

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/answers/export
```

## Path parameters

| Name | Description |
|------|-------------|
| `survey_id` | **Type:** string. Pattern: `^[a-fA-F\d]{24}$` |

## Body

application/json

```
{
  "format": "xlsx",
  "upload": "default",
  "started_at": "2025-01-01T00:00:00Z",
  "finished_at": "2025-01-01T00:00:00Z",
  "pks": [
    0
  ],
  "columns": [
    "example"
  ],
  "limit": 0,
  "upload_files": true
}
```

| Name | Description |
|------|-------------|
| `columns` | **Type:** string[] — List of questions/columns to export. Example: `["example"]` |
| `finished_at` | **Type:** string\<date-time\> — End of the answer export range. Example: `2025-01-01T00:00:00Z` |
| `format` | **All of 1 type:** [AnswerExportFormatType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_export_answers_view#entity-AnswerExportFormatType) — an enumeration (enum: `csv`, `xlsx`). Export format. Default: `xlsx` |
| `limit` | **Type:** integer — Number of answers to export |
| `pks` | **Type:** integer[] — List of answer IDs to export. Example: `[0]` |
| `started_at` | **Type:** string\<date-time\> — Start of the answer export range. Example: `2025-01-01T00:00:00Z` |
| `upload` | **All of 1 type:** [AnswerExportUploadType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_export_answers_view#entity-AnswerExportUploadType) — an enumeration (enum: `default`, `disk`). Where to upload answers. Default: `default` |
| `upload_files` | **Type:** boolean — Allow exporting files to Yandex Disk |

## AnswerExportFormatType

An enumeration.

**Type**: string

*Enum:* `csv`, `xlsx`

## AnswerExportUploadType

An enumeration.

**Type**: string

*Enum:* `default`, `disk`

# Responses

# 202 Accepted

Accepted

## Body

application/json

```
{
  "id": "example",
  "status": "ok",
  "message": "example"
}
```

| Name | Description |
|------|-------------|
| `id` | **Type:** string — Operation ID. Example: `example` |
| `status` | **All of 1 type:** [OperationStatusType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_export_answers_view#entity-OperationStatusType) — an enumeration (enum: `ok`, `fail`, `wait`, `not_running`). Operation status. Example: `ok` |
| `message` | **Type:** string — Operation message. Example: `example` |

## OperationStatusType

An enumeration.

**Type**: string

*Enum:* `ok`, `fail`, `wait`, `not_running`

Previous

Next