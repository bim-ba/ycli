---
type: how-to
---

# Частые задачи

Повседневные операции, каждая — тремя способами. Выберите вкладку один раз, и все примеры на сайте переключатся на неё.

- **CLI** — команда, которую вводите вы.
- **MCP** — вызов инструмента, который делает агент, когда вы просите его словами.
- **SDK** — вызов на клиенте `tracker = TrackerClient(oauth_token="…", organization_id="…")` (для `wiki` и `forms` так же).

Каждый пример здесь сгенерирован из теста, который выполняет его всеми тремя способами.

## Найти задачи

--8<-- "docs/examples/operations/tracker.issues.search.md"

CLI и инструмент принимают частые фильтры как опции; для остального передайте запрос на языке запросов Трекера: `ycli tracker issues search 'Queue: DE AND Status: open'`.

## Прочитать задачу

--8<-- "docs/examples/operations/tracker.issues.get.md"

## Создать задачу

--8<-- "docs/examples/operations/tracker.issues.create.md"

## Изменить задачу

--8<-- "docs/examples/operations/tracker.issues.update.md"

## Оставить комментарий

--8<-- "docs/examples/operations/tracker.comments.add.md"

## Перевести задачу по воркфлоу

Задача переходит в другой статус через переход, и у каждого статуса переходы свои. Сначала посмотрите доступные:

--8<-- "docs/examples/operations/tracker.transitions.list.md"

Затем выполните нужный по его идентификатору:

--8<-- "docs/examples/operations/tracker.transitions.execute.md"

## Записать время

--8<-- "docs/examples/operations/tracker.worklog.create.md"

## Создать страницу в Вики

--8<-- "docs/examples/operations/wiki.pages.create.md"

## Прочитать форму

--8<-- "docs/examples/operations/forms.surveys.get.md"

Все остальные операции — в справочнике (на английском): [CLI](https://bim-ba.github.io/ycli/reference/cli/), [MCP-инструменты](https://bim-ba.github.io/ycli/reference/mcp/tracker/), [SDK](https://bim-ba.github.io/ycli/reference/sdk/tracker/).
