# Изменить метрики сущности

- [Добавить или изменить метрики](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/metric#patch-metrics)
- [Получить метрики сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/metric#get-metrics)
- [Удалить метрики](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/metric#delete-metrics)

Для работы с метриками в проектах, портфелях и целях используется параметр сущности `metricItems`.

См. подробнее:

- [Дополнительные параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/about-entities#query-params).
- [Метрики в проекте](https://yandex.ru/support/tracker/manager/create-project.html#add-metrics).

## Добавить или изменить метрики

Чтобы добавить или изменить список метрик в проекте, портфеле или цели, используйте запрос [Изменить сущность](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/update-entity). В теле запроса передайте объект `fields` с вложенным массивом  `metricItems`: см. [Дополнительные параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/about-entities#query-params).

**Параметры объектов массива** `metricItems`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| text | Название метрики. Обязательный параметр | Строка |
| url | Ссылка виджета для iframe | Строка |

> Пример 1: Добавить в цель две метрики. Если в цели уже есть метрики, они будут заменены новыми.
>
>
>
>
> ```
> PATCH /v3/entities/goal/655f328********?fields=metricItems
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Org-ID: 1234******
>
> {
>  "fields": {
>    "metricItems": [
>      {
>        "text": "First metric",
>        "url": "https://tracker.yandex.ru/dashboard/12/widget/34?_embedded=1&_no_controls=1"
>      },
>      {
>        "text": "Second metric",
>        "url": "https://tracker.yandex.ru/dashboard/23/widget/45?_embedded=1&_no_controls=1"
>      }
>    ]
>  }
> }
> ```

> Пример 2: Добавить к существующим метрикам проекта одну новую.
>
>
>
>
> ```
> PATCH /v3/entities/project/655f8cc52*****?fields=metricItems
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Cloud-Org-ID: ab1c******
>
> {
>  "fields": {
>    "metricItems": {
>      "add": {
>        "text": "My metric",
>        "url": "https://tracker.yandex.ru/dashboard/12/widget/34?_embedded=1&_no_controls=1"
>      }
>    }
>  }
> }
> ```

## Получить метрики сущности

Чтобы получить метрики проекта, портфеля или цели, используйте запрос [Получить параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/get-entity) с параметром `fields=metricItems`:

```
GET https://api.tracker.yandex.net/v3/entities/<тип_сущности>/<id_сущности>?fields=metricItems
```

Параметры массива ключевых результатов `metricItems` приведены в разделе [Дополнительные параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/about-entities#query-params).

## Удалить метрики

Для удаления метрик проекта, портфеля или цели используйте запрос [Изменить сущность](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/update-entity):

- Чтобы удалить все метрики, передайте значение `"metricItems": null`.
- Чтобы удалить одну или несколько метрик, обновите список (см. [Добавить или изменить метрики](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/metric#patch-metrics)) или используйте оператор `remove`.

> Пример 1. Удалить все метрики цели.
>
>
>
>
> ```
> PATCH /v3/entities/goal/655f328********?fields=metricItems
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Org-ID: 1234******
>
> {
>  "fields": {
>        "metricItems": null
>    }
> }
> ```

> Пример 2. Удалить одну метрику из списка.
>
>
>
>
> ```
> PATCH /v3/entities/project/655f8cc52*****?fields=metricItems
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> X-Cloud-Org-ID: ab1c******
>
> {
>   "fields": {
>      "metricItems": {
>          "remove": {
>              "id": "6789*******",
>              "text": "My metric",
>              "url": "https://tracker.yandex.ru/dashboard/12/widget/34?_embedded=1&_no_controls=1"
>          }
>      }
>   }
> }
> ```

При удалении конкретной метрики из списка требуется передать объект с параметрами метрики в том же формате, в котором метрика возвращается в ответ на запрос [Получить параметры сущности](https://yandex.ru/support/tracker/ru/api-ref/entities/ru/api-ref/entities/get-entity).

---
