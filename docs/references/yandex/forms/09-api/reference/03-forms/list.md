---
source: https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view
title: "Get list of available forms - Forms |"
word_count: 402
token_estimate: 3537
extracted: "2026-05-22T18:09:28Z"
mode: quality
---

# Request

GET

```
https://api.forms.yandex.net/v1/surveys
```

## Query parameters

| Name | Description |
|------|-------------|
| `favourite` | **Type:** boolean. Filter by favorites |
| `group` | **Type:** string. Filter by form groups. Example: `` |
| `limit` | **Type:** integer. Maximum number of forms per page. Default: `10` |
| `name` | **Type:** string. Filter by form name. Example: `` |
| `offset` | **Type:** integer. Offset for paginated output |
| `orderby` | **Type:** string. Sorting (e.g. name,-modified,-count). Example: `` |
| `ownership` | **Type:** OwnershipType (string, enumeration; enum: `mine`, `shared`). Filter: created by me or accessible by rights. Example: `` |
| `published` | **Type:** boolean. Filter by publication status |

# Responses

# 200 OK

OK

## Body

application/json

```
{
  "links": {
    "next": "example"
  },
  "result": [
    {
      "id": "example",
      "name": "example",
      "dir_id": "example",
      "created": "2025-01-01T00:00:00Z",
      "modified": "2025-01-01T00:00:00Z",
      "language": "example",
      "group": {
        "id": 0,
        "name": "example",
        "dir_id": "example"
      },
      "is_published": true,
      "is_public": true,
      "is_banned": true,
      "answers": 0,
      "is_favourite": true
    }
  ]
}
```

| Name | Description |
|------|-------------|
| `links` | **Type:** [LinksOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view#entity-LinksOut). Next page |
| `result` | **Type:** [SurveyShortPublicOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view#entity-SurveyShortPublicOut)[]. List of objects |

`links` example:

```json
{
  "next": "example"
}
```

`result` example:

```json
[
  {
    "id": "example",
    "name": "example",
    "dir_id": "example",
    "created": "2025-01-01T00:00:00Z",
    "modified": "2025-01-01T00:00:00Z",
    "language": "example",
    "group": {
      "id": 0,
      "name": "example",
      "dir_id": "example"
    },
    "is_published": true,
    "is_public": true,
    "is_banned": true,
    "answers": 0,
    "is_favourite": true
  }
]
```

## LinksOut

| Name | Description |
|------|-------------|
| `next` | **Type:** string. Link to the next page. Example: `example` |

**Example**

```
{
  "next": "example"
}
```

## SurveyGroupShortOut

| Name | Description |
|------|-------------|
| `id` | **Type:** integer. Form group ID |
| `dir_id` | **Type:** string. Organization ID in Connect. Example: `example` |
| `name` | **Type:** string. Form group name. Example: `example` |

**Example**

```
{
  "id": 0,
  "name": "example",
  "dir_id": "example"
}
```

## SurveyShortPublicOut

| Name | Description |
|------|-------------|
| `id` | **Type:** string. Form identifier. Pattern: `^[a-fA-F\d]{24}$`. Example: `example` |
| `answers` | **Type:** integer. Number of responses |
| `created` | **Type:** string&lt;date-time&gt;. Form creation date. Example: `2025-01-01T00:00:00Z` |
| `dir_id` | **Type:** string. Organization ID in 360. Example: `example` |
| `group` | **Type:** [SurveyGroupShortOut](https://yandex.ru/support/forms/en/api-ref/surveys/events_b2b_v1_views_surveys_get_surveys_public_view#entity-SurveyGroupShortOut). Form group. Example: `{"id": 0, "name": "example", "dir_id": "example"}` |
| `is_banned` | **Type:** boolean. Form is blocked |
| `is_favourite` | **Type:** boolean. Form is in favorites |
| `is_public` | **Type:** boolean. Form is public |
| `is_published` | **Type:** boolean. Form is published |
| `language` | **Type:** string. Language at form creation. Example: `example` |
| `modified` | **Type:** string&lt;date-time&gt;. Form modification date. Example: `2025-01-01T00:00:00Z` |
| `name` | **Type:** string. Form name. Example: `example` |

**Example**

```
{
  "id": "example",
  "name": "example",
  "dir_id": "example",
  "created": "2025-01-01T00:00:00Z",
  "modified": "2025-01-01T00:00:00Z",
  "language": "example",
  "group": {
    "id": 0,
    "name": "example",
    "dir_id": "example"
  },
  "is_published": true,
  "is_public": true,
  "is_banned": true,
  "answers": 0,
  "is_favourite": true
}
```