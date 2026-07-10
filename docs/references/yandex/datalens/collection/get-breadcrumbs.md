---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getCollectionBreadcrumbs
title: "Yandex DataLens | DataLens API: Get collection breadcrumbs"
author: "Yandex Cloud"
extracted: "2026-07-09T13:26:55Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/getCollectionBreadcrumbs
```

# Body parameters

**Request schema: application/json**

```
{
  "collectionId": "string",
  "includePermissionsInfo": "boolean"
}
```

| Field | Description |
| --- | --- |
| collectionId | **string** Required field. |
| includePermissionsInfo | **boolean** |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
"array"
```
