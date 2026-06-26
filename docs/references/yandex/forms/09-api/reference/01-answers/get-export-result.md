---
source: https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_export_answers_results_view
title: "Get answer export result - Answers |"
word_count: 307
token_estimate: 2207
extracted: "2026-05-22T18:07:42Z"
mode: quality
---

Returns the answer export result.

Parameters:

-   **survey\_id**: form ID
-   **task\_id**: operation ID

# Request

GET

```
https://api.forms.yandex.net/v1/surveys/{survey_id}/answers/export-results
```

## Path parameters

| Name | Description |
|------|-------------|
| `survey_id` | **Type:** string. Pattern: `^[a-fA-F\d]{24}$` |

## Query parameters

| Name | Description |
|------|-------------|
| `task_id` | **Type:** string |

# Responses

# 200 OK

OK

# 202 Accepted

Accepted

## Body

application/json

```
{
  "id": "example",
  "status": "ok",
  "message": "example"
}
```

| Name | Description |
|------|-------------|
| `id` | **Type:** string — Operation ID. Example: `example` |
| `status` | **All of 1 type:** [OperationStatusType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_export_answers_results_view#entity-OperationStatusType) — an enumeration (enum: `ok`, `fail`, `wait`, `not_running`). Operation status. Example: `ok` |
| `message` | **Type:** string — Operation message. Example: `example` |

## OperationStatusType

An enumeration.

**Type**: string

*Enum:* `ok`, `fail`, `wait`, `not_running`

# 302 Moved Temporarily

Found

# 422 Unprocessable Entity

Unprocessable Content

## Body

application/json

```
{
  "loc": [],
  "error_code": "disabled",
  "msg": "example",
  "value": null
}
```

| Name | Description |
|------|-------------|
| `error_code` | **All of 1 type:** [ErrorType](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_export_answers_results_view#entity-ErrorType) — an enumeration (enum: `disabled`, `value_error.not_found`, `value_error.missing`, `value_error.not_permitted`, `value_error.duplicated`, `value_error`, `value_error.wrong_condition`, `value_error.too_many`, `value_error.too_often`, `value_error.bad_karma`, `dependency_error.subscription_variable`, `dependency_error.template_variable`, `dependency_error.hook_condition`, `dependency_error.submit_condition`, `dependency_error.page_condition`, `dependency_error.question_condition`, `value_error.file_storage`, `value_error.default_styles_template`, `export_error`, `license_required`). Error code. Example: `disabled` |
| `msg` | **Type:** string — Error message. Example: `example` |
| `loc` | **Type:** unknown[] — Field location in the request. Default: `[]`. Example: `[null]` |
| `value` | **Type:** unknown — Error value. Example: `null` |

## ErrorType

An enumeration.

**Type**: string

*Enum:* `disabled`, `value_error.not_found`, `value_error.missing`, `value_error.not_permitted`, `value_error.duplicated`, `value_error`, `value_error.wrong_condition`, `value_error.too_many`, `value_error.too_often`, `value_error.bad_karma`, `dependency_error.subscription_variable`, `dependency_error.template_variable`, `dependency_error.hook_condition`, `dependency_error.submit_condition`, `dependency_error.page_condition`, `dependency_error.question_condition`, `value_error.file_storage`, `value_error.default_styles_template`, `export_error`, `license_required`