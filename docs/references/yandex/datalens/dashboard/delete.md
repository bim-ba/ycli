---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/deleteDashboard
title: "Yandex DataLens | DataLens API: Delete dashboard"
author: "Yandex Cloud"
extracted: "2026-07-09T13:29:05Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/deleteDashboard
```

# Body parameters

**Request schema: application/json**

```
{
  "dashboardId": "string",
  "lockToken": "string"
}
```

| Field | Description |
| --- | --- |
| dashboardId | **string** Required field. |
| lockToken | **string** |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{}
```

| Field | Description |
| --- | --- |
| Empty |  |
