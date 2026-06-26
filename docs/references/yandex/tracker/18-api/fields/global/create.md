# Создать поле задачи

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/create-field#query)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/issues/create-field#answer)

Запрос позволяет создать [глобальное поле](https://yandex.ru/support/tracker/user/create-param.html#global-field) задачи.

POST

```
https://api.tracker.yandex.net/v3/fields
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

Чтобы создать поле, используйте HTTP-запрос с методом `POST`. В теле запроса укажите параметры в формате JSON:

```
POST /v3/fields
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
Content-Type: application/json
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

{
    "name":
    {
        "en": "Название на английском языке",
        "ru": "Название на русском языке"
    },
    "id": "global_field_key",
    "category": "0000000000000001********",
    "type": "ru.yandex.startrek.core.fields.StringFieldType"
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
| name | Название поля:en — на английском языке;ru — на русском языке. | Строка |
| id | Идентификатор поля. | Строка |
| category | Объект с информацией о категории поля.Чтобы получить список всех категорий, используйте HTTP запрос:GET /v3/fields/categories | Строка |
| type | Тип поля:ru.yandex.startrek.core.fields.DateFieldType — Дата;ru.yandex.startrek.core.fields.DateTimeFieldType — Дата/Время;ru.yandex.startrek.core.fields.StringFieldType — Текстовое однострочное поле;ru.yandex.startrek.core.fields.TextFieldType — Текстовое многострочное поле;ru.yandex.startrek.core.fields.FloatFieldType — Дробное число;ru.yandex.startrek.core.fields.IntegerFieldType — Целое число;ru.yandex.startrek.core.fields.UserFieldType — Имя пользователя;ru.yandex.startrek.core.fields.UriFieldType — Ссылка. | Строка |

**Дополнительные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| optionsProvider | Объект с информацией об элементах списка. | Объект |
| order | Порядковый номер в списке полей организации: https://tracker.yandex.ru/admin/fields. | Число |
| description | Описание поля. | Строка |
| readonly | Возможность редактировать значение поля:true — значение поля нельзя изменить;false — значение поля можно изменить. | Логический |
| visible | Признак отображения поля в интерфейсе:true — всегда отображать поле в интерфейсе;false — не отображать поле в интерфейсе. | Логический |
| hidden | Признак видимости поля в интерфейсе:true — скрывать поле даже в том случае, если оно заполнено;false — не скрывать поле. | Логический |
| container | Признак возможности указать в поле одновременно несколько значений (например, как в поле Теги):true — в поле можно указать несколько значений;false — в поле можно указать только одно значение.Этот параметр допустимо использовать для полей следующих типов:ru.yandex.startrek.core.fields.StringFieldType — Текстовое однострочное поле;ru.yandex.startrek.core.fields.UserFieldType — Имя пользователя;выпадающий список (см. описание объекта optionsProvider). | Логический |

**Поля объекта** `optionsProvider`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| type | Тип выпадающего списка: FixedListOptionsProvider — список строковых или числовых значений (для полей с типом ru.yandex.startrek.core.fields.StringFieldType или ru.yandex.startrek.core.fields.IntegerFieldType);FixedUserListOptionsProvider — список пользователей (для полей с типом ru.yandex.startrek.core.fields.UserFieldType). | Строка |
| values | Значения для выпадающего списка. В поле «Выпадающий список» можно добавить до 3000 значений. При нажатии на поле отображается не более 10 элементов. | Массив строк |

> Пример: Создать поле типа «Выпадающий список» с фиксированным набором строковых значений.
>
>
> - Используется HTTP-метод POST.
> - Тип поля: `FixedListOptionsProvider`.
> - Значения в выпадающем списке: «первый элемент списка», «второй элемент списка», «третий элемент списка».
>
>
>  
>  
> ```
> POST /v3/fields
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-Id: <идентификатор_организации>
>
> {
>    "name":
>    {
>        "en": "Название на английском языке",
>        "ru": "Название на русском языке"
>    },
>    "id": "myglobalfield",
>    "category": "0000000000000003********",
>    "type": "ru.yandex.startrek.core.fields.StringFieldType",
>    "optionsProvider": {
>        "type": "FixedListOptionsProvider",
>        "values": [
>            "первый элемент списка",
>            "второй элемент списка",
>            "третий элемент списка"
>        ]
>    }
> }
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `201 Created`.

Тело ответа содержит информацию о созданном поле задачи в формате JSON.

```
{
  "self": "https://api.tracker.yandex.net/v3/fields/global_field_key",
  "id": "global_field_key",
  "name": "Field name",
  "description": "Field description",
  "key": "global_field_key",
  "version": 1,
  "schema": {
      "type": "array",
      "items": "string",
      "required": false
  },
  "readonly": false,
  "options": true,
  "suggest": false,
  "optionsProvider": {
      "type": "FixedListOptionsProvider",
      "needValidation": true,
      "values": [
          "First item",
          "Second item",
          "Third item"
      ]
  },
  "queryProvider": {
      "type": "StringOptionalQueryProvider"
  },
  "order": 5,
  "category": {
      "self": "https://api.tracker.yandex.net/v3/fields/categories/0000000000000001********",
      "id": "0000000000000001********",
      "display": "Системные"
  },
  "type": "standard"
}
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| type | Тип поля. | Строка |
| self | Адрес ресурса API, который содержит информацию о поле. | Строка |
| id | Уникальный идентификатор поля. | Строка |
| name | Название поля. | Строка |
| description | Описание поля. | Строка |
| key | Ключ поля. | Строка |
| version | Версия поля. Каждое изменение поля увеличивает номер версии. | Число |
| schema | Объект с информацией о типе данных значения поля. | Объект |
| readonly | Возможность редактировать значение поля:true — значение поля нельзя изменить;false — значение поля можно изменить. | Логический |
| options | Ограничение списка значений:true — список значений не ограничен, можно задать любое значение;false — список значений ограничен настройками организации. | Логический |
| suggest | Наличие подсказки при вводе значения поля:true — при вводе значения появляется поисковая подсказка;false — функция поисковой подсказки отключена. | Логический |
| optionsProvider | Объект с информацией об элементах выпадающего списка. | Объект |
| queryProvider | Объект с информацией о классе языка запроса.Класс невозможно изменить с помощью API. | Объект |
| order | Порядковый номер в списке полей организации: https://tracker.yandex.ru/admin/fields | Число |
| category | Объект с информацией о категории поля.Чтобы получить список всех категорий, используйте HTTP запрос:GET /v3/fields/categories | Объект |

**Поля объекта** `schema`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| type | Тип значения поля. Возможные типы данных:string — строка. Присутствует у полей с единственным значением.array — массив. Присутствует у полей с несколькими значениями. | Строка |
| items | Тип значений. Присутствует у полей с несколькими значениями. | Строка |
| required | Обязательность заполнения поля:true — поле обязательно для заполнения;false — поле не обязательно для заполнения. | Логический |

**Поля объекта** `optionsProvider`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| type | Тип выпадающего списка. | Строка |
| needValidation | Проверка значения на валидность:true — проверять значение списка на валидность;false — не проверять значение списка на валидность. | Логический |
| values | Элементы списка. | Массив строк |

**Поля объекта** `queryProvider`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| type | Тип языка запроса. | Строка |

**Поля объекта** `category`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию о категории поля. | Строка |
| id | Идентификатор категории поля. | Строка |
| display | Отображаемое название категории. | Строка |

Если запрос не был успешно обработан, API возвращает ответ с кодом ошибки:

400
Один или несколько параметров запроса имеют недопустимое значение.

401
Пользователь не авторизован. Проверьте, были ли выполнены действия, описанные в разделе [Доступ к API](https://yandex.ru/support/tracker/ru/api-ref/issues/ru/api-ref/access).

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

422
Ошибка валидации JSON, запрос отклонен.

500
Внутренняя ошибка сервиса. Попробуйте повторно отправить запрос через некоторое время.

503
Сервис API временно недоступен.

---
