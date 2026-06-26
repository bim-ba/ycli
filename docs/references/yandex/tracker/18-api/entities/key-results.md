# Изменить ключевые результаты цели

- [Добавить или изменить ключевые результаты](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/keyresults#patch-key-results)
- [Получить ключевые результаты цели](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/keyresults#get-key-results)
- [Удалить ключевые результаты](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/keyresults#delete-key-results)

Для работы с ключевыми результатами используется параметр цели `keyResultItems`.

См. подробнее:

- [Дополнительные параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/about-entities#query-params).
- [Ключевые результаты цели](https://yandex.ru/support/tracker/goals/goals-settings.html#key-results).

## Добавить или изменить ключевые результаты

Чтобы добавить или изменить список ключевых результатов цели, используйте запрос [Изменить сущность](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/update-entity). В теле запроса передайте объект `fields` с вложенным массивом  `keyResultItems`: см. [Дополнительные параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/about-entities#query-params).

**Параметры объектов массива** `keyResultItems`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| type | Способ измерения прогресса ключевого результата: value — по значению; binary — по факту выполнения. Обязательный параметр | Строка |
| text | Текст ключевого результата. Обязательный параметр | Строка |
| assignee | Идентификатор или логин пользователя, который является исполнителем ключевого результата | Число или строка |
| deadline | Дедлайн ключевого результата | Объект |
| progress | Количественные показатели измерения прогресса. Обязательный параметр при измерении прогресса «по значению» (value) | Объект |
| achieved | Признак достижения ключевого результата при измерении прогресса «по факту выполнения» (binary). Допустимые значения: true, false | Логический |

**Параметры объекта** `deadline`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| date | Дата дедлайна в формате YYYY-MM-DD. Обязательный параметр | Строка |
| deadlineType | Тип дедлайна, для ключевых результатов имеет значение date. Обязательный параметр | Строка |

**Параметры объекта** `progress`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| start | Начальное значение показателя. Обязательный параметр | Число |
| end | Конечное значение показателя. Обязательный параметр | Число |
| current | Текущее значение показателя | Число |

> Пример 1: Добавить в цель список из двух ключевых результатов. Если в цели уже есть ключевые результаты, они будут заменены новыми.
>
>
>
>
> ```
> PATCH /v3/entities/goal/655f328********?fields=keyResultItems
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Org-ID: 1234******
>
> {
>  "fields": {
>    "keyResultItems": [
>       {
>         "type": "value",
>         "text": "Key result 1",
>         "assignee": "username1",
>         "deadline": {"date": "2025-06-03", "deadlineType": "date"},
>         "progress": {
>             "start": 1,
>             "end": 10,
>             "current": 5
>         }
>       },
>       {
>         "type": "binary",
>         "text": "Key result 2",
>         "assignee": "username2",
>         "deadline": {"date": "2025-06-03", "deadlineType": "date"},
>         "achieved": false
>       }
>    ]
>  }
> }
> ```

> Пример 2: Добавить к существующим ключевым результатам один пункт.
>
>
>
>
> ```
> PATCH /v3/entities/goal/655f328********?fields=keyResultItems
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Cloud-Org-ID: ab1c******
>
> {
>  "fields": {
>    "keyResultItems": {
>      "add": {
>        "type": "binary",
>        "text": "Key result 3",
>        "assignee": "username1"
>      }
>    }
>  }
> }
> ```

## Получить ключевые результаты цели

Чтобы получить список ключевых результатов цели, используйте запрос [Получить параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/get-entity) с параметром `fields=keyResultItems`:

```
GET https://api.tracker.yandex.net/v3/entities/goal/<id_цели>?fields=keyResultItems
```

Параметры массива ключевых результатов `keyResultItems` приведены в разделе [Дополнительные параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/about-entities#query-params).

## Удалить ключевые результаты

Для удаления ключевых результатов используйте запрос [Изменить сущность](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/update-entity):

- Чтобы удалить все ключевые результаты цели, передайте значение `"keyResultItems": null`.
- Чтобы удалить один или несколько ключевых результатов, обновите список (см. [Добавить или изменить ключевые результаты](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/keyresults#patch-key-results)) или используйте оператор `remove`.

> Пример 1. Удалить все ключевые результаты цели.
>
>
>
>
> ```
> PATCH /v3/entities/goal/655f328********?fields=keyResultItems
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Org-ID: 1234******
>
> {
>  "fields": {
>        "keyResultItems": null
>    }
> }
> ```

> Пример 2. Удалить один ключевой результат из списка.
>
>
>
>
> ```
> PATCH /v3/entities/goal/655f328********?fields=keyResultItems
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Cloud-Org-ID: ab1c******
>
> {
>   "fields": {
>      "keyResultItems": {
>          "remove": {
>              "id": "6789*******",
>              "type": "binary",
>              "text": "My key result",
>              "assignee": {
>                  "self": "https://api.tracker.yandex.net/v3/users/11********",
>                  "id": "11********",
>                  "display": "Имя Фамилия",
>                  "cloudUid": "ajevuhegoggf********",
>                  "passportUid": 11********
>              }
>          }
>      }
>   }
> }
> ```

При удалении конкретного пункта из списка ключевых результатов требуется передать объект с параметрами пункта в том же формате, в котором ключевой результат возвращается в ответ на запрос [Получить параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/get-entity).

---
