---
type: how-to
---

# Установка в вашем ИИ-клиенте

Каждый ИИ-клиент получает один и тот же MCP-сервер под одним ключом `yandex-360` и с одними и теми же
двумя переменными. Задайте их один раз в своей оболочке (см. [Аутентификация](authenticate.md));
ни одно значение ниже не содержит секретов.

```bash
export YANDEX_ID_OAUTH_TOKEN=...        # OAuth-токен Яндекса с доступом к Трекеру, Вики и Формам
export YANDEX_ID_ORGANIZATION_ID=...    # идентификатор организации Яндекс 360
```

| ИИ-клиент | Как | Требуется |
|---|---|---|
| [Claude Code](#claude-code) | плагин (навыки + сервер) или `claude mcp add` | `uv` |
| [Claude Desktop](#claude-desktop) | пакет `.mcpb` из релиза на GitHub | `uv` |
| [Cursor](#cursor) | `mcp.json` или ссылка для установки | `uv` |
| [VS Code](#vs-code) | `.vscode/mcp.json` или `code --add-mcp` | `uv` |
| [Codex CLI](#codex-cli) | `~/.codex/config.toml` | `uv` |
| [Gemini CLI](#gemini-cli) | `settings.json` | `uv` |
| [opencode](#opencode) | `opencode.jsonc` | `uv` |
| [ChatGPT](#chatgpt) | локально: через Codex; веб: свой HTTP-сервер | |
| [Docker](#docker) | `ghcr.io/bim-ba/ycli` | Docker |
| [MCP Registry](#mcp-registry) | `io.github.bim-ba/ycli` | |
| [Только навыки](#skills-only) | `npx skills add` | `npx` |

Каждая команда ниже запускает сервер как `uvx --from 'yandex-cli[mcp]' ycli mcp start`: предварительная
установка не нужна, всегда берётся последний релиз. Чтобы зафиксировать версию, укажите
`yandex-cli[mcp]==<version>`. Как отдать меньше инструментов или только чтение, описано в разделе
[Запуск MCP-сервера](serve-the-mcp-server.md).

## Claude Code

Плагин (навыки и сервер вместе, версия сервера совпадает с версией плагина):

```text
/plugin marketplace add bim-ba/ycli
/plugin install yandex-360@ycli
```

Только сервер:

```bash
claude mcp add yandex-360 --transport stdio \
  --env YANDEX_ID_OAUTH_TOKEN="$YANDEX_ID_OAUTH_TOKEN" \
  --env YANDEX_ID_ORGANIZATION_ID="$YANDEX_ID_ORGANIZATION_ID" \
  -- uvx --from 'yandex-cli[mcp]' ycli mcp start
```

## Claude Desktop

Скачайте `yandex-360-<version>.mcpb` из [последнего релиза](https://github.com/bim-ba/ycli/releases/latest)
и откройте его. Claude Desktop запросит токен (он хранится в связке ключей ОС) и идентификатор организации.
Пакет относится к типу `uv` в MCPB, поэтому на машине должен быть `uv`, а Claude Desktop должен
поддерживать этот тип пакетов; если ваш не поддерживает, используйте команду с `uvx` выше в
`claude_desktop_config.json`.

## Cursor

`~/.cursor/mcp.json` (или `.cursor/mcp.json` в проекте):

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

Установка в один клик: [установить в Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=yandex-360&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJ5YW5kZXgtY2xpW21jcF0iLCJ5Y2xpIiwibWNwIiwic3RhcnQiXSwiZW52Ijp7IllBTkRFWF9JRF9PQVVUSF9UT0tFTiI6IiR7ZW52OllBTkRFWF9JRF9PQVVUSF9UT0tFTn0iLCJZQU5ERVhfSURfT1JHQU5JWkFUSU9OX0lEIjoiJHtlbnY6WUFOREVYX0lEX09SR0FOSVpBVElPTl9JRH0ifX0=)
(некоторые просмотрщики блокируют ссылки `cursor://`; вставьте её в адресную строку браузера). Ссылка —
это base64 от объекта сервера выше; заново её можно получить так:

```bash
printf '%s' '{"command":"uvx","args":["--from","yandex-cli[mcp]","ycli","mcp","start"],"env":{"YANDEX_ID_OAUTH_TOKEN":"${env:YANDEX_ID_OAUTH_TOKEN}","YANDEX_ID_ORGANIZATION_ID":"${env:YANDEX_ID_ORGANIZATION_ID}"}}' \
  | base64 -w0   # macOS: base64 -b 0; затем cursor://anysphere.cursor-deeplink/mcp/install?name=yandex-360&config=<вывод>
```

## VS Code

`.vscode/mcp.json` (VS Code спросит два значения и скроет токен):

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

Или в профиль пользователя из командной строки, со значениями из переменных оболочки:

```bash
code --add-mcp '{"name":"yandex-360","command":"uvx","args":["--from","yandex-cli[mcp]","ycli","mcp","start"],"env":{"YANDEX_ID_OAUTH_TOKEN":"${env:YANDEX_ID_OAUTH_TOKEN}","YANDEX_ID_ORGANIZATION_ID":"${env:YANDEX_ID_ORGANIZATION_ID}"}}'
```

## Codex CLI

`~/.codex/config.toml` (или `.codex/config.toml` в доверенном проекте). `env_vars` пробрасывает
переменные из вашей оболочки, поэтому никакие значения нигде не хранятся:

```toml
[mcp_servers.yandex-360]
command = "uvx"
args = ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"]
env_vars = ["YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID"]
startup_timeout_sec = 60   # при первом запуске uvx скачивает пакет
```

## Gemini CLI

`~/.gemini/settings.json` (или `.gemini/settings.json` в проекте):

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

## opencode

`opencode.jsonc` (в проекте) или `~/.config/opencode/opencode.json`:

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
      "enabled": true
    }
  }
}
```

## ChatGPT

| Где | Работает | Почему |
|---|---|---|
| Codex (CLI, десктоп, IDE) | да | локальный stdio, см. [Codex CLI](#codex-cli) |
| ChatGPT в вебе | со своим сервером | он подключается только к удалённым MCP-серверам по HTTPS: запустите `ycli mcp start --transport http` за HTTPS, см. [Свой сервер по HTTP](self-host-over-http.md); публичного экземпляра ycli нет |

## Docker

Образ запускает `ycli mcp start` по stdio. Передавайте переменные по имени, чтобы значения не попадали
в командную строку:

```bash
docker run -i --rm -e YANDEX_ID_OAUTH_TOKEN -e YANDEX_ID_ORGANIZATION_ID ghcr.io/bim-ba/ycli
docker run --rm ghcr.io/bim-ba/ycli --version        # подойдёт и любая другая команда
```

Как запись в MCP-клиенте (тот же ключ, что и везде):

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

Теги: `<version>` (по одному на релиз) и `latest`; `linux/amd64` и `linux/arm64`.

## MCP Registry

Публикуется при каждом релизе как `io.github.bim-ba/ycli` в
[официальном MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.bim-ba/ycli);
клиенты с поддержкой реестра показывают его в списке и оттуда ставят пакет PyPI или образ Docker.

## Только навыки { #skills-only }

Без MCP-сервера четыре пользовательских навыка ставятся в любого агента, который поддерживает
[skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add bim-ba/ycli/plugins/yandex-360
```

`npx skills add bim-ba/ycli` ставит те же четыре навыка: других навыков в репозитории нет.
