# Удалить комментарий

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/entities/comments/delete-comment#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/entities/comments/delete-comment#answer)

Запрос позволяет удалить комментарий [сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/entities/about-entities).

DELETE

```
https://api.tracker.yandex.net/v3/entities/<тип_сущности>/<id_сущности>/comments/<id_комментария>
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/entities/comments/ru/api-ref/access).

Для удаления комментария используйте HTTP-запрос с методом `DELETE`.

```
DELETE /v3/entities/<тип_сущности>/<id_сущности>/comments/<id_комментария>
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
| notify | Уведомлять пользователей, которые указаны в полях Автор, Ответственный, Участники, Заказчики и Наблюдатели. Значение по умолчанию — true. | Логический |
| notifyAuthor | Уведомлять автора изменений. Значение по умолчанию — false. | Логический |

> Пример: Удалить комментарий
>
>
> - Используется HTTP-метод DELETE.
>
>
>  
>  
> ```
> DELETE https://api.tracker.yandex.net/v3/entities/project/<id_проекта>/comments/16
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `204`.

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

400
Один или несколько параметров запроса имеют недопустимое значение.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

422
Ошибка валидации JSON, запрос отклонен.

---
