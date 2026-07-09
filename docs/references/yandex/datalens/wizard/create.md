---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/createWizardChart
title: "Yandex DataLens | DataLens API: 🚧 [Experimental] Create wizard chart"
author: "Yandex Cloud"
extracted: "2026-07-09T13:31:19Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/createWizardChart
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
| template | **enum** Required field. `datalens` |
| annotation | **[Annotation](https://yandex.cloud/ru/docs/datalens/openapi-ref/createWizardChart#Annotation)** Required field. |
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
