# Получить список типов задач

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/admin/ru/api-ref/admin/get-issue-types#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/admin/ru/api-ref/admin/get-issue-types#answer)

Запрос позволяет получить список доступных [типов задач](https://yandex.ru/support/tracker/add-ticket-type.html).

GET

```
https://api.tracker.yandex.net/v3/issuetypes
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/admin/ru/api-ref/access).

Чтобы получить список типов задач, используйте HTTP-запрос с методом `GET`:

```
GET /v3/issuetypes
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/admin/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/admin/ru/api-ref/access#iam-token)
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело ответа содержит JSON-объект со списком типов задач.

```
[
    {
    "self": "https://api.tracker.yandex.net/v3/issuetypes/1",
    "id": 1,
    "version": 1,
    "key": "task",
    "name": "Задача",
    "description": "A task that needs to be done."
    }
]
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о типе задачи. | Строка |
| id | Уникальный идентификатор типа задачи в Трекере. | Число |
| version | Версия типа задачи. | Число |
| key | Ключ типа задачи. | Строка |
| name | Отображаемое название типа задачи. | Строка |
| description | Описание типа задачи. | Строка |
| deleted | Признак удаленного типа задачи:true — тип задачи удален;параметр отсутствует, если тип задачи не удален. | Логический |

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/admin/ru/api-ref/access).

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---
