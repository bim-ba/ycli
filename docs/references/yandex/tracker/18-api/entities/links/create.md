# Связать сущности

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/entities/links/ru/api-ref/entities/links/add-links#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/entities/links/ru/api-ref/entities/links/add-links#answer)

Запрос позволяет создать связи между несколькими [сущностями](https://yandex.ru/support/tracker/ru/api-ref/entities/links/ru/api-ref/entities/about-entities).

POST

```
https://api.tracker.yandex.net/v3/entities/<тип_сущности>/<id_сущности>/links
```

Чтобы добавить родительскую сущность для проекта или портфеля, отредактируйте поле `parentEntity` с помощью запроса [Изменить сущность](https://yandex.ru/support/tracker/ru/api-ref/entities/links/ru/api-ref/entities/update-entity).

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/entities/links/ru/api-ref/access).

Для создания связей используйте HTTP-запрос с методом `POST`. Информация о связях передается в теле запроса в формате JSON. Связь создается между текущей сущностью (указывается в `<id_сущности>` запроса) и сущностями, идентификаторы которых указаны в полях `entity` тела запроса.

```
POST /v3/entities/<тип_сущности>/<id_сущности>/links
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
Content-Type: application/json
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

{
  "relationship": "<тип_связи>",
  "entity": "<идентификатор_связываемой_сущности>"
}
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/entities/links/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/entities/links/ru/api-ref/access#iam-token)
- `Content-Type`: формат тела запроса. Должен иметь значение `application/json`.
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Ресурс

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <тип_сущности> | Тип сущности:project — проект;portfolio — портфель;goal — цель | Строка |
| <id_сущности> | Идентификатор сущности. Чтобы получить идентификатор, посмотрите список сущностей. В качестве идентификатора можно использовать параметр id или shortId. | Строка |

Параметры тела запроса
**Обязательные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| relationship | Тип связи. Для проектов и портфелей: depends on — текущая сущность зависит от связанной is dependent by — текущая сущность блокирует связанную works towards — связь проекта с целью Для цели: parent entity — родительская цель child entity — подцель depends on — текущая цель зависит от связанной is dependent by — текущая цель блокирует связанную is supported by — связь с проектом | Строка |
| entity | Идентификатор связанной сущности. | Строка |

> Пример: Создать связь между сущностями
>
>
> - Используется HTTP-метод POST.
>
>
>  
>  
> ```
> POST /v3/entities/project/<id_проекта>/links
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-ID: 1234******
>
> [
>   {
>      "relationship":"is dependent by",
>      "entity": "6582874de6db7f5f********"
>   },
>   {
>      "relationship":"works towards",
>      "entity": "65868f3fe2b9ef74********"
>   }
> ]
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

400
Один или несколько параметров запроса имеют недопустимое значение.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

422
Ошибка валидации JSON, запрос отклонен.

---
