---
description: ycli управляет Яндекс Трекером, Вики и Формами из командной строки, MCP-сервера для ИИ-агентов и Python SDK.
---

# ycli

**Яндекс 360 для людей и для агентов.** Трекер, Вики и Формы из командной строки, MCP-сервера и Python: один инструмент, и у каждой операции везде одно имя.

[Начать](tutorials/first-steps.md){ .md-button .md-button--primary }
[Подключить ИИ-клиент](how-to/install-in-your-harness.md){ .md-button }

## От установки до первого вызова

--8<-- "docs/examples/terminal/first-call.ru.md"

`ycli auth login` выполняет вход через Яндекс ID и сохраняет токен. В первый раз ему нужно ваше OAuth-приложение Яндекса: как его завести, описано в разделе [Аутентификация](how-to/authenticate.md).

## Одна операция — три способа

--8<-- "docs/examples/operations/tracker.issues.get.md"

Команда, инструмент, который вызывает агент, и метод Python — это одна операция под одним именем. Достаточно выучить её один раз.

## Что вы получаете

<div class="grid cards" markdown>

-   :material-console: **Командная строка, удобная для скриптов**

    JSON при передаче по конвейеру, встроенный `--jq`, `--dry-run` для любой записи и свой код возврата для каждого вида ошибки.

    [CLI в скриптах](how-to/script-the-cli.md)

-   :material-robot-outline: **MCP-сервер, которому агент может доверять**

    Каждый инструмент сообщает, читает он, пишет или удаляет. Можно отдать только чтение или небольшой набор на каждый день.

    [Запуск MCP-сервера](how-to/serve-the-mcp-server.md)

-   :material-language-python: **Типизированный Python SDK**

    Pydantic-модели для каждого ответа и примеры, которые выполняет набор тестов.

    [Справочник SDK (англ.)](https://bim-ba.github.io/ycli/reference/sdk/tracker/)

-   :material-shield-check-outline: **Бережно к вашим данным**

    Удаление сначала спрашивает, запись можно посмотреть заранее, а токен уходит только на хосты самого Яндекса.

    [Аутентификация](how-to/authenticate.md)

-   :material-puzzle-outline: **Любой клиент**

    Claude, Cursor, VS Code, Windsurf, Zed, Codex, Gemini CLI, opencode, Docker: одна страница, для каждого один и тот же порядок.

    [Установка в вашем ИИ-клиенте](how-to/install-in-your-harness.md)

-   :material-source-branch: **Пайплайны**

    Оставить комментарий в задаче после выкладки или перевести её по воркфлоу — из GitHub Actions или GitLab CI.

    [Использование в CI](how-to/use-in-ci.md)

</div>

## Куда идти

| Вы хотите | Читайте |
|---|---|
| попробовать ycli в первый раз | [Первые шаги](tutorials/first-steps.md) |
| выполнить повседневную задачу | [Частые задачи](how-to/common-tasks.md) |
| получить токен и идентификатор организации | [Аутентификация](how-to/authenticate.md) |
| подключить ИИ-клиент | [Установка в вашем ИИ-клиенте](how-to/install-in-your-harness.md) |
| запустить один сервер на команду | [Свой MCP-сервер по HTTP](how-to/self-host-over-http.md) |
| вызвать эндпоинт, который ycli не оборачивает | [Вызов необёрнутого эндпоинта](how-to/call-an-unwrapped-endpoint.md) |
| найти команду, инструмент, метод или настройку | [Справочник](reference/configuration.md) |
| понять, почему ycli устроен именно так | [Устройство](explanation/design.md) |

ycli — открытый проект под лицензией MIT: [github.com/bim-ba/ycli](https://github.com/bim-ba/ycli).
