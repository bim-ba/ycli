---
description: "Подключите MCP-сервер Яндекс Трекера, Вики и Форм к Claude, Cursor, VS Code, Windsurf, Zed, Codex, Gemini CLI или opencode."
type: how-to
---

# Установка в вашем ИИ-клиенте

Подключите MCP-сервер ycli к ИИ-клиенту, которым вы уже пользуетесь. Каждый клиент получает один и тот же сервер под именем `yandex-360` и одни и те же два значения.

## Перед началом { #before-you-start }

1. Установите [uv](https://docs.astral.sh/uv/getting-started/installation/): каждый фрагмент ниже запускает сервер через `uvx`, который скачивает ycli при первом использовании.
2. Получите два значения (см. [Аутентификация](authenticate.md)):

    | Переменная | Что это |
    |---|---|
    | `YANDEX_ID_OAUTH_TOKEN` | OAuth-токен Яндекса с доступом к Трекеру, Вики и Формам |
    | `YANDEX_ID_ORGANIZATION_ID` | идентификатор вашей организации Яндекс 360 |

3. Клиент, который читает их из окружения, должен получить их экспортированными в той оболочке, которая его запускает:

    ```bash
    export YANDEX_ID_OAUTH_TOKEN=...
    export YANDEX_ID_ORGANIZATION_ID=...
    ```

Ни один фрагмент на этой странице не хранит значения: каждый ссылается на переменную или спрашивает значение у вас.

## Выберите клиент { #pick-your-client }

| Клиент | В один клик | Файл конфигурации | Команда |
|---|---|---|---|
| [Claude Code](#claude-code) | плагин | `.mcp.json` | `claude mcp add` |
| [Claude Desktop](#claude-desktop) | пакет `.mcpb` | `claude_desktop_config.json` | |
| [Cursor](#cursor) | [ссылка для установки](cursor://anysphere.cursor-deeplink/mcp/install?name=yandex-360&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJ5YW5kZXgtY2xpW21jcF0iLCJ5Y2xpIiwibWNwIiwic3RhcnQiXSwiZW52Ijp7IllBTkRFWF9JRF9PQVVUSF9UT0tFTiI6IiR7ZW52OllBTkRFWF9JRF9PQVVUSF9UT0tFTn0iLCJZQU5ERVhfSURfT1JHQU5JWkFUSU9OX0lEIjoiJHtlbnY6WUFOREVYX0lEX09SR0FOSVpBVElPTl9JRH0ifX0=) | `mcp.json` | |
| [VS Code](#vs-code) | [ссылка для установки](https://insiders.vscode.dev/redirect/mcp/install?name=yandex-360&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22yandex-oauth-token%22%2C%22description%22%3A%22Yandex%20OAuth%20token%22%2C%22password%22%3Atrue%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22yandex-organization-id%22%2C%22description%22%3A%22Yandex%20360%20organization%20id%22%7D%5D&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22yandex-cli%5Bmcp%5D%22%2C%22ycli%22%2C%22mcp%22%2C%22start%22%5D%2C%22env%22%3A%7B%22YANDEX_ID_OAUTH_TOKEN%22%3A%22%24%7Binput%3Ayandex-oauth-token%7D%22%2C%22YANDEX_ID_ORGANIZATION_ID%22%3A%22%24%7Binput%3Ayandex-organization-id%7D%22%7D%7D) | `.vscode/mcp.json` | `code --add-mcp` |
| [Windsurf (Devin Desktop)](#windsurf-devin-desktop) | | `mcp_config.json` | `devin mcp add` |
| [Zed](#zed) | | `settings.json` | |
| [Codex](#codex) | | `config.toml` | `codex mcp add` |
| [Gemini CLI](#gemini-cli) | | `settings.json` | |
| [opencode](#opencode) | | `opencode.json` | |
| [ChatGPT](#chatgpt) | | | |
| [Любой другой клиент](#any-other-client) | | собственный файл клиента | |

Предпочитаете контейнер вместо `uv`? См. [Docker](#docker). Что-то не работает? См. [Если не работает](#if-it-does-not-work).

## Claude Code { #claude-code }

=== "В один клик"

    Плагин ставит сервер и четыре навыка вместе, с версией, равной версии плагина:

    ```text
    /plugin marketplace add bim-ba/ycli
    /plugin install yandex-360@ycli
    ```

=== "Файл конфигурации"

    `.mcp.json` в корне проекта (общий для команды; Claude Code подставляет `${VAR}` при запуске сервера):

    ```json
    {
      "mcpServers": {
        "yandex-360": {
          "type": "stdio",
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "${YANDEX_ID_OAUTH_TOKEN}",
            "YANDEX_ID_ORGANIZATION_ID": "${YANDEX_ID_ORGANIZATION_ID}"
          }
        }
      }
    }
    ```

=== "Команда"

    ```bash
    claude mcp add yandex-360 --transport stdio \
      --env YANDEX_ID_OAUTH_TOKEN='${YANDEX_ID_OAUTH_TOKEN}' \
      --env YANDEX_ID_ORGANIZATION_ID='${YANDEX_ID_ORGANIZATION_ID}' \
      -- uvx --from 'yandex-cli[mcp]' ycli mcp start
    ```

    Оставьте одинарные кавычки: с двойными ваша оболочка подставит настоящий токен в конфигурацию. Добавьте `--scope project`, чтобы записать `.mcp.json`, а не ваши личные настройки.

Проверка: `claude mcp get yandex-360` показывает `Connected`. *Проверено в Claude Code 2.1.285 на 2026-10-03: команда и файл подключаются.*

## Claude Desktop { #claude-desktop }

=== "В один клик"

    Скачайте `yandex-360-<version>.mcpb` из [последнего релиза](https://github.com/bim-ba/ycli/releases/latest) и откройте его или выберите его в **Settings → Extensions → Advanced settings → Extension Developer → Install Extension…**. Claude Desktop запросит токен (он хранится в связке ключей системы) и идентификатор организации.

=== "Файл конфигурации"

    | Система | Файл |
    |---|---|
    | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
    | Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

    Claude Desktop не читает переменные вашей оболочки, поэтому в этом файле лежат сами значения. Лучше используйте пакет: он хранит токен в связке ключей.

    ```json
    {
      "mcpServers": {
        "yandex-360": {
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "<ваш токен>",
            "YANDEX_ID_ORGANIZATION_ID": "<идентификатор организации>"
          }
        }
      }
    }
    ```

После любого из изменений полностью закройте Claude Desktop и запустите его снова. *Сверено с документацией Claude на 2026-10-03; не запускалось.*

## Cursor { #cursor }

=== "В один клик"

    [Установить в Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=yandex-360&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJ5YW5kZXgtY2xpW21jcF0iLCJ5Y2xpIiwibWNwIiwic3RhcnQiXSwiZW52Ijp7IllBTkRFWF9JRF9PQVVUSF9UT0tFTiI6IiR7ZW52OllBTkRFWF9JRF9PQVVUSF9UT0tFTn0iLCJZQU5ERVhfSURfT1JHQU5JWkFUSU9OX0lEIjoiJHtlbnY6WUFOREVYX0lEX09SR0FOSVpBVElPTl9JRH0ifX0=). Некоторые просмотрщики блокируют ссылки `cursor://`: скопируйте ссылку в адресную строку браузера.

=== "Файл конфигурации"

    `~/.cursor/mcp.json` для всех проектов или `.cursor/mcp.json` для одного:

    ```json
    {
      "mcpServers": {
        "yandex-360": {
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "${env:YANDEX_ID_OAUTH_TOKEN}",
            "YANDEX_ID_ORGANIZATION_ID": "${env:YANDEX_ID_ORGANIZATION_ID}"
          }
        }
      }
    }
    ```

Ссылка устанавливает ровно тот объект, что во вкладке с файлом (его base64). *Сверено с документацией Cursor на 2026-10-03; не запускалось.*

## VS Code { #vs-code }

=== "В один клик"

    [Установить в VS Code](https://insiders.vscode.dev/redirect/mcp/install?name=yandex-360&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22yandex-oauth-token%22%2C%22description%22%3A%22Yandex%20OAuth%20token%22%2C%22password%22%3Atrue%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22yandex-organization-id%22%2C%22description%22%3A%22Yandex%20360%20organization%20id%22%7D%5D&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22yandex-cli%5Bmcp%5D%22%2C%22ycli%22%2C%22mcp%22%2C%22start%22%5D%2C%22env%22%3A%7B%22YANDEX_ID_OAUTH_TOKEN%22%3A%22%24%7Binput%3Ayandex-oauth-token%7D%22%2C%22YANDEX_ID_ORGANIZATION_ID%22%3A%22%24%7Binput%3Ayandex-organization-id%7D%22%7D%7D). При первом запуске VS Code спросит два значения и скроет токен.

=== "Файл конфигурации"

    `.vscode/mcp.json` в рабочей области (для вашего пользовательского профиля выполните **MCP: Open User Configuration**):

    ```json
    {
      "inputs": [
        { "type": "promptString", "id": "yandex-oauth-token", "description": "Yandex OAuth token", "password": true },
        { "type": "promptString", "id": "yandex-organization-id", "description": "Yandex 360 organization id" }
      ],
      "servers": {
        "yandex-360": {
          "type": "stdio",
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "${input:yandex-oauth-token}",
            "YANDEX_ID_ORGANIZATION_ID": "${input:yandex-organization-id}"
          }
        }
      }
    }
    ```

=== "Команда"

    В ваш пользовательский профиль, с теми же запросами значений:

    ```bash
    code --add-mcp '{"name":"yandex-360","command":"uvx","args":["--from","yandex-cli[mcp]","ycli","mcp","start"],"env":{"YANDEX_ID_OAUTH_TOKEN":"${input:yandex-oauth-token}","YANDEX_ID_ORGANIZATION_ID":"${input:yandex-organization-id}"},"inputs":[{"type":"promptString","id":"yandex-oauth-token","description":"Yandex OAuth token","password":true},{"type":"promptString","id":"yandex-organization-id","description":"Yandex 360 organization id"}]}'
    ```

VS Code отправляет в одном запросе не больше 128 инструментов, а у ycli их больше: начните с `--toolsets core` (добавьте `"--toolsets", "core"` в `args`), см. [Запуск MCP-сервера](serve-the-mcp-server.md). *Проверено в VS Code 1.139.1 на 2026-10-03: команда записывает сервер и оба запроса значений в пользовательский профиль. Ссылка и сеанс чата не запускались.*

## Windsurf (Devin Desktop) { #windsurf-devin-desktop }

Windsurf теперь называется Devin Desktop; оба его агента читают один и тот же файл.

=== "Файл конфигурации"

    | Система | Файл |
    |---|---|
    | macOS, Linux | `~/.config/devin/mcp_config.json` |
    | Windows | `%APPDATA%\devin\mcp_config.json` |

    ```json
    {
      "mcpServers": {
        "yandex-360": {
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start", "--toolsets", "core"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "${env:YANDEX_ID_OAUTH_TOKEN}",
            "YANDEX_ID_ORGANIZATION_ID": "${env:YANDEX_ID_ORGANIZATION_ID}"
          }
        }
      }
    }
    ```

=== "Команда"

    ```bash
    devin mcp add -s user yandex-360 -- uvx --from 'yandex-cli[mcp]' ycli mcp start --toolsets core
    ```

    Затем добавьте блок `env` выше в запись, которую команда создала.

Агент Cascade принимает всего 100 инструментов, поэтому фрагмент отдаёт набор `core`. Старый Windsurf держит файл в `~/.codeium/windsurf/mcp_config.json`. *Сверено с документацией Devin на 2026-10-03; не запускалось. Старого пути в текущей документации нет.*

## Zed { #zed }

=== "Файл конфигурации"

    Откройте файл настроек (**zed: open settings file**) или добавьте сервер в **Settings → AI → MCP Servers → Add Server → Add Local Server**:

    ```json
    {
      "context_servers": {
        "yandex-360": {
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start", "--toolsets", "core"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "<ваш токен>",
            "YANDEX_ID_ORGANIZATION_ID": "<идентификатор организации>"
          }
        }
      }
    }
    ```

В документации Zed нет способа сослаться здесь на переменную, поэтому в файле лежат сами значения. *Сверено с документацией Zed на 2026-10-03; не запускалось.*

## Codex { #codex }

=== "Файл конфигурации"

    `~/.codex/config.toml` или `.codex/config.toml` в доверенном проекте. `env_vars` пробрасывает переменные из вашей оболочки:

    ```toml
    [mcp_servers.yandex-360]
    command = "uvx"
    args = ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"]
    env_vars = ["YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID"]
    startup_timeout_sec = 60   # при первом запуске uvx скачивает пакет
    ```

=== "Команда"

    ```bash
    codex mcp add yandex-360 -- uvx --from 'yandex-cli[mcp]' ycli mcp start
    ```

    Затем добавьте строки `env_vars` и `startup_timeout_sec` выше в запись, которую команда создала: `--env` сохранил бы сам токен.

Проверка: `codex mcp list` показывает `yandex-360` как `enabled`. После изменений перезапустите Codex. *Проверено в Codex 0.159.2 на 2026-10-03: он принимает файл, а команда создаёт запись. Сеанс не запускался.*

## Gemini CLI { #gemini-cli }

=== "Файл конфигурации"

    `~/.gemini/settings.json` или `.gemini/settings.json` в проекте:

    ```json
    {
      "mcpServers": {
        "yandex-360": {
          "command": "uvx",
          "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
          "env": {
            "YANDEX_ID_OAUTH_TOKEN": "$YANDEX_ID_OAUTH_TOKEN",
            "YANDEX_ID_ORGANIZATION_ID": "$YANDEX_ID_ORGANIZATION_ID"
          }
        }
      }
    }
    ```

    Оставьте блок `env`: Gemini CLI скрывает унаследованные переменные, в имени которых есть `TOKEN`, если сервер их не перечислил.

*Сверено с документацией Gemini CLI на 2026-10-03; не запускалось.*

## opencode { #opencode }

=== "Файл конфигурации"

    `opencode.json` в проекте или `~/.config/opencode/opencode.json`:

    ```json
    {
      "$schema": "https://opencode.ai/config.json",
      "mcp": {
        "yandex-360": {
          "type": "local",
          "command": ["uvx", "--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
          "environment": {
            "YANDEX_ID_OAUTH_TOKEN": "{env:YANDEX_ID_OAUTH_TOKEN}",
            "YANDEX_ID_ORGANIZATION_ID": "{env:YANDEX_ID_ORGANIZATION_ID}"
          },
          "timeout": 60000,
          "enabled": true
        }
      }
    }
    ```

    Оставьте `timeout`: opencode по умолчанию ждёт 5 секунд, а для запуска сервера этого мало.

Проверка: `opencode mcp list` показывает `yandex-360` как `connected`. *Проверено в opencode 2.0.20 на 2026-10-03: файл подключается; без `timeout` сервер оставался в состоянии `pending`. Сеанс не запускался.*

## ChatGPT { #chatgpt }

| Где | Работает | Как |
|---|---|---|
| Codex (CLI, десктоп, IDE) | да | локальный сервер, см. [Codex](#codex) |
| ChatGPT в вебе | со своим сервером | он подключается только к удалённым HTTPS-серверам: см. [Свой MCP-сервер по HTTP](self-host-over-http.md). Публичного экземпляра ycli нет |

## Любой другой клиент { #any-other-client }

Клиенту, который говорит по MCP через stdio, нужны три вещи, как бы ни назывался его файл: команда, её аргументы и две переменные.

```json
{
  "mcpServers": {
    "yandex-360": {
      "command": "uvx",
      "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"],
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "<ваш токен>",
        "YANDEX_ID_ORGANIZATION_ID": "<идентификатор организации>"
      }
    }
  }
}
```

Если клиент ограничивает число принимаемых инструментов, добавьте `"--toolsets", "core"` в `args`. Клиенты с поддержкой реестра также находят сервер как `io.github.bim-ba/ycli` в [официальном MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.bim-ba/ycli); он публикуется при каждом релизе.

## Docker { #docker }

Образ `ghcr.io/bim-ba/ycli` — это сам ycli: без аргументов он отдаёт MCP по stdio, с аргументами выполняет указанную команду. Используйте его в любом клиенте вместо `uvx`; `-e NAME` без значения передаёт переменную из вашего окружения:

```json
{
  "mcpServers": {
    "yandex-360": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "YANDEX_ID_OAUTH_TOKEN", "-e", "YANDEX_ID_ORGANIZATION_ID", "ghcr.io/bim-ba/ycli"]
    }
  }
}
```

Как обычный CLI, с двумя переменными в файле:

```bash
docker run --rm --env-file .env ghcr.io/bim-ba/ycli tracker issues get TRACKER-1
docker run --rm ghcr.io/bim-ba/ycli --version
```

Теги: `<version>` для каждого релиза и `latest`; `linux/amd64` и `linux/arm64`. О конвейерах см. [Использование в CI](use-in-ci.md). *Проверено в Docker на 2026-10-03: обе команды работают.*

## Только навыки { #skills-only }

Без MCP-сервера четыре навыка ставятся в любого агента, который поддерживает [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add bim-ba/ycli/plugins/yandex-360
```

## Обновление и фиксация версии { #update-or-pin-the-version }

`uvx` скачивает последний релиз при первом запуске и потом использует эту копию.

| Что нужно | Что написать |
|---|---|
| самый новый релиз при каждом запуске | `uvx --from 'yandex-cli[mcp]@latest' ycli mcp start` |
| одна фиксированная версия | `uvx --from 'yandex-cli[mcp]==0.49.0' ycli mcp start` |
| один раз обновить копию | `uvx --refresh-package yandex-cli --from 'yandex-cli[mcp]' ycli --version` |

## Если не работает { #if-it-does-not-work }

| Симптом | Причина и решение |
|---|---|
| Клиент не находит `uvx` | Приложение, запущенное из Dock или лаунчера, не видит `PATH` вашей оболочки. Укажите в `command` полный путь: его печатает `which uvx` |
| Каждый вызов отвечает, что `YANDEX_ID_OAUTH_TOKEN` или `YANDEX_ID_ORGANIZATION_ID` не задан | Клиент не передал две переменные. Десктопное приложение не читает экспорты вашей оболочки: используйте его запрос значений или пакет либо впишите значения туда, где сказано в его разделе |
| После правки конфигурации ничего не меняется | Перезапустите клиент; Claude Desktop нужно закрыть полностью |
| Первый запуск завершается по тайм-ауту | При первом запуске `uvx` скачивает пакет. Один раз выполните в терминале `uvx --from 'yandex-cli[mcp]' ycli --version` или увеличьте тайм-аут запуска в клиенте |
| Клиент отклоняет сервер или скрывает инструменты | Он ограничивает число инструментов (VS Code 128, Cascade 100). Отдавайте меньше: `--toolsets core`, см. [Запуск MCP-сервера](serve-the-mcp-server.md) |
| Вызов отвечает 401 или 403 | Токен неверный или ему не хватает права: выполните `ycli doctor` с теми же двумя значениями: он назовёт проверку, которая не прошла, и что исправить |

Чтобы увидеть, что делает сервер, запустите его вручную и прочитайте ошибку, которую он печатает:

```bash
uvx --from 'yandex-cli[mcp]' ycli mcp methods --toolsets core   # показывает инструменты, учётные данные не нужны
uvx --from 'yandex-cli[mcp]' ycli auth status                   # проверяет два значения
```

Команда, которая выполнит эти проверки за вас, запланирована: следите за [#206](https://github.com/bim-ba/ycli/issues/206).
