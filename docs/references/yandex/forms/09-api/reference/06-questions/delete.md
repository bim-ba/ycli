---
source: https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_delete_question_view
title: "Delete question - Questions |"
word_count: 78
token_estimate: 469
extracted: "2026-05-22T18:12:33Z"
mode: quality
---

Deletes a question, checking before deletion whether the question is used in conditions.
The check can be disabled if needed.

Parameters:

-   **survey\_id**: form ID
-   **question\_id**: question ID
-   **force**: disable the condition check. By default the check is enabled

# Request

DELETE

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/questions/{question_id}
```

## Path parameters

| Name | Description |
|------|-------------|
| *question_id* | **Type**: integer |
| *survey_id* | **Type**: string *Pattern:* `^[a-fA-F\d]{24}$` *Example:* `` |

## Query parameters

| Name | Description |
|------|-------------|
| *force* | **Type**: boolean *Default:* `false` |

# Responses

# 204 No Content

No Content