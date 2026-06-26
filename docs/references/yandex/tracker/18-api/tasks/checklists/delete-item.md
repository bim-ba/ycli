# Удалить пункт чеклиста

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/delete-checklist-item#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/delete-checklist-item#answer)

Запрос позволяет удалить пункт чеклиста из задачи.

DELETE

```
https://api.tracker.yandex.net/v3/issues/<id_задачи>/checklistItems/<id_пункта_чеклиста>
```

## Формат запроса

Чтобы удалить пункт чеклиста из задачи, используйте HTTP-запрос с методом `DELETE`:

```
DELETE /v3/issues/<id_задачи>/checklistItems/<id_пункта_чеклиста>
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access#iam-token)
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Ресурс

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <id_задачи> | Идентификатор или ключ задачи. | Строка |
| <id_пункта_чеклиста> | Идентификатор пункта чеклиста. Чтобы получить идентификатор, выполните запрос. | Строка |

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело ответа содержит JSON-объект с параметрами пунктов чеклиста и параметрами задачи, из которой был удален пункт чеклиста.

```
{
    "self": "https://api.tracker.yandex.net/v3/issues/ORG-3",
    "id": "5f981c00b982f075********",
    "key": "ORG-3",
    "version": 151,
    "lastCommentUpdatedAt": "2020-12-13T13:18:22.965+0000",
    "pendingReplyFrom": [
        {
            "self": "https://api.tracker.yandex.net/v3/users/11********",
            "id": "11********",
            "display": "Имя Фамилия"
        }
    ],
    "summary": "Название задачи",
    "statusStartTime": "2020-11-03T11:19:24.733+0000",
    "updatedBy": {
        "self": "https://api.tracker.yandex.net/v3/users/19********",
        "id": "11********",
        "display": "Имя Фамилия"
    },
    "checklistDone": "0",
    "project": {
      "self": "https://api.tracker.yandex.net/v3/projects/7",
      "id": "7",
      "display": "My project"
    },
    "description": "My ticket",
    "boards": [
            {
              "id": 14
            }
        ],
    "type": {
        "self": "https://api.tracker.yandex.net/v3/issuetypes/2",
        "id": "2",
        "key": "task",
        "display": "Задача"
    },
    "priority": {
        "self": "https://api.tracker.yandex.net/v3/priorities/3",
        "id": "3",
        "key": "normal",
        "display": "Средний"
    },
    "previousStatusLastAssignee": {
        "self": "https://api.tracker.yandex.net/v3/users/11********",
        "id": "11********",
        "display": "Имя Фамилия"
    },
    "createdAt": "2020-10-27T13:09:20.085+0000",
    "followers": [
        {
            "self": "https://api.tracker.yandex.net/v3/users/19********",
            "id": "11********",
            "display": "Имя Фамилия"
        }
    ],
    "createdBy": {
        "self": "https://api.tracker.yandex.net/v3/users/11********",
        "id": "11********",
        "display": "Имя Фамилия"
    },
    "checklistItems": [
         {
               "id": "5fde5f0a1aee261d********",
               "text": "List item text",
               "textHtml": "List item text in HTML",
               "checked": false,
               "assignee": {
                  "id": 11********,
                  "display": "Имя Фамилия",
                  "passportUid": 11********,
                  "login": "user_login",
                  "firstName": "Имя",
                  "lastName": "Фамилия",
                  "email": "user_login@example.com",
                  "trackerUid": 11********
                  },
               "deadline": {
                  "date": "2021-05-09T00:00:00.000+0000",
                  "deadlineType": "date",
                  "isExceeded": false
                  },
               "checklistItemType": "standard"
         },
       ...
      ],
   "checklistTotal": 4,
   "votes": 0,
   "assignee": {
        "self": "https://api.tracker.yandex.net/v3/users/11********",
        "id": "11********",
        "display": "Имя Фамилия"
    },
   "deadline": "2020-10-28",
   "queue": {
        "self": "https://api.tracker.yandex.net/v3/queues/ORG",
        "id": "1",
        "key": "ORG",
        "display": "My queue"
    },
   "updatedAt": "2021-02-16T08:28:41.095+0000",
   "status": {
        "self": "https://api.tracker.yandex.net/v3/statuses/1",
        "id": "2",
        "key": "open",
        "display": "Открыт"
    },
    "previousStatus": {
        "self": "https://api.tracker.yandex.net/v3/statuses/3",
        "id": "3",
        "key": "resolved",
        "display": "Решен"
    },
    "favorite": false
}
```

Параметры ответа
В таблице перечислены основные поля ответа. Полный список полей и их описание см. на странице [Параметры ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/response-fields).

Также в ответе могут содержаться глобальные пользовательские поля и локальные поля очередей.

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о задаче. | Строка |
| id | Идентификатор задачи. | Число |
| key | Ключ задачи. | Строка |
| version | Версия задачи. Каждое изменение параметров увеличивает номер версии. Редактирование задачи будет заблокировано, если версия достигнет предельного значения: для роботов 10100, для пользователей 11100. | Число |
| lastCommentUpdatedAt | Время обновления последнего комментария. | Строка |
| pendingReplyFrom | Объект с информацией о сотруднике, от которого ожидается ответ. | Объект |
| summary | Название задачи. | Строка |
| statusStartTime | Время создание задачи. | Строка |
| updatedBy | Объект с информацией о последнем сотруднике, изменявшим задачу. | Объект |
| checklistDone | Количество пунктов в чеклисте, которые отмечены как выполненные. | Число |
| project | Объект с информацией о проекте, в который входит задача. | Объект |
| description | Описание задачи. | Строка |
| boards | Массив объектов с информацией о досках, на которых расположена задача. | Объект |
| type | Объект с информацией о типе задачи. | Объект |
| priority | Объект с информацией о приоритете. | Объект |
| previousStatusLastAssignee | Объект с информацией об исполнителе задачи в предыдущем статусе. | Объект |
| createdAt | Дата и время создания задачи. | Строка |
| followers | Массив объектов с информацией о наблюдателях задачи. | Объект |
| createdBy | Объект с информацией о создателе задачи. | Объект |
| checklistItems | Массив объектов с информацией о пунктах чеклиста. | Объект |
| checklistTotal | Количество пунктов в чеклисте. | Число |
| votes | Количество голосов за задачу. | Число |
| assignee | Объект с информацией об исполнителе задачи. | Объект |
| deadline | Крайний срок выполнения задачи. | Строка |
| queue | Объект с информацией об очереди задачи. | Объект |
| updatedAt | Дата и время последнего обновления задачи. | Строка |
| status | Объект с информацией о статусе задачи. | Объект |
| previousStatus | Объект с информацией о предыдущем статусе задачи. | Объект |
| favorite | Признак избранной задачи:true — пользователь добавил задачу в избранное;false — задача не добавлена в избранное. | Число |

**Поля объекта** `updatedBy`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о пользователе. | Строка |
| id | Идентификатор пользователя. | Строка |
| display | Отображаемое имя пользователя. | Строка |
| passportUid | Уникальный идентификатор аккаунта пользователя в организации Яндекс 360 для бизнеса и Яндекс ID. | Число |
| cloudUid | Уникальный идентификатор пользователя в Yandex Cloud Organization. | Строка |

**Поля объекта** `project`
