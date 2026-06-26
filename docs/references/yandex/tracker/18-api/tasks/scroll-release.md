# Освободить ресурсы просмотра прокрутки

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/search-release#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/search-release#answer)

Запрос позволяет освободить ресурсы после просмотра слепка поиска в запросе [Найти задачи](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/search-issues).

POST

```
https://api.tracker.yandex.net/v3/system/search/scroll/_clear
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

Для освобождения результатов прокрутки используйте HTTP-запрос с методом `POST`:

```
POST /v3/system/search/scroll/_clear
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
Content-Type: application/json
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

{
    "srollId": "scrollToken"
}
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access#iam-token)
- `Content-Type`: формат тела запроса. Должен иметь значение `application/json`.
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Параметры тела запроса
**Обязательные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| scrollId | Идентификатор страницы результатов прокрутки. Значение идентификатора указывается из заголовка X-Scroll-Id ответа на запрос Найти задачи. | Строка |
| scrollToken | Токен, удостоверяющий принадлежность запроса текущему пользователю. Значение идентификатора указывается из заголовка X-Scroll-Token ответа на запрос Найти задачи. | Строка |

В запросе необходимо передать все пары `"srollId": "scrollToken"` вашего запроса. Количество таких пар равно количеству страниц с результатами поискового запроса.

> Освобождение результатов прокрутки:
>
>
> - Используется HTTP-метод POST.
>
>
>  
>  
> ```
> POST /v3/system/search/scroll/_clear HTTP/1.1
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-ID: 1234******
>
> {
>   "cXVlcnlUaGVuRmV0Y2g7NjsyNDU5MzpmQ0gwd0JOM1RvQ2NPM3ZJRkpfTnFBOzI0NTkyOmZDSDB3Qk4zVG9DY08zdklGSl9OcUE7MjQ1OTU6ZkNIMHdCTjNUb0NjTzN2SUZKX05xQTsyNDU5NDpmQ0gwd0JOM1RvQ2NPM3ZJRkpfTnFBOzIwMzg2OkNfVnFZdHZCU3Y2VUowT0N6dGVGdFE7MjAzODE6U3RqelpvSWZTYmVFX2VZYWRBcX********==": "c44356850f446b88e5b5cd65a34a1409aaaa0ec1b93f8925d6b1c91d********:14503********",
>   "cXVlcnlUaGVuRmV0Y2g7NjsyMDQ0MzpTdGp6Wm9JZlNiZUVfZVlhZEFxeXNnOzIwNDQ1OkNfVnFZdHZCU3Y2VUowT0N6dGVGdFE7MjA0NDI6U3RqelpvSWZTYmVFX2VZYWRBcXlzZzsyMDQ0NDpDX1ZxWXR2QlN2NlVKME9DenRlRnRROzI0NjcxOmZDSDB3Qk4zVG9DY08zdklGSl9OcUE7MjQ2NzI6ZkNIMHdCTjNUb0NjTzN2SUZKX0********==": "b8e1c56966f037d9c4e241af40d31dc80af186fa079d75022822b2be********:14525********"
> }
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

400
Один или несколько параметров запроса имеют недопустимое значение.

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

---
