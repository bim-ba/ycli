# Создать версию очереди

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/create-version#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/create-version#answer)

Запрос позволяет создать [версию в очереди](https://yandex.ru/support/tracker/manager/versions.html).

POST

```
https://api.tracker.yandex.net/v3/versions/
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

Чтобы создать версию очереди используйте HTTP-запрос с методом `POST`. В теле запроса укажите параметры в формате JSON.

```
POST /v3/versions/
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
Content-Type: application/json
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

{
   "queue": "<ключ_очереди>",
   "name": "<название_версии>"
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

Параметры тела запроса
Тело запроса содержит информацию, необходимую для создания новой версии очереди:

**Обязательные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| queue | Ключ очереди. | Строка |
| name | Название версии. | Строка |

**Дополнительные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| description | Описание версии. | Строка |
| startDate | Дата начала версии в формате YYYY-MM-DD. | Строка |
| dueDate | Дата завершения версии в формате YYYY-MM-DD. | Строка |

> Пример: Создать версию очереди `Test Queue`.
>
>
> - Используется HTTP-метод `POST`.
> - Создается версия очереди с ключом `TESTQUEUE`.
> - Задается название версии `version 0.1`.
> - Задается описание версии `Test version 1`.
> - Задается дата начала версии `2023.10.03`.
> - Задается дата завершения версии `2024.06.03`.
>
>
>  
>  
> ```
> POST /v3/queues/TEST/versions HTTP/1.1
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-ID: 1234******
> {
>   "queue": "TESTQUEUE",
>   "name": "version 0.1",
>   "description": "Test version 1",
>   "startDate": "2023-10-03",
>   "dueDate": "2024-06-03"
> }
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

```
[
    {
        "self": "https://api.tracker.yandex.net/v3/versions/1",
        "id": 1,
        "version": 1,
        "queue": {
            "self": "https://api.tracker.yandex.net/v3/queues/TESTQUEUE",
            "id": "6",
            "key": "TESTQUEUE",
            "display": "Test Queue"
        },
        "name": "version 0.1",
        "description": "Test version 1",
        "startDate": "2023-10-03",
        "dueDate": "2024-06-03",
        "released": false,
        "archived": false
    }
]
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Ссылка на объект версии. | Строка |
| id | Идентификатор версии. | Число |
| version | Номер версии. | Число |
| queue | Объект с информацией об очереди. | Объект |
| name | Название версии. | Строка |
| description | Текстовое описание версии. | Строка |
| startDate | Дата начала версии. | Строка |
| dueDate | Дата завершения версии. | Строка |
| released | Признак выпущенной версии. | Логический |
| archived | Признак архивной версии. | Логический |

**Поля объекта** `queue`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию об очереди. | Строка |
| id | Идентификатор очереди. | Строка |
| key | Ключ очереди. | Строка |
| display | Отображаемое название очереди. | Строка |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---

# Получить версии очереди

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/get-versions#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/get-versions#answer)

Запрос позволяет получить информацию о [версиях очереди](https://yandex.ru/support/tracker/manager/versions.html). Очередь выбирается при указании идентификатора или ключа.

GET

```
https://api.tracker.yandex.net/v3/queues/<id_очереди>/versions
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

Для получения версий очереди используйте HTTP-запрос с методом `GET`.

```
GET /v3/queues/<id_очереди>/versions
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#iam-token)
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Ресурс

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <id_очереди> | Идентификатор или ключ очереди. Ключ очереди чувствителен к регистру символов. | Строка или число |

> Пример: Получить версии очереди `TEST`.
>
>
> - Используется HTTP-метод `GET`.
>
>
>  
>  
> ```
> GET https://api.tracker.yandex.net/v3/queues/TEST/versions
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

```
[
    {
        "self": "https://api.tracker.yandex.net/v3/versions/49***",
        "id": 49***,
        "version": 1,
        "queue": {
            "self": "https://api.tracker.yandex.net/v3/queues/JUNE",
            "id": "1928",
            "key": "JUNE",
            "display": "june"
        },
        "name": "My version",
        "description": "iohb ±!@#$%^&*()_+=-/\\?<>.,/§:»'|;",
        "startDate": "2017-06-09",
        "dueDate": "20227-06-09",
        "released": false,
        "archived": false
    },
    ...
]
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Ссылка на объект версии | Строка |
| id | Идентификатор версии | Число |
| version | Номер версии | Число |
| queue | Объект с информацией об очереди | Объект |
| name | Название версии | Строка |
| description | Текстовое описание версии | Строка |
| startDate | Начальная дата очереди | Строка |
| dueDate | Конечная дата очереди | Строка |
| released | Признак выпущенной версии | Логический |
| archived | Признак архивной версии | Логический |

**Поля объекта** `queue`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию об очереди. | Строка |
| id | Идентификатор очереди. | Строка |
| key | Ключ очереди. | Строка |
| display | Отображаемое название очереди. | Строка |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---
