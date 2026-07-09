---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbooksList
title: "Yandex DataLens | DataLens API: Get workbooks list"
author: "Yandex Cloud"
extracted: "2026-07-09T13:32:00Z"
---

# HTTP request

```
POST https://api.datalens.tech/rpc/getWorkbooksList
```

# Body parameters

**Request schema: application/json**

```
{
  "collectionId": "string | null",
  "includePermissionsInfo": "boolean",
  "filterString": "string",
  "page": "number",
  "pageSize": "number",
  "orderField": "string",
  "orderDirection": "string",
  "onlyMy": "boolean"
}
```

| Field | Description |
| --- | --- |
| collectionId | **string \| null** |
| includePermissionsInfo | **boolean** |
| filterString | **string** |
| page | **number** |
| pageSize | **number** |
| orderField | **enum** `title`, `createdAt`, `updatedAt` |
| orderDirection | **enum** `asc`, `desc` |
| onlyMy | **boolean** |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "workbooks": [
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
  ],
  "nextPageToken": "string"
}
```

| Field | Description |
| --- | --- |
| workbooks[] | **[WorkbooksItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbooksList#WorkbooksItem)** Required field. |
| nextPageToken | **string** |

# WorkbooksItem

| Field | Description |
| --- | --- |
| workbookId | **string** Required field. |
| collectionId | **string \| null** Required field. |
| title | **string** Required field. |
| description | **string \| null** Required field. |
| tenantId | **string** Required field. |
| meta | All of **[Meta0](https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbooksList#Meta0)** & **object** (map<**string**, **unknown**>) |
| createdBy | **string** Required field. |
| createdAt | **string** Required field. |
| updatedBy | **string** Required field. |
| updatedAt | **string** Required field. |
| status | **enum** `creating`, `deleting`, `active` |
| permissions | **[Permissions](https://yandex.cloud/ru/docs/datalens/openapi-ref/getWorkbooksList#Permissions)** Required field. |

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
