---
source: https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view
title: "Get form settings for filling - Form Filling |"
word_count: 6899
token_estimate: 66501
extracted: "2026-05-22T18:10:42Z"
mode: quality
---

Returns form settings that affect how the form is filled out.
The request checks whether the form is published and other settings that affect form filling.

Parameters:

-   **survey**: form ID, its slug, or a combination of the form ID and a verification key.
-   **key**: key for filling out the form. For more information, see [Generate a personal link](https://yandex.com/support/forms/publish#personal-link)

# Request

GET

```
https://api.forms.yandex.net/v1/surveys/{survey}/form
```

## Path parameters

| Name | Description |
|------|-------------|
| *survey* | **Type**: string *Example:* `` |

## Query parameters

| Name | Description |
|------|-------------|
| *key* | **Type**: string *Example:* `` |

# Responses

# 200 OK

OK

## Body

application/json

```
{
  "id": "example",
  "name": "example",
  "metric": {
    "form": 0,
    "group": 0
  },
  "teaser": true,
  "footer": true,
  "iframe": true,
  "styles": {
    "custom": {},
    "images": {
      "page": null,
      "form": null
    }
  },
  "texts": {
    "submit": "example",
    "back": "example",
    "next": "example"
  },
  "org": {
    "dir_id": "example",
    "collab_id": "example"
  },
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "pages": [
    {
      "conditions": [
        null
      ],
      "items": [
        {}
      ]
    }
  ],
  "values": {}
}
```

- *id* — **Type**: string Form ID *Pattern:* `^[a-fA-F\d]{24}$` *Example:* `example`

- *pages* — **Type**: [FrontendPageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendPageOut)[] List of pages in the form **Example**:

  ```
  [
    {
      "conditions": [
        {
          "operator": "and",
          "items": [
            {}
          ]
        }
      ],
      "items": [
        {
          "id": "example",
          "label": "example",
          "comment": "example",
          "placeholder": "example",
          "hidden": true,
          "conditions": [
            null
          ],
          "image": null,
          "type": "boolean",
          "validations": [
            null
          ]
        }
      ]
    }
  ]
  ```

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Submit button display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *footer* — **Type**: boolean Show footer

- *iframe* — **Type**: boolean Show only in iframe

- *metric* — **All of 1 type**: **FrontendMetricOut** **Type**: [FrontendMetricOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendMetricOut) **Example**: Metrica counters **Example**:

  ```
  {
    "form": 0,
    "group": 0
  }
  ```

  ```
  {
    "form": 0,
    "group": 0
  }
  ```

- *name* — **Type**: string Form name *Example:* `example`

- *org* — **All of 1 type**: **FrontendOrganizationOut** **Type**: [FrontendOrganizationOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendOrganizationOut) **Example**: Organization containing the form **Example**:

  ```
  {
    "dir_id": "example",
    "collab_id": "example"
  }
  ```

  ```
  {
    "dir_id": "example",
    "collab_id": "example"
  }
  ```

- *styles* — **All of 1 type**: **FrontendStylesOut** **Type**: [FrontendStylesOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendStylesOut) **Example**: Styles for form design **Example**:

  ```
  {
    "custom": {},
    "images": {
      "page": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": null
      },
      "form": null
    }
  }
  ```

  ```
  {
    "custom": {},
    "images": {
      "page": null,
      "form": null
    }
  }
  ```

- *teaser* — **Type**: boolean Show teaser

- *texts* — **All of 1 type**: **FrontendTextsOut** **Type**: [FrontendTextsOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendTextsOut) **Example**: Button texts on the form **Example**:

  ```
  {
    "submit": "example",
    "back": "example",
    "next": "example"
  }
  ```

  ```
  {
    "submit": "example",
    "back": "example",
    "next": "example"
  }
  ```

- *values* — **Type**: Values: - *[additional]* — **Any of 8 types**: **Type**: boolean, **Type**: integer, **Type**: string *Example:* `example`, **Type**: string[] **Example**:, **Type**: [FrontendMatrixItemOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendMatrixItemOut)[] **Example**:, **Type**: [FrontendFileItemOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendFileItemOut)[] **Example**:, **FrontendDateRangeOut** **Type**: [FrontendDateRangeOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendDateRangeOut) **Example**:, **Type**: object[] - *[additional]* — **Any of 7 types**:,,,,,, *Example:* `true` **Example**:, **Type**: boolean, **Type**: integer, **Type**: string *Example:* `example`, **Type**: string[] **Example**:, **Type**: [FrontendMatrixItemOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendMatrixItemOut)[] **Example**:, **Type**: [FrontendFileItemOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendFileItemOut)[] **Example**:, **FrontendDateRangeOut** **Type**: [FrontendDateRangeOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendDateRangeOut) **Example**: *Example:* `true` Data for filling in question fields **Example**:

  ```
  [ "example"
  ]
  ```

  ```
  [ { "row": "example", "column": "example" }
  ]
  ```

  ```
  [ { "name": "example", "path": "example" }
  ]
  ```

  ```
  { "begin": "example", "end": "example"
  }
  ```

  ```
  [ {}
  ]
  ```

  ```
  [ "example"
  ]
  ```

  ```
  [ { "row": "example", "column": "example" }
  ]
  ```

  ```
  [ { "name": "example", "path": "example" }
  ]
  ```

  ```
  { "begin": "example", "end": "example"
  }
  ```

  ```
  {}
  ```

## FrontendMetricOut

| Name | Description |
|------|-------------|
| *form* | **Type**: integer Form Metrica counter ID |
| *group* | **Type**: integer Form group Metrica counter ID |

**Example**

```
{
  "form": 0,
  "group": 0
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

- *check_status* — **All of 1 type**: **FileCheckStatusType** **Type**: [FileCheckStatusType](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FileCheckStatusType) An enumeration. *Enum:* `check`, `ready`, `infected`, `error`, `deleted` Image upload status *Example:* `check`

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

## FrontendStylesImagesOut

- *form* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Background image for the form backdrop **Example**:

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

- *page* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Background image behind the text **Example**:

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

**Example**

```
{
  "page": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  },
  "form": null
}
```

## FrontendStylesOut

- *custom* — **Type**: object Custom style settings for the form **Example**:

  ```
  {}
  ```

- *images* — **All of 1 type**: **FrontendStylesImagesOut** **Type**: [FrontendStylesImagesOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendStylesImagesOut) **Example**: Images for form styling **Example**:

  ```
  {
    "page": {
      "id": 0,
      "links": {},
      "name": "example",
      "check_status": "check"
    },
    "form": null
  }
  ```

  ```
  {
    "page": {
      "id": 0,
      "links": {},
      "name": "example",
      "check_status": "check"
    },
    "form": null
  }
  ```

**Example**

```
{
  "custom": {},
  "images": {
    "page": {
      "id": 0,
      "links": {},
      "name": "example",
      "check_status": null
    },
    "form": null
  }
}
```

## FrontendTextsOut

| Name | Description |
|------|-------------|
| *back* | **Type**: string Text on the Back button *Example:* `example` |
| *next* | **Type**: string Text on the Next button *Example:* `example` |
| *submit* | **Type**: string Text on the Submit button *Example:* `example` |

**Example**

```
{
  "submit": "example",
  "back": "example",
  "next": "example"
}
```

## FrontendOrganizationOut

| Name | Description |
|------|-------------|
| *collab_id* | **Type**: string Organization ID in collab *Example:* `example` |
| *dir_id* | **Type**: string Organization ID in the directory *Example:* `example` |

**Example**

```
{
  "dir_id": "example",
  "collab_id": "example"
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

## FrontendConditionItemOut

| Name | Description |
|------|-------------|
| *condition* | **All of 1 type**: **ConditionType** **Type**: [ConditionType](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ConditionType) An enumeration. *Enum:* `eq`, `neq`, `lt`, `gt` Condition type *Example:* `eq` |
| *operator* | **All of 1 type**: **OperatorType** **Type**: [OperatorType](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-OperatorType) An enumeration. *Enum:* `and`, `or` Operator type *Example:* `and` |
| *type* | **All of 1 type**: **ConditionItemType** **Type**: [ConditionItemType](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ConditionItemType) An enumeration. *Enum:* `question`, `language`, `origin` Element type *Example:* `question` |
| *value* | **Type**: string Value for comparison *Example:* `example` |
| *question* | **Type**: string Question slug *Example:* `example` |

**Example**

```
{
  "type": "question",
  "operator": "and",
  "condition": "eq",
  "question": "example",
  "value": "example"
}
```

## FrontendConditionOut

- *items* — **Type**: [FrontendConditionItemOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionItemOut)[] List of conditions **Example**:

  ```
  [
    {
      "type": "question",
      "operator": "and",
      "condition": "eq",
      "question": "example",
      "value": "example"
    }
  ]
  ```

- *operator* — **All of 1 type**: **OperatorType** **Type**: [OperatorType](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-OperatorType) An enumeration. *Enum:* `and`, `or` Operator type *Example:* `and`

**Example**

```
{
  "operator": "and",
  "items": [
    {
      "type": "question",
      "operator": null,
      "condition": "eq",
      "question": "example",
      "value": "example"
    }
  ]
}
```

## ValidationRequiredOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Required for filling *Const:* `required` *Example:* `example` |

**Example**

```
{
  "type": "required"
}
```

## ValidationExternalOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Validation via external endpoint *Const:* `external` *Example:* `example` |

**Example**

```
{
  "type": "external"
}
```

## FrontendBooleanQuestionOut

- *id* — **Type**: string Question slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *type* — **Type**: string Question type *Const:* `boolean` *Example:* `example`

- *comment* — **Type**: string Question comment *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Question is hidden

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the question title **Example**:

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

- *placeholder* — **Type**: string Question placeholder *Example:* `example`

- *validations* — **Type**: array: **Any of 2 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRequiredOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

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
  "id": "example",
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "hidden": true,
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
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
  "validations": [
    {
      "type": "required"
    }
  ]
}
```

## ValidationMinIntegerOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Minimum value *Const:* `min` *Example:* `example` |
| *value* | **Type**: integer Validation value |

**Example**

```
{
  "type": "min",
  "value": 0
}
```

## ValidationMaxIntegerOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Maximum value *Const:* `max` *Example:* `example` |
| *value* | **Type**: integer Validation value |

**Example**

```
{
  "type": "max",
  "value": 0
}
```

## FrontendIntegerQuestionOut

- *id* — **Type**: string Question slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *type* — **Type**: string Question type *Const:* `integer` *Example:* `example`

- *comment* — **Type**: string Question comment *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Question is hidden

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the question title **Example**:

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

- *placeholder* — **Type**: string Question placeholder *Example:* `example`

- *validations* — **Type**: array: **Any of 4 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRequiredOut) **Example**:, **ValidationMinIntegerOut** **Type**: [ValidationMinIntegerOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMinIntegerOut) **Example**:, **ValidationMaxIntegerOut** **Type**: [ValidationMaxIntegerOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMaxIntegerOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

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
  "id": "example",
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "hidden": true,
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
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
  "validations": [
    {
      "type": "required"
    }
  ]
}
```

