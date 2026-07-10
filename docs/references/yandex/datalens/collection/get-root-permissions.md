---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/getRootCollectionPermissions
title: "Yandex DataLens | DataLens API: Get root collection permissions"
author: "Yandex Cloud"
extracted: "2026-07-09T13:27:30Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/getRootCollectionPermissions
```

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "createCollectionInRoot": "boolean",
  "createWorkbookInRoot": "boolean"
}
```

| Field | Description |
| --- | --- |
| createCollectionInRoot | **boolean** Required field. |
| createWorkbookInRoot | **boolean** Required field. |
