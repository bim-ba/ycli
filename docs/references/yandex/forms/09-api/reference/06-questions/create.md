---
source: https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view
title: "Create question - Questions |"
word_count: 4842
token_estimate: 37623
extracted: "2026-05-22T18:12:14Z"
mode: quality
---

Creates a question.
The new question is added to the end of the form's question list.
After creation, it can be moved.

# 201 Created

Created

## Body

application/json

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        null
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": null
  },
  "type": "string",
  "initial": "example",
  "multiline": true,
  "hint_source": {
    "name": "example",
    "params": [
      null
    ]
  },
  "validators": [
    {}
  ],
  "has_quiz": true,
  "quiz_items": [
    {
      "label": "example",
      "correct": true,
      "scores": 0.5
    }
  ]
}
```
**Any of 2 types**

-   **QuestionOut**

    **Type**: [QuestionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionOut)

    Question data

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {}
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "string",
      "initial": "example",
      "multiline": true,
      "hint_source": {
        "name": "example",
        "params": [
          {}
        ]
      },
      "validators": [
        {
          "type": "required"
        }
      ],
      "has_quiz": true,
      "quiz_items": [
        {
          "label": "example",
          "correct": true,
          "scores": 0.5
        }
      ]
    }
    ```

-   **QuestionSeriesOut**

    **Type**: [QuestionSeriesOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionSeriesOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "series",
      "items": [
        {
          "id": 0,
          "label": "example",
          "comment": "example",
          "placeholder": "example",
          "slug": "example",
          "hidden": false,
          "conditions": [
            null
          ],
          "image": null,
          "type": "string",
          "initial": "example",
          "multiline": true,
          "hint_source": null,
          "validators": [
            null
          ],
          "has_quiz": true,
          "quiz_items": [
            {}
          ]
        }
      ]
    }
    ```

## OperatorType

An enumeration.

**Type**: string

*Enum:* `and`, `or`

## ConditionItemType

An enumeration.

**Type**: string

*Enum:* `question`, `language`, `origin`

## ConditionType

An enumeration.

**Type**: string

*Enum:* `eq`, `neq`, `lt`, `gt`

## ConditionItemOut

| Name | Description |
|------|-------------|
| *condition* | **All of 1 type**: **ConditionType** **Type**: [ConditionType](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionType) An enumeration. *Enum:* `eq`, `neq`, `lt`, `gt` Comparison operator *Example:* `eq` |
| *operator* | **All of 1 type**: **OperatorType** **Type**: [OperatorType](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-OperatorType) An enumeration. *Enum:* `and`, `or` Operator between conditions *Example:* `and` |
| *type* | **All of 1 type**: **ConditionItemType** **Type**: [ConditionItemType](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionItemType) An enumeration. *Enum:* `question`, `language`, `origin` Condition type *Example:* `question` |
| *question* | **Type**: string Question slug *Example:* `example` |
| *value* | **Type**: string Condition value *Max length:* `100` *Example:* `example` |

**Example**

```
{
  "operator": "and",
  "type": "question",
  "condition": "eq",
  "question": "example",
  "value": "example"
}
```

## ConditionOut

- *id* — **Type**: integer Condition group ID

- *operator* — **Type**: string Condition group operator *Example:* `example`

- *items* — **Type**: [ConditionItemOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionItemOut)[] List of conditions in the group **Example**:

  ```
  [
    {
      "operator": "and",
      "type": "question",
      "condition": "eq",
      "question": "example",
      "value": "example"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "operator": "example",
  "items": [
    {
      "operator": "and",
      "type": "question",
      "condition": "eq",
      "question": "example",
      "value": "example"
    }
  ]
}
```

## FileCheckStatusType

An enumeration.

**Type**: string

*Enum:* `check`, `ready`, `infected`, `error`, `deleted`

## ImageOut

- *links* — **Type**: Links: - *[additional]* — **Type**: string<uri> *Min length:* `1` *Max length:* `2083` *Example:* `https://example.com` List of links to different image sizes **Example**:

  ```
  {}
  ```

- *check_status* — **All of 1 type**: **FileCheckStatusType** **Type**: [FileCheckStatusType](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-FileCheckStatusType) An enumeration. *Enum:* `check`, `ready`, `infected`, `error`, `deleted` Image upload status *Example:* `check`

- *id* — **Type**: integer Image ID

- *name* — **Type**: string Original image file name *Example:* `example`

**Example**

```
{
  "id": 0,
  "links": {},
  "name": "example",
  "check_status": "check"
}
```

## QuestionQuizItemOut

| Name | Description |
|------|-------------|
| *correct* | **Type**: boolean Correct answer option flag |
| *label* | **Type**: string Answer option text *Example:* `example` |
| *scores* | **Type**: number Points for the answer |

**Example**

```
{
  "label": "example",
  "correct": true,
  "scores": 0.5
}
```

## QuestionStringOut

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *multiline* — **Type**: boolean Multiline text flag

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *has_quiz* — **Type**: boolean Test presence flag

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *hint_source* — **All of 1 type**: **QuestionHintSource** **Type**: [QuestionHintSource](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionHintSource) **Example**: Question hint source **Example**:

  ```
  {
    "name": "example",
    "params": [
      {
        "type": "example",
        "value": "example"
      }
    ]
  }
  ```

  ```
  {
    "name": "example",
    "params": [
      {
        "type": "example",
        "value": "example"
      }
    ]
  }
  ```

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *initial* — **Type**: string Initial value *Example:* `example`

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *quiz_items* — **Type**: [QuestionQuizItemOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionQuizItemOut)[] List of test answer options **Example**:

  ```
  [
    {
      "label": "example",
      "correct": true,
      "scores": 0.5
    }
  ]
  ```

- *type* — **Type**: string Question type *Default:* `string` *Const:* `string`

- *validators* — **Type**: array: **Any of 11 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationMinStringOut** **Type**: [ValidationMinStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMinStringOut) **Example**:, **ValidationMaxStringOut** **Type**: [ValidationMaxStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMaxStringOut) **Example**:, **ValidationEmailStringOut** **Type**: [ValidationEmailStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationEmailStringOut) **Example**:, **ValidationUrlStringOut** **Type**: [ValidationUrlStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationUrlStringOut) **Example**:, **ValidationPhoneStringOut** **Type**: [ValidationPhoneStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationPhoneStringOut) **Example**:, **ValidationInnStringOut** **Type**: [ValidationInnStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationInnStringOut) **Example**:, **ValidationDecimalStringOut** **Type**: [ValidationDecimalStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationDecimalStringOut) **Example**:, **ValidationRussianStringOut** **Type**: [ValidationRussianStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRussianStringOut) **Example**:, **ValidationRegexpStringOut** **Type**: [ValidationRegexpStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRegexpStringOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "min",
    "value": 0
  }
  ```

  ```
  {
    "type": "max",
    "value": 0
  }
  ```

  ```
  {
    "type": "email"
  }
  ```

  ```
  {
    "type": "url"
  }
  ```

  ```
  {
    "type": "phone"
  }
  ```

  ```
  {
    "type": "inn"
  }
  ```

  ```
  {
    "type": "decimal"
  }
  ```

  ```
  {
    "type": "russian"
  }
  ```

  ```
  {
    "type": "regexp",
    "value": "example"
  }
  ```

  ```
  {
    "type": "external"
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "string",
  "initial": "example",
  "multiline": true,
  "hint_source": {
    "name": "example",
    "params": [
      {
        "type": "example",
        "value": "example"
      }
    ]
  },
  "validators": [
    {
      "type": "required"
    }
  ],
  "has_quiz": true,
  "quiz_items": [
    {
      "label": "example",
      "correct": true,
      "scores": 0.5
    }
  ]
}
```

## QuestionBooleanOut

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *initial* — **Type**: boolean Initial value

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `boolean` *Const:* `boolean`

- *validators* — **Type**: array: **Any of 2 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "external"
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "boolean",
  "initial": true,
  "validators": [
    {
      "type": "required"
    }
  ]
}
```

## QuestionIntegerOut

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *initial* — **Type**: integer Initial value

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `integer` *Const:* `integer`

- *validators* — **Type**: array: **Any of 4 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationMinIntegerOut** **Type**: [ValidationMinIntegerOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMinIntegerOut) **Example**:, **ValidationMaxIntegerOut** **Type**: [ValidationMaxIntegerOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMaxIntegerOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "min",
    "value": 0
  }
  ```

  ```
  {
    "type": "max",
    "value": 0
  }
  ```

  ```
  {
    "type": "external"
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "integer",
  "initial": 0,
  "validators": [
    {
      "type": "required"
    }
  ]
}
```

## QuestionFileOut

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `file` *Const:* `file`

- *validators* — **Type**: array: **Any of 4 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationMaxSizeFileOut** **Type**: [ValidationMaxSizeFileOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMaxSizeFileOut) **Example**:, **ValidationMaxCountFileOut** **Type**: [ValidationMaxCountFileOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMaxCountFileOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "size",
    "value": 20
  }
  ```

  ```
  {
    "type": "count",
    "value": 20
  }
  ```

  ```
  {
    "type": "external"
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "file",
  "validators": [
    {
      "type": "required"
    }
  ]
}
```

- *header* — **Type**: boolean Header flag

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `comment` *Const:* `comment`

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "comment",
  "header": true
}
```

## QuestionDateOut

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `date` *Const:* `date`

- *validators* — **Type**: array: **Any of 4 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationMinDateOut** **Type**: [ValidationMinDateOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMinDateOut) **Example**:, **ValidationMaxDateOut** **Type**: [ValidationMaxDateOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMaxDateOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "min",
    "value": "2025-01-01"
  }
  ```

  ```
  {
    "type": "max",
    "value": "2025-01-01"
  }
  ```

  ```
  {
    "type": "external"
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "date",
  "validators": [
    {
      "type": "required"
    }
  ]
}
```