## FrontendEnumItemOut

- *id* — **Type**: string Answer option identifier *Example:* `example`

- *label* — **Type**: string Answer option name *Example:* `example`

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the answer option **Example**:

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

**Example**

```
{
  "id": "example",
  "label": "example",
  "image": {
    "id": 0,
    "links": {},
    "name": "example",
    "check_status": "check"
  }
}
```

## FrontendStringHintItemsOut

- *items* — **Type**: [FrontendEnumItemOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendEnumItemOut)[] Answer options to display in the interface **Example**:

  ```
  [
    {
      "id": "example",
      "label": "example",
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": "check"
      }
    }
  ]
  ```

**Example**

```
{
  "items": [
    {
      "id": "example",
      "label": "example",
      "image": {
        "id": 0,
        "links": {},
        "name": "example",
        "check_status": null
      }
    }
  ]
}
```

## DataSourceType

An enumeration.

**Type**: string

*Enum:* `survey_question_choice`, `survey_question_matrix_choice`, `country`, `city`, `university`, `address`, `user_email_list`, `wiki_table_source`, `gender`, `dir_user`, `dir_department`, `dir_group`

## FrontendStringHintSuggestOut

| Name | Description |
|------|-------------|
| *data_source* | **All of 1 type**: **DataSourceType** **Type**: [DataSourceType](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-DataSourceType) An enumeration. *Enum:* `survey_question_choice`, `survey_question_matrix_choice`, `country`, `city`, `university`, `address`, `user_email_list`, `wiki_table_source`, `gender`, `dir_user`, `dir_department`, `dir_group` Data source type *Example:* `survey_question_choice` |

