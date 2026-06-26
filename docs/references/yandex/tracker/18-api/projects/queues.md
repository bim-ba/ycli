# Получить список очередей проекта

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/projects/ru/api-ref/projects/get-project-queues#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/projects/ru/api-ref/projects/get-project-queues#answer)

Запрос позволяет получить список очередей, задачи которых попадают в *проект*.

GET

```
https://api.tracker.yandex.net/v3/projects/<id_проекта>/queues
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/projects/ru/api-ref/access).

Чтобы получить список очередей проекта, используйте HTTP-запрос с методом `GET`.

```
GET /v3/projects/<id_проекта>/queues
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/projects/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/projects/ru/api-ref/access#iam-token)
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Ресурс

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <id_проекта> | Идентификатор проекта | Число |

Параметры запроса
**Дополнительные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| expand | Дополнительные поля, которые будут включены в ответ. Если проект содержит несколько очередей, параметры отображаются для каждой очереди:all — все параметры очереди;projects — все проекты организации;components — компоненты очереди;versions — версии очереди;types — типы задач очереди;team — участники команды очереди;workflows — жизненные циклы очереди и их типы задач;fields — обязательные поля очереди;notification_fields — поля в уведомлениях о задачах очереди;issue_types_config — настройки задач очереди;enabled_feaures — настройки интеграций очереди; signature_settings — информация о почтовом ящике очереди: адрес, псевдоним и подпись. | Строка |

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело ответа содержит информацию о проекте в формате JSON.

```
[
    {
        "self": "https://api.tracker.yandex.net/v3/queues/ORG",
        "id": 1,
        "key": "ORG",
        "version": 6,
        "name": "Default",
        "description": "Queue description",
        "lead": {
            "self": "https://api.tracker.yandex.net/v3/users/11********",
            "id": "11********",
            "display": "Имя Фамилия",
            "cloudUid": "ajeppa7dgp53********",
            "passportUid": 11********
        },
        "assignAuto": false,
        "defaultType": {
            "self": "https://api.tracker.yandex.net/v3/issuetypes/2",
            "id": "2",
            "key": "task",
            "display": "Задача"
        },
        "defaultPriority": {
            "self": "https://api.tracker.yandex.net/v3/priorities/3",
            "id": "3",
            "key": "normal",
            "display": "Средний"
        },
        "allowExternalMailing": true,
        "addIssueKeyInEmail": true,
        "denyVoting": false,
        "denyConductorAutolink": false,
        "denyTrackerAutolink": true,
        "useComponentPermissionsIntersection": false,
        "useLastSignature": false
    },
    {
        "self": "https://api.tracker.yandex.net/v3/queues/TEST",
        "id": 3,
        "key": "TEST",
        "version": 8,
        "name": "Testing",
        "description": "Queue description",
        "lead": {
            "self": "https://api.tracker.yandex.net/v3/users/11********",
            "id": "11********",
            "display": "Имя Фамилия",
            "cloudUid": "ajeppa7dgp53********",
            "passportUid": 11********
        },
        "assignAuto": true,
        "defaultType": {
            "self": "https://api.tracker.yandex.net/v3/issuetypes/2",
            "id": "2",
            "key": "task",
            "display": "Задача"
        },
        "defaultPriority": {
            "self": "https://api.tracker.yandex.net/v3/priorities/3",
            "id": "3",
            "key": "normal",
            "display": "Средний"
        },
        "allowExternalMailing": false,
        "addIssueKeyInEmail": false,
        "denyVoting": false,
        "denyConductorAutolink": false,
        "denyTrackerAutolink": false,
        "useComponentPermissionsIntersection": false,
        "useLastSignature": false
    }
]
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию об очереди. | Строка |
| id | Идентификатор очереди. | Число |
| key | Ключ очереди. | Строка |
| version | Версия очереди. Каждое изменение очереди увеличивает номер версии. | Строка |
| name | Название очереди. | Строка |
| description | Текстовое описание очереди. | Строка |
| lead | Блок с информацией о владельце очереди. | Объект |
| assignAuto | Признак автоматического назначения исполнителя для новых задач очереди:true — назначить;false — не назначать. | Логический |
| defaultType | Блок с информацией о типе задачи по умолчанию. | Объект |
| defaultPriority | Блок с информацией о приоритете задачи по умолчанию. | Объект |
| allowExternalMailing | Признак отправки писем на внешние адреса:true — разрешить;false — запретить. | Логический |
| addIssueKeyInEmail | Признак добавления номера задачи в тему письма:true — добавить;false — не добавлять. | Логический |
| denyVoting | Признак запрета голосования за задачи:true – голосование запрещено;false — голосование разрешено. | Логический |
| denyConductorAutolink | Служебный параметр. | Логический |
| denyTrackerAutolink | Признак автоматической связи с задачами других очередей:true — добавить связь;false — не добавлять связь, если ключ задачи из другой очереди добавлен в комментарий или в описание. | Логический |
| useComponentPermissionsIntersection | Способ получения прав доступа к задачам с несколькими компонентами:true — как пересечение прав доступа к компонентам;false — как объединение прав доступа к компонентам. | Логический |
| useLastSignature | Служебный параметр. | Логический |

**Поля объекта** `lead`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о пользователе. | Строка |
| id | Идентификатор пользователя. | Число |
| display | Отображаемое имя пользователя. | Строка |

**Поля объекта** `defaultType`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о типе задаче. | Строка |
| id | Идентификатор типа задачи. | Число |
| key | Ключ типа задачи. | Строка |
| display | Отображаемое название типа задачи. | Строка |

**Поля объекта** `defaultPriority`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о приоритете задаче. | Строка |
| id | Идентификатор приоритета задачи. | Число |
| key | Ключ приоритета задачи. | Строка |
| display | Отображаемое название приоритета задачи. | Строка |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

400
Один или несколько параметров запроса имеют недопустимое значение.

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/projects/ru/api-ref/access).

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

Проект в Трекере — это набор задач, которые направлены на достижение общего результата в определенный срок. У проекта есть дедлайн и ответственный сотрудник. В проект могут входить задачи из разных очередей, поэтому с помощью проектов может быть удобно группировать задачи нескольких команд. [Как управлять проектами](https://yandex.ru/support/tracker/ru/api-ref/projects/ru/manager/create-project)

---
