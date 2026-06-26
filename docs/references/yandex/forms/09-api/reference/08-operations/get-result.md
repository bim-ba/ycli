---
source: https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view
title: "Get operation result - Operations |"
word_count: 105
token_estimate: 767
extracted: "2026-05-22T18:14:13Z"
mode: quality
---

Returns the operation result.

Parameters:

-   **operation\_id**: operation ID

# Request

GET

```
https://api.forms.yandex.net/v1/operations/{operation_id}
```

## Path parameters

| Name | Description |
|------|-------------|
| `operation_id` | **Type:** string |

# Responses

# 200 OK

OK

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
| `status` | **All of 1 type:** [OperationStatusType](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view#entity-OperationStatusType) — an enumeration (enum: `ok`, `fail`, `wait`, `not_running`). Operation status. Example: `ok` |
| `message` | **Type:** string — Operation message. Example: `example` |

## OperationStatusType

An enumeration.

**Type**: string

*Enum:* `ok`, `fail`, `wait`, `not_running`

Previous

Next