**Example**

```
{
  "data_source": "survey_question_choice"
}
```

## ValidationMinStringOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Minimum number of characters *Const:* `min` *Example:* `example` |
| *value* | **Type**: integer Validation value |

**Example**

```
{
  "type": "min",
  "value": 0
}
```

## ValidationMaxStringOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Maximum number of characters *Const:* `max` *Example:* `example` |
| *value* | **Type**: integer Validation value |

**Example**

```
{
  "type": "max",
  "value": 0
}
```

## ValidationEmailStringOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Email validation *Const:* `email` *Example:* `example` |

**Example**

```
{
  "type": "email"
}
```

## ValidationUrlStringOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string URL validation *Const:* `url` *Example:* `example` |

**Example**

```
{
  "type": "url"
}
```

## ValidationPhoneStringOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Phone number validation *Const:* `phone` *Example:* `example` |

**Example**

```
{
  "type": "phone"
}
```

## ValidationInnStringOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string TIN (INN) validation *Const:* `inn` *Example:* `example` |

**Example**

```
{
  "type": "inn"
}
```

## ValidationDecimalStringOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Decimal number validation *Const:* `decimal` *Example:* `example` |

**Example**

```
{
  "type": "decimal"
}
```

## ValidationRussianStringOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Russian letters validation *Const:* `russian` *Example:* `example` |

