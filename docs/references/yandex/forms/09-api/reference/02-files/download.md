---
source: https://yandex.ru/support/forms/en/api-ref/files/events_v1_views_files_get_file_view
title: "Download file - Files |"
word_count: 111
token_estimate: 436
extracted: "2026-05-22T18:08:23Z"
mode: quality
---

Downloads an attached file.
To access the file, the user must have the `change_survey` or `viewfile_survey` role, or be the user who uploaded the file.
An anonymous user can download the file by passing the `hash` parameter in the request.
The `hash` parameter is returned when uploading a file.

Parameters:

-   **path**: path for downloading the file
-   **download**: adds the `Content-Disposition` header with the file name to the response
-   **hash**: allows downloading the file if access to it cannot be verified

# Request

GET

```
https://api.forms.yandex.net/v1/files
```

## Query parameters

| Name | Description |
|------|-------------|
| `path` | **Type:** string |
| `download` | **Type:** boolean. Default: `false` |
| `hash` | **Type:** string |

# Responses

# 200 OK

OK