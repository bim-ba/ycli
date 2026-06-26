# Изменить триггер с помощью запроса к API

- [Формат запроса](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger#query)
- [Примеры](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger#examples)
- [Формат ответа](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger#answer)

Запрос позволяет изменить триггер.

PATCH

```
https://api.tracker.yandex.net/v3/queues/<id_очереди>/triggers/<id_триггера>?version=<текущая_версия_триггера>
```

## Формат запроса

Перед выполнением запроса [получите доступ к API](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access).

Чтобы изменить триггер, используйте HTTP-запрос с методом `PATCH`. В теле запроса укажите параметры в формате JSON.

```
PATCH /v3/queues/<id_очереди>/triggers/<id_триггера>?version=<текущая_версия_триггера>
Host: api.tracker.yandex.net
Authorization: OAuth <OAuth-токен>
Content-Type: application/json
X-Org-ID или X-Cloud-Org-ID: <идентификатор_организации>

{
    "name": "<имя_триггера>",
    "actions": [<параметры_действия_триггера>],
    "conditions": [<параметры_условия_триггера>]
}
```

Заголовки

- `Host`: адрес узла, предоставляющего API.
- `Authorization`: токен для авторизации в одном из форматов:

  - `OAuth <OAuth-токен>` при авторизации по протоколу OAuth 2.0. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#about_OAuth)
  - `Bearer <IAM-токен>` при авторизации с помощью IAM-токена — если к Трекеру привязана организация Yandex Cloud Organization. [Читать подробнее](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/access#iam-token)
- `Content-Type`: формат тела запроса. Должен иметь значение `application/json`.
- `X-Org-ID` или `X-Cloud-Org-ID`: идентификатор организации.

  - если к Трекеру привязана организация Яндекс 360 для бизнеса, используйте заголовок `X-Org-ID`,
  - если к Трекеру привязана организация Yandex Cloud Organization, используйте заголовок `X-Cloud-Org-ID`.

Чтобы узнать идентификатор организации, перейдите на страницу **Администрирование** → [**Организации**](https://tracker.yandex.ru/admin/orgs) и скопируйте значение поля **идентификатор**.

Ресурс

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| <id_очереди> | Идентификатор или ключ очереди. Ключ очереди чувствителен к регистру символов. | Строка или число |
| <id_триггера> | Идентификатор триггера. | Число |
| <текущая_версия_триггера> | Текущая версия триггера. | Число |

Текущую версию триггера можно найти с помощью [запроса для получения параметров триггера](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/get-trigger).

Параметры тела запроса
**Дополнительные параметры**

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| name | Название триггера. | Строка |
| actions | Массив с объектами действий триггера. Подробнее в разделе Объекты действий триггера. | Массив объектов |
| conditions | Массив с условиями срабатывания триггера Подробнее в разделе Условия срабатывания триггера. | Массив объектов |
| active | Статус триггера. Допустимые значения:true— активный;false— неактивный. | Логический |
| before | Идентификатор триггера, перед которым нужно поместить данный триггер. | Число |

#### Условия срабатывания триггера

В зависимости от того, должны ли сработать все или хотя бы одно из условий, занчение поля **conditions** можно указать в одном их двух форматов: либо  (), либо массив с объектами, включающими как массив элементарных объектов условий срабатывания триггера, так и тип логического объединения условий:

- Массив элементарных объектов условий срабатывания триггера. Подробнее в разделе [Объекты условий срабатывания триггера](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions).

В этом случае триггер сработает при выполнении всех условий, как при объединении условий с типом «логическое И».

```
{
    "conditions": [
       {<уcловиe_триггера_1>},
       {<уcловиe_триггера_2>}
    ]
}
```

- Объект с указанием типа объединения условий срабатывания триггера:

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| type | Тип логического объединения условий. Допустимые значения:Or— логическое ИЛИ (Любое);And— логическое И (Все). | Строка |
| conditions | Массив с элементарными объектами условия срабатывания триггера. | Массив объектов |

```
{
    "conditions": {
        "type": "Or",
        "conditions": [
            {<уcловиe_триггера_1>},
            {<уcловиe_триггера_2>}
        ]
    }
}
```

## Примеры

1. [Триггер, срабатывающий при выполнении хотя бы одного из условий](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger#or-condition).
2. [Изменить действие триггера](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger#and-condition).
3. [Триггер, срабатывающий при выполнении группы условий](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger#condition-group).
4. [Отключить триггер](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger#deactivation).
5. [Переместить триггер в списке и активировать](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger#move-before).

Пример 1: Изменить условия срабатывания и действие триггера. Триггер должен срабатывать при выполнении хотя бы одного из заданных условий.

> - Используется HTTP-метод `PATCH`.
> - Изменяется триггер для очереди DESIGN.
> - ID триггера — 16, текущая версия — 1.
> - Меняется условие срабатывания триггера: текст комментария совпадает с фразой «Need info» или «Нужна информация».
> - Действие триггера: переход задачи в статус «Требуется информация».
>
>
>  
>  
> ```
> PATCH /v3/queues/DESIGN/triggers/16?version=1
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-ID: 1234******
> {
>   "actions": [
>       { "type": "Transition",
>           "status": {
>              "key": "needInfo"
>           }
>       }
>   ],
>   "conditions": [
>       { "type": "Or",
>            "conditions": [
>                { "type": "CommentFullyMatchCondition", "word": "Need info" },
>                { "type": "CommentFullyMatchCondition", "word": "Нужна информация" }
>            ]
>       }
>   ]
> }
> ```

Пример 2: Изменить действие триггера.

> - Используется HTTP-метод `PATCH`.
> - Изменяется триггер для очереди DESIGN.
> - ID триггера — 16, текущая версия — 2.
> - Меняется действие триггера: создается чеклист, где указаны названия пунктов, исполнитель и дедлайн.
>
>
>  
>  
> ```
> PATCH /v3/queues/DESIGN/triggers/16?version=2
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Cloud-Org-ID: ab1c******
> {
>   "actions": [
>      {
>         "type": "CreateChecklist",
>         "checklistItems": [
>            {
>               "text": "Сделать то",
>               "assignee": "username",
>               "deadline": {"date": "2025-05-23"}
>            },
>            {
>               "text": "Сделать это",
>               "assignee": "username",
>               "deadline": {"date": "2025-05-23"}
>            },
>            {"text": "Отчитаться за все"}
>         ]
>      }
>   ]
> }
> ```

Пример 3: Изменить условия срабатывания и действие триггера. Триггер должен срабатывать при выполнении одной из групп условий.

> - Используется HTTP-метод `PATCH`.
> - Изменяется триггер для очереди DESIGN.
> - ID триггера — 16, текущая версия — 3.
> - Меняется условие срабатывания триггера — триггер срабатывает, если выполняется одна из групп условий:
> - - Текст комментария совпадает с фразой «Need info» и статус задачи равен `В работе`;
> - - Текст комментария совпадает с фразой «No data» ;
> - Меняется действие триггера: переход задачи в статус «Требуется информация».
>
>
>  
>  
> ```
> PATCH /v3/queues/DESIGN/triggers/16?version=3
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-ID: 1234******
>
> {
>    "actions": [
>        {
>            "type": "Transition",
>            "status": {
>                "key": "needInfo"
>            }
>        }
>    ],
>    "conditions": [
>        {
>            "type": "Or",
>            "conditions": [
>                {
>                    "type": "And",
>                    "conditions": [
>                        {
>                            "ignoreCase": false,
>                            "noMatchBefore": false,
>                            "removeMarkup": false,
>                            "type": "CommentFullyMatchCondition",
>                            "word": "Need info"
>                        },
>                        {
>                            "type": "FieldEquals",
>                            "field": "status",
>                            "value": "inProgress"
>                        }
>                    ]
>                },
>                {
>                    "ignoreCase": false,
>                    "noMatchBefore": false,
>                    "removeMarkup": false,
>                    "type": "CommentFullyMatchCondition",
>                    "word": "No data"
>                }
>            ]
>        }
>    ]
> }
> ```

Пример 4: Отключить триггер.

> - Используется HTTP-метод `PATCH`.
> - Изменяется триггер для очереди DESIGN.
> - ID триггера — 16, текущая версия — 4.
> - Триггер деактивируется.
>
>
>  
>  
> ```
> PATCH /v3/queues/DESIGN/triggers/16?version=4
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Cloud-Org-ID: ab1c******
> {
>   "active": false
> }
> ```

Пример 5: Переместить триггер в списке и активировать.

> - Используется HTTP-метод `PATCH`.
> - Изменяется триггер для очереди DESIGN.
> - ID триггера — 16, текущая версия — 4.
> - Триггер переносится в позицию перед триггером с идентификатором `6` и активируется.
>
>
>  
>  
> ```
> PATCH /v3/queues/DESIGN/triggers/16?version=4
> Host: api.tracker.yandex.net
> Authorization: OAuth y0__xAbc******
> Content-Type: application/json
> X-Org-ID: 1234******
> { "before": 6, "active": true }
> ```

## Формат ответа

Запрос выполнен успешно
Запрос выполнен с ошибкой

В случае успешного выполнения запроса API возвращает ответ с кодом `200 OK`.

Тело запроса содержит информацию о созданном триггере в формате JSON.

```
{
   "id": 16,
   "self": "https://api.tracker.yandex.net/v3/queues/DESIGN/triggers/16",
   "queue": {
      "self": "https://api.tracker.yandex.net/v3/queues/DESIGN",
      "id": "26",
      "key": "DESIGN",
      "display": "Design"
   },
   "name": "TriggerName",
   "order": "0.0002",
   "actions": [
      {
         "type": "Transition",
         "id": 2,
         "status": {
            "self": "https://api.tracker.yandex.net/v3/statuses/2",
            "id": "2",
            "key": "needInfo",
            "display": "Требуется информация"
         }
      }
   ],
   "conditions": [
      {
         "type": "Or",
         "conditions": [
            {
               "type": "CommentFullyMatchCondition",
               "word": "Need info",
               "ignoreCase": true,
               "removeMarkup": true,
               "noMatchBefore": false
            },
            {
               "type": "CommentFullyMatchCondition",
               "word": "Требуется информация",
               "ignoreCase": true,
               "removeMarkup": true,
               "noMatchBefore": false
            }
         ]
      }
      ],
      "version": 2,
      "active": true
   }
```

Параметры ответа

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| id | Идентификатор триггера. | Строка |
| self | Ссылка на триггер. | Строка |
| queue | Очередь, в которой нужно создать триггер. | Объект |
| name | Название триггера. | Строка |
| order | Вес триггера. Параметр влияет на порядок отображения триггера в интерфейсе. | Строка |
| actions | Массив с действиями триггера. | Массив объектов |
| conditions | Массив с условиями срабатывания триггера. | Массив объектов |
| version | Версия триггера. Каждое изменение триггера увеличивает номер версии. | Число |
| active | Статус триггера. | Логический |

**Поля объекта** `queue`

| Параметр | Описание | Тип данных |
| --- | --- | --- |
| self | Адрес ресурса API, который содержит информацию об очереди. | Строка |
| id | Идентификатор очереди. | Строка |
| key | Ключ очереди. | Строка |
| display | Отображаемое название очереди. | Строка |

Если запрос не был успешно обработан, ответное сообщение содержит информацию о возникших ошибках:

400
Один или несколько параметров запроса имеют недопустимое значение.

403
У вас не хватает прав на выполнение этого действия. Наличие прав можно перепроверить в интерфейсе Трекера — для выполнения действия при помощи API и через интерфейс требуются одинаковые права.

404
Запрошенный объект не был найден. Возможно, вы указали неверное значение идентификатора или ключа объекта.

409
При редактировании объекта возник конфликт. Возможно, ошибка возникла из-за неправильно указанной версии изменений.

412
При редактировании объекта возник конфликт. Возможно, ошибка возникла из-за неправильно указанной версии изменений.

422
Ошибка валидации JSON, запрос отклонен.

500
Внутренняя ошибка сервиса. Попробуйте повторно отправить запрос через некоторое время.

503
Сервис API временно недоступен.

---