**Example**

```
{
  "type": "russian"
}
```

## ValidationRegexpStringOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Regular expression validation *Const:* `regexp` *Example:* `example` |
| *value* | **Type**: string Validation value *Example:* `example` |

**Example**

```
{
  "type": "regexp",
  "value": "example"
}
```

## FrontendStringQuestionOut

- *id* — **Type**: string Question slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *type* — **Type**: string Question type *Const:* `string` *Example:* `example`

- *comment* — **Type**: string Question comment *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Question is hidden

- *hint* — **Any of 2 types**: **FrontendStringHintItemsOut** **Type**: [FrontendStringHintItemsOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendStringHintItemsOut) **Example**:, **FrontendStringHintSuggestOut** **Type**: [FrontendStringHintSuggestOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendStringHintSuggestOut) **Example**: Hint for the string question **Example**:

  ```
  {
    "items": [
      {
        "id": "example",
        "label": "example",
        "image": {
          "id": 0,
          "links": {},
          "name": "example",
          "check_status": null
        }
      }
    ]
  }
  ```

  ```
  {
    "data_source": "survey_question_choice"
  }
  ```

  ```
  {
    "items": [
      {
        "id": "example",
        "label": "example",
        "image": null
      }
    ]
  }
  ```

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the question title **Example**:

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

- *multiline* — **Type**: boolean Multiline text

- *placeholder* — **Type**: string Question placeholder *Example:* `example`

- *validations* — **Type**: array: **Any of 11 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRequiredOut) **Example**:, **ValidationMinStringOut** **Type**: [ValidationMinStringOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMinStringOut) **Example**:, **ValidationMaxStringOut** **Type**: [ValidationMaxStringOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMaxStringOut) **Example**:, **ValidationEmailStringOut** **Type**: [ValidationEmailStringOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationEmailStringOut) **Example**:, **ValidationUrlStringOut** **Type**: [ValidationUrlStringOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationUrlStringOut) **Example**:, **ValidationPhoneStringOut** **Type**: [ValidationPhoneStringOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationPhoneStringOut) **Example**:, **ValidationInnStringOut** **Type**: [ValidationInnStringOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationInnStringOut) **Example**:, **ValidationDecimalStringOut** **Type**: [ValidationDecimalStringOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationDecimalStringOut) **Example**:, **ValidationRussianStringOut** **Type**: [ValidationRussianStringOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRussianStringOut) **Example**:, **ValidationRegexpStringOut** **Type**: [ValidationRegexpStringOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRegexpStringOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

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
  "id": "example",
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "hidden": true,
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
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
  "multiline": true,
  "hint": {
    "items": [
      {
        "id": "example",
        "label": "example",
        "image": null
      }
    ]
  },
  "validations": [
    {
      "type": "required"
    }
  ]
}
```

## FrontendCaptchaQuestionOut

- *id* — **Type**: string Captcha slug *Example:* `example`

- *key* — **Type**: string Captcha verification key *Example:* `example`

- *label* — **Type**: string Text prompting the user to enter the captcha *Example:* `example`

- *mode* — **Type**: string Captcha type for frontend refresh *Example:* `example`

- *type* — **Type**: string Question type *Const:* `captcha` *Example:* `example`

- *url* — **Type**: string<uri> Captcha link *Min length:* `1` *Max length:* `2083` *Example:* `https://example.com`

- *validations* — **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRequiredOut)[] List of validators **Example**:

  ```
  [
    {
      "type": "required"
    }
  ]
  ```

- *voice_url* — **Type**: string<uri> Voice captcha link *Min length:* `1` *Max length:* `2083` *Example:* `https://example.com`

**Example**

```
{
  "id": "example",
  "type": "captcha",
  "label": "example",
  "url": "https://example.com",
  "voice_url": "https://example.com",
  "key": "example",
  "mode": "example",
  "validations": [
    {
      "type": "required"
    }
  ]
}
```

## ValidationMaxSizeFileOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Maximum file size, MB *Const:* `size` *Example:* `example` |
| *value* | **Type**: integer Validation value *Max value:* `20` |

**Example**

```
{
  "type": "size",
  "value": 20
}
```

## ValidationMaxCountFileOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Maximum number of files *Const:* `count` *Example:* `example` |
| *value* | **Type**: integer Validation value *Max value:* `20` |

**Example**

```
{
  "type": "count",
  "value": 20
}
```

## FrontendFileQuestionOut

