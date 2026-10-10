<div align="center">

# ycli

**Яндекс 360 для людей и для агентов.**

Трекер, Вики и Формы из командной строки, MCP-сервера и Python: один инструмент и одно имя у каждой операции везде.

[English](README.md) · **Русский**

[![CI](https://img.shields.io/github/actions/workflow/status/bim-ba/ycli/ci.yml?branch=main&logo=githubactions&logoColor=white&label=ci)](https://github.com/bim-ba/ycli/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=pytest&logoColor=white)](https://github.com/bim-ba/ycli)
[![PyPI](https://img.shields.io/pypi/v/yandex-cli?logo=pypi&logoColor=white&label=pypi)](https://pypi.org/project/yandex-cli/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-ycli.savaznatnov.dev-blue?logo=materialformkdocs&logoColor=white)](https://ycli.savaznatnov.dev/ru/)
[![DeepWiki](https://img.shields.io/badge/deepwiki-ask%20the%20repo-blue?logo=readthedocs&logoColor=white)](https://deepwiki.com/bim-ba/ycli)

<img src="https://raw.githubusercontent.com/bim-ba/ycli/main/docs/assets/demo.gif" alt="ycli in action" width="760">

</div>

- **Командная строка, удобная для скриптов.** JSON при передаче по конвейеру, готовый для `jq`, `--dry-run` для любой записи, свой код возврата для каждого вида ошибки.
- **MCP-сервер, которому агент может доверять.** Каждый инструмент сообщает, читает он, пишет или удаляет; можно отдать только чтение или небольшой набор на каждый день.
- **Типизированный Python SDK.** Pydantic-модели для каждого ответа и примеры, которые запускает набор тестов.
- **Бережно с вашими данными.** Удаление сначала спрашивает, а токен уходит только на хосты самого Яндекса.

Документация: [ycli.savaznatnov.dev/ru](https://ycli.savaznatnov.dev/ru/).

## Установка

```bash
uv tool install 'yandex-cli[mcp]'   # команда ycli вместе с MCP-сервером
uvx yandex-cli --help               # или разовый запуск без установки
pipx install 'yandex-cli[mcp]'      # или через pipx
```

Команда называется `ycli` (и `yandex-cli`). Затем войдите: `ycli auth login` ([как](https://ycli.savaznatnov.dev/ru/how-to/authenticate/)).

Пишете на Python? Добавьте SDK в проект: `uv add yandex-cli`.

| Extra | Что добавляет | Установка |
|---|---|---|
| `mcp` | MCP-сервер, `ycli mcp start` | `uv tool install 'yandex-cli[mcp]'` |
| `service-account` | `ServiceAccountAuth` из SDK для ключа сервисного аккаунта Yandex Cloud | `uv add 'yandex-cli[service-account]'` |

### Подключите ИИ-клиент

Каждый клиент получает один и тот же MCP-сервер, `uvx --from 'yandex-cli[mcp]' ycli mcp start`, и одни и те же две переменные.

| Клиент | Самый быстрый способ |
|---|---|
| Claude Code | `/plugin marketplace add bim-ba/ycli`, затем `/plugin install yandex-360@ycli` |
| Claude Desktop | откройте файл `.mcpb` из [последнего релиза](https://github.com/bim-ba/ycli/releases/latest) |
| Cursor | [установка в один клик](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#cursor) |
| VS Code | [установка в один клик](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#vs-code) |
| Windsurf (Devin Desktop) | [файл настроек](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#windsurf-devin-desktop) |
| Zed | [файл настроек](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#zed) |
| Codex | [файл настроек](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#codex) |
| Gemini CLI | [файл настроек](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#gemini-cli) |
| opencode | [файл настроек](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#opencode) |
| Любой другой MCP-клиент | [три значения для копирования](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#any-other-client) |

Ещё: образ Docker `ghcr.io/bim-ba/ycli` ([как сервер или как обычный CLI](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#docker)), [конвейеры CI](https://ycli.savaznatnov.dev/ru/how-to/use-in-ci/) и запись `io.github.bim-ba/ycli` в [официальном реестре MCP](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.bim-ba/ycli).

Что-то не работает? [Если не работает](https://ycli.savaznatnov.dev/ru/how-to/install-in-your-harness/#if-it-does-not-work).

## Как пользоваться

### Командная строка

```bash
ycli tracker issues get TRACKER-1                  # таблица в терминале
ycli tracker issues get TRACKER-1 | jq .summary    # JSON при передаче по конвейеру
ycli -o yaml wiki pages get onboarding             # или выберите: -o json | yaml | pretty | csv | markdown | ndjson | name
ycli tracker boards delete 7 --dry-run             # напечатать запрос, который отправила бы запись
ycli tracker boards delete 7 --yes                 # удаление сначала спрашивает; --yes отвечает
ycli api issues/TRACKER-1 --service tracker        # эндпоинт, который ycli не оборачивает
```

Подробнее: [CLI в скриптах](https://ycli.savaznatnov.dev/ru/how-to/script-the-cli/), [Вызов необёрнутого эндпоинта](https://ycli.savaznatnov.dev/ru/how-to/call-an-unwrapped-endpoint/), [справочник CLI](https://ycli.savaznatnov.dev/reference/cli/) (на английском).

### MCP-сервер

```bash
ycli mcp start                     # все инструменты, чтение и запись
ycli mcp start --read-only         # только чтение
ycli mcp start --toolsets core     # около 40 инструментов на каждый день, если клиент ограничивает их число
ycli mcp methods --toolsets core   # список имён инструментов без запуска сервера
```

Подробнее: [Запуск MCP-сервера](https://ycli.savaznatnov.dev/ru/how-to/serve-the-mcp-server/), [Свой MCP-сервер по HTTP](https://ycli.savaznatnov.dev/ru/how-to/self-host-over-http/) для команды, [справочник инструментов](https://ycli.savaznatnov.dev/reference/mcp/tracker/) (на английском).

### Python

```python
from ycli.yandex.tracker.client import TrackerClient

tracker = TrackerClient(oauth_token="…", organization_id="…")
print(tracker.issues.get("TRACKER-1").summary)
```

Подробнее: [справочник SDK](https://ycli.savaznatnov.dev/reference/sdk/tracker/) (на английском).

### Плагин для Claude Code

```
/plugin marketplace add bim-ba/ycli
/plugin install yandex-360@ycli
```

Он добавляет MCP-сервер и пять навыков (`yandex-360`, `yandex-360-tracker`, `yandex-360-wiki`, `yandex-360-forms`, `yandex-360-datalens`), которые учат агента командам и особенностям API. Исходники: [`plugins/yandex-360/`](plugins/yandex-360/).

## Настройка

```bash
ycli auth login     # получает токен через Яндекс ID, находит вашу организацию, сохраняет оба значения в .env
ycli auth status    # чей это токен и принимает ли его каждый сервис
ycli doctor         # что-то не работает? все проверки по порядку и что исправить
```

В первый раз для `ycli auth login` нужно собственное OAuth-приложение Яндекса: страница [Аутентификация](https://ycli.savaznatnov.dev/ru/how-to/authenticate/) проведёт по шагам. ycli читает две переменные — из окружения или из файла `.env`:

```bash
YANDEX_ID_OAUTH_TOKEN=...        # OAuth-токен Яндекса с доступом к Трекеру, Вики и Формам
YANDEX_ID_ORGANIZATION_ID=...    # идентификатор вашей организации в Яндекс 360
```

Тайм-ауты, повторы, пределы, логирование и коды возврата — в [справочнике по настройкам](https://ycli.savaznatnov.dev/ru/reference/configuration/).

<!-- COVERAGE:START (generated by scripts/gen_coverage.py — do not edit by hand) -->
## Покрытие API

<img src="https://raw.githubusercontent.com/bim-ba/ycli/main/docs/assets/coverage.svg" alt="Операций: 467, ресурсов: 88" width="760">

Операций API Трекера, Вики, Форм и DataLens: **467** (Трекер — 190, Вики — 58, Формы — 85, DataLens — 134), ресурсов: **88**; все операции доступны из **Python SDK** и **CLI**. MCP-инструментов для агентов: **457**. Таблицы по ресурсам и операциям — в [английском README](README.md#coverage).

Из опубликованных Яндексом операций обёрнуто: Трекер — 188 из 190, Вики — 56 из 56, Формы — 84 из 84, DataLens — 134 из 141. Чего ycli пока не умеет (параметры запросов, поля ответов), перечислено в разделе [Against the published API](README.md#against-the-published-api); сверка повторяется каждую неделю.
<!-- COVERAGE:END -->

## Разработка

```bash
uv sync --all-extras   # тесты используют все extras
uv run pytest          # порог покрытия 100%; HTTP подменён, живой сети нет
```

Структура исходников и инварианты, которые держат её в порядке, описаны в [ARCHITECTURE.md](ARCHITECTURE.md); соглашения и порядок добавления эндпоинта — в [CONTRIBUTING.md](CONTRIBUTING.md). Мы рады вашему участию.

## Лицензия

[MIT](LICENSE) © 2026 Sava Znatnov
