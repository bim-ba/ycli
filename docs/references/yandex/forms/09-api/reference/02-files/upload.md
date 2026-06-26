---
source: https://yandex.ru/support/forms/en/api-ref/files/events_v1_views_files_save_survey_file_view
title: "Upload file for form filling - Files |"
word_count: 197
token_estimate: 1091
extracted: "2026-05-22T18:08:36Z"
mode: quality
---

Uploads a file that can then be used to fill in a File-type field on the form.

A file can only be uploaded if an external file storage is connected in the form settings: [How to save files from responses to storage](https://yandex.com/support/forms/storage-for-attached-files).

For forms with connected storage, files can be uploaded without size or retention limits.

Parameters:

-   **survey\_id**: form ID
-   **file**: file data, passed in the request body in `multipart/form-data` format.

# Request

POST

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/files
```

## Path parameters

| Name | Description |
|------|-------------|
| `survey_id` | **Type:** string. Pattern: `^[a-fA-F\d]{24}$` |

# Responses

# 201 Created

Created

## Body

application/json

```
{
  "name": "example",
  "path": "example",
  "size": 0,
  "url": "example",
  "check_status": "check"
}
```

| Name | Description |
|------|-------------|
| `name` | **Type:** string — File name. Example: `example` |
| `path` | **Type:** string — File download path. Example: `example` |
| `size` | **Type:** integer — File size |
| `check_status` | **All of 1 type:** [FileCheckStatusType](https://yandex.ru/support/forms/en/api-ref/files/events_v1_views_files_save_survey_file_view#entity-FileCheckStatusType) — an enumeration (enum: `check`, `ready`, `infected`, `error`, `deleted`). File check status. Example: `check` |
| `url` | **Type:** string — File download URL. Example: `example` |

## FileCheckStatusType

An enumeration.

**Type**: string

*Enum:* `check`, `ready`, `infected`, `error`, `deleted`

Previous

Next