- *id* — **Type**: string Question slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *type* — **Type**: string Question type *Const:* `file` *Example:* `example`

- *comment* — **Type**: string Question comment *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Question is hidden

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the question title **Example**:

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

- *placeholder* — **Type**: string Question placeholder *Example:* `example`

- *validations* — **Type**: array: **Any of 4 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRequiredOut) **Example**:, **ValidationMaxSizeFileOut** **Type**: [ValidationMaxSizeFileOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMaxSizeFileOut) **Example**:, **ValidationMaxCountFileOut** **Type**: [ValidationMaxCountFileOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMaxCountFileOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

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
  "id": "example",
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "hidden": true,
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
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
  "validations": [
    {
      "type": "required"
    }
  ]
}
```

## FrontendMatrixRowOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Answer matrix row identifier *Example:* `example` |
| *label* | **Type**: string Answer matrix row name *Example:* `example` |

**Example**

```
{
  "id": "example",
  "label": "example"
}
```

## FrontendMatrixColumnOut

| Name | Description |
|------|-------------|
| *id* | **Type**: string Answer matrix column identifier *Example:* `example` |
| *label* | **Type**: string Answer matrix column name *Example:* `example` |

**Example**

```
{
  "id": "example",
  "label": "example"
}
```

## FrontendMatrixQuestionOut

- *columns* — **Type**: [FrontendMatrixColumnOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendMatrixColumnOut)[] List of answer matrix columns **Example**:

  ```
  [
    {
      "id": "example",
      "label": "example"
    }
  ]
  ```

- *id* — **Type**: string Question slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *rows* — **Type**: [FrontendMatrixRowOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendMatrixRowOut)[] List of answer matrix rows **Example**:

  ```
  [
    {
      "id": "example",
      "label": "example"
    }
  ]
  ```

- *type* — **Type**: string Question type *Const:* `matrix` *Example:* `example`

- *comment* — **Type**: string Question comment *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Question is hidden

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the question title **Example**:

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

- *placeholder* — **Type**: string Question placeholder *Example:* `example`

- *validations* — **Type**: array: **Any of 2 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRequiredOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

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
  "id": "example",
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "hidden": true,
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
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
      "id": "example",
      "label": "example"
    }
  ],
  "columns": [
    {
      "id": "example",
      "label": "example"
    }
  ],
  "validations": [
    {
      "type": "required"
    }
  ]
}
```

## FrontendSuggestQuestionOut

- *data_source* — **All of 1 type**: **DataSourceType** **Type**: [DataSourceType](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-DataSourceType) An enumeration. *Enum:* `survey_question_choice`, `survey_question_matrix_choice`, `country`, `city`, `university`, `address`, `user_email_list`, `wiki_table_source`, `gender`, `dir_user`, `dir_department`, `dir_group` Data source type *Example:* `survey_question_choice`

- *id* — **Type**: string Question slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *type* — **Type**: string Question type *Const:* `suggest` *Example:* `example`

- *comment* — **Type**: string Question comment *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Question is hidden

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the question title **Example**:

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

- *multichoice* — **Type**: boolean Suggestion allows multiple selection

- *parent* — **Type**: string Question identifier for Master/Detail relationship *Example:* `example`

- *placeholder* — **Type**: string Question placeholder *Example:* `example`

