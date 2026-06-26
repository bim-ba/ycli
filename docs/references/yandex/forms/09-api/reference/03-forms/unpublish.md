---
source: https://yandex.ru/support/forms/en/api-ref/surveys/events_v1_views_surveys_unpublish_survey_view
title: "Unpublish form - Forms |"
word_count: 50
token_estimate: 299
extracted: "2026-05-22T18:10:10Z"
mode: quality
---

Unpublishes the form.
Any published form can be unpublished,
including forms with auto-publication enabled before the auto-publication end time is reached.

Parameters:

-   **survey\_id**: form ID

# Request

POST

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/unpublish
```

## Path parameters

| Name | Description |
|------|-------------|
| `survey_id` | **Type:** string. Pattern: `^[a-fA-F\d]{24}$`. Example: `` |

# Responses

# 200 OK

OK