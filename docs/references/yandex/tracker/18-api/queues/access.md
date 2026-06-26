# Выдать права доступа к очереди

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/manage-access#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/manage-access#answer)

Запрос позволяет настроить [доступы к очереди](https://yandex.ru/support/tracker/manager/queue-access.html).

PATCH

```
https://api.tracker.yandex.net/v3/queues/<id_очереди>/permissions
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

Чтобы настроить доступы к очереди, используйте HTTP-запрос с методом `PATCH`. В теле запроса укажите параметры в формате JSON.

```
PATCH /v3/queues/<id_очереди>/permissions
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
Content-Type: application/json
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

{
   "create": {
      "groups": [3, 5]
   },
   "write": {
      "users": {
         "remove": ["username1", "username2"]
      },
      "groups": {
         "add":[4]
       },
      "roles": {
         "add":["author", "assignee"]
      }
   },
   "read": {
      "groups": {
         "add":[4]
       },
      "roles": {
         "add":["follower"]
      }
   },
   "grant": {
      "users": {
         "remove": ["username3",  "username4"]
      }
   }

}
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#iam-token)
- `Content-Type`: формат тела запроса. Должен иметь значение `application/json`.
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Ресурс

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <id_очереди> | Идентификатор или ключ очереди. Ключ очереди чувствителен к регистру символов. | Строка |

Параметры тела запроса
Тело запроса содержит информацию, необходимую для управления доступами.

**Допустимые поля объекта тела запроса**

Укажите в запросе хотя бы одно из полей:

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| create | Разрешения на создание задач в очереди. | Объект |
| write | Разрешения на редактирование задач в очереди. | Объект |
| read | Разрешения на чтение задач в очереди. | Объект |
| grant | Разрешения на изменение настроек очереди. | Объект |

**Допустимые поля объектов, к которым применяются разрешения**

Каждое из полей тела запроса содержит перечень пользователей, групп, ролей, к которым применяется действие разрешения. Укажите в перечне хотя бы одно из полей:

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| users | Список пользователей. | Объект или массив элементов |
| groups | Список групп. | Объект или массив элементов |
| roles | Список ролей. | Объект или массив элементов |

**Допустимые значения полей объектов, к которым применяются разрешения**

В каждом из полей можно указать либо массив идентификаторов, либо объект:

- Если указан массив идентификаторов, то разрешения для данных ресурсов будут созданы или перезаписаны в соответствии с запросом;
- Если указан объект, то разрешения будут добавлены или отозваны в соответствии с указанным ключом:

| Ключ | Описание | Тип данных |
| --- | --- | --- |
| add | Добавить разрешение. | Массив элементов |
| remove | Отозвать разрешение. | Массив элементов |

**Допустимые идентификаторы**

| Тип ресурса | Идентификатор | Описание | Тип данных |
| --- | --- | --- | --- |
| users | login | Логин пользователя. | Строка |
|  | uid | Уникальный идентификатор учетной записи пользователя в Трекере. | Число |
|  | passportUid | Уникальный идентификатор аккаунта пользователя в Яндекс ID. | Число |
|  | cloudUid | Уникальный идентификатор пользователя в Yandex Cloud Organization. | Строка |
|  | trackerUid | Уникальный идентификатор аккаунта пользователя в Трекере. | Число |
| groups | id | Идентификатор группы. Идентификаторы групп можно получить запросом https://api.tracker.yandex.net/v3/groups. | Число |
| roles | role_id | Идентификатор роли: author — Автор, assignee — Исполнитель, follower — Наблюдатель, access — С правом доступа. | Строка |

> Пример 1: Выдать права на создание и редактирование задач в очереди с ключом `TESTQUEUE` пользователю с логином `user1`.
>
>
> - Используется HTTP-метод `PATCH`.
> - Права выдаются пользователю `user1` в очереди с ключом `TESTQUEUE`.
> - В результате запроса имеющиеся у пользователя права в очереди будут перезаписаны.
>
>
>  
>  
> ```
> PATCH /v3/queues/TESTQUEUE/permissions HTTP/1.1
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-ID: 1234******
>
> {
>     "create": {
>        "users": ["user1"]
>     },
>     "write": {
>        "users": ["user1"]
>     }
> }
> ```

> Пример 2: Настроить права доступа к очереди с ключом `TESTQUEUE`:
>
>
> - Используется HTTP-метод `PATCH`.
> - Пользователю `user1` выдается право настройки очереди с ключом `TESTQUEUE`.
> - У пользователя с идентификатором `12345` отзывается право настройки очереди с ключом `TESTQUEUE`.
>
>
>  
>  
> ```
> PATCH /v3/queues/TESTQUEUE/permissions HTTP/1.1
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Cloud-Org-ID: ab1c******
>
> {
>     "grant": {
>        "users": {
>           "add":["user1"],
>           "remove":[12345]
>        }
>     }
> }
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

```
{
    "self": "https://api.tracker.yandex.net/v3/queues/TESTQUEUE/permissions",
    "version": 11,
    "create": {
        "self": "https://api.tracker.yandex.net/v3/queues/TESTQUEUE/permissions/create",
        "users": [
            {
              "self": "https://api.tracker.yandex.net/v3/users/11********",
              "id": "11********",
              "display": "Имя Фамилия",
              "cloudUid": "ajeppa7dgp53********",
              "passportUid": 11********
            }
        ],
        "roles": [
            { "self": "https://api.tracker.yandex.net/v3/roles/author", "id": "author", "display": "Автор" },
            { "self": "https://api.tracker.yandex.net/v3/roles/queue-lead", "id": "queue-lead", "display": "Владелец очереди" },
            { "self": "https://api.tracker.yandex.net/v3/roles/assignee", "id": "assignee", "display": "Исполнитель" }
        ]
    },
    "write": {
        "self": "https://api.tracker.yandex.net/v3/queues/TESTQUEUE/permissions/write",
        "users": [
             {
              "self": "https://api.tracker.yandex.net/v3/users/11********",
              "id": "11********",
              "display": "Имя Фамилия",
              "cloudUid": "ajeppa7dgp53********",
              "passportUid": 11********
            }
        ],
        "roles": [
            { "self": "https://api.tracker.yandex.net/v3/roles/author", "id": "author", "display": "Автор" },
            { "self": "https://api.tracker.yandex.net/v3/roles/queue-lead", "id": "queue-lead", "display": "Владелец очереди" },
            { "self": "https://api.tracker.yandex.net/v3/roles/assignee", "id": "assignee", "display": "Исполнитель" }
        ]
    },
    "grant": {
        "self": "https://api.tracker.yandex.net/v3/queues/TESTQUEUE/permissions/grant",
        "users": [
             {
              "self": "https://api.tracker.yandex.net/v3/users/11********",
              "id": "11********",
              "display": "Имя Фамилия",
              "cloudUid": "ajeppa7dgp53********",
              "passportUid": 11********
            }
        ],
        "roles": [
            { "self": "https://api.tracker.yandex.net/v3/roles/author", "id": "author", "display": "Автор" },
            { "self": "https://api.tracker.yandex.net/v3/roles/queue-lead", "id": "queue-lead", "display": "Владелец очереди" },
            { "self": "https://api.tracker.yandex.net/v3/roles/assignee", "id": "assignee", "display": "Исполнитель" }
        ]
    }
}
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Ссылка на объект выданных доступов в очереди. | Строка |
| version | Номер версии. | Число |
| create | Разрешения на создание задач в очереди. | Объект |
| write | Разрешения на редактирование задач в очереди. | Объект |
| read | Разрешения на чтение задач в очереди. | Объект |
| grant | Разрешения на изменение настроек очереди. | Объект |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---

# Получить информацию о правах доступа пользователя в очереди

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/get-user-access#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/get-user-access#answer)

Запрос позволяет просмотреть [права пользователя](https://yandex.ru/support/tracker/manager/queue-access.html) в очереди.

GET

```
https://api.tracker.yandex.net/v3/queues/<id_очереди>/permissions/users/<логин_или_id_пользователя>
```

Чтобы настроить доступы к очереди при помощи API, используйте запрос [Выдать права доступа к очереди](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/manage-access).

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

Для получения информации о правах используйте HTTP-запрос с методом `GET`.

```
GET v3/queues/<id_очереди>/permissions/users/<логин_или_id_пользователя>
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#iam-token)
- `Content-Type`: формат тела запроса. Должен иметь значение `application/json`.
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Ресурс

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <id_очереди> | Идентификатор или ключ очереди. Ключ очереди чувствителен к регистру символов | Строка или число |
| <логин_или_id_пользователя> | Уникальный идентификатор учетной записи или логин пользователя | Строка или число |

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

```
{
    "user": {
        "self": "https://api.tracker.yandex.net/v3/users/11********",
        "id": "11********",
        "display": "Имя Фамилия",
        "cloudUid": "ajeppa7dgp53********",
        "passportUid": 11********
    },
    "permissions": {
        "CREATE": {
            "users": [
                {
                    "self": "https://api.tracker.yandex.net/v3/users/11********",
                    "id": "11********",
                    "display": "Имя Фамилия",
                    "cloudUid": "ajeppa7dgp53********",
                    "passportUid": 11********
                }
            ],
            "groups": [
                {
                    "self": "https://api.tracker.yandex.net/v3/groups/5",
                    "id": "5",
                    "display": "All users"
                }
            ],
            "roles": [
                {
                    "self": "https://api.tracker.yandex.net/v3/roles/queue-lead",
                    "id": "queue-lead",
                    "display": "Владелец очереди"
                }
            ]
        },
        ...
    },
    "components": [
        {
            "self": "https://api.tracker.yandex.net/v3/components/1",
            "id": "1",
            "display": "Component 1"
        },
        {...}
    ]
}
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| user | Объект с информацией о пользователе, для которого выполняется запрос прав | Объект |
| permissions | Массив объектов с информацией о доступах пользователя в очереди. Возможные значения:GRANT— Настройки очереди;CREATE— Создание задач;READ— Просмотр задач;WRITE— Редактирование задач;DENY— доступ запрещен. Доступы могут быть выданы персонально, на группу или в соответствии с ролью | Массив объектов |
| users | Объект с информацией о пользователе с персональным доступом | Объект |
| groups | Объект с информацией о группе, в которую входит пользователь | Объект |
| roles | Объект с информацией о роли пользователя, для которой настроен доступ | Объект |
| components | Массив объектов с информацией о компонентах, к которым у пользователя есть доступ | Массив объектов |

**Поля объектов** `user` и `users`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о пользователе. | Строка |
| id | Идентификатор пользователя. | Строка |
| display | Отображаемое имя пользователя. | Строка |
| passportUid | Уникальный идентификатор аккаунта пользователя в организации Яндекс 360 для бизнеса и Яндекс ID. | Число |
| cloudUid | Уникальный идентификатор пользователя в Yandex Cloud Organization. | Строка |

**Поля объекта** `groups`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о группе, в которую входит пользователь | Строка |
| id | Идентификатор группы, в которую входит пользователь | Строка |
| display | Отображаемое название группы, в которую входит пользователь | Строка |

**Поля объекта** `roles`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о роли пользователя | Строка |
| id | Идентификатор роли пользователя | Строка |
| display | Отображаемое название роли пользователя | Строка |

**Поля объекта** `components`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о компоненте | Строка |
| id | Идентификатор компонента | Строка |
| display | Отображаемое название компонента | Строка |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---

# Получить информацию о правах доступа группы в очереди

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/get-group-access#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/get-group-access#answer)

Запрос позволяет просмотреть [права группы](https://yandex.ru/support/tracker/manager/queue-access.html) в очереди.

GET

```
https://api.tracker.yandex.net/v3/queues/<id_очереди>/permissions/groups/<id_группы>
```

Чтобы настроить доступы к очереди при помощи API, используйте запрос [Выдать права доступа к очереди](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/manage-access).

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

Для получения информации о правах используйте HTTP-запрос с методом `GET`.

```
GET v3/queues/<id_очереди>/permissions/groups/<id_группы>
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#iam-token)
- `Content-Type`: формат тела запроса. Должен иметь значение `application/json`.
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Ресурс

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <id_очереди> | Идентификатор или ключ очереди. Ключ очереди чувствителен к регистру символов | Строка или число |
| <идентификатор_группы> | Уникальный идентификатор группы в организации | Число |

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

```
{
    "group": {
        "self": "https://api.tracker.yandex.net/v3/groups/5",
        "id": "5",
        "display": "All users"
    },
    "permissions": {
        "CREATE": {
            "groups": [
                {
                    "self": "https://api.tracker.yandex.net/v3/groups/5",
                    "id": "5",
                    "display": "All users"
                }
            ]
        },
        ...
    },
    "components": [
        {
            "self": "https://api.tracker.yandex.net/v3/components/1",
            "id": "1",
            "display": "Component 1"
        },
        {...}
    ]
}
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| group | Объект с информацией о группе, для которой выполняется запрос прав | Объект |
| permissions | Массив объектов с информацией о доступах группы в очереди. Возможные значения:GRANT— Настройки очереди;CREATE— Создание задач;READ— Просмотр задач;WRITE— Редактирование задач;DENY— доступ запрещен | Массив объектов |
| groups | Объект с информацией о группе | Объект |
| components | Массив объектов с информацией о компонентах, к которым у группы есть доступ | Массив объектов |

**Поля объектов** `group` и `groups`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о группе | Строка |
| id | Идентификатор группы | Строка |
| display | Отображаемое название группы | Строка |

**Поля объекта** `components`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о компоненте | Строка |
| id | Идентификатор компонента | Строка |
| display | Отображаемое название компонента | Строка |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---