- *validations* — **Type**: array: **Any of 2 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRequiredOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

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
  "id": "example",
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "hidden": true,
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
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
  "data_source": "survey_question_choice",
  "multichoice": true,
  "parent": "example",
  "validations": [
    {
      "type": "required"
    }
  ]
}
```

- *header* — **Type**: boolean Use as heading

- *id* — **Type**: string Question slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *type* — **Type**: string Question type *Const:* `comment` *Example:* `example`

- *comment* — **Type**: string Question comment *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Question is hidden

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the question title **Example**:

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

- *placeholder* — **Type**: string Question placeholder *Example:* `example`

**Example**

```
{
  "id": "example",
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "hidden": true,
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
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

## ValidationMinDateOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Minimum date *Const:* `min` *Example:* `example` |
| *value* | **Type**: string<date> Validation value *Example:* `2025-01-01` |

**Example**

```
{
  "type": "min",
  "value": "2025-01-01"
}
```

## ValidationMaxDateOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Maximum date *Const:* `max` *Example:* `example` |
| *value* | **Type**: string<date> Validation value *Example:* `2025-01-01` |

**Example**

```
{
  "type": "max",
  "value": "2025-01-01"
}
```

## FrontendDateQuestionOut

- *id* — **Type**: string Question slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *type* — **Type**: string Question type *Enum:* `date`, `daterange`

- *comment* — **Type**: string Question comment *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *hidden* — **Type**: boolean Question is hidden

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the question title **Example**:

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

- *placeholder* — **Type**: string Question placeholder *Example:* `example`

- *validations* — **Type**: array: **Any of 4 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRequiredOut) **Example**:, **ValidationMinDateOut** **Type**: [ValidationMinDateOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMinDateOut) **Example**:, **ValidationMaxDateOut** **Type**: [ValidationMaxDateOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMaxDateOut) **Example**:, **ValidationExternalOut** **Type**: [ValidationExternalOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationExternalOut) **Example**: List of validators **Example**:

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
  "id": "example",
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "hidden": true,
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
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
  "validations": [
    {
      "type": "required"
    }
  ]
}
```

## ValidationMinPaymentOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Minimum amount *Const:* `min` *Example:* `example` |
| *value* | **Type**: integer Validation value |

**Example**

```
{
  "type": "min",
  "value": 0
}
```

## ValidationMaxPaymentOut

| Name | Description |
|------|-------------|
| *type* | **Type**: string Maximum amount *Const:* `max` *Example:* `example` |
| *value* | **Type**: integer Validation value |

**Example**

```
{
  "type": "max",
  "value": 0
}
```

## FrontendPaymentQuestionOut

- *id* — **Type**: string Question slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *type* — **Type**: string Question type *Const:* `payment` *Example:* `example`

- *comment* — **Type**: string Question comment *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *fixed* — **Type**: boolean Fixed amount

- *hidden* — **Type**: boolean Question is hidden

- *image* — **All of 1 type**: **ImageOut** **Type**: [ImageOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ImageOut) **Example**: Image to display in the question title **Example**:

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

- *placeholder* — **Type**: string Question placeholder *Example:* `example`

- *validations* — **Type**: array: **Any of 3 types**: **ValidationRequiredOut** **Type**: [ValidationRequiredOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationRequiredOut) **Example**:, **ValidationMinPaymentOut** **Type**: [ValidationMinPaymentOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMinPaymentOut) **Example**:, **ValidationMaxPaymentOut** **Type**: [ValidationMaxPaymentOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-ValidationMaxPaymentOut) **Example**: List of validators **Example**:

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
  "id": "example",
  "label": "example",
  "comment": "example",
  "placeholder": "example",
  "hidden": true,
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
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
  "validations": [
    {
      "type": "required"
    }
  ]
}
```

## FrontendSeriesOut

- *id* — **Type**: string Question series slug *Example:* `example`

- *label* — **Type**: string Question text *Example:* `example`

