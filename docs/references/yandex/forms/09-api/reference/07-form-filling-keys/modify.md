---
source: https://yandex.ru/support/forms/en/api-ref/keysets/events_v1_views_keysets_modify_keyset_view
title: "Modify key set for form filling - Form Filling Keys |"
word_count: 130
token_estimate: 938
extracted: "2026-05-22T18:13:33Z"
mode: quality
---

Modifies the key set for form filling.

Parameters:

-   **survey\_id**: form ID

-   **keyset\_id**: key set ID

# Request

PATCH

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/keysets/{keyset_id}
```

## Path parameters

| Name | Description |
| --- | --- |
| *keyset_id* | **Type:** integer |
| *survey_id* | **Type:** string<br>**Pattern:** `^[a-fA-F\d]{24}$`<br>**Example:** `` |

## Body

application/json

```
{
  "name": "example",
  "total": 0,
  "is_enabled": true
}
```

| Name | Description |
| --- | --- |
| *is_enabled* | **Type:** boolean<br>Active key set flag |
| *name* | **Type:** string<br>Key set name<br>**Example:** `example` |
| *total* | **Type:** integer<br>Number of keys in the set |

# Responses

# 200 OK

OK

## Body

application/json

```
{
  "id": 0,
  "name": "example",
  "total": 0,
  "used": 0,
  "is_enabled": true
}
```

| Name | Description |
| --- | --- |
| *id* | **Type:** integer<br>Key set ID |
| *is_enabled* | **Type:** boolean<br>Active key set flag |
| *name* | **Type:** string<br>Key set name<br>**Example:** `example` |
| *total* | **Type:** integer<br>Number of keys in the set |
| *used* | **Type:** integer<br>Number of used keys in the set |

Previous

Next