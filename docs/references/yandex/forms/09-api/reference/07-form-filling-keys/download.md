---
source: https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_download_keyset_view
title: "Download key set for form filling - Form Filling Keys |"
word_count: 65
token_estimate: 516
extracted: "2026-05-22T18:13:12Z"
mode: quality
---

Request

-   [Request](https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_download_keyset_view#request)
    -   [Path parameters](https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_download_keyset_view#path-parameters)
-   [Responses](https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_download_keyset_view#responses)
-   [200 OK](https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_download_keyset_view#200-ok)

# Download key set for form filling

## Request

GET

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/keysets/{keyset_id}/download
```

### Path parameters

| Name | Description |
| --- | --- |
| *keyset_id* | **Type:** integer |
| *survey_id* | **Type:** string<br>**Pattern:** `^[a-fA-F\d]{24}$`<br>**Example:** `` |

## Responses

## 200 OK

OK

### Was the article helpful?

YesNo