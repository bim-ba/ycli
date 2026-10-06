---
description: "ycli рядом с MCP-серверами и CLI самого Яндекса и серверами сообщества: сервисы, число инструментов, запись, установка, лицензия. Факты с источниками."
type: explanation
---

# ycli и другие инструменты

Подключить агента или терминал к Яндекс Трекеру, Вики и Формам можно несколькими инструментами. Здесь их опубликованные факты стоят рядом, чтобы вы выбрали подходящий. Каждая цифра проверена **3 октября 2026 года**, источник указан ниже; в ячейке написано «не описано», если на страницах самого проекта ответа нет.

## Что покрывает каждый

| Проект | Сервисы | Инструменты MCP | Запись | Режим только чтения | Инструменты с пометкой «чтение / запись» |
|---|---|---|---|---|---|
--8<-- "docs/examples/services/comparison.row.ru.md"
| MCP-сервер Яндекс Трекера | Трекер | 72 | да | не описан | 72 из 72 |
| MCP-сервер Яндекс Вики | Вики | 33 | да | не описан; токен только с правом `wiki:read` писать не может | 0 из 33 |
| MCP-сервер Яндекс Форм | Формы | 18 | да | не описан | 0 из 18 |
| `ytracker`, CLI Трекера | Трекер | это не MCP-сервер | да | не описан | неприменимо |
| aikts/yandex-tracker-mcp 0.10.0 | Трекер | 55 по умолчанию, 94 с `TRACKER_ENTITIES_ENABLED` | да | `TRACKER_READ_ONLY`, 35 инструментов | 55 из 55 |
| n-r-w/yandex-mcp v1.0.3 | Трекер, Вики | 23: Трекер 18, Вики 5 | нет | всегда | не проверялось |

--8<-- "docs/examples/services/comparison.operations.ru.md"

## Как его получить и запустить

| Проект | Другие способы работы | Где работает | Установка | Лицензия | Последний релиз |
|---|---|---|---|---|---|
| ycli | CLI, Python SDK, плагин Claude Code | ваш компьютер (stdio) или ваш сервер (HTTP) | `uv tool install 'yandex-cli[mcp]'`, образ Docker | MIT | при каждом слиянии: см. [PyPI](https://pypi.org/project/yandex-cli/#history) |
| MCP-сервер Яндекс Трекера | не описаны | сервер Яндекса | ставить нечего: адрес и два заголовка | исходный код на странице не опубликован | размещён у Яндекса, версий нет |
| MCP-сервер Яндекс Вики | не описаны | сервер Яндекса | ставить нечего: адрес и два заголовка | исходный код на странице не опубликован | размещён у Яндекса, версий нет |
| MCP-сервер Яндекс Форм | не описаны | сервер Яндекса | ставить нечего: адрес и два заголовка | исходный код на странице не опубликован | размещён у Яндекса, версий нет |
| `ytracker`, CLI Трекера | только CLI | ваш компьютер | установочный скрипт (shell, в Windows — PowerShell) | на странице не указана | не проверялось: не устанавливали |
| aikts/yandex-tracker-mcp | не описаны | ваш компьютер (stdio) или ваш сервер (HTTP, с OAuth) | `uvx yandex-tracker-mcp@latest`, образ Docker, `.mcpb` для Claude Desktop | Apache-2.0 | 0.10.0, 6 сентября 2026 года |
| n-r-w/yandex-mcp | не описаны | ваш компьютер | готовые сборки, Homebrew, `go install` | MIT | v1.0.3, 17 сентября 2026 года |

## Источники

| Проект | Источник | Как получена цифра |
|---|---|---|
| ycli | [README, Coverage](https://github.com/bim-ba/ycli#coverage) | создаётся из кода при каждом изменении, а тест держит эту страницу равной ему |
| MCP-сервер Яндекс Трекера | [yandex.ru/support/tracker/ru/user/mcp-server](https://yandex.ru/support/tracker/ru/user/mcp-server) | страница и ответ самого сервера на `tools/list` |
| MCP-сервер Яндекс Вики | [yandex.ru/support/wiki/ru/mcp](https://yandex.ru/support/wiki/ru/mcp) | страница и ответ самого сервера на `tools/list` |
| MCP-сервер Яндекс Форм | [yandex.ru/support/forms/ru/mcp](https://yandex.ru/support/forms/ru/mcp) | страница и ответ самого сервера на `tools/list` |
| `ytracker` | [yandex.ru/support/tracker/ru/user/cli](https://yandex.ru/support/tracker/ru/user/cli) | только страница; сам инструмент не устанавливали |
| aikts/yandex-tracker-mcp | [github.com/aikts/yandex-tracker-mcp](https://github.com/aikts/yandex-tracker-mcp) | README, релиз на GitHub и `tools/list` релиза 0.10.0, запущенного локально с каждой настройкой |
| n-r-w/yandex-mcp | [github.com/n-r-w/yandex-mcp](https://github.com/n-r-w/yandex-mcp) | README и релиз на GitHub; сервер не запускали |

Серверы Яндекса отвечают на `tools/list` без токена, так что подсчёт может повторить кто угодно:

```bash
curl -s -X POST https://mcp.tracker.yandex.net/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Серверы Вики и Форм принимают тот же запрос по адресам `https://mcp.wiki.yandex.net` и `https://mcp.forms.yandex.net`. Инструмент «с пометкой» — тот, у которого в записи есть `annotations`, например `readOnlyHint` или `destructiveHint`: по ним клиент спрашивает подтверждение перед записью.

Нашли устаревшую цифру? [Создайте issue](https://github.com/bim-ba/ycli/issues/new) с источником — страницу исправим.