- *type* — **Type**: string Question series type *Const:* `series` *Example:* `example`

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Question series display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *items* — **Type**: array: **Any of 10 types**: **FrontendBooleanQuestionOut** **Type**: [FrontendBooleanQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendBooleanQuestionOut) **Example**:, **FrontendIntegerQuestionOut** **Type**: [FrontendIntegerQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendIntegerQuestionOut) **Example**:, **FrontendStringQuestionOut** **Type**: [FrontendStringQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendStringQuestionOut) **Example**:, **FrontendCaptchaQuestionOut** **Type**: [FrontendCaptchaQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendCaptchaQuestionOut) **Example**:, **FrontendFileQuestionOut** **Type**: [FrontendFileQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendFileQuestionOut) **Example**:, **FrontendMatrixQuestionOut** **Type**: [FrontendMatrixQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendMatrixQuestionOut) **Example**:, **FrontendSuggestQuestionOut** **Type**: [FrontendSuggestQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendSuggestQuestionOut) **Example**:, **FrontendCommentQuestionOut** **Type**: [FrontendCommentQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendCommentQuestionOut) **Example**:, **FrontendDateQuestionOut** **Type**: [FrontendDateQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendDateQuestionOut) **Example**:, **FrontendPaymentQuestionOut** **Type**: [FrontendPaymentQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendPaymentQuestionOut) **Example**: List of questions in the series **Example**:

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "multiline": true,
    "hint": {
      "items": [
        {
          "id": "example",
          "label": "example",
          "image": null
        }
      ]
    },
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "type": "captcha",
    "label": "example",
    "url": "https://example.com",
    "voice_url": "https://example.com",
    "key": "example",
    "mode": "example",
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
        "id": "example",
        "label": "example"
      }
    ],
    "columns": [
      {
        "id": "example",
        "label": "example"
      }
    ],
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "data_source": "survey_question_choice",
    "multichoice": true,
    "parent": "example",
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  [
    {
      "id": "example",
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "hidden": true,
      "conditions": [
        {
          "operator": null,
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
      "type": "boolean",
      "validations": [
        {}
      ]
    }
  ]
  ```

**Example**

```
{
  "id": "example",
  "type": "series",
  "label": "example",
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "items": [
    {
      "id": "example",
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "hidden": true,
      "conditions": [
        null
      ],
      "image": null,
      "type": "boolean",
      "validations": [
        null
      ]
    }
  ]
}
```

## FrontendLayoutOut

- *id* — **Type**: string Question group slug *Example:* `example`

- *type* — **Type**: string Question group type *Const:* `layout` *Example:* `example`

- *items* — **Type**: array: **Any of 11 types**: **FrontendBooleanQuestionOut** **Type**: [FrontendBooleanQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendBooleanQuestionOut) **Example**:, **FrontendIntegerQuestionOut** **Type**: [FrontendIntegerQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendIntegerQuestionOut) **Example**:, **FrontendStringQuestionOut** **Type**: [FrontendStringQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendStringQuestionOut) **Example**:, **FrontendCaptchaQuestionOut** **Type**: [FrontendCaptchaQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendCaptchaQuestionOut) **Example**:, **FrontendFileQuestionOut** **Type**: [FrontendFileQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendFileQuestionOut) **Example**:, **FrontendMatrixQuestionOut** **Type**: [FrontendMatrixQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendMatrixQuestionOut) **Example**:, **FrontendSuggestQuestionOut** **Type**: [FrontendSuggestQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendSuggestQuestionOut) **Example**:, **FrontendCommentQuestionOut** **Type**: [FrontendCommentQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendCommentQuestionOut) **Example**:, **FrontendDateQuestionOut** **Type**: [FrontendDateQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendDateQuestionOut) **Example**:, **FrontendPaymentQuestionOut** **Type**: [FrontendPaymentQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendPaymentQuestionOut) **Example**:, **FrontendSeriesOut** **Type**: [FrontendSeriesOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendSeriesOut) **Example**: List of questions and series in the group **Example**:

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "multiline": true,
    "hint": {
      "items": [
        {
          "id": "example",
          "label": "example",
          "image": null
        }
      ]
    },
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "type": "captcha",
    "label": "example",
    "url": "https://example.com",
    "voice_url": "https://example.com",
    "key": "example",
    "mode": "example",
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
        "id": "example",
        "label": "example"
      }
    ],
    "columns": [
      {
        "id": "example",
        "label": "example"
      }
    ],
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "data_source": "survey_question_choice",
    "multichoice": true,
    "parent": "example",
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "type": "series",
    "label": "example",
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
            "condition": null,
            "question": "example",
            "value": "example"
          }
        ]
      }
    ],
    "items": [
      {
        "id": "example",
        "label": "example",
        "comment": "example",
        "placeholder": "example",
        "hidden": true,
        "conditions": [
          null
        ],
        "image": null,
        "type": "boolean",
        "validations": [
          null
        ]
      }
    ]
  }
  ```

  ```
  [
    {
      "id": "example",
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "hidden": true,
      "conditions": [
        {
          "operator": null,
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
      "type": "boolean",
      "validations": [
        {}
      ]
    }
  ]
  ```

**Example**

```
{
  "id": "example",
  "type": "layout",
  "items": [
    {
      "id": "example",
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "hidden": true,
      "conditions": [
        {}
      ],
      "image": null,
      "type": "boolean",
      "validations": [
        null
      ]
    }
  ]
}
```

## FrontendPageOut

- *conditions* — **Type**: [FrontendConditionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendConditionOut)[] Page display conditions **Example**:

  ```
  [
    {
      "operator": "and",
      "items": [
        {
          "type": "question",
          "operator": null,
          "condition": "eq",
          "question": "example",
          "value": "example"
        }
      ]
    }
  ]
  ```

- *items* — **Type**: array: **Any of 12 types**: **FrontendBooleanQuestionOut** **Type**: [FrontendBooleanQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendBooleanQuestionOut) **Example**:, **FrontendIntegerQuestionOut** **Type**: [FrontendIntegerQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendIntegerQuestionOut) **Example**:, **FrontendStringQuestionOut** **Type**: [FrontendStringQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendStringQuestionOut) **Example**:, **FrontendCaptchaQuestionOut** **Type**: [FrontendCaptchaQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendCaptchaQuestionOut) **Example**:, **FrontendFileQuestionOut** **Type**: [FrontendFileQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendFileQuestionOut) **Example**:, **FrontendMatrixQuestionOut** **Type**: [FrontendMatrixQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendMatrixQuestionOut) **Example**:, **FrontendSuggestQuestionOut** **Type**: [FrontendSuggestQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendSuggestQuestionOut) **Example**:, **FrontendCommentQuestionOut** **Type**: [FrontendCommentQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendCommentQuestionOut) **Example**:, **FrontendDateQuestionOut** **Type**: [FrontendDateQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendDateQuestionOut) **Example**:, **FrontendPaymentQuestionOut** **Type**: [FrontendPaymentQuestionOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendPaymentQuestionOut) **Example**:, **FrontendSeriesOut** **Type**: [FrontendSeriesOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendSeriesOut) **Example**:, **FrontendLayoutOut** **Type**: [FrontendLayoutOut](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_get_form_view#entity-FrontendLayoutOut) **Example**: List of questions, series, and groups on the page **Example**:

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "multiline": true,
    "hint": {
      "items": [
        {
          "id": "example",
          "label": "example",
          "image": null
        }
      ]
    },
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "type": "captcha",
    "label": "example",
    "url": "https://example.com",
    "voice_url": "https://example.com",
    "key": "example",
    "mode": "example",
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
        "id": "example",
        "label": "example"
      }
    ],
    "columns": [
      {
        "id": "example",
        "label": "example"
      }
    ],
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "data_source": "survey_question_choice",
    "multichoice": true,
    "parent": "example",
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "label": "example",
    "comment": "example",
    "placeholder": "example",
    "hidden": true,
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
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
    "validations": [
      {
        "type": "required"
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "type": "series",
    "label": "example",
    "conditions": [
      {
        "operator": "and",
        "items": [
          {
            "type": null,
            "operator": null,
            "condition": null,
            "question": "example",
            "value": "example"
          }
        ]
      }
    ],
    "items": [
      {
        "id": "example",
        "label": "example",
        "comment": "example",
        "placeholder": "example",
        "hidden": true,
        "conditions": [
          null
        ],
        "image": null,
        "type": "boolean",
        "validations": [
          null
        ]
      }
    ]
  }
  ```

  ```
  {
    "id": "example",
    "type": "layout",
    "items": [
      {
        "id": "example",
        "label": "example",
        "comment": "example",
        "placeholder": "example",
        "hidden": true,
        "conditions": [
          {}
        ],
        "image": null,
        "type": "boolean",
        "validations": [
          null
        ]
      }
    ]
  }
  ```

  ```
  [
    {
      "id": "example",
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "hidden": true,
      "conditions": [
        {
          "operator": null,
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
      "type": "boolean",
      "validations": [
        {}
      ]
    }
  ]
  ```

**Example**

```
{
  "conditions": [
    {
      "operator": "and",
      "items": [
        {
          "type": null,
          "operator": null,
          "condition": null,
          "question": "example",
          "value": "example"
        }
      ]
    }
  ],
  "items": [
    {
      "id": "example",
      "label": "example",
      "comment": "example",
      "placeholder": "example",
      "hidden": true,
      "conditions": [
        null
      ],
      "image": null,
      "type": "boolean",
      "validations": [
        null
      ]
    }
  ]
}
```

## FrontendMatrixItemOut

| Name | Description |
|------|-------------|
| *column* | **Type**: string Column ID *Example:* `example` |
| *row* | **Type**: string Row ID *Example:* `example` |

**Example**

```
{
  "row": "example",
  "column": "example"
}
```

## FrontendFileItemOut

| Name | Description |
|------|-------------|
| *name* | **Type**: string File name *Example:* `example` |
| *path* | **Type**: string Unique file identifier key *Example:* `example` |

**Example**

```
{
  "name": "example",
  "path": "example"
}
```

## FrontendDateRangeOut

| Name | Description |
|------|-------------|
| *begin* | **Type**: string Start of the date range *Example:* `example` |
| *end* | **Type**: string End of the date range *Example:* `example` |

**Example**

```
{
  "begin": "example",
  "end": "example"
}
```

# 403 Forbidden

Forbidden

## Body

application/json

```
{
  "code": "not_permitted",
  "detail": "example"
}
```

| Name | Description |
|------|-------------|
| *code* | **Type**: string Error code *Const:* `not_permitted` *Example:* `example` |
| *detail* | **Type**: string Error text *Example:* `example` |

# 404 Not Found

Not Found

## Body

application/json

```
{
  "code": "not_found",
  "detail": "example"
}
```

| Name | Description |
|------|-------------|
| *code* | **Type**: string Error code *Const:* `not_found` *Example:* `example` |
| *detail* | **Type**: string Error text *Example:* `example` |

# 422 Unprocessable Entity

Unprocessable Content

## Body

application/json

```
{
  "code": "not_published",
  "detail": "example"
}
```

| Name | Description |
|------|-------------|
| *code* | **Type**: string Error code *Enum:* `not_published`, `already_answered` |
| *detail* | **Type**: string Error text *Example:* `example` |