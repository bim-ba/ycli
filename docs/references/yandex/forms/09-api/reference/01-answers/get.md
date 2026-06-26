---
source: https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view
title: "Get answer - Answers |"
word_count: 1148
token_estimate: 9892
extracted: "2026-05-22T18:07:31Z"
mode: quality
---

Returns answer data.

# 200 OK

OK

## Body

application/json

```
{
  "id": 0,
  "created": "example",
  "survey": {
    "id": "example",
    "name": "example"
  },
  "quiz": {
    "scores": 0.5,
    "total": 0.5,
    "questions": 0,
    "title": "example",
    "subtitle": "example",
    "image": {
      "id": 0,
      "links": {},
      "name": "example",
      "check_status": null
    },
    "show_results": true
  },
  "data": [
    {
      "id": "example",
      "label": "example",
      "type": "string",
      "widget": "radio",
      "multiline": true,
      "multichoice": true,
      "is_deleted": true,
      "items": [
        {}
      ],
      "scores": 0.5,
      "value": "example"
    }
  ]
}
```

| Name | Description |
|------|-------------|
| `data` | **Type:** [AnswerQuestionOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerQuestionOut)[] — Answer data. Example: `[{"id": "example", "label": "example", "type": "string", "widget": "radio", "multiline": true, "multichoice": true, "is_deleted": true, "items": [{"label": "example", "scores": 0.5}], "scores": 0.5, "value": "example"}]` |
| `id` | **Type:** integer — Answer ID |
| `survey` | **All of 1 type:** [AnswerSurveyOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerSurveyOut) — Form data (Example: `{"id": "example", "name": "example"}`). Example: `{"id": "example", "name": "example"}` |
| `created` | **Type:** string — Answer date. Example: `example` |
| `quiz` | **All of 1 type:** [AnswerQuizOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerQuizOut) — Test results (Example: `{"scores": 0.5, "total": 0.5, "questions": 0, "title": "example", "subtitle": "example", "image": {"id": 0, "links": {}, "name": "example", "check_status": "check"}, "show_results": true}`). Example: `{"scores": 0.5, "total": 0.5, "questions": 0, "title": "example", "subtitle": "example", "image": {"id": 0, "links": {}, "name": "example", "check_status": "check"}, "show_results": true}` |

## AnswerSurveyOut

| Name | Description |
|------|-------------|
| `id` | **Type:** string — Form ID. Example: `example` |
| `name` | **Type:** string — Form name. Example: `example` |

**Example**

```
{
  "id": "example",
  "name": "example"
}
```

## FileCheckStatusType

An enumeration.

**Type**: string

*Enum:* `check`, `ready`, `infected`, `error`, `deleted`

## ImageOut

| Name | Description |
|------|-------------|
| `links` | **Type:** Links — List of links to different image sizes. Nested property `[additional]`: **Type:** string\<uri\>, Min length: `1`, Max length: `2083`, Example: `https://example.com`. Example: `{}` |
| `check_status` | **All of 1 type:** [FileCheckStatusType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-FileCheckStatusType) — an enumeration (enum: `check`, `ready`, `infected`, `error`, `deleted`). Image upload status. Example: `check` |
| `id` | **Type:** integer — Image ID |
| `name` | **Type:** string — Original image file name. Example: `example` |

**Example**

```
{
  "id": 0,
  "links": {},
  "name": "example",
  "check_status": "check"
}
```

## AnswerQuizOut

| Name | Description |
|------|-------------|
| `questions` | **Type:** integer — Number of questions with tests |
| `scores` | **Type:** number — Points scored for the form response |
| `show_results` | **Type:** boolean — Whether to show test results |
| `total` | **Type:** number — Maximum points for the form response |
| `image` | **All of 1 type:** [ImageOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-ImageOut) — Image for the test result page (Example: `{"id": 0, "links": {}, "name": "example", "check_status": "check"}`). Example: `{"id": 0, "links": {}, "name": "example", "check_status": "check"}` |
| `subtitle` | **Type:** string — Subtitle of the test result page. Example: `example` |
| `title` | **Type:** string — Title of the test result page. Example: `example` |

**Example**

```
{
  "scores": 0.5,
  "total": 0.5,
  "questions": 0,
  "title": "example",
  "subtitle": "example",
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "show_results": true
}
```

## QuestionType

An enumeration.

**Type**: string

*Enum:* `string`, `boolean`, `integer`, `date`, `daterange`, `file`, `radio`, `checkbox`, `dropdown`, `stars`, `onerow`, `matrix`, `suggest`, `comment`, `payment`, `captcha`, `series`, `layout`, `enum`

## WidgetType

An enumeration.

**Type**: string

*Enum:* `radio`, `checkbox`, `dropdown`, `stars`, `onerow`

## AnswerStringScoresOut

| Name | Description |
|------|-------------|
| `label` | **Type:** string — String question name. Example: `example` |
| `scores` | **Type:** number — Points for the string answer |

**Example**

```
{
  "label": "example",
  "scores": 0.5
}
```

## AnswerEnumItemOut

