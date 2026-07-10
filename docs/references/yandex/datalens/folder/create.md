---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/createFolder
title: "Yandex DataLens | DataLens API: CreateFolder"
author: "Yandex Cloud"
extracted: "2026-07-09T13:34:53Z"
---

# HTTP request

```
POST https://api.datalens.tech/rpc/createFolder
```

# Body parameters

**Request schema: application/json**

```
{
  "key": "string",
  "initialPermissions": {
    "acl_adm": [
      {
        "comment": "string",
        "subject": "string"
      }
    ],
    "acl_edit": [
      {
        "comment": "string",
        "subject": "string"
      }
    ],
    "acl_view": [
      {
        "comment": "string",
        "subject": "string"
      }
    ],
    "acl_execute": [
      {
        "comment": "string",
        "subject": "string"
      }
    ]
  }
}
```

# InitialPermissions

# AclAdmItem

| Field | Description |
| --- | --- |
| comment | **string** Required field. |
| subject | **string** Required field. |

# AclEditItem

| Field | Description |
| --- | --- |
| comment | **string** Required field. |
| subject | **string** Required field. |

# AclViewItem

| Field | Description |
| --- | --- |
| comment | **string** Required field. |
| subject | **string** Required field. |

# AclExecuteItem

| Field | Description |
| --- | --- |
| comment | **string** Required field. |
| subject | **string** Required field. |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "entryId": "string",
  "scope": "string",
  "type": "string",
  "key": "string",
  "unversionedData": {},
  "createdBy": "string",
  "createdAt": "string",
  "updatedBy": "string",
  "updatedAt": "string",
  "savedId": "string",
  "revId": "string",
  "publishedId": "string | null",
  "tenantId": "string",
  "data": {},
  "meta": {},
  "annotation": "null",
  "hidden": "boolean",
  "mirrored": "boolean",
  "public": "boolean",
  "workbookId": "null",
  "collectionId": "null",
  "version": "null",
  "sourceVersion": "null",
  "links": "null"
}
```

| Field | Description |
| --- | --- |
| entryId | **string** Required field. |
| scope | **enum** Required field. `folder` |
| type | **enum** Required field. `` |
| key | **string** Required field. |
| unversionedData | **[UnversionedData](https://yandex.cloud/ru/docs/datalens/openapi-ref/createFolder#UnversionedData)** Required field. |
| createdBy | **string** Required field. |
| createdAt | **string** Required field. |
| updatedBy | **string** Required field. |
| updatedAt | **string** Required field. |
| savedId | **string** Required field. |
| revId | **string** Required field. |
| publishedId | **string \| null** Required field. |
| tenantId | **string** Required field. |
| data | **[Data](https://yandex.cloud/ru/docs/datalens/openapi-ref/createFolder#Data)** Required field. |
| meta | **[Meta](https://yandex.cloud/ru/docs/datalens/openapi-ref/createFolder#Meta)** Required field. |
| annotation | **null** Required field. |
| hidden | **boolean** Required field. |
| mirrored | **boolean** Required field. |
| public | **boolean** Required field. |
| workbookId | **null** Required field. |
| collectionId | **null** Required field. |
| version | **null** Required field. |
| sourceVersion | **null** Required field. |
| links | **null** Required field. |

# UnversionedData

| Field | Description |
| --- | --- |
| Empty |  |

# Data

| Field | Description |
| --- | --- |
| Empty |  |

| Field | Description |
| --- | --- |
| Empty |  |
