# Скачать миниатюру

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/get-attachment-preview#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/get-attachment-preview#answer)

Запрос позволяет получить миниатюру графического файла, прикрепленного к задаче.

GET

```
https://api.tracker.yandex.net/v3/issues/<id_задачи>/thumbnails/<id_файла>
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

Чтобы получить миниатюру, используйте HTTP-запрос с методом `GET`.

```
GET /v3/issues/<id_задачи>/thumbnails/<id_файла>
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
| <id_задачи> | Идентификатор или ключ задачи | Строка |
| <id_файла> | Уникальный идентификатор прикрепленного файла | Строка или число |

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело ответа содержит миниатюру графического файла.

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---
