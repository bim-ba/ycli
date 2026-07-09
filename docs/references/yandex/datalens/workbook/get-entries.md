---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbookEntries
title: "Yandex DataLens | DataLens API: Get workbook entries"
author: "Yandex Cloud"
extracted: "2026-07-09T13:32:25Z"
---

# HTTP request

```
POST https://api.datalens.tech/rpc/getWorkbookEntries
```

# Body parameters

**Request schema: application/json**

```
{
  "workbookId": "string",
  "includePermissionsInfo": "boolean",
  "page": "number",
  "pageSize": "number",
  "createdBy": "string",
  "scope": "unknown",
  "orderBy": {
    "field": "string",
    "direction": "string"
  },
  "filters": {
    "name": "string"
  }
}
```

| Field | Description |
| --- | --- |
| workbookId | **string** Required field. |
| includePermissionsInfo | **boolean** |
| page | **number** |
| pageSize | **number** |
| createdBy | **string** |
| scope | Any of **string** \| **string** |
| orderBy | **[OrderBy](https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbookEntries#OrderBy)** Required field. |
| filters | **[Filters](https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbookEntries#Filters)** Required field. |

# OrderBy

| Field | Description |
| --- | --- |
| field | **enum** Required field. `name`, `createdAt` |
| direction | **enum** Required field. `asc`, `desc` |

# Filters

| Field | Description |
| --- | --- |
| name | **string** Required field. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "entries": [
    {
      "entryId": "string",
      "scope": "string",
      "type": "string",
      "key": "string | null",
      "displayKey": "string | null",
      "createdBy": "string",
      "createdAt": "string",
      "updatedBy": "string",
      "updatedAt": "string",
      "savedId": "string | null",
      "publishedId": "string | null",
      "revId": "string",
      "meta": "object | null",
      "hidden": "boolean | null",
      "workbookId": "string | null",
      "collectionId": "string | null",
      "tenantId": "string | null",
      "isFavorite": "boolean",
      "isLocked": "boolean",
      "permissions": {
        "execute": "boolean",
        "read": "boolean",
        "edit": "boolean",
        "admin": "boolean"
      },
      "mirrored": "boolean | null"
    }
  ],
  "nextPageToken": "string"
}
```

| Field | Description |
| --- | --- |
| entries[] | **[EntriesItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbookEntries#EntriesItem)** Required field. |
| nextPageToken | **string** |

# EntriesItem

| Field | Description |
| --- | --- |
| entryId | **string** Required field. |
| scope | **enum** Required field. `dash`, `widget`, `dataset`, `folder`, `connection` |
| type | **string** Required field. |
| key | **string \| null** Required field. |
| displayKey | **string \| null** Required field. |
| createdBy | **string** Required field. |
| createdAt | **string** Required field. |
| updatedBy | **string** Required field. |
| updatedAt | **string** Required field. |
| savedId | **string \| null** Required field. |
| publishedId | **string \| null** Required field. |
| revId | **string** Required field. |
| meta | **object \| null** Required field. |
| hidden | **boolean \| null** Required field. |
| workbookId | **string \| null** Required field. |
| collectionId | **string \| null** Required field. |
| tenantId | **string \| null** Required field. |
| isFavorite | **boolean** Required field. |
| isLocked | **boolean** Required field. |
| permissions | **[Permissions](https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbookEntries#Permissions)** Required field. |
| mirrored | **boolean \| null** Required field. |

# Permissions

| Field | Description |
| --- | --- |
| execute | **boolean** Required field. |
| read | **boolean** Required field. |
| edit | **boolean** Required field. |
| admin | **boolean** Required field. |
