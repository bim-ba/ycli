---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/updateWizardChart
title: "Yandex DataLens | DataLens API: 🚧 [Experimental] Update wizard chart"
author: "Yandex Cloud"
extracted: "2026-07-09T13:31:13Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/updateWizardChart
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
| template | **enum** Required field. `datalens` |
| annotation | **[Annotation](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateWizardChart#Annotation)** Required field. |
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
