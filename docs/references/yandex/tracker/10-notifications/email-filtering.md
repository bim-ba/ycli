---
source: https://yandex.ru/support/tracker/ru/user/email-filtering
title: "Как отфильтровать входящую почту |"
word_count: 473
token_estimate: 1255
extracted: "2026-05-13T11:04:42Z"
mode: quality
---

Почтовые уведомления Трекера содержат служебные заголовки (хедеры), которые можно использовать для обработки писем. Вы можете настроить фильтрацию по заголовкам, чтобы перемещать письма с уведомлениями в отдельную папку, отмечать письма определённой меткой или удалять ненужные письма.

Список заголовков приведен в таблице [Описание заголовков](https://yandex.ru/support/tracker/ru/user/email-filtering#headers).

Как просмотреть свойства письма и заголовки, читайте в [Справке Яндекс Почты](https://yandex.ru/support/yandex-360/customers/mail/ru/tech-glossary.html#mail-titles).

# Как создать правило для обработки писем

Рассмотрим настройку правила для фильтрации писем в [Яндекс Почте](https://mail.yandex.ru/#setup/filters). Например, чтобы перекладывать уведомления об ответе на комментарий в отдельную папку, настройте правило для фильтрации писем по заголовку `X-Tracker-Answer`.

1. В интерфейсе Яндекс Почты в правом верхнем углу нажмите значок → **Все настройки**.

2. Выберите **Правила обработки писем**.

3. Нажмите кнопку **Создать правило**.

4. В блоке **Применять** выберите, к какому типу писем вы хотите применять правило.

5. В блоке **Если** выберите условие **Заголовок** и в открывшемся окне введите `X-Tracker-Answer`.

6. Затем выберите **Совпадает с** и введите `yes`.

7. В блоке **Выполнить действие** выберите, что нужно сделать с письмом: **Положить в папку**.

8. Если нужно, включите опцию **Не применять остальные правила**.

9. Если вы хотите задать имя для правила, введите его в поле **Название**.

10. Нажмите кнопку **Создать правило**.

Подробная инструкция по созданию правил — в [Справке Яндекс Почты](https://yandex.ru/support/yandex-360/customers/mail/ru/web/preferences/filters/create-filter).

| Заголовок | Комментарий | Пример |
| --- | --- | --- |
| X-Tracker | Заголовок означает, что письмо от Трекера | yes |
| X-Tracker-Key | *Ключ задачи* | TEST-1 |
| X-Tracker-Priority | Приоритет | Normal |
| X-Tracker-Reporter | Автор задачи | 123\*\*\*@tracker-reporter |
| X-Tracker-IssueType | Тип задачи | Task |
| X-Tracker-Assignee | Исполнитель | username |
| X-Tracker-EntityType | Тип [сущности](https://yandex.ru/support/tracker/api-ref/entities/about-entities.html): проект, портфель, цель | Portfolio |
| X-Tracker-EntityId | Идентификатор [сущности](https://yandex.ru/support/tracker/api-ref/entities/about-entities.html) (проекта, портфеля, цели) | 655f328da834c763\*\*\*\*\*\*\*\* |
| X-Tracker-EntityShortId | Короткий идентификатор [сущности](https://yandex.ru/support/tracker/api-ref/entities/about-entities.html) (проекта, портфеля, цели), может отсутствовать | 12345 |
| X-Tracker-Tags | Теги | mytag |
| X-Tracker-From | Пользователь, который инициировал отправку уведомления (например, автор последнего изменения задачи) | username@example.com |
| X-Tracker-Cc | Наблюдатели задачи | 123\*\*\*@tracker-cc |
| X-Tracker-Component | Компоненты задачи | 5075543ae4b03135cc676db1@tracker-component |
| X-Tracker-Changed | Измененные поля. Присутствует только в том случае, если поля менялись. При создании задачи отсутствует | Followers,Type,Queue,Key,Tags |
| X-Tracker-Fix-Version | Значение поля «Исправить в версиях» | Release\_05.07.2016 |
| X-Tracker-Affected-Version | Значение поля «Найдено в версиях» | 0.1.2 |
| X-Tracker-FingerPrint | Хэш MAC-адреса бэкенда | 2b953364 |
| X-Tracker-Old-Status | Старый статус задачи | Testing |
| X-Tracker-New-Status | Текущий статус задачи | Testing |
| X-Tracker-Summon | Присутствует, если письмо — уведомление о призыве в комментарии | yes |
| X-Tracker-Answer | Присутствует, если письмо — уведомление об ответе на комментарий | yes |
| X-Tracker-Queue | *Ключ очереди*, в которой находится задача | TEST |
| X-Tracker-Voted | Присутствует, если вы голосовали за эту задачу | yes |
| X-Tracker-Favorite | Присутствует, если задача у вас в избранном | yes |
