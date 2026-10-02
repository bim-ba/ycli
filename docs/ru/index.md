# ycli

ycli работает с Яндекс 360 (**Трекер**, **Вики** и **Формы**) через один SDK, доступный четырьмя способами:

| Способ | Когда подходит | С чего начать |
|---|---|---|
| CLI (`ycli`) | вы работаете в терминале или пишете скрипты | [справочник по CLI](https://bim-ba.github.io/ycli/reference/cli/) |
| MCP-сервер (`ycli mcp start`) | ИИ-агент должен читать и изменять данные Яндекс 360 | [Запуск MCP-сервера](how-to/serve-the-mcp-server.md) |
| Python SDK (`ycli.yandex`) | вы пишете на Python | [справочник по SDK](https://bim-ba.github.io/ycli/reference/sdk/tracker/) |
| Плагин для Claude Code | вы работаете в Claude Code и хотите получить ещё и навыки | [Установка в вашем ИИ-клиенте](how-to/install-in-your-harness.md) |

Каждая операция одинакова на любом из способов: `ycli tracker boards get 31` — это MCP-инструмент
`tracker_boards_get` и вызов SDK `tracker.boards.get(31)`.

```bash
uv tool install 'yandex-cli[mcp]'
ycli auth login
ycli tracker issues get TRACKER-1
```

## Куда дальше

| Вы хотите | Читайте |
|---|---|
| попробовать ycli в первый раз | [Первые шаги](tutorials/first-steps.md) |
| получить токен и идентификатор организации | [Аутентификация](how-to/authenticate.md) |
| подключить Claude, Cursor, VS Code, Codex или другой ИИ-клиент | [Установка в вашем ИИ-клиенте](how-to/install-in-your-harness.md) |
| отдать агенту меньше инструментов или только чтение | [Запуск MCP-сервера](how-to/serve-the-mcp-server.md) |
| запустить один сервер на всю команду | [Свой сервер по HTTP](how-to/self-host-over-http.md) |
| использовать ycli в shell-скрипте | [CLI в скриптах](how-to/script-the-cli.md) |
| вызвать эндпоинт, которого ycli не оборачивает | [Вызов необёрнутого эндпоинта](how-to/call-an-unwrapped-endpoint.md) |
| найти команду, инструмент, метод или настройку | [Справочник](reference/configuration.md) |
| понять, почему ycli устроен именно так | [Устройство](explanation/design.md) |

ycli — проект с открытым исходным кодом под лицензией MIT: [github.com/bim-ba/ycli](https://github.com/bim-ba/ycli).
