# App Config and Server

> 47 nodes · cohesion 0.10

## Key Concepts

- **AppConfig** (39 connections) — `src/ycli/settings.py`
- **ClientFactory** (27 connections) — `src/ycli/yandex/factory.py`
- **Credentials** (25 connections) — `src/ycli/settings.py`
- **YandexError** (19 connections) — `src/ycli/yandex/errors.py`
- **OutputFormat** (15 connections) — `src/ycli/output.py`
- **ServiceProbe** (11 connections) — `src/ycli/yandex/status.py`
- **AuthReport** (10 connections) — `src/ycli/yandex/status.py`
- **ServiceAuthStatus** (10 connections) — `src/ycli/yandex/status.py`
- **Credentials** (9 connections) — `src/ycli/yandex/status.py`
- **_main()** (9 connections) — `src/ycli/cli.py`
- **Any** (8 connections) — `src/ycli/yandex/status.py`
- **Context** (8 connections) — `src/ycli/yandex/status.py`
- **status.py** (8 connections) — `src/ycli/yandex/status.py`
- **SerializationStrategy** (6 connections) — `src/ycli/context.py`
- **AppConfig** (6 connections) — `src/ycli/context.py`
- **Console** (6 connections) — `src/ycli/context.py`
- **Context** (6 connections) — `src/ycli/context.py`
- **FormsClient** (6 connections) — `src/ycli/context.py`
- **TrackerClient** (6 connections) — `src/ycli/context.py`
- **WikiClient** (6 connections) — `src/ycli/context.py`
- **status()** (6 connections) — `src/ycli/yandex/status.py`
- **OutputFormat** (5 connections) — `src/ycli/cli.py`
- **Context** (5 connections) — `src/ycli/cli.py`
- **help** (5 connections) — `src/ycli/cli.py`
- **Option** (5 connections) — `src/ycli/cli.py`
- *... and 22 more nodes in this community*

## Relationships

- [[CLI Commands and Auth]] (29 shared connections)
- [[CLI Command Groups]] (16 shared connections)
- [[Architecture and Docs]] (16 shared connections)
- [[MCP Cached Providers]] (6 shared connections)
- [[Composition Roots Deps]] (4 shared connections)
- [[Wiki Pages MCP]] (4 shared connections)
- [[Forms Answers MCP]] (3 shared connections)
- [[Wiki User Page Models]] (2 shared connections)
- [[Logging MCP Server]] (2 shared connections)
- [[Forms Answers Client]] (1 shared connections)

## Source Files

- `src/ycli/cli.py`
- `src/ycli/context.py`
- `src/ycli/mcp.py`
- `src/ycli/output.py`
- `src/ycli/settings.py`
- `src/ycli/yandex/_mcp.py`
- `src/ycli/yandex/errors.py`
- `src/ycli/yandex/factory.py`
- `src/ycli/yandex/status.py`

## Audit Trail

- EXTRACTED: 106 (35%)
- INFERRED: 201 (65%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*