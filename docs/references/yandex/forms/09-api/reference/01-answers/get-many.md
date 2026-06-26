---
source: https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view
title: "Get answers - Answers |"
word_count: 1241
token_estimate: 9248
extracted: "2026-05-22T18:07:55Z"
mode: quality
---

Returns answer data.
Supports paginated output.

Parameters:

-   **survey\_id**: form ID
-   **use\_slugs**: replace numeric question and answer option IDs with slugs (default: numeric IDs)
-   **date\_from**: start date of the period for retrieving answers
-   **date\_to**: end date of the period for retrieving answers
-   **format**: answer output format; answers can be output in internal representation
-   **ordering**: answer sorting, newest first by default
-   **page\_size**: maximum number of objects per page in the output
-   **id**: service ID for paginated output

Example of raw format for answer output:

```
    {
      "answers": [
        {
          "id": 23344738,  // answer ID
          "created": "2025-02-14T09:15:17Z",  // answer creation date
          "uid": "1120000000039962",  // user passport uid
          "data": {
            "id-text": {  // question ID or its slug (when using use_slugs)
              "value": "yet another text value"  // text field
            },
            "id-integer": {
              "value": 13  // integer value
            },
            "id-boolean": {
              "value": false  // boolean value
            },
            "id-radio": {
              "value": [
                {
                  "key": "id-option2",  // answer option ID (slug)
                  "slug": "id-option2",
                  "text": "Option2"
                }
              ]
            }
          }
        }
      ]
    }
```

# Request

