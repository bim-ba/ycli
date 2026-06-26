---
source: https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_delete_keyset_view
title: "Delete key set for form filling - Form Filling Keys |"
word_count: 57
token_estimate: 471
extracted: "2026-05-22T18:13:27Z"
mode: quality
---

-   [Request](https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_delete_keyset_view#request)
    -   [Path parameters](https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_delete_keyset_view#path-parameters)
-   [Responses](https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_delete_keyset_view#responses)
-   [200 OK](https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_delete_keyset_view#200-ok)

Deletes the key set for form filling.

Parameters:

-   **survey\_id**: form ID

-   **keyset\_id**: key set ID

# Request

DELETE

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/keysets/{keyset_id}
```

## Path parameters

| Name | Description |
| --- | --- |
| *keyset_id* | **Type:** integer |
| *survey_id* | **Type:** string<br>**Pattern:** `^[a-fA-F\d]{24}$`<br>**Example:** `` |

# Responses

# 200 OK

OK

## Was the article helpful?