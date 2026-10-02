<div align="center">

# ycli

**Один набор инструментов для Яндекс 360 — четыре способа работы.**
Управляйте **Трекером**, **Вики** и **Формами** из CLI, MCP-сервера, Python SDK
или плагина для Claude Code. Сделан прежде всего для ИИ-агентов, но и людям работать с ним приятно.

[English](README.md) · **Русский**

[![CI](https://img.shields.io/github/actions/workflow/status/bim-ba/ycli/ci.yml?branch=main&logo=githubactions&logoColor=white&label=ci)](https://github.com/bim-ba/ycli/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=pytest&logoColor=white)](https://github.com/bim-ba/ycli)
[![PyPI](https://img.shields.io/pypi/v/yandex-cli?logo=pypi&logoColor=white&label=pypi)](https://pypi.org/project/yandex-cli/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-bim--ba.github.io%2Fycli-blue?logo=materialformkdocs&logoColor=white)](https://bim-ba.github.io/ycli/ru/)
[![DeepWiki](https://img.shields.io/badge/deepwiki-ask%20the%20repo-blue?logo=readthedocs&logoColor=white)](https://deepwiki.com/bim-ba/ycli)

<img src="https://raw.githubusercontent.com/bim-ba/ycli/main/docs/assets/demo.gif" alt="ycli in action" width="760">

</div>

- 🧩 **Один SDK, четыре способа работы** — пишете логику один раз, а используете как CLI, MCP-сервер,
  Python-библиотеку или плагин для Claude Code.
- 🤖 **Создан для агентов** — MCP-сервер отдаёт инструменты `tracker_*`, `wiki_*`, `forms_*` и для
  чтения, **и для записи**, по одному на каждую операцию SDK и CLI, плюс сквозной инструмент `status`
  (числа — в разделе [Покрытие API](#покрытие-api)), с честными аннотациями (чтения помечены как
  «только чтение», записи сообщают, разрушающие они или идемпотентные); `ycli mcp start --read-only`
  отдаёт только чтение для осторожных развёртываний, а `--toolsets core` — отобранный набор на каждый
  день, если хост ограничивает число принимаемых инструментов.
- 🛡️ **Надёжность** — типизированные pydantic-модели, особенности настоящего API Яндекса учтены за вас,
  а набор тестов держится на **100% покрытия**.
- ⚡ **Быстрый старт** — `uv add yandex-cli`, `ycli auth login` — и вперёд.

Полная документация (обучение, руководства, справочник по CLI, MCP и SDK) — на
[bim-ba.github.io/ycli/ru](https://bim-ba.github.io/ycli/ru/).

## Установка

```bash
uv add yandex-cli            # CLI + Python SDK
uv add 'yandex-cli[mcp]'     # …плюс MCP-сервер (`ycli mcp start`)
```

Запустить без установки или поставить как отдельный инструмент:

```bash
uvx yandex-cli --help                 # разово, без установки
uv tool install yandex-cli            # постоянный CLI
uv tool install 'yandex-cli[mcp]'     # …с MCP-сервером
```

`pip install yandex-cli` тоже работает. CLI поставляется под двумя именами: `yandex-cli` и коротким `ycli`.

Пользуетесь ИИ-клиентом (Claude Code, Claude Desktop, Cursor, VS Code, Codex, Gemini CLI, opencode,
Docker)? См. [Установка в вашем ИИ-клиенте](https://bim-ba.github.io/ycli/ru/how-to/install-in-your-harness/).

Для `ServiceAccountAuth` из SDK (IAM-токены, выпускаемые по ключу сервисного аккаунта Yandex Cloud)
нужно дополнение `service-account`: `uv add 'yandex-cli[service-account]'`.

## Быстрый старт

Выберите способ, который подходит вашей работе.

<details open>
<summary><b>CLI</b></summary>

```bash
uv add yandex-cli
ycli --help
ycli tracker issues get TRACKER-1
ycli wiki pages get onboarding
```

**Форматы вывода** — глобальный флаг `--format` / `-o` выбирает, как печатать результат (глобальные опции работают до подкоманды и после неё: `ycli -o json tracker issues get K` = `ycli tracker issues get K -o json`; команда, у которой есть собственная одноимённая опция, например `forms answers export --format`, оставляет её себе):

```bash
ycli tracker issues get TRACKER-1            # auto: красивая таблица в терминале…
ycli tracker issues get TRACKER-1 | jq .     # …и чистый JSON при передаче по конвейеру (безопасно для агентов и скриптов)
ycli -o yaml wiki pages get onboarding       # или: -o json | -o yaml | -o pretty
ycli --jq .summary tracker issues get TRACKER-1   # отфильтровать JSON через jq; строка печатается без кавычек
```

`--jq EXPR` выполняет программу [jq](https://jqlang.org) над JSON-результатом команды и печатает как
`jq -r`: строка выводится как есть, всё остальное — по одному компактному значению JSON в строке.
Сочетать его с `-o yaml` / `-o pretty` нельзя, а ещё ему нужен Python-пакет `jq` (это зависимость;
сборки для Windows на ARM у него нет).

**Удаление сначала спрашивает.** Команда, которая уничтожает данные (любые `delete`, `clear`, `abort`…),
в терминале спрашивает в stderr `DELETE <url> — this deletes data. Continue?` и завершается с кодом 1,
если вы отказались. В скрипте, конвейере или CI спрашивать некого, поэтому она завершается с кодом 2,
пока вы не передадите `--yes` / `-y`: `ycli tracker boards delete 7 --yes`. Чтения и обычные записи
никогда не спрашивают.

**Предпросмотр записи.** `--dry-run` ничего не отправляет ни для какой записи: вместо этого он печатает
запрос (метод, URL, тело; но никогда не ваш токен) через тот же вывод `-o` / `--jq` и завершается с
кодом 0. Чтения всё равно выполняются, поэтому команда, которая сначала читает, а потом пишет, покажет
только свою первую запись: `ycli tracker boards delete 7 --dry-run`. (Две команды, которые просят
проверить запрос сам API, — `forms filling submit` и `wiki pages move`, — называют это
`--validate-only`.)

**Эндпоинт, который ycli не оборачивает.** `ycli api PATH --service tracker|wiki|forms` вызывает его так
же, как [`gh api`](https://cli.github.com/manual/gh_api): с той же аутентификацией, повторами, выводом и
кодами возврата:

```bash
ycli api issues/TRACKER-1 --service tracker --jq .summary           # GET (метод по умолчанию)
ycli api issues/TRACKER-1/comments --service tracker -F text=@note.md   # POST: поле превращает запрос в него
ycli api pages/descendants --service wiki -f slug=docs --paginate   # все страницы одним JSON-массивом
```

`PATH` задаётся относительно базового URL сервиса; полному URL сервиса `--service` не нужен, а любой
другой хост отклоняется (ваш токен никуда больше не уходит). `-f key=value` — это строка, `-F` —
типизированное значение (`true`, `null`, числа, JSON, `@file` — текст файла, `key[sub]=v` — вложенное
поле, `key[]=v` — элемент массива); поля запроса GET или DELETE уходят в строку запроса, во всех остальных
случаях — в JSON-тело (`--input FILE` отправляет вместо этого тело как есть). `-H 'Name: value'` добавляет
заголовок, `-X` задаёт метод, а `--dry-run`, `--yes` и `--jq` работают так же, как везде. `--paginate`
идёт по `Link: rel="next"` в Трекере и по `next_cursor` в Вики; Формы разбивают списки на страницы
несколькими способами, поэтому параметры постраничной выдачи передавайте сами через `-f`.
</details>

<details>
<summary><b>MCP-сервер</b> (чтение и запись)</summary>

Запуск по stdio (нужно дополнение `mcp`):

```bash
ycli mcp start               # полный набор инструментов для чтения и записи (честные аннотации)
ycli mcp start --read-only   # только чтение, для осторожных развёртываний
```

Если отдавать все инструменты, `tools/list` получается огромным, а некоторые хосты ограничивают
запрос (VS Code принимает 128 инструментов), поэтому выберите то, что нужно в этой сессии:

| Флаг | Что отдаёт |
|---|---|
| `--toolsets tracker,wiki` | только перечисленные сервисы (`tracker`, `wiki`, `forms`); по умолчанию `all` |
| `--toolsets core` | отобранный набор на каждый день, около 40 инструментов (задачи, комментарии, переходы, учёт времени, страницы Вики и поиск, чтение форм) |
| `--tools a,b` / `--exclude-tools a,b` | добавить или скрыть отдельные инструменты по имени (неизвестное имя приводит к ошибке при запуске) |
| `--read-only` | без инструментов записи; всегда главнее перечисленных выше флагов |
| `--tool-search` | вместо инструментов показывает инструмент поиска и прокси для вызова; используйте с большим набором |

`status_get` отдаётся всегда. В списке нет схем вывода и примеров для doctest (результаты по-прежнему
содержат `structuredContent`), из-за чего `tools/list` для полного набора сокращается примерно с 1,9 МБ
до 0,5 МБ.

Для нескольких пользователей поднимите сервер по HTTP: каждый MCP-клиент входит от имени своего
пользователя через Яндекс ID (OAuth), и каждый вызов инструмента выполняется с собственным токеном
Яндекса этого пользователя. Настройка, включая OAuth-приложение Яндекса и обратный прокси, описана в
разделе [Свой сервер по HTTP](https://bim-ba.github.io/ycli/ru/how-to/self-host-over-http/).

```bash
ycli mcp start --transport http --toolsets core   # нужны YCLI__MCP__BASE_URL и OAuth-приложение
```

Посмотреть имена инструментов, которые дадут выбранные флаги, не запуская сервер:

```bash
ycli mcp methods --toolsets core --read-only
```

Направьте на него MCP-клиент — предварительная установка через `uvx` не нужна (у инструментов
префиксы `tracker_*`, `wiki_*`, `forms_*`):

```json
{
  "mcpServers": {
    "yandex": {
      "command": "uvx",
      "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "...",
        "YANDEX_ID_ORGANIZATION_ID": "..."
      }
    }
  }
}
```
</details>

<details>
<summary><b>Python SDK</b></summary>

```python
from ycli.yandex.tracker.client import TrackerClient

tracker = TrackerClient(oauth_token="…", organization_id="…")
issue = tracker.issues.get("TRACKER-1")
print(issue.summary)
```
</details>

<details>
<summary><b>Плагин для Claude Code</b></summary>

```
/plugin marketplace add bim-ba/ycli
/plugin install yandex-360@ycli
```

Учит агента работать с Яндекс 360 через `ycli` — включая настоящие особенности API.
См. [`plugins/yandex-360/`](plugins/yandex-360/).
</details>

## Навыки (плагин для Claude Code)

| Навык | Для чего |
|-------|---------|
| `yandex-360` | Точка входа — установка и аутентификация, выбор способа работы (CLI/MCP/SDK), переход к нужной области |
| `yandex-360-tracker` | Задачи, эпики, комментарии, переходы, связи, учёт времени, история изменений |
| `yandex-360-wiki` | Страницы Вики, дерево страниц, комментарии, вложения, разметка YFM |
| `yandex-360-forms` | Формы, вопросы и схема, ответы, публикация |

Навыки описывают команды чтения и записи **и** запутанные особенности API Яндекса
(эпик и родитель, поиск переходов, постоянные слаги страниц Вики, правила `fields=`, ловушки с хостом и
заголовком в Формах, постраничная выдача ответов).

## Настройка

`ycli` читает два значения из окружения (или из файла `.env` — `cp .env.example .env`):

```bash
YANDEX_ID_OAUTH_TOKEN=...        # OAuth-токен Яндекса с доступом к Трекеру, Вики и Формам
YANDEX_ID_ORGANIZATION_ID=...    # идентификатор вашей организации в Яндекс 360
```

ycli передаёт идентификатор организации как `X-Org-Id` для каждого сервиса (имена HTTP-заголовков не
чувствительны к регистру по RFC 9110, поэтому один вариант написания подходит всем).

Необязательные настройки задаются по схеме `YCLI__<GROUP>__<SETTING>`; ycli отклоняет недопустимое
значение при запуске и называет переменную:

| Переменная | По умолчанию | Значение |
|---|---|---|
| `YCLI__HTTP__TIMEOUT_SECONDS` | `30` | Тайм-аут одного запроса, секунды (> 0) |
| `YCLI__HTTP__RETRIES` | `3` | Число повторов идемпотентных запросов после 429/5xx (≥ 0) |
| `YCLI__HTTP__MAX_ITEMS` | `500` | Предел числа элементов в списках без `--limit`/`--all` (> 0) |
| `YCLI__LOGGING__LEVEL` | `WARNING` | `DEBUG`, `INFO`, `WARNING`, `ERROR` или `CRITICAL`; `-v` означает `INFO` (каждый HTTP-запрос), `-vv` — `DEBUG` |
| `YCLI__LOGGING__FORMAT` | `text` | `text` или `json` (один объект в строке); логи всегда идут в stderr |

### Получите учётные данные

Яндекс выдаёт OAuth-токены только через **зарегистрированное приложение**, поэтому нужно один раз
зарегистрировать приложение и выполнить одну команду.

**1. Зарегистрируйте OAuth-приложение** на [oauth.yandex.ru](https://oauth.yandex.ru/client/new) и
выдайте ему права на **Трекер**, **Вики** и **Формы** (чтение **и** запись — CLI и MCP-сервер оба
пишут; одних прав на чтение хватает, только если вы запускаете MCP-сервер как
`ycli mcp start --read-only`). Положите **ClientID** — а также **Client secret**, если нужен сценарий
без браузера, — в свой `.env` (ycli читает его оттуда):

```bash
YANDEX_OAUTH_CLIENT_ID=...        # из вашего приложения
YANDEX_OAUTH_CLIENT_SECRET=...    # необязательно — включает device flow без браузера
```

**2. Войдите.** `ycli auth login` получает токен, определяет вашу организацию и записывает оба значения
в `.env`:

```bash
ycli auth login
```

- **client id + secret** → **device flow**: ycli печатает код и ссылку `https://ya.ru/device`; вы
  подтверждаете вход там, и он получает токен — без редиректа, работает и по SSH.
- **только client id** (или `--implicit`) → **browser flow**: ycli открывает страницу авторизации Яндекса;
  вы подтверждаете вход, затем копируете показанный токен и вставляете его обратно.

Проверить можно в любой момент командой `ycli auth status`: она показывает, чей это токен (по данным
Яндекс ID), вашу организацию (для её названия нужен необязательный доступ
`directory:read_organization`; без него вы получите идентификатор и пояснение) и принимает ли токен
каждый сервис. `ycli tracker auth status` (или `wiki`, `forms`) проверяет только один сервис. Обе команды
завершаются с ненулевым кодом, если сервис отклонил токен.

<details>
<summary><b>Хотите сделать это вручную?</b></summary>

**Без браузера (device flow):**

```bash
# 1. запустить процесс — вернёт user_code + verification_url
curl -s -X POST https://oauth.yandex.ru/device/code -d "client_id=$YANDEX_OAUTH_CLIENT_ID"
# 2. открыть https://ya.ru/device, ввести user_code, подтвердить
# 3. обменять device_code на токен
curl -s -X POST https://oauth.yandex.ru/token \
  -d grant_type=device_code -d "code=<device_code>" \
  -d "client_id=$YANDEX_OAUTH_CLIENT_ID" -d "client_secret=$YANDEX_OAUTH_CLIENT_SECRET"
```

**Браузер (implicit):** откройте
`https://oauth.yandex.ru/authorize?response_type=token&client_id=<ClientID>` в браузере, где вы вошли
в аккаунт, подтвердите доступ и скопируйте токен со страницы. (Обычным `curl` так не получится — для
implicit нужна интерактивная сессия в браузере.)

**Идентификатор организации:** [tracker.yandex.ru/admin/orgs](https://tracker.yandex.ru/admin/orgs) →
ваша организация → скопируйте идентификатор.
</details>

Документация Яндекса по каждому шагу:

| Шаг | Документация Яндекса |
|---|---|
| Регистрация OAuth-приложения | [Регистрация приложения](https://yandex.ru/dev/id/doc/ru/register-client) (Яндекс ID) |
| Device flow (`ycli auth login` с секретом) | [Ввод кода на странице авторизации](https://yandex.ru/dev/id/doc/ru/codes/screen-code-oauth) |
| Browser flow (`--implicit`) | [Получение токена вручную](https://yandex.ru/dev/id/doc/ru/tokens/debug-token) |
| Токен и заголовок организации для каждого сервиса | Доступ к API: [Трекер](https://yandex.ru/support/tracker/ru/api/access) · [Вики](https://yandex.ru/support/wiki/ru/api-ref/access) · [Формы](https://yandex.ru/support/forms/ru/api-ref/access) |

## Коды возврата

Завершившаяся ошибкой команда `ycli` возвращает код, который говорит, что именно пошло не так, поэтому скрипт может ветвиться, не разбирая текст сообщения.

| Код | Значение | Когда |
|---|---|---|
| 0 | успех | команда выполнена |
| 1 | сбой | любой другой сбой: 4xx, который отклонил API, неопознанная ошибка, отказ от подтверждения |
| 2 | использование | неверная командная строка или недопустимая настройка `YCLI__…` |
| 3 | не найдено | API ответил 404 (или токен не видит этот объект) |
| 4 | аутентификация | 401 / 403 или не заданы учётные данные |
| 5 | лимит запросов | API ответил 429, и повторы закончились (в подсказке указан `Retry-After`) |
| 6 | временный сбой | 5xx, тайм-аут или потеря соединения: стоит повторить позже |

<!-- COVERAGE:START (generated by scripts/gen_coverage.py — do not edit by hand) -->
## Покрытие API

<img src="https://raw.githubusercontent.com/bim-ba/ycli/main/docs/assets/coverage.svg" alt="Операций: 334, ресурсов: 62" width="760">

Операций REST API Трекера, Вики и Форм: **334** (Трекер — 190, Вики — 58, Формы — 86), ресурсов: **62**; все операции доступны из **Python SDK** и **CLI**. MCP-инструментов для агентов: **322**. Таблицы по ресурсам и операциям — в [английском README](README.md#coverage).
<!-- COVERAGE:END -->

## Разработка

```bash
uv sync --all-extras   # --all-extras подтягивает дополнение `mcp`, которое используют тесты
uv run pytest          # порог покрытия 100%; HTTP подменён через `MockAPI` (без живой сети)
```

Структура исходников и инварианты, которые держат её в порядке, описаны в [ARCHITECTURE.md](ARCHITECTURE.md);
соглашения и порядок добавления эндпоинта — в [CONTRIBUTING.md](CONTRIBUTING.md).
Мы рады вашему участию.

## Лицензия

[MIT](LICENSE) © 2026 Sava Znatnov
