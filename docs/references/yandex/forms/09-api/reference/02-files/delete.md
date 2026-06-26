---
source: https://yandex.ru/support/forms/en/api-ref/files/events_v1_views_files_delete_file_view
title: "Delete file - Files |"
word_count: 69
token_estimate: 373
extracted: "2026-05-22T18:08:29Z"
mode: quality
---

Deletes an attached file.
To access the file, the user must have the `change_survey` or `viewfile_survey` role, or be the user who uploaded the file.

# Request

DELETE

```
https://api.forms.yandex.net/v1/files
```

## Body

application/json

```
{
  "path": "example",
  "url": "example"
}
```

| Name | Description |
|------|-------------|
| `path` | **Type:** string — File download path. Example: `example` |
| `url` | **Type:** string — File download URL. Example: `example` |

# Responses

# 200 OK

OK

Previous

Next