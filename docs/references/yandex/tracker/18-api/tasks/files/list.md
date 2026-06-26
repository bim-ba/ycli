# Получить список прикрепленных файлов

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/get-attachments-list#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/get-attachments-list#answer)

Запрос позволяет получить список файлов, прикрепленных к задаче и к комментариям под ней.

GET

```
https://api.tracker.yandex.net/v3/issues/<id_задачи>/attachments
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

Чтобы получить список прикрепленных файлов, используйте HTTP-запрос с методом `GET`.

```
GET /v3/issues/<id_задачи>/attachments
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

> Пример: Запросить список прикрепленных файлов задачи с ключом `JUNE-2`.
>
>
> - Используется HTTP-метод `GET`.
>
>
>  
>  
> ```
> GET  https://api.tracker.yandex.net/v3/issues/JUNE-2/attachments
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело ответа содержит JSON-массив со списком прикрепленных файлов.

```
[
{
  "self" : "https://api.tracker.yandex.net/v3/issues/JUNE-2/attachments/123***",
  "id" : "123***",
  "name" : "picture.jpg",
  "content" : "https://api.tracker.yandex.net/v3/issues/JUNE-2/attachments/123***/picture.jpg",
  "thumbnail" : "https://api.tracker.yandex.net/v3/issues/JUNE-2/thumbnails/123***",
  "createdBy": {
      "self": "https://api.tracker.yandex.net/v3/users/11********",
      "id": "11********",
      "display": "Имя Фамилия",
      "cloudUid": "ajeppa7dgp53********",
      "passportUid": 11********
  },
  "createdAt" : "2017-06-11T05:11:12.347+0000",
  "mimetype" : "image/jpg",
  "size" : 19090,
  "metadata" : {
    "size" : "550x175"
  }
},
...
]
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который соответствует прикрепленному файлу. | Строка |
| id | Уникальный идентификатор файла. | Строка |
| name | Имя файла. | Строка |
| content | Адрес ресурса для скачивания файла. | Строка |
| thumbnail | Адрес ресурса для скачивания миниатюры предпросмотра. Доступно только для графических файлов. | Строка |
| createdBy | Объект с информацией о пользователе, прикрепившем файл. | Объект |
| createdAt | Дата и время загрузки файла в формате:YYYY-MM-DDThh:mm:ss.sss±hhmm | Строка |
| mimetype | Тип файла, например:text/plain — текстовый файл;image/png — изображение в формате png. | Строка |
| size | Размер файла в байтах. | Целое число |
| metadata | Объект с метаданными файла. | Объект |

**Поля объекта** `createdBy`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса, соответствующего пользователю, загрузившему файл | Строка |
| id | Логин пользователя | Строка |
| display | Имя пользователя (как в интерфейсе) | Строка |

**Поля объекта** `metadata`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| size | Размер изображения в пикселях | Строка |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---
