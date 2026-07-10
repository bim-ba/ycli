---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbook
title: "Yandex DataLens | DataLens API: Get workbook"
author: "Yandex Cloud"
extracted: "2026-07-09T13:31:54Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/getWorkbook
```

# Body parameters

**Request schema: application/json**

```
{
  "workbookId": "string",
  "includePermissionsInfo": "boolean"
}
```

| Field | Description |
| --- | --- |
| workbookId | **string** Required field. |
| includePermissionsInfo | **boolean** |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "workbookId": "string",
  "collectionId": "string | null",
  "title": "string",
  "description": "string | null",
  "tenantId": "string",
  "meta": "unknown",
  "createdBy": "string",
  "createdAt": "string",
  "updatedBy": "string",
  "updatedAt": "string",
  "status": "string",
  "permissions": {
    "listAccessBindings": "boolean",
    "updateAccessBindings": "boolean",
    "limitedView": "boolean",
    "view": "boolean",
    "update": "boolean",
    "copy": "boolean",
    "move": "boolean",
    "publish": "boolean",
    "embed": "boolean",
    "delete": "boolean"
  }
}
```

| Field | Description |
| --- | --- |
| workbookId | **string** Required field. |
| collectionId | **string \| null** Required field. |
| title | **string** Required field. |
| description | **string \| null** Required field. |
| tenantId | **string** Required field. |
| meta | All of **[Meta0](https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbook#Meta0)** & **object** (map<**string**, **unknown**>) |
| createdBy | **string** Required field. |
| createdAt | **string** Required field. |
| updatedBy | **string** Required field. |
| updatedAt | **string** Required field. |
| status | **enum** `creating`, `deleting`, `active` |
| permissions | **[Permissions](https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbook#Permissions)** Required field. |

| Field | Description |
| --- | --- |
| importId | **string** |

# Permissions

| Field | Description |
| --- | --- |
| listAccessBindings | **boolean** Required field. |
| updateAccessBindings | **boolean** Required field. |
| limitedView | **boolean** Required field. |
| view | **boolean** Required field. |
| update | **boolean** Required field. |
| copy | **boolean** Required field. |
| move | **boolean** Required field. |
| publish | **boolean** Required field. |
| embed | **boolean** Required field. |
| delete | **boolean** Required field. |
