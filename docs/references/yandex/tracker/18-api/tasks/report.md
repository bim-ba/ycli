# Создать отчет по задачам

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/create-report#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/create-report#answer)

Запрос позволяет создать отчет по задачам, который формируется на основе заданных критериев поиска задач.

POST

```
https://api.tracker.yandex.net/v3/entities/report/
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

Для создания отчета используйте HTTP-запрос с методом `POST`. Тело запроса содержит параметры отчета и критерии для поиска задач.

```
POST /v3/entities/report/
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
Content-Type: application/json
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

{
  "fields": {
    "summary": "Выгрузка задач",
    "parameters": {
      "type": "issueFilterExport",
      "format": "xlsx",
      "filter": {
        "query": "Queue: SUPPORT \"Sort by\": Updated DESC",
        "sorts": [
          {
            "orderBy": "updated",
            "orderAsc": false
          }
        ]
      },
      "fields": [
        "priority",
        "type",
        "key",
        "summary",
        "assignee",
        "status",
        "updated"
      ]
    }
  }
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

| Параметр | Описание | Формат |
| --- | --- | --- |
| fields | Объект с параметрами отчета. | Объект |

**Поля объекта** `fields`

| Параметр | Описание | Формат |
| --- | --- | --- |
| summary | Название отчета. | Строка |
| parameters | Объект с настройками экспорта. | Объект |

**Поля объекта** `parameters`

| Параметр | Описание | Формат |
| --- | --- | --- |
| type | Тип экспорта. Значение: issueFilterExport. | Строка |
| format | Формат выгрузки. Значения: xlsx, xml, csv. | Строка |
| filter | Объект с параметрами фильтрации задач. | Объект |
| fields | Список полей задачи, которые будут включены в отчет. Например: priority, type, key, summary, assignee, status, updated. | Массив строк |

**Поля объекта** `filter`

| Параметр | Описание | Формат |
| --- | --- | --- |
| query | Фильтр на языке запросов. | Строка |
| filter | Параметры фильтрации задач. В параметре можно указать название любого поля и значение, по которому будет производиться фильтрация. Полный список полей задачи | Объект |
| filterId | Идентификатор сохраненного фильтра. | Число |
| sorts | Массив объектов с параметрами сортировки. | Массив объектов |

Вы можете использовать один из следующих параметров:

- `query` — фильтр на языке запросов;
- `filter` — объект с параметрами фильтрации;
- `filterId` — идентификатор сохраненного фильтра.

Использование нескольких параметров одновременно не поддерживается.

**Поля объекта** `sorts`

| Параметр | Описание | Формат |
| --- | --- | --- |
| orderBy | Поле для сортировки. | Строка |
| orderAsc | Направление сортировки: true — по возрастанию, false — по убыванию. | Логический |

> Пример 1: Создание отчета с использованием языка запросов
>
>
> - Отчет по задачам в формате XLSX.
> - Отчет содержит задачи из очереди «SUPPORT».
> - Результаты отсортированы по дате обновления в убывающем порядке.
> - В отчет включены поля: приоритет, тип, ключ, название, исполнитель, статус, дата обновления.
>
>
>  
>  
> ```
> POST /v3/entities/report/ HTTP/1.1
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-ID: 1234******
>
> {
>   "fields": {
>     "summary": "Выгрузка задач очереди SUPPORT",
>     "parameters": {
>       "type": "issueFilterExport",
>       "format": "xlsx",
>       "filter": {
>         "query": "Queue: SUPPORT \"Sort by\": Updated DESC",
>         "sorts": [
>           {
>             "orderBy": "updated",
>             "orderAsc": false
>           }
>         ]
>       },
>       "fields": [
>         "priority",
>         "type",
>         "key",
>         "summary",
>         "assignee",
>         "status",
>         "updated"
>       ]
>     }
>   }
> }
> ```

> Пример 2: Создание отчета с использованием объекта фильтрации
>
>
> - Отчет по задачам в формате XLSX.
> - Отчет формируется по параметрам: задачи из очереди «TREK», у которых нет исполнителя.
> - В отчет включены основные поля задачи.
>
>
>  
>  
> ```
> POST /v3/entities/report/ HTTP/1.1
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Cloud-Org-ID: ab1c******
>
> {
>   "fields": {
>     "summary": "Задачи без исполнителя",
>     "parameters": {
>       "type": "issueFilterExport",
>       "format": "xlsx",
>       "filter": {
>         "filter": {
>           "queue": "TREK",
>           "assignee": "empty()"
>         }
>       },
>       "fields": [
>         "key",
>         "summary",
>         "status",
>         "priority",
>         "created"
>       ]
>     }
>   }
> }
> ```

> Пример 3: Создание отчета с использованием сохраненного фильтра
>
>
> - Отчет по задачам в формате XLSX.
> - Отчет создается на основе сохраненного фильтра с ID `12345`.
> - В отчет включены основные поля задачи.
>
>
>  
>  
> ```
> POST /v3/entities/report/ HTTP/1.1
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-ID: 1234******
>
> {
>   "fields": {
>     "summary": "Отчет по сохраненному фильтру",
>     "parameters": {
>       "type": "issueFilterExport",
>       "format": "xlsx",
>       "filter": {
>         "filterId": 12345
>       }
>       "fields": [
>         "key",
>         "summary",
>         "status",
>         "assignee",
>         "priority",
>         "updated"
>       ]
>     }
>   }
> }
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело ответа содержит информацию о созданном отчете в формате JSON.

```
{
    "self": "https://api.tracker.yandex.net/v3/entities/report/68f68b553cdc3969e0445570",
    "id": "68f68b553cdc3969e0445570",
    "version": 1,
    "shortId": 142,
    "entityType": "report",
    "createdBy": {
        "self": "https://api.tracker.yandex.net/v3/users/8000000000000004",
        "id": "8000000000000004",
        "display": "Имя Фамилия",
        "cloudUid": "aje71i6t2tuvanuoimem",
        "passportUid": 1234567890
    },
    "createdAt": "2025-10-20T19:19:49.120+0000",
    "updatedAt": "2025-10-20T19:19:49.120+0000"
}
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию об отчете. | Строка |
| id | Идентификатор отчета. Чтобы открыть отчет в интерфейсе Трекера, подставьте идентификатор в адрес и откройте его в браузере: https://tracker.yandex.ru/pages/reports/<id_отчета> | Строка |
| version | Версия отчета. | Число |
| shortId | Короткий идентификатор отчета. | Число |
| entityType | Тип сущности. Значение: report. | Строка |
| createdBy | Объект с информацией о создателе отчета. | Объект |
| createdAt | Дата и время создания отчета в формате YYYY-MM-DDThh:mm:ss.sss±hhmm. | Строка |
| updatedAt | Дата и время последнего обновления отчета в формате YYYY-MM-DDThh:mm:ss.sss±hhmm. | Строка |

**Поля объекта** `createdBy`

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

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

Фильтр в Трекере — это инструмент, который позволяет искать задачи по параметрам. Например, найти все задачи в заданной очереди, у которых вы автор или исполнитель. [Как настроить фильтр задач](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/user/create-filter)

---
