---
source: https://yandex.ru/support/tracker/ru/manager/queue-access-examples
title: "Примеры настройки доступов к очереди |"
word_count: 150
token_estimate: 478
extracted: "2026-05-13T10:50:08Z"
mode: quality
---

# Для HR-специалистов

Настройте очередь так, чтобы все сотрудники могли создавать новые задачи, но видеть их могли бы только автор и исполнитель задачи. Например, сотрудник обращается в отдел с частным запросом, который никто, кроме HR-специалиста, не должен видеть.

**Решение:** В разделе [**Основные участники**](https://yandex.ru/support/tracker/ru/manager/queue-access#main) для всех пользователей организации настройте доступ только для создания задач, а для команды HR-специалистов — на редактирование задач. В разделе **Роли в задачах** автору и исполнителю выдайте доступ на просмотр и редактирование: [Настройки доступа для ролей](https://yandex.ru/support/tracker/ru/manager/queue-access#task-role).

# Для информационной безопасности

Настройте ограничения доступа к задачам с помощью [компонента](https://yandex.ru/support/tracker/ru/manager/components). Например, необходимо ограничить доступ для всех пользователей с разными ролями в задаче, кроме группы **Информационная безопасность**: [Настройки доступа для компонентов](https://yandex.ru/support/tracker/ru/manager/queue-access#access-component).

**Решение:** [Создайте](https://yandex.ru/support/tracker/ru/manager/components#create-component) в очереди компонент, например, **private**. Для компонента **private** в разделе [**Основные участники**](https://yandex.ru/support/tracker/ru/manager/queue-access#main) для группы **Информационная безопасность** выдайте права на создание, просмотр и редактирование задач. Раздел [**Роли в задаче**](https://yandex.ru/support/tracker/ru/manager/queue-access#task-role) оставьте без изменений, с лейблами **Не влияет на доступ**.
