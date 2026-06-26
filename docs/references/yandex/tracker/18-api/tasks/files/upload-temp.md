# Загрузить временный файл

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/temp-attachment#query)
- [Пример запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/temp-attachment#example)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/temp-attachment#answer)

Запрос позволяет загрузить временный файл. Используйте этот запрос, чтобы предварительно загрузить файл в Трекер, а затем прикрепить его при создании [задачи](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/create-issue) или [комментария](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/add-comment).

Идентификатор временного файла, полученный в ответ на запрос, можно использовать для добавления вложения только один раз.

POST

```
https://api.tracker.yandex.net/v3/attachments/
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

Чтобы добавить временный файл, используйте HTTP-запрос с методом `POST`.

```
POST /v3/attachments/
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
Content-Type: multipart/form-data
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

<файл>
```

Заголовки

- `Host`: адрес узла, предоставляющего API
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access#iam-token)
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

- `Content-Type`: формат тела запроса. Должен иметь значение `multipart/form-data`.

Параметры запроса
**Дополнительные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| filename | Новое имя файла, с которым он будет храниться на сервере. Если параметр не указан, будет использовано собственное имя файла. | Строка |

Параметры тела запроса
**Обязательные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <файл> | Загружаемый файл. Размер файла не должен превышать 1024 Мбит. | Файл |

## Пример запроса

Пример загрузки временного файла с помощью curl:

Unix
Windows

```
curl -X POST 'https://api.tracker.yandex.net/v3/attachments/' \
     -H 'Authorization: OAuth y0__xAbc******' \
     -H 'Content-Type: multipart/form-data' \
     -H 'X-Org-ID: 1234******' \
     --form 'file=@/path/to/image.png'
```

```
curl.exe -X POST "https://api.tracker.yandex.net/v3/attachments/" ^
  -H "Authorization: OAuth y0__xAbc******" ^
  -H "Content-Type: multipart/form-data" ^
  -H "X-Org-ID: 1234******" ^
  --form "file=@C:\Users\Default\Downloads\image.png"
```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `201 Created`.

Тело ответа содержит параметры прикрепленного файла в формате JSON.

```
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
}
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который соответствует прикрепленному файлу. | Строка |
| id | Уникальный идентификатор файла. Используйте его, чтобы прикрепить файл при создании задачи или комментария. | Строка |
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

400
Один или несколько параметров запроса имеют недопустимое значение.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---
