# Просмотреть логи триггера

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/view-trigger-logs#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/view-trigger-logs#answer)

Запрос позволяет получить для указанного триггера логи выполнения действия [HTTP-запроса](https://yandex.ru/support/tracker/user/set-action.html#create-http).

GET

```
https://api.tracker.yandex.net/v3/queues/<ключ_очереди>/triggers/<id_триггера>/webhooks/log
```

Примечание

По умолчанию запрос возвращает только 10 последних записей логов. Чтобы получить больше записей, используйте параметр [limit](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/view-trigger-logs#limit).

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

Для получения логов используйте HTTP-запрос с методом `GET`:

```
GET /v3/queues/<ключ_очереди>/triggers/<id_триггера>/webhooks/log
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
| <ключ_очереди> | Идентификатор или ключ очереди. Ключ очереди чувствителен к регистру символов. | Строка или число. |
| <id_триггера> | Идентификатор триггера. | Строка |

Параметры запроса
**Дополнительные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| issueId | Идентификатор задачи, в которой произошел запуск триггера. | Строка |
| limit | Количество записей логов в ответе. Значение по умолчанию — 10. Максимальное значение — 100. Пример: limit=100 | Число |
| from | Начало временного диапазона для фильтрации логов в формате YYYY-MM-DDThh:mm:ss.sss±hhmm. | Строка |
| to | Конец временного диапазона для фильтрации логов в формате YYYY-MM-DDThh:mm:ss.sss±hhmm. | Строка |

> Пример 1: Получить 100 последних записей логов, для конкретной задачи.
>
>
> - Используется HTTP-метод GET.
> - Запрос для триггера из очереди `DEV`.
> - ID триггера — 6.
> - Идентификатор задачи — `DEV-123`, в ответе будут логи, связанные только с данной задачей.
> - Задаем максимальное количество записей логов в ответе.
>
>
>  
>  
> ```
> GET /v3/queues/DEV/triggers/6/webhooks/log?issueId=DEV-123&limit=100
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Org-ID: 1234******
> ```

> Пример 2: Получить записи логов за определенный период времени.
>
>
> - Используется HTTP-метод GET.
> - Запрос для триггера из очереди `DEV`.
> - ID триггера — 6.
> - Указываем временной диапазон: 23 сентября 2025 года — с полуночи до 23:59.
>
>
>  
>  
> ```
> GET /v3/queues/DEV/triggers/6/webhooks/log?from=2025-09-23T00:00:00&to=2025-09-23T23:59:59
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Cloud-Org-ID: ab1c******
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело ответа содержит результаты в формате JSON.

```
[
    {
        "startTime": "2025-02-25T14:22:03.596+0000",
        "endTime": "2025-02-25T14:22:03.831+0000",
        "duration": 235,
        "triggerId": 123***,
        "actionId": 1,
        "issueId": "66f682f13f442b**********",
        "request": {
            "method": "POST",
            "endpoint": "https://api.telegram.org/bot123*******:AAHCATQsN**********/sendMessage",
            "headers": {
                "X-Startrek-Transport": "vNCc******/aRh5**********",
                "Content-Type": "PSb4IkZm+OemrDmVvPX0h4uFOP8sKid9vp**********"
            },
            "body": "{\n\"chat_id\":\"-4116*****\",\n\"parse_mode\":\"markdown\",\n\"text\":\"Привет!\"\n}",
            "webhookAuthContext": {
                "type": "noauth"
            }
        },
        "response": {
            "headers": {
                "Access-Control-Expose-Headers": "XXX",
                "Strict-Transport-Security": "XXX",
                "Server": "XXX",
                "Access-Control-Allow-Origin": "XXX",
                "Access-Control-Allow-Methods": "XXX",
                "X-Ya-Instance": "XXX",
                "Connection": "XXX",
                "Content-Length": "XXX",
                "Date": "XXX",
                "Content-Type": "XXX"
            },
            "statusCode": 200
        },
        "id": "67bdd20b604a9c**********"
    }
]
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| startTime | Время начала запуска триггера в формате YYYY-MM-DDThh:mm:ss.sss±hhmm. | Строка |
| endTime | Время завершения запуска триггера в формате YYYY-MM-DDThh:mm:ss.sss±hhmm. | Строка |
| duration | Длительность выполнения запуска триггера в миллисекундах. | Строка |
| triggerId | Идентификатор триггера. | Строка |
| actionId | Идентификатор действия внутри триггера. | Строка |
| issueId | Идентификатор задачи, в которой произошел запуск триггера. | Строка |
| request | Объект с информацией о параметрах отправленного HTTP-запроса. | Объект |
| response | Объект с информацией о параметрах полученного ответа. | Объект |
| id | Идентификатор запуска триггера | Строка |

**Поля объекта** `request`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| method | Метод HTTP-запроса. | Строка |
| endpoint | Адрес ресурса, по которому отправлен HTTP-запрос. | Строка |
| headers | Заголовки HTTP-запроса. | Объект |
| body | Тело HTTP-запроса. | Строка |
| webhookAuthContext | Объект с информацией о способе авторизации запроса. | Объект |

**Поля объекта** `webhookAuthContext`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| type | Способ авторизации. | Строка |

**Поля объекта** `response`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| headers | Заголовки ответа. | Объект |
| statusCode | Код состояния HTTP-запроса. | Число |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

400
Один или несколько параметров запроса имеют недопустимое значение.

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

---
