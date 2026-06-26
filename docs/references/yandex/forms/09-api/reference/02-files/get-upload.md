---
source: https://yandex.ru/support/forms/en/api-ref/files/events_v1_views_files_verify_file_view
title: "Get file upload status - Files |"
word_count: 215
token_estimate: 1410
extracted: "2026-05-22T18:09:09Z"
mode: quality
---

Returns file upload statuses.

Parameters:

-   **survey\_id**: form ID.
-   **data**: list of files whose statuses need to be checked. Download access to the file is verified.

# Request

POST

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/files/verify
```

## Path parameters

| Name | Description |
|------|-------------|
| `survey_id` | **Type:** string. Pattern: `^[a-fA-F\d]{24}$` |

## Body

application/json

```
[
  {
    "path": "example",
    "url": "example"
  }
]
```

**Type**: [FileIn](https://yandex.ru/support/forms/en/api-ref/files/events_v1_views_files_verify_file_view#entity-FileIn)

## FileIn

| Name | Description |
|------|-------------|
| `path` | **Type:** string — File download path. Example: `example` |
| `url` | **Type:** string — File download URL. Example: `example` |

**Example**

```
{
  "path": "example",
  "url": "example"
}
```

# Responses

# 200 OK

OK

## Body

application/json

```
[
  {
    "name": "example",
    "path": "example",
    "size": 0,
    "url": "example",
    "check_status": "check"
  }
]
```

**Type**: [FileOut](https://yandex.ru/support/forms/en/api-ref/files/events_v1_views_files_verify_file_view#entity-FileOut)

## FileCheckStatusType

An enumeration.

**Type**: string

*Enum:* `check`, `ready`, `infected`, `error`, `deleted`

## FileOut

| Name | Description |
|------|-------------|
| `name` | **Type:** string — File name. Example: `example` |
| `path` | **Type:** string — File download path. Example: `example` |
| `size` | **Type:** integer — File size |
| `check_status` | **All of 1 type:** [FileCheckStatusType](https://yandex.ru/support/forms/en/api-ref/files/events_v1_views_files_verify_file_view#entity-FileCheckStatusType) — an enumeration (enum: `check`, `ready`, `infected`, `error`, `deleted`). File check status. Example: `check` |
| `url` | **Type:** string — File download URL. Example: `example` |

**Example**

```
{
  "name": "example",
  "path": "example",
  "size": 0,
  "url": "example",
  "check_status": "check"
}
```