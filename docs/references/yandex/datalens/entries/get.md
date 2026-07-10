---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getEntries
title: "Yandex DataLens | DataLens API: Get entries"
author: "Yandex Cloud"
extracted: "2026-07-09T13:30:11Z"
---

Returns the specified DataLens entry.

# HTTP request

```
POST https://api.datalens.tech/rpc/getEntries
```

# Body parameters

**Request schema: application/json**

```
{
  "<allOf>": [
    {
      "excludeLocked": "boolean",
      "includeData": "boolean",
      "includeLinks": "boolean",
      "filters": {
        "name": "string"
      },
      "orderBy": {
        "field": "string",
        "direction": "string"
      },
      "createdBy": "unknown",
      "page": "number",
      "pageSize": "number",
      "includePermissionsInfo": "boolean",
      "ignoreWorkbookEntries": "boolean"
    },
    "unknown"
  ]
}
```

All of:

| Field | Description |
| --- | --- |
| excludeLocked | **boolean** Exclude locked entries from results. |
| includeData | **boolean** Include data in the response. |
| includeLinks | **boolean** Include links in the response. |
| filters | **[Filters](https://yandex.cloud/ru/docs/datalens/openapi-ref/getEntries#Filters)** Filtering configuration. |
| orderBy | **[OrderBy](https://yandex.cloud/ru/docs/datalens/openapi-ref/getEntries#OrderBy)** Required field. Sorting configuration. |
| createdBy | Any of **string** \| **string** Filter entries by creator. |
| page | **number** Page number for pagination. |
| pageSize | **number** Number of entries per page. |
| includePermissionsInfo | **boolean** Include permission information in response. |
| ignoreWorkbookEntries | **boolean** Ignore workbook entries in results. |

> The body is empty.

| Field | Description |
| --- | --- |
| Empty |  |

# Filters

Filtering configuration.

| Field | Description |
| --- | --- |
| name | **string** Filter entries by name. |

# OrderBy

Sorting configuration.

| Field | Description |
| --- | --- |
| field | **enum** Required field. Field to order by entries: `createdAt` — date of field creation;, `name` — name of the field. |
| direction | **enum** Required field. Sorting direction. `desc` — descending;, `asc` — ascending. |

# Response

**HTTP Code: 200**

**Response schema: application/json**

```
{
  "nextPageToken": "string",
  "entries": [
    {
      "<anyOf>": [
        {
          "isLocked": "boolean",
          "entryId": "string",
          "scope": "string",
          "type": "string"
        },
        {
          "entryId": "string",
          "key": "string",
          "scope": "string",
          "type": "string",
          "meta": "object | null",
          "createdAt": "string",
          "updatedAt": "string",
          "createdBy": "string",
          "updatedBy": "string",
          "savedId": "string",
          "publishedId": "string | null",
          "hidden": "boolean",
          "workbookId": "string | null",
          "workbookTitle": "string | null",
          "collectionId": "string | null",
          "collectionTitle": "string | null",
          "isFavorite": "boolean",
          "isLocked": "boolean",
          "permissions": {
            "execute": "boolean",
            "read": "boolean",
            "edit": "boolean",
            "admin": "boolean"
          },
          "links": "object | null",
          "data": {
            "string": "unknown"
          }
        }
      ]
    }
  ]
}
```

| Field | Description |
| --- | --- |
| nextPageToken | **string** Indicates if there are more pages. |
| entries[] | **unknown** Required field. Entry information. |
