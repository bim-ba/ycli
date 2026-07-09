---
source: https://yandex.cloud/ru/docs/datalens/operations/api-start?ysclid=mrdjbz61ak264161970&utm_referrer=https%3A%2F%2Fya.ru%2F
title: "Yandex DataLens | Работа с Public API"
author: "Yandex Cloud"
extracted: "2026-07-09T13:26:06Z"
---

DataLens предоставляет публичное API [https://api.datalens.tech](https://api.datalens.tech/) для автоматизации операций с дашбордами, чартами, датасетами и подключениями.

DataLens Public API — это набор методов, аналогичный тем, что используются в веб-интерфейсе DataLens. API описывается OpenAPI-спецификацией и аутентифицируется через IAM-токены Yandex Cloud.

При работе с API учитывайте действующие [лимиты](https://yandex.cloud/ru/docs/datalens/concepts/limits#datalens-api-limits).

Для работы с API требуется [IAM-токен](https://yandex.cloud/ru/docs/iam/operations/iam-token/create) и [идентификатор организации](https://yandex.cloud/ru/docs/datalens/settings/#service-settings).

Например, подставьте свои значения `<IAM_TOKEN>`, `<ORG_ID>` и `<ENTRY_ID>` в следующий запрос, чтобы получить список всех связанных с сущностью объектов:

```
curl -X 'POST' \
  'https://api.datalens.tech/rpc/getEntriesRelations' \
  -H 'accept: application/json' \
  -H 'x-dl-api-version: 1' \
  -H 'Authorization: Bearer <IAM_TOKEN>' \
  -H 'x-dl-org-id: <ORG_ID>' \
  -H 'Content-Type: application/json' \
  -d '{
  "entryIds": [
    "<ENTRY_ID>"
  ]
}'
```

Swagger - https://api.datalens.tech
OpenAPI - https://api.datalens.tech/json/
