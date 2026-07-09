---
source: https://yandex.cloud/ru/docs/datalens/openapi-ref/updateCollectionAccessBindings
title: "Yandex DataLens | DataLens API: Update collection access bindings"
author: "Yandex Cloud"
extracted: "2026-07-09T13:34:35Z"
updated: 2026-03-16
---

# HTTP request

```
POST https://api.datalens.tech/rpc/updateCollectionAccessBindings
```

# Body parameters

**Request schema: application/json**

```
{
  "collectionId": "string",
  "deltas": [
    {
      "action": "string",
      "accessBinding": {
        "roleId": "string",
        "subject": {
          "id": "string",
          "type": "string"
        }
      }
    }
  ]
}
```

| Field | Description |
| --- | --- |
| collectionId | **string** Required field. |
| deltas[] | **[DeltasItem](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateCollectionAccessBindings#DeltasItem)** Required field. |

# DeltasItem

| Field | Description |
| --- | --- |
| action | **enum** Required field. `ADD`, `REMOVE` |
| accessBinding | **[AccessBinding](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateCollectionAccessBindings#AccessBinding)** Required field. |

# AccessBinding

| Field | Description |
| --- | --- |
| roleId | **string** Required field. |
| subject | **[Subject](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateCollectionAccessBindings#Subject)** Required field. |

# Subject

| Field | Description |
| --- | --- |
| id | **string** Required field. |
| type | **enum** Required field. `system`, `userAccount`, `federatedUser`, `serviceAccount`, `group`, `invitee` |

# Response

**HTTP Code: 200**

Response

**Response schema: application/json**

```
{
  "id": "string",
  "description": "string",
  "createdBy": "string",
  "createdAt": {
    "seconds": "string",
    "nanos": "number"
  },
  "modifiedAt": {
    "seconds": "string",
    "nanos": "number"
  },
  "metadata": {},
  "done": "boolean"
}
```

| Field | Description |
| --- | --- |
| id | **string** Required field. |
| description | **string** Required field. |
| createdBy | **string** Required field. |
| createdAt | **[CreatedAt](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateCollectionAccessBindings#CreatedAt)** Required field. |
| modifiedAt | **[ModifiedAt](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateCollectionAccessBindings#ModifiedAt)** Required field. |
| metadata | **[Metadata](https://yandex.cloud/ru/docs/datalens/openapi-ref/updateCollectionAccessBindings#Metadata)** Required field. |
| done | **boolean** Required field. |

# CreatedAt

| Field | Description |
| --- | --- |
| seconds | **string** Required field. |
| nanos | **number** |

# ModifiedAt

| Field | Description |
| --- | --- |
| seconds | **string** Required field. |
| nanos | **number** |

| Field | Description |
| --- | --- |
| Empty |  |
