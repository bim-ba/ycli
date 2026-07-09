---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/updateQlChart
title: "Yandex DataLens | DataLens API: 🚧 [Experimental] Update QL chart"
author: "Yandex Cloud"
extracted: "2026-07-09T13:30:35Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/updateQLChart
```

# Body parameters

**Request schema: application/json**

```
{
  "entryId": "string",
  "template": "string",
  "annotation": {
    "description": "string"
  },
  "mode": "string",
  "data": {
    "string": "unknown"
  }
}
```

| Field | Description |
| --- | --- |
| entryId | **string** Required field. |
| template | **enum** Required field. `ql` |
| annotation | **[Annotation](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateQlChart#Annotation)** Required field. |
| mode | **enum** Required field. `save`, `publish` |
| data | **object** (map<**string**, **unknown**>) Required field. |

# Annotation

| Field | Description |
| --- | --- |
| description | **string** Required field. |

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