## QuestionDateRangeOut

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `daterange` *Const:* `daterange`

- *validators* — **Type**: array: **Any of 4 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationMinDateOut** **Type**: [ValidationMinDateOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMinDateOut) **Example**:, **ValidationMaxDateOut** **Type**: [ValidationMaxDateOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMaxDateOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "min",
    "value": "2025-01-01"
  }
  ```

  ```
  {
    "type": "max",
    "value": "2025-01-01"
  }
  ```

  ```
  {
    "type": "external"
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "daterange",
  "validators": [
    {
      "type": "required"
    }
  ]
}
```

## QuestionPaymentOut

- *account_id* — **Type**: string Wallet number for payment *Example:* `example`

- *fixed* — **Type**: boolean Allow changing the payment amount

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *initial* — **Type**: integer Initial value

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `payment` *Const:* `payment`

- *validators* — **Type**: array: **Any of 3 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationMinPaymentOut** **Type**: [ValidationMinPaymentOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMinPaymentOut) **Example**:, **ValidationMaxPaymentOut** **Type**: [ValidationMaxPaymentOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationMaxPaymentOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "min",
    "value": 0
  }
  ```

  ```
  {
    "type": "max",
    "value": 0
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "payment",
  "fixed": true,
  "account_id": "example",
  "initial": 0,
  "validators": [
    {
      "type": "required"
    }
  ]
}
```

