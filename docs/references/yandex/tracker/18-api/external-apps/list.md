# Получить список внешних приложений

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/get-applications#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/get-applications#answer)

Запрос позволяет получить список внешних приложений, с которыми можно [создать связь](https://yandex.ru/support/tracker/external-links.html).

GET

```
https://api.tracker.yandex.net/v3/applications
```

## Формат запроса

Чтобы получить список доступных внешних приложений, используйте HTTP-запрос с методом `GET`:

```
GET /v3/applications
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

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело ответа содержит информацию о внешних приложениях в формате JSON.

```
[
    {
        "self": "https://api.tracker.yandex.net/v3/applications/my-application",
        "id": "my-application",
        "type": "my-application",
        "name": "Application name"
    },
    ...
]
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о приложении. | Строка |
| id | Идентификатор приложения. | Строка |
| type | Тип приложения. Значение совпадает со значением параметра id. | Строка |
| name | Имя приложения. | Строка |

400
Один или несколько параметров запроса имеют недопустимое значение.

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

500
Внутренняя ошибка сервиса. Попробуйте повторно отправить запрос через некоторое время.

503
Сервис API временно недоступен.

---