GET

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/answers
```

## Path parameters

| Name | Description |
|------|-------------|
| `survey_id` | **Type:** string. Pattern: `^[a-fA-F\d]{24}$` |

## Query parameters

| Name | Description |
|------|-------------|
| `date_from` | **Type:** string\<date-time\> |
| `date_to` | **Type:** string\<date-time\> |
| `format` | **All of:** AnswerFormatType — **Type:** string, an enumeration (enum: `default`, `raw`). Default: `default` |
| `id` | **Type:** integer |
| `ordering` | **All of:** OrderingType — **Type:** string, an enumeration (enum: `asc`, `desc`). Default: `desc` |
| `page_size` | **Type:** integer. Default: `25` |
| `questions` | **Type:** string |
| `use_slugs` | **Type:** boolean. Default: `false` |

# Responses

# 200 OK

OK

## Body

application/json

```
{
  "columns": [
    {
      "id": 0,
      "slug": "example",
      "type": "string",
      "text": "example",
      "has_scores": true,
      "rows": [
        null
      ]
    }
  ],
  "answers": [
    {
      "id": 0,
      "created": "example",
      "scores": 0.5,
      "total_scores": 0.5,
      "data": [
        {}
      ]
    }
  ],
  "next": {
    "next_url": "example"
  }
}
```
**Any of 2 types**

-   **AnswersOut**

    **Type**: [AnswersOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-AnswersOut)

    **Example**

    ```
    {
      "columns": [
        {
          "id": 0,
          "slug": "example",
          "type": "string",
          "text": "example",
          "has_scores": true,
          "rows": [
            "example"
          ]
        }
      ],
      "answers": [
        {
          "id": 0,
          "created": "example",
          "scores": 0.5,
          "total_scores": 0.5,
          "data": [
            {
              "value": null,
              "scores": 0.5
            }
          ]
        }
      ],
      "next": {
        "next_url": "example"
      }
    }
    ```

-   **RawAnswersOut**

    **Type**: [RawAnswersOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-RawAnswersOut)

    **Example**

    ```
    {
      "answers": [
        {
          "id": 0,
          "created": "example",
          "uid": "example",
          "quiz": {
            "total_scores": 0.5,
            "scores": 0.5,
            "question_count": 0,
            "title": "example",
            "description": "example",
            "image_path": "example",
            "check_status": "example"
          },
          "data": [
            {}
          ]
        }
      ],
      "next": {
        "next_url": "example"
      }
    }
    ```

## QuestionType

An enumeration.

**Type**: string

*Enum:* `string`, `boolean`, `integer`, `date`, `daterange`, `file`, `radio`, `checkbox`, `dropdown`, `stars`, `onerow`, `matrix`, `suggest`, `comment`, `payment`, `captcha`, `series`, `layout`, `enum`

## AnswerColumnOut

| Name | Description |
|------|-------------|
| `has_scores` | **Type:** boolean |
| `id` | **Type:** integer |
| `slug` | **Type:** string. Example: `example` |
| `text` | **Type:** string. Example: `example` |
| `type` | **Type:** [QuestionType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-QuestionType) — an enumeration (enum: `string`, `boolean`, `integer`, `date`, `daterange`, `file`, `radio`, `checkbox`, `dropdown`, `stars`, `onerow`, `matrix`, `suggest`, `comment`, `payment`, `captcha`, `series`, `layout`, `enum`) |
| `rows` | **Type:** string[]. Example: `["example"]` |

**Example**

```
{
  "id": 0,
  "slug": "example",
  "type": "string",
  "text": "example",
  "has_scores": true,
  "rows": [
    "example"
  ]
}
```

## AnswerColumnSeriesOut

| Name | Description |
|------|-------------|
| `depth` | **Type:** integer |
| `has_scores` | **Type:** boolean |
| `id` | **Type:** integer |
| `items` | **Type:** [AnswerColumnOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-AnswerColumnOut)[]. Example: `[{"id": 0, "slug": "example", "type": "string", "text": "example", "has_scores": true, "rows": ["example"]}]` |
| `slug` | **Type:** string. Example: `example` |
| `text` | **Type:** string. Example: `example` |
| `type` | **Type:** [QuestionType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-QuestionType) — an enumeration (enum: `string`, `boolean`, `integer`, `date`, `daterange`, `file`, `radio`, `checkbox`, `dropdown`, `stars`, `onerow`, `matrix`, `suggest`, `comment`, `payment`, `captcha`, `series`, `layout`, `enum`) |
| `rows` | **Type:** string[]. Example: `["example"]` |

**Example**

```
{
  "id": 0,
  "slug": "example",
  "type": "string",
  "text": "example",
  "has_scores": true,
  "rows": [
    "example"
  ],
  "items": [
    {
      "id": 0,
      "slug": "example",
      "type": null,
      "text": "example",
      "has_scores": true,
      "rows": [
        "example"
      ]
    }
  ],
  "depth": 0
}
```

## AnswerDataValueOut

| Name | Description |
|------|-------------|
| `scores` | **Type:** number |
| `value` | **Any of 4 types:** integer; boolean; string (Example: `example`); unknown[] (Example: `[null]`). Example: `0` |

**Example**

```
{
  "value": 0,
  "scores": 0.5
}
```

## AnswerDataOut

| Name | Description |
|------|-------------|
| `created` | **Type:** string. Example: `example` |
| `data` | **Type:** [AnswerDataValueOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-AnswerDataValueOut)[]. Example: `[{"value": 0, "scores": 0.5}]` |
| `id` | **Type:** integer |
| `scores` | **Type:** number |
| `total_scores` | **Type:** number |

**Example**

```
{
  "id": 0,
  "created": "example",
  "scores": 0.5,
  "total_scores": 0.5,
  "data": [
    {
      "value": 0,
      "scores": 0.5
    }
  ]
}
```

## AnswersNextOut

| Name | Description |
|------|-------------|
| `next_url` | **Type:** string. Example: `example` |

**Example**

```
{
  "next_url": "example"
}
```

## AnswersOut

| Name | Description |
|------|-------------|
| `answers` | **Type:** [AnswerDataOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-AnswerDataOut)[]. Example: `[{"id": 0, "created": "example", "scores": 0.5, "total_scores": 0.5, "data": [{"value": 0, "scores": 0.5}]}]` |
| `columns` | **Type:** array — **Any of 2 types:** [AnswerColumnOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-AnswerColumnOut) (Example: `{"id": 0, "slug": "example", "type": "string", "text": "example", "has_scores": true, "rows": ["example"]}`); [AnswerColumnSeriesOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-AnswerColumnSeriesOut) (Example: `{"id": 0, "slug": "example", "type": "string", "text": "example", "has_scores": true, "rows": ["example"], "items": [{"id": 0, "slug": "example", "type": null, "text": "example", "has_scores": true, "rows": ["example"]}], "depth": 0}`). Example: `[{"id": 0, "slug": "example", "type": "string", "text": "example", "has_scores": true, "rows": ["example"]}]` |
| `next` | **Type:** [AnswersNextOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-AnswersNextOut). Example: `{"next_url": "example"}` |

**Example**

```
{
  "columns": [
    {
      "id": 0,
      "slug": "example",
      "type": "string",
      "text": "example",
      "has_scores": true,
      "rows": [
        "example"
      ]
    }
  ],
  "answers": [
    {
      "id": 0,
      "created": "example",
      "scores": 0.5,
      "total_scores": 0.5,
      "data": [
        {
          "value": null,
          "scores": 0.5
        }
      ]
    }
  ],
  "next": {
    "next_url": "example"
  }
}
```

## FrontendAnswerQuizOut

| Name | Description |
|------|-------------|
| `scores` | **Type:** number — Points scored |
| `total_scores` | **Type:** number — Maximum number of points |
| `check_status` | **Type:** string — Image loading status. Example: `example` |
| `description` | **Type:** string — Test result text. Example: `example` |
| `image_path` | **Type:** string — Test result image. Example: `example` |
| `question_count` | **Type:** integer — Number of questions with tests |
| `title` | **Type:** string — Test result title. Example: `example` |

**Example**

```
{
  "total_scores": 0.5,
  "scores": 0.5,
  "question_count": 0,
  "title": "example",
  "description": "example",
  "image_path": "example",
  "check_status": "example"
}
```

## RawAnswerDataOut

| Name | Description |
|------|-------------|
| `created` | **Type:** string. Example: `example` |
| `data` | **Type:** object[]. Example: `[{}]` |
| `id` | **Type:** integer |
| `quiz` | **Type:** [FrontendAnswerQuizOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-FrontendAnswerQuizOut). Example: `{"total_scores": 0.5, "scores": 0.5, "question_count": 0, "title": "example", "description": "example", "image_path": "example", "check_status": "example"}` |
| `uid` | **Type:** string. Example: `example` |

**Example**

```
{
  "id": 0,
  "created": "example",
  "uid": "example",
  "quiz": {
    "total_scores": 0.5,
    "scores": 0.5,
    "question_count": 0,
    "title": "example",
    "description": "example",
    "image_path": "example",
    "check_status": "example"
  },
  "data": [
    {}
  ]
}
```

## RawAnswersOut

| Name | Description |
|------|-------------|
| `answers` | **Type:** [RawAnswerDataOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-RawAnswerDataOut)[]. Example: `[{"id": 0, "created": "example", "uid": "example", "quiz": {"total_scores": 0.5, "scores": 0.5, "question_count": 0, "title": "example", "description": "example", "image_path": "example", "check_status": "example"}, "data": [{}]}]` |
| `next` | **Type:** [AnswersNextOut](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answers_view#entity-AnswersNextOut). Example: `{"next_url": "example"}` |

**Example**

```
{
  "answers": [
    {
      "id": 0,
      "created": "example",
      "uid": "example",
      "quiz": {
        "total_scores": 0.5,
        "scores": 0.5,
        "question_count": 0,
        "title": "example",
        "description": "example",
        "image_path": "example",
        "check_status": "example"
      },
      "data": [
        {}
      ]
    }
  ],
  "next": {
    "next_url": "example"
  }
}
```