## QuestionEnumOut

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *has_quiz* — **Type**: boolean Test presence flag

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *initial* — **Type**: [QuestionEnumItemIn](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionEnumItemIn)[] Initial value **Example**:

  ```
  [
    {
      "id": 0,
      "slug": "example",
      "label": "",
      "hidden": true,
      "image": {
        "id": 0,
        "links": {},
        "name": "example"
      },
      "correct": true,
      "scores": 0.5
    }
  ]
  ```

- *items* — **Type**: [QuestionEnumItemIn](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionEnumItemIn)[] List of items **Example**:

  ```
  [
    {
      "id": 0,
      "slug": "example",
      "label": "",
      "hidden": true,
      "image": {
        "id": 0,
        "links": {},
        "name": "example"
      },
      "correct": true,
      "scores": 0.5
    }
  ]
  ```

- *modify_choices* — **All of 1 type**: **QuestionModifyChoicesType** **Type**: [QuestionModifyChoicesType](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionModifyChoicesType) An enumeration. *Enum:* ``, `natural`, `sort`, `shuffle` Item sort type *Example:* ``

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *show_first* — **Type**: boolean Whether to show the first value (for dropdown)

- *type* — **Type**: string Question type *Default:* `enum` *Const:* `enum`

- *validators* — **Type**: array: **Any of 3 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationEnumSingleOut** **Type**: [ValidationEnumSingleOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationEnumSingleOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "single"
  }
  ```

  ```
  {
    "type": "external"
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

- *widget* — **All of 1 type**: **WidgetType** **Type**: [WidgetType](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-WidgetType) An enumeration. *Enum:* `radio`, `checkbox`, `dropdown`, `stars`, `onerow` Question display type *Default:* `radio`

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "enum",
  "widget": "radio",
  "items": [
    {
      "id": 0,
      "slug": "example",
      "label": "",
      "hidden": true,
      "image": {
        "id": 0,
        "links": {},
        "name": "example"
      },
      "correct": true,
      "scores": 0.5
    }
  ],
  "initial": [
    null
  ],
  "modify_choices": "",
  "validators": [
    {
      "type": "required"
    }
  ],
  "show_first": true,
  "has_quiz": true
}
```

## QuestionSuggestOut

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *multichoice* — **Type**: boolean Enable multiple choice

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *data_source* — **Type**: [QuestionDataSource](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionDataSource) **Example**:

  ```
  {
    "name": "example",
    "params": [
      {
        "type": "example",
        "value": "example"
      }
    ]
  }
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `suggest` *Const:* `suggest`

