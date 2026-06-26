---
source: https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_move_question_view
title: "Move question - Questions |"
word_count: 158
token_estimate: 1021
extracted: "2026-05-22T18:12:46Z"
mode: quality
---

Moves a question.

Display condition consistency is validated.

Parameters:

-   **survey\_id**: form ID

-   **question\_id**: question ID

# Request

POST

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/questions/{question_id}/move
```

## Path parameters

| Name | Description |
|------|-------------|
| *question_id* | **Type**: integer |
| *survey_id* | **Type**: string *Pattern:* `^[a-fA-F\d]{24}$` *Example:* `` |

## Body

application/json

```
{
  "question": 0,
  "page": 0,
  "page_id": 0,
  "create_page": false,
  "position": 1
}
```

| Name | Description |
|------|-------------|
| *create_page* | **Type**: boolean Create a new page and place the question on it. Used together with the `page` parameter. *Default:* `false` |
| *page* | **Type**: integer Page number (1-based) *Min value:* `0` |
| *page_id* | **Type**: integer Page ID |
| *position* | **Type**: integer New position of the question on the page (1-based) *Min value:* `1` |
| *question* | **Any of 2 types**: **Type**: integer, **Type**: string *Example:* `example` Question ID or slug to move into the question series *Example:* `0` |

# Responses

# 200 OK

OK

## Body

application/json

```
{
  "id": 0
}
```

| Name | Description |
|------|-------------|
| *id* | **Type**: integer Question ID |

Previous

Next