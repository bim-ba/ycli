# Получить комментарий сущности

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/entities/comments/get-comment#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/entities/comments/get-comment#answer)

Запрос позволяет получить комментарий [сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/entities/about-entities).

GET

```
https://api.tracker.yandex.net/v3/entities/<тип_сущности>/<id_сущности>/comments/<id_комментария>
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/access).

Для получения комментария используйте HTTP-запрос с методом `GET`.

```
GET /v3/entities/<тип_сущности>/<id_сущности>/comments/<id_комментария>
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/access#iam-token)
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Ресурс

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <тип_сущности> | Тип сущности:project — проект;portfolio — портфель;goal — цель | Строка |
| <id_сущности> | Идентификатор сущности. Чтобы получить идентификатор, посмотрите список сущностей. | Строка |
| <id_комментария> | Уникальный идентификатор комментария. | Строка или число |

Параметры запроса
**Дополнительные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| expand | Дополнительная информация, которая будет включена в ответ: all — все;html — HTML-разметка комментария;attachments — вложенные файлы;reactions — реакции на комментарий. | Строка |

> Пример: Получить комментарий
>
>
> - Используется HTTP-метод GET.
> - В ответе выводится информация о комментарии.
>
>
>  
>  
> ```
> GET https://api.tracker.yandex.net/v3/entities/project/<id_проекта>/comments/15?expand=all
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело ответа содержит информацию о комментарии сущности в формате JSON.

```
{
    "self": "https://api.tracker.yandex.net/v3/entities/project/6586d6fee2b9ef74********/comments/15",
    "id": 15,
    "longId": "65a156a29d5d2000********",
    "text": "Комментарий **номер один.**",
    "textHtml": "<p>Комментарий <strong>номер один.</strong></p>\n",
    "attachments": [
        {
            "self": "https://api.tracker.yandex.net/v3/entities/project/6586d6fee2b9ef74********/attachments/25",
            "id": "25",
            "display": "image.jpg"
        }
    ],
    "createdBy": {
        "self": "https://api.tracker.yandex.net/v3/users/11********",
        "id": "11********",
        "display": "Имя Фамилия",
        "cloudUid": "ajeppa7dgp53********",
        "passportUid": 11********
    },
    "updatedBy": {
        "self": "https://api.tracker.yandex.net/v3/users/11********",
        "id": "11********",
        "display": "Имя Фамилия",
        "cloudUid": "ajeppa7dgp53********",
        "passportUid": 11********
    },
    "createdAt": "2024-01-12T15:11:30.278+0000",
    "updatedAt": "2024-01-12T16:33:35.988+0000",
    "usersReacted": {
        "like": [
            {
                "self": "https://api.tracker.yandex.net/v3/users/11********",
                "id": "11********",
                "display": "Имя Фамилия",
                "cloudUid": "ajeppa7dgp71********",
                "passportUid": 11********
            }
        ]
    },
    "ownReactions": ["like"],
    "summonees": [
        {
            "self": "https://api.tracker.yandex.net/v3/users/11********",
            "id": "11********",
            "display": "Имя Фамилия",
            "cloudUid": "ajeppa7dgp32********",
            "passportUid": 11********
        }
    ],
    "version": 3,
    "type": "standard",
    "transport": "internal"
}
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Ссылка на объект комментария. | Строка |
| id | Идентификатор комментария. | Число |
| longId | Идентификатор комментария в виде строки. | Строка |
| text | Текст комментария. | Строка |
| textHtml | HTML-разметка комментария. | Строка |
| attachments | Вложения. | Строка |
| createdBy | Объект с информацией о создателе комментария. | Объект |
| updatedBy | Объект с информацией о сотруднике, внесшем последнее изменение в комментарий. | Объект |
| createdAt | Дата и время создания комментария в формате:YYYY-MM-DDThh:mm:ss.sss±hhmm. | Строка |
| updatedAt | Дата и время обновления комментария в формате:YYYY-MM-DDThh:mm:ss.sss±hhmm. | Строка |
| usersReacted | Реакции пользователей (присутствует в ответе, если в запросе для параметра expand указано значение all или reactions):like;dislike;laugh;tada;hooray;confused;heart;rocket;eyes;fire;ok;facepalm;check. | Объект со списком реакций и отреагировавших |
| reactionsCount | Количество реакций (присутствует в ответе, если в запросе для параметра expand не указано значение all или reactions). | Объект со списком и количеством реакций |
| ownReactions | Реакции автора комментария:like;dislike;laugh;tada;hooray;confused;heart;rocket;eyes;fire;ok;facepalm;check. | Список строк |
| summonees | Список вызываемых в комментарии пользователей. | Список объектов |
| version | Версия комментария. Каждое изменение комментария увеличивает номер версии. | Число |
| type | Тип комментария:standart — отправлен через интерфейс Трекера;incoming — создан из входящего письма;outcoming — создан из исходящего письма. | Строка |
| transport | Способ добавления комментария:internal — через интерфейс Трекера;email — через письмо. | Строка |

**Поля объекта** `createdBy`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о пользователе. | Строка |
| id | Идентификатор пользователя. | Строка |
| display | Отображаемое имя пользователя. | Строка |
| passportUid | Уникальный идентификатор аккаунта пользователя в организации Яндекс 360 для бизнеса и Яндекс ID. | Число |
| cloudUid | Уникальный идентификатор пользователя в Yandex Cloud Organization. | Строка |

**Поля объекта** `updatedBy`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о пользователе. | Строка |
| id | Идентификатор пользователя. | Строка |
| display | Отображаемое имя пользователя. | Строка |
| passportUid | Уникальный идентификатор аккаунта пользователя в организации Яндекс 360 для бизнеса и Яндекс ID. | Число |
| cloudUid | Уникальный идентификатор пользователя в Yandex Cloud Organization. | Строка |

**Поля объекта** `usersReacted`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о пользователе. | Строка |
| id | Идентификатор пользователя. | Строка |
| display | Отображаемое имя пользователя. | Строка |
| passportUid | Уникальный идентификатор аккаунта пользователя в организации Яндекс 360 для бизнеса и Яндекс ID. | Число |
| cloudUid | Уникальный идентификатор пользователя в Yandex Cloud Organization. | Строка |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

400
Один или несколько параметров запроса имеют недопустимое значение.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

422
Ошибка валидации JSON, запрос отклонен.

---