- *validators* — **Type**: array: **Any of 2 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "external"
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "suggest",
  "data_source": {
    "name": "example",
    "params": [
      {
        "type": "example",
        "value": "example"
      }
    ]
  },
  "multichoice": true,
  "validators": [
    {
      "type": "required"
    }
  ]
}
```

## QuestionMatrixRowOut

| Name | Description |
|------|-------------|
| *id* | **Type**: integer Scale evaluation item ID |
| *label* | **Type**: string Scale evaluation item text *Example:* `example` |
| *slug* | **Type**: string Scale evaluation item slug *Example:* `example` |

**Example**

```
{
  "id": 0,
  "slug": "example",
  "label": "example"
}
```

## QuestionMatrixOut

- *columns* — **Type**: [QuestionMatrixRowOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionMatrixRowOut)[] List of columns **Example**:

  ```
  [
    {
      "id": 0,
      "slug": "example",
      "label": "example"
    }
  ]
  ```

- *id* — **Type**: integer Question ID

- *label* — **Type**: string Question label *Example:* `example`

- *rows* — **Type**: [QuestionMatrixRowOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionMatrixRowOut)[] List of rows **Example**:

  ```
  [
    {
      "id": 0,
      "slug": "example",
      "label": "example"
    }
  ]
  ```

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `matrix` *Const:* `matrix`

- *validators* — **Type**: array: **Any of 2 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationRequiredOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

  ```
  {
    "type": "required"
  }
  ```

  ```
  {
    "type": "external"
  }
  ```

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "matrix",
  "rows": [
    {
      "id": 0,
      "slug": "example",
      "label": "example"
    }
  ],
  "columns": [
    null
  ],
  "validators": [
    {
      "type": "required"
    }
  ]
}
```

## QuestionOut

Question data

**Any of 11 types**

-   **QuestionStringOut**

    **Type**: [QuestionStringOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionStringOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "string",
      "initial": "example",
      "multiline": true,
      "hint_source": {
        "name": "example",
        "params": [
          {
            "type": "example",
            "value": "example"
          }
        ]
      },
      "validators": [
        {
          "type": "required"
        }
      ],
      "has_quiz": true,
      "quiz_items": [
        {
          "label": "example",
          "correct": true,
          "scores": 0.5
        }
      ]
    }
    ```

-   **QuestionBooleanOut**

    **Type**: [QuestionBooleanOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionBooleanOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "boolean",
      "initial": true,
      "validators": [
        {
          "type": "required"
        }
      ]
    }
    ```

-   **QuestionIntegerOut**

    **Type**: [QuestionIntegerOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionIntegerOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "integer",
      "initial": 0,
      "validators": [
        {
          "type": "required"
        }
      ]
    }
    ```

-   **QuestionFileOut**

    **Type**: [QuestionFileOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionFileOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "file",
      "validators": [
        {
          "type": "required"
        }
      ]
    }
    ```

-   **QuestionCommentOut**

    **Type**: [QuestionCommentOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionCommentOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "comment",
      "header": true
    }
    ```

-   **QuestionDateOut**

    **Type**: [QuestionDateOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionDateOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "date",
      "validators": [
        {
          "type": "required"
        }
      ]
    }
    ```

