---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/createQlChart
title: "Yandex DataLens | DataLens API: 🚧 [Experimental] Create QL chart"
author: "Yandex Cloud"
extracted: "2026-07-09T13:30:43Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/createQLChart
```

# Body parameters

**Request schema: application/json**

```
{
  "<allOf>": [
    {
      "string": "unknown"
    },
    {
      "key": "string",
      "workbookId": "string",
      "name": "string"
    }
  ]
}
```

All of:

| Field | Description |
| --- | --- |
| template | **enum** Required field. `ql` |
| annotation | **[Annotation](https://yandex.cloud/ru/docs/datalens/openapi-ref/createQlChart#Annotation)** Required field. |
| data | **object** (map<**string**, **unknown**>) Required field. |

| Field | Description |
| --- | --- |
| key | **string** |
| workbookId | **string** |
| name | **string** |

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
