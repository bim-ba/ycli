---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getCollectionContent
title: "Yandex DataLens | DataLens API: Get collection content"
author: "Yandex Cloud"
extracted: "2026-07-09T13:27:22Z"
---

# HTTP request

```
POST https://api.datalens.tech/rpc/getCollectionContent
```

# Body parameters

**Request schema: application/json**

```
{
  "collectionId": "string | null",
  "page": "string | null",
  "filterString": "string",
  "orderField": "string",
  "orderDirection": "string",
  "onlyMy": "boolean",
  "mode": "string",
  "pageSize": "number",
  "includePermissionsInfo": "boolean"
}
```

| Field | Description |
| --- | --- |
| collectionId | **string \| null** Required field. |
| page | **string \| null** |
| filterString | **string** |
| orderField | **enum** `title`, `createdAt`, `updatedAt` |
| orderDirection | **enum** `asc`, `desc` |
| onlyMy | **boolean** |
| mode | **enum** `all`, `onlyCollections`, `onlyWorkbooks` |
| pageSize | **number** |
| includePermissionsInfo | **boolean** |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "items": [
    {
      "<oneOf>": [
        {
          "collectionId": "string",
          "title": "string",
          "description": "string | null",
          "parentId": "string | null",
          "tenantId": "string",
          "createdBy": "string",
          "createdAt": "string",
          "updatedBy": "string",
          "updatedAt": "string",
          "meta": {
            "string": "unknown"
          },
          "entity": "string",
          "permissions": {
            "listAccessBindings": "boolean",
            "updateAccessBindings": "boolean",
            "createSharedEntry": "boolean",
            "createCollection": "boolean",
            "createWorkbook": "boolean",
            "limitedView": "boolean",
            "view": "boolean",
            "update": "boolean",
            "copy": "boolean",
            "move": "boolean",
            "delete": "boolean"
          }
        },
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
          "entity": "string",
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
      ]
    }
  ],
  "nextPageToken": "string | null"
}
```

| Field | Description |
| --- | --- |
| items[] | **unknown** Required field. |
| nextPageToken | **string \| null** |
