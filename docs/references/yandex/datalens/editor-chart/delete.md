---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/deleteEditorChart
title: "Yandex DataLens | DataLens API: Delete editor chart"
author: "Yandex Cloud"
extracted: "2026-07-09T13:32:48Z"
updated: 2026-03-16
---

Deletes the specified Editor chart.

# HTTP request

```
POST https://api.datalens.tech/rpc/deleteEditorChart
```

# Body parameters

**Request schema: application/json**

```
{
  "chartId": "string"
}
```

| Field | Description |
| --- | --- |
| chartId | **string** Required field. ID of the Editor chart to delete. |

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
