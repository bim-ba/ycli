# Объекты условий срабатывания триггера

- [События](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#events)
- [Чеклист](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#checklist)
- [Текст комментария](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#comment-text)
- [Автор комментария](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#comment-author)
- [Тип комментария](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#comment-type)
- [Действие со связью](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#relationship)
- [Поля задачи](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#task-fields)
  - [Значение поля](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#znachenie-polya)
  - [Состояние поля](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#sostoyanie-polya)
  - [Дата](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#data)
  - [Группы пользователей](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#gruppy-polzovatelej)
  - [Количество элементов](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#kolichestvo-elementov)
  - [Числовые значения](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#chislovye-znacheniya)
  - [Строковые значения](https://yandex.ru/support/tracker/ru/api-ref/queues/ru/api-ref/queues/change-trigger-conditions#strokovye-znacheniya)

Чтобы задать условия срабатывания триггера, укажите один или несколько объектов.

## События

| Параметр | Описание | Допустимые значения | Тип данных |
| --- | --- | --- | --- |
| type | Тип условия | Одно из значений:Event.update — Задача изменилась;CalculationFormulaWatch — Поля формулы изменились;Event.comment-create — Создан комментарий;Event.create — Создана задача; | Строка |

> Пример: Триггер сработает, если задача изменилась.
>
>
>
>
> ```
> {"type": "Event.update"}
> ```

## Чеклист

| Параметр | Описание | Допустимые значения | Тип данных |
| --- | --- | --- | --- |
| type | Тип условия | ChecklistDone | Строка |

> Пример: Триггер сработает, если все пункты чеклиста были выполнены.
>
>
>
>
> ```
> {"type": "ChecklistDone"}
> ```

## Текст комментария

| Параметр | Описание | Допустимые значения | Тип данных |
| --- | --- | --- | --- |
| type | Тип условия | Одно из значений:CommentNoneMatchCondition — Не содержит ни одного из фрагментов;CommentStringNotMatchCondition — Не содержит фрагмент;CommentFullyMatchCondition — Совпадает с;CommentAnyMatchCondition — Содержит любой из фрагментов;CommentStringMatchCondition — Содержит фрагмент; | Строка |
| word | Текст комментария | Строки для поиска | Строка или Массив строк |
| ignoreCase | Игнорировать регистр | true или false | Логический |
| removeMarkup | Игнорировать разметку | true или false | Логический |
| noMatchBefore | Параметр изменился | true или false | Логический |

**Тип данных в зависимости от типа условия**

| Тип условия | Тип данных |
| --- | --- |
| CommentNoneMatchCondition | Массив строк |
| CommentStringNotMatchCondition | Строка |
| CommentFullyMatchCondition | Строка |
| CommentAnyMatchCondition | Массив строк |
| CommentStringMatchCondition | Строка |

> Пример: Триггер сработает, если комментарий не содержит текстов `Version 0.1` или `Version 0.2` в любых регистре и разметке.
>
>
>
>
> ```
> {
> 	"type": "CommentNoneMatchCondition",
> 	"words": ["Version 0.1", "Version 0.2"],
> 	"ignoreCase": true,
> 	"removeMarkup": true,
> 	"noMatchBefore": false
> }
> ```

## Автор комментария

| Параметр | Описание | Допустимые значения | Тип данных |
| --- | --- | --- | --- |
| type | Тип условия | Одно из значений:CommentAuthorNot — Значение поля не равно;CommentAuthor — Значение поля равно. | Строка |
| user | Автор комментария | Идентификатор пользователя | Строка |

> Пример: Триггер сработает, если автор комментария — кто-то кроме пользователя с логином `@user1`.
>
>
>
>
> ```
> { "type": "CommentAuthorNot", "user": "user1" }
> ```

## Тип комментария

| Параметр | Описание | Допустимые значения | Тип данных |
| --- | --- | --- | --- |
| type | Тип условия | Одно из значений:CommentMessageInternal — Комментарий в Трекере;CommentMessageExternal — Письмо на почту. | Строка |
| user | Автор комментария | Идентификатор пользователя | Строка |

> Примеры
>
>
> 1. Триггер сработает, если тип комментария — `Комментарий в Трекере`.
>  
>  
> ```
> { "type": "CommentMessageInternal" }
> ```
>
> 2. Триггер сработает, если тип комментария — `Письмо на почту`.
>  
>  
> ```
> { "type": "CommentMessageExternal" }
> ```

## Действие со связью

| Параметр | Описание | Допустимые значения | Тип данных |
| --- | --- | --- | --- |
| type | Тип условия | Одно из значений:UpdatedLinkCondition — Связь обновлена;CreatedLinkCondition — Связь создана;RemovedLinkCondition — Связь удалена. | Строка |
| relationship | Тип связи между задачами | Список связей | Массив строк |

Типы связей

- `relates` — простая связь.
- `is dependent by` — текущая задача является блокером.
- `depends on` — текущая задача зависит от связываемой.
- `is subtask for` — текущая задача является подзадачей связываемой.
- `is parent task for` — текущая задача является родительской для связываемой задачи.
- `duplicates` — текущая задача дублирует связываемую.
- `is duplicated by` — связываемая задача дублирует текущую.
- `is epic of` — текущая задача является эпиком связываемой. Связь такого типа можно установить только для задач типа "Эпик".
- `has epic` — связываемая задача является эпиком текущей. Связь такого типа можно установить только для задач типа "Эпик".

> Пример: Триггер сработает, если связи с родительской задачей и эпиком удалены.
>
>
>
>
> ```
> { "type": "RemovedLinkCondition", "relationship": ["is parent task for", "is epic of"] }
> ```

## Поля задачи

В общем случае условие срабатывания триггера, связанное с полем задачи, может быть описано объектом с двумя обязательными параметрами:

| Параметр | Описание | Допустимые значения | Тип данных |
| --- | --- | --- | --- |
| type | Тип условия | <идентификатор_условия> | Строка |
| field | Поле задачи | <идентификатор_поля> | Строка |

Объект может также содержать дополнительные параметры.

Доступные значения типа условия зависят от конкретного поля задачи. Дополнительные параметры объекта зависят от комбинации обязательных параметров.

### Значение поля

Для большинства полей доступны следующие три типа условий, связанных со значением поля:

| Тип условия | Описание | Дополнительные параметры | Тип данных |
| --- | --- | --- | --- |
| FieldChangedCondition | Значение поля изменилось | Без параметров |  |
| FieldEquals | равно | value | Строка |
| FieldBecameEqual | стало равно | value | Строка |

Список полей, для которых применимы условия

| Поле | Идентификатор |
| --- | --- |
| Очередь | queue |
| Тип | type |
| Приоритет | priority |
| Ключ | key |
| Задача | summary |
| Описание * | description |
| Статус | status |
| Резолюция | resolution |
| Статус изменен | statusStartTime |
| Создано | createdAt |
| Обновлено | updatedAt |
| Разрешен | resolvedAt |
| Последний комментарий | lastCommentUpdatedAt |
| Дедлайн | deadline |
| Дата начала | start |
| Дата завершения | end |
| Автор | createdBy |
| Исполнитель | assignee |
| Наблюдатели | followers |
| Доступ | access |
| Изменил | updatedBy |
| Решивший | resolvedBy |
| Рассылки | followingMaillists |
| Проект | project |
| Теги | tags |
| Компоненты | components |
| Найдено в версиях | affectedVersions |
| Исправить в версиях | fixVersions |
| Родительский тикет | parent |
| Старая очередь | previousQueue |
| Проголосовали | votedBy |
| Проголосовало | votes |
| Комментариев без сообщения | commentWithoutExternalMessageCount |
| Комментариев с сообщением | commentWithExternalMessageCount |
| Доски | boards |
| Нужен ответ пользователя | pendingReplyFrom |
| Предыдущая очередь | lastQueue |
| Суммарный процент участия | participantPercentsTotal |
| Возможно спам | possibleSpam |
| Тип статуса | statusType |
| QA-инженер | qaEngineer |
| Первоначальная оценка | originalEstimation |
| Оценка | estimation |
| Затрачено времени | spent |
| Epic | epic |
| Story Points | storyPoints |
| Спринт | sprint |
| От * | emailFrom |
| Кому | emailTo |
| Копия | emailCc |
| Создано по письму на адрес * | emailCreatedBy |

- Для полей, отмеченных звездочкой, вместо типа условия **равно** (`FieldEquals`) используется **Равно строке** (`FieldEqualsString`).

Примеры:

> 1. Триггер сработает, если значение поля «Приоритет» изменилось.
>  
>  
> ```
> { "type": "FieldChangedCondition", "field": "priority" }
> ```
>
> 2. Триггер сработает, если значение поля «Приоритет» — `Блокер`.
>  
>  
> ```
> { "type": "FieldEquals", "field": "priority", "value": "blocker" }
> ```
>
> 3. Триггер сработает, если значение поля «Приоритет» изменилось на `Блокер`.
>  
>  
> ```
> { "type": "FieldBecameEqual", "field": "priority", "value": "blocker" }
> ```

### Состояние поля

Условия, связанные с наличием в поле значения:

| Тип условия | Описание | Дополнительные параметры |
| --- | --- | --- |
| FieldIsNotEmpty | Значение поля не пусто | Без параметров |
| FieldIsEmpty | Значение поля пусто | Без параметров |
| FieldBecameEmpty | Значение поля удалено | Без параметров |
| FieldBecameNotEmpty | Значение поля установлено | Без параметров |

Список полей, для которых применимы условия

| Поле | Идентификатор |
| --- | --- |
| Описание | description |
| Резолюция | resolution |
| Статус изменен | statusStartTime |
| Разрешен | resolvedAt |
| Последний комментарий | lastCommentUpdatedAt |
| Дедлайн | deadline |
| Дата начала | start |
| Дата завершения | end |
| Исполнитель | assignee |
| Наблюдатели | followers |
| Доступ | access |
| Решивший | resolvedBy |
| Рассылки | followingMaillists |
| Проект | project |
| Теги | tags |
| Компоненты | components |
| Найдено в версиях | affectedVersions |
| Исправить в версиях | fixVersions |
| Родительский тикет | parent |
| Старая очередь | previousQueue |
| Проголосовали | votedBy |
| Доски | boards |
| Нужен ответ пользователя | pendingReplyFrom |
| Предыдущая очередь | lastQueue |
| Суммарный процент участия | participantPercentsTotal |
| Возможно спам | possibleSpam |
| Тип статуса | statusType |
| QA-инженер | qaEngineer |
| Первоначальная оценка | originalEstimation |
| Оценка | estimation |
| Затрачено времени | spent |
| Epic | epic |
| Story Points | storyPoints |
| Спринт | sprint |
| От | emailFrom |
| Кому | emailTo |
| Копия | emailCc |
| Создано по письму на адрес | emailCreatedBy |

Примеры:

> 1. Триггер сработает, если исполнитель уже назначен.
>  
>  
> ```
> { "type": "FieldIsNotEmpty", "field": "assignee" }
> ```
>
> 2. Триггер сработает, если исполнитель не назначен.
>  
>  
> ```
> { "type": "FieldIsEmpty", "field": "assignee" }
> ```
>
> 3. Триггер сработает, если поле «Исполнитель» стало пустым.
>  
>  
> ```
> { "type": "FieldBecameEmpty", "field": "assignee" }
> ```
>
> 4. Триггер сработает, если поле «Исполнитель» стало непустым.
>  
>  
> ```
> { "type": "FieldBecameNotEmpty", "field": "assignee" }
> ```

### Дата

Условия, связанные с датами:

| Тип условия | Описание | Дополнительные параметры | Тип данных |
| --- | --- | --- | --- |
| DateEqualCondition | Дата совпадает | value | Строка в формате даты |
| DateGreaterCondition | Позднее | value | Строка в формате даты |
| DateGreaterOrEqualCondition | Позднее или равно | value | Строка в формате даты |
| DateLessCondition | Раньше | value | Строка в формате даты |
| DateLessOrEqualCondition | Раньше или равно | value | Строка в формате даты |

Список полей, для которых применимы условия

| Поле | Идентификатор |
| --- | --- |
| Статус изменен | statusStartTime |
| Создано | createdAt |
| Обновлено | updatedAt |
| Разрешен | resolvedAt |
| Последний комментарий | lastCommentUpdatedAt |
| Дедлайн | deadline |
| Дата начала | start |
| Дата завершения | end |

> Примеры:
>
>
> 1. Триггер сработает, если в поле «Создано» указана дата позднее 28 октября 2023.
>  
>  
> ```
> { "type": "DateGreaterCondition", "field": "createdAt", "value": "2023-10-28T09:25:00"}
> ```
>
> 2. Триггер сработает, если в поле «Дата завершения» указана дата раньше либо равная 28 октября 2023.
>  
>  
> ```
> { "type": "DateLessOrEqualCondition", "field": "end", "value": "2023-10-28T09:25:00"}
> ```

### Группы пользователей

Условия, связанные с группами пользователей:

| Тип условия | Описание | Дополнительные параметры | Тип данных |
| --- | --- | --- | --- |
| UserInGroups | Пользователь входит в одну из групп | value | Строка или Массив строк |
| UserNotInGroups | Пользователь не входит ни в одну из групп | value | Строка или Массив строк |

Список полей, для которых применимы условия

| Поле | Идентификатор |
| --- | --- |
| Автор | createdBy |
| Исполнитель | assignee |
| Изменил | updatedBy |
| Решивший | resolvedBy |
| QA-инженер | qaEngineer |

Примеры:

> 1. Триггер сработает, если пользователь, создавший задачу, входит в группу c идентификатором `1`.
>  
>  
> ```
> {"type": "UserInGroups", "field": "createdBy","value": "1"}
> ```
>
> 2. Триггер сработает, если пользователь, создавший задачу, не входит в группу c идентификатором `1`.
>  
>  
> ```
> {"type": "UserNotInGroups", "field": "createdBy","value": ["1", "4"]}
> ```

### Количество элементов

Условия, связанные с количеством элементов:

| Тип условия | Описание | Дополнительные параметры | Тип данных |
| --- | --- | --- | --- |
| Container.SizeGreater | Количество элементов больше | value | Число |
| Container.SizeGreaterOrEquals | Количество элементов больше или равно | value | Число |
| Container.SizeLess | Количество элементов меньше | value | Число |
| Container.SizeLessOrEquals | Количество элементов меньше или равно | value | Число |
| Container.SizeNotEquals | Количество элементов не равно | value | Число |
| Container.SizeEquals | Количество элементов равно | value | Число |
| ContainerContainsNone | Не содержит ни одного элемента | valuenoMatchBefore | МассивЛогический |
| ContainerContainsAll | Содержит все элементы | valuenoMatchBefore | МассивЛогический |
| ContainerContainsAny | Содержит любой из элементов | valuenoMatchBefore | МассивЛогический |

Список полей, для которых применимы условия

| Поле | Идентификатор |
| --- | --- |
| Наблюдатели | followers |
| Доступ | access |
| Теги | tags |
| Компоненты | components |
| Найдено в версиях | affectedVersions |
| Исправить в версиях | fixVersions |
| Проголосовали | votedBy |
| Доски | boards |
| Нужен ответ пользователя | pendingReplyFrom |
| Спринт | sprint |
| Копия | emailCc |
| Кому | emailTo |
| Рассылки | followingMaillists |

Примеры:

> 1. Триггер сработает, если количество голосов больше либо равно пяти.
>  
>  
> ```
> { "type": "Container.SizeGreaterOrEquals", "field": "votedBy", "value": 5 }
> ```
>
> 2. Триггер сработает, если компонентов ровно пять.
>  
>  
> ```
> { "type": "Container.SizeEquals", "field": "components", "value": 5 }
> ```
>
> 3. Триггер сработает, если поле «Наблюдатели» когда-либо содержало любое из значений `user11` или `user12`.
>  
>  
> ```
> { "type": "ContainerContainsAll", "field": "followers", "value": ["user11", "user22"], "noMatchBefore": true }
> ```

### Числовые значения

Условия, связанные с числовыми значениями:

| Тип условия | Описание | Дополнительные параметры | Тип данных |
| --- | --- | --- | --- |
| GreaterCondition | больше | value | Число |
| GreaterOrEqualCondition | больше или равно | value | Число |
| LessCondition | меньше | value | Число |
| LessOrEqualCondition | меньше или равно | value | Число |
| BecameGreaterCondition | стало больше | value | Число |
| BecameGreaterOrEqualCondition | стало больше или равно | value | Число |
| BecameLessCondition | стало меньше | value | Число |
| BecameLessOrEqualCondition | стало меньше или равно | value | Число |

Список полей, для которых применимы условия

| Поле | Идентификатор |
| --- | --- |
| Проголосовало | votes |
| Комментариев без сообщения | commentWithoutExternalMessageCount |
| Комментариев с сообщением | commentWithExternalMessageCount |
| Суммарный процент участия | participantPercentsTotal |
| Возможно спам | possibleSpam |
| Первоначальная оценка | originalEstimation |
| Оценка | estimation |
| Затрачено времени | spent |
| Story Points | storyPoints |

Примеры:

> 1. Триггер сработает, если значение поля «Story Points» меньше или равно пяти.
>  
>  
> ```
> { "type": "LessOrEqualCondition", "field": "storyPoints", "value": 5 }
> ```
>
> 2. Триггер сработает, если значение поля «Проголосовало» стало больше пяти.
>  
>  
> ```
> { "type": "BecameGreaterCondition", "field": "votes", "value": 6 }
> ```

### Строковые значения

Условия, связанные со строковыми значениями:

| Тип условия | Описание | Дополнительные параметры | Тип данных |
| --- | --- | --- | --- |
| ContainsNoneOfStrings | Не содержит ни одного из фрагментов | valueignoreCase | МассивЛогический |
| FieldEqualsString | Равно строке | valueignoreCase | СтрокаЛогический |
| ContainsAnyOfStrings | Содержит любой из фрагментов | valueignoreCase | МассивЛогический |

Список полей, для которых применимы условия

| Поле | Идентификатор |
| --- | --- |
| Ключ | key |
| Задача | summary |
| Описание | description |
| От | emailFrom |
| Создано по письму на адрес | emailCreatedBy |

Примеры:

> 1. Триггер сработает, если описание задачи не содержит значений `Test task` и `12345` в любых регистре и разметке.
>  
>  
> ```
> { "type": "ContainsNoneOfStrings", "field": "description", "value": ["Test task", "12345"], "ignoreCase": true }
> ```
>
> 2. Триггер сработает, если название задачи — `New-Task`.
>  
>  
> ```
> { "type": "FieldEqualsString", "field": "summary", "value": "New-Task", "ignoreCase": false }
> ```

---
