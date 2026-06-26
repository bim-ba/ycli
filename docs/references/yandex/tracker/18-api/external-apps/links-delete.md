# Удалить внешнюю связь

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/delete-external-link#rec-format)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/delete-external-link#answer)

Запрос позволяет удалить связь задачи с [объектом внешнего приложения](https://yandex.ru/support/tracker/external-links.html).

DELETE

```
https://api.tracker.yandex.net/v3/issues/<id_задачи>/remotelinks/<id_внешней_связи>
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

Чтобы удалить внешнюю связь, используйте HTTP-запрос с методом `DELETE`.

```
DELETE /v3/issues/<id_задачи>/remotelinks/<id_внешней_связи>
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
| <id_задачи> | Идентификатор или ключ текущей задачи. | Строка |
| <id_внешней_связи> | Идентификатор внешней связи. | Строка |

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `204`.

Тело ответа отсутствует.

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

400
Один или несколько параметров запроса имеют недопустимое значение.

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

---