| Name | Description |
|------|-------------|
| `id` | **Type:** string — Answer option ID. Example: `example` |
| `label` | **Type:** string — Answer option name. Example: `example` |
| `scores` | **Type:** number — Points for the answer option |

**Example**

```
{
  "id": "example",
  "label": "example",
  "scores": 0.5
}
```

## AnswerMatrixOut

| Name | Description |
|------|-------------|
| `columns` | **Type:** [AnswerEnumItemOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerEnumItemOut)[] — Columns in the scale rating. Example: `[{"id": "example", "label": "example", "scores": 0.5}]` |
| `rows` | **Type:** [AnswerEnumItemOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerEnumItemOut)[] — Rows in the scale rating. Example: `[{"id": "example", "label": "example", "scores": 0.5}]` |

**Example**

```
{
  "rows": [
    {
      "id": "example",
      "label": "example",
      "scores": 0.5
    }
  ],
  "columns": [
    null
  ]
}
```

## AnswerDateRangeOut

| Name | Description |
|------|-------------|
| `begin` | **Type:** string — Start of the date range. Example: `example` |
| `end` | **Type:** string — End of the date range. Example: `example` |

**Example**

```
{
  "begin": "example",
  "end": "example"
}
```

## AnswerFileOut

| Name | Description |
|------|-------------|
| `name` | **Type:** string — File name. Example: `example` |
| `path` | **Type:** string — File download path. Example: `example` |

**Example**

```
{
  "name": "example",
  "path": "example"
}
```

## AnswerMatrixItemOut

| Name | Description |
|------|-------------|
| `column` | **All of 1 type:** [AnswerEnumItemOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerEnumItemOut) — Column in the scale rating (Example: `{"id": "example", "label": "example", "scores": 0.5}`). Example: `{"id": "example", "label": "example", "scores": 0.5}` |
| `row` | **All of 1 type:** [AnswerEnumItemOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerEnumItemOut) — Row in the scale rating (Example: `{"id": "example", "label": "example", "scores": 0.5}`). Example: `{"id": "example", "label": "example", "scores": 0.5}` |

**Example**

```
{
  "row": {
    "id": "example",
    "label": "example",
    "scores": 0.5
  },
  "column": null
}
```

## AnswerQuestionOut

| Name | Description |
|------|-------------|
| `id` | **Type:** string — Question ID. Example: `example` |
| `label` | **Type:** string — Question name. Example: `example` |
| `type` | **All of 1 type:** [QuestionType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-QuestionType) — an enumeration (enum: `string`, `boolean`, `integer`, `date`, `daterange`, `file`, `radio`, `checkbox`, `dropdown`, `stars`, `onerow`, `matrix`, `suggest`, `comment`, `payment`, `captcha`, `series`, `layout`, `enum`). Question type. Example: `string` |
| `value` | **Any of 8 types:** string (Example: `example`); boolean; integer; [AnswerDateRangeOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerDateRangeOut) (Example: `{"begin": "example", "end": "example"}`); [AnswerFileOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerFileOut)[] (Example: `[{"name": "example", "path": "example"}]`); [AnswerEnumItemOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerEnumItemOut)[] (Example: `[{"id": "example", "label": "example", "scores": 0.5}]`); [AnswerMatrixItemOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerMatrixItemOut)[] (Example: `[{"row": {"id": "example", "label": "example", "scores": 0.5}, "column": null}]`); [AnswerQuestionOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerQuestionOut)[][] (Example: `[[{"id": "example", "label": "example", "type": "string", "widget": "radio", "multiline": true, "multichoice": true, "is_deleted": true, "items": [{}], "scores": 0.5, "value": "example"}]]`). Answer value for the question. Example: `example` |
| `is_deleted` | **Type:** boolean — Question is deleted |
| `items` | **Any of 3 types:** [AnswerStringScoresOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerStringScoresOut)[] (Example: `[{"label": "example", "scores": 0.5}]`); [AnswerEnumItemOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerEnumItemOut)[] (Example: `[{"id": "example", "label": "example", "scores": 0.5}]`); [AnswerMatrixOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-AnswerMatrixOut) (Example: `{"rows": [{"id": "example", "label": "example", "scores": 0.5}], "columns": [null]}`). Answer options for the question. Example: `[{"label": "example", "scores": 0.5}]` |
| `multichoice` | **Type:** boolean — Enable multiple answer option selection |
| `multiline` | **Type:** boolean — Multiline text flag |
| `scores` | **Type:** number — Points for the question |
| `widget` | **All of 1 type:** [WidgetType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view#entity-WidgetType) — an enumeration (enum: `radio`, `checkbox`, `dropdown`, `stars`, `onerow`). Question display type. Example: `radio` |

**Example**

```
{
  "id": "example",
  "label": "example",
  "type": "string",
  "widget": "radio",
  "multiline": true,
  "multichoice": true,
  "is_deleted": true,
  "items": [
    {
      "label": "example",
      "scores": 0.5
    }
  ],
  "scores": 0.5,
  "value": "example"
}
```