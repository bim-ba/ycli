---
source: https://yandex.ru/support/forms/en/api-ref/surveys/events_v1_views_surveys_publish_survey_view
title: "Publish form - Forms |"
word_count: 80
token_estimate: 344
extracted: "2026-05-22T18:10:02Z"
mode: quality
---

Publishes the form.
Parameters:

-   **survey\_id**: form ID

The request cannot publish:

-   a blocked form that violates the service rules;
-   a form that has reached the maximum number of responses;
-   a form with a response time limit enabled where the time has not yet expired. For more information, see [Restrict the response period](https://yandex.com/support/forms/restrictions#period).

# Request

POST

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/publish
```

## Path parameters

| Name | Description |
|------|-------------|
| `survey_id` | **Type:** string. Pattern: `^[a-fA-F\d]{24}$`. Example: `` |

# Responses

# 200 OK

OK