-   **QuestionDateRangeOut**

    **Type**: [QuestionDateRangeOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionDateRangeOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "daterange",
      "validators": [
        {
          "type": "required"
        }
      ]
    }
    ```

-   **QuestionPaymentOut**

    **Type**: [QuestionPaymentOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionPaymentOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "payment",
      "fixed": true,
      "account_id": "example",
      "initial": 0,
      "validators": [
        {
          "type": "required"
        }
      ]
    }
    ```

-   **QuestionEnumOut**

    **Type**: [QuestionEnumOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionEnumOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "enum",
      "widget": "radio",
      "items": [
        {
          "id": 0,
          "slug": "example",
          "label": "",
          "hidden": true,
          "image": {
            "id": 0,
            "links": {},
            "name": "example"
          },
          "correct": true,
          "scores": 0.5
        }
      ],
      "initial": [
        null
      ],
      "modify_choices": "",
      "validators": [
        {
          "type": "required"
        }
      ],
      "show_first": true,
      "has_quiz": true
    }
    ```

-   **QuestionSuggestOut**

    **Type**: [QuestionSuggestOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionSuggestOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "suggest",
      "data_source": {
        "name": "example",
        "params": [
          {
            "type": "example",
            "value": "example"
          }
        ]
      },
      "multichoice": true,
      "validators": [
        {
          "type": "required"
        }
      ]
    }
    ```

-   **QuestionMatrixOut**

    **Type**: [QuestionMatrixOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionMatrixOut)

    **Example**

    ```
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            {
              "operator": null,
              "type": null,
              "condition": null,
              "question": "example",
              "value": "example"
            }
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      },
      "type": "matrix",
      "rows": [
        {
          "id": 0,
          "slug": "example",
          "label": "example"
        }
      ],
      "columns": [
        null
      ],
      "validators": [
        {
          "type": "required"
        }
      ]
    }
    ```
**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {}
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "string",
  "initial": "example",
  "multiline": true,
  "hint_source": {
    "name": "example",
    "params": [
      {}
    ]
  },
  "validators": [
    {
      "type": "required"
    }
  ],
  "has_quiz": true,
  "quiz_items": [
    {
      "label": "example",
      "correct": true,
      "scores": 0.5
    }
  ]
}
```

## QuestionSeriesOut

- *id* — **Type**: integer Question ID

- *items* — **Type**: [QuestionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-QuestionOut)[] List of questions in the series **Example**:

  ```
  [
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        {
          "id": 0,
          "operator": "example",
          "items": [
            null
          ]
        }
      ],
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": null
      },
      "type": "string",
      "initial": "example",
      "multiline": true,
      "hint_source": {
        "name": "example",
        "params": [
          null
        ]
      },
      "validators": [
        {}
      ],
      "has_quiz": true,
      "quiz_items": [
        {
          "label": "example",
          "correct": true,
          "scores": 0.5
        }
      ]
    }
  ]
  ```

- *label* — **Type**: string Question label *Example:* `example`

- *slug* — **Type**: string Question slug *Example:* `example`

- *comment* — **Type**: string Question hint *Example:* `example`

- *conditions* — **Type**: [ConditionOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ConditionOut)[] Conditions for the question **Example**:

  ```
  [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": "and",
          "type": "question",
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Hidden question flag *Default:* `false`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/questions/events_v1_views_questions_create_question_view#entity-ImageOut) **Example**: Question image **Example**:

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

  ```
  {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
  ```

- *placeholder* — **Type**: string Placeholder text for the question *Example:* `example`

- *type* — **Type**: string Question type *Default:* `series` *Const:* `series`

**Example**

```
{
  "id": 0,
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "slug": "example",
  "hidden": false,
  "conditions": [
    {
      "id": 0,
      "operator": "example",
      "items": [
        {
          "operator": null,
          "type": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "type": "series",
  "items": [
    {
      "id": 0,
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "slug": "example",
      "hidden": false,
      "conditions": [
        null
      ],
      "image": null,
      "type": "string",
      "initial": "example",
      "multiline": true,
      "hint_source": null,
      "validators": [
        null
      ],
      "has_quiz": true,
      "quiz_items": [
        {}
      ]
    }
  ]
}
```