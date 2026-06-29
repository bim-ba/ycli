# MCP Cached Providers

> 10 nodes · cohesion 0.22

## Key Concepts

- **CachedProvider** (8 connections) — `src/ycli/yandex/_mcp.py`
- **_mcp.py** (5 connections) — `src/ycli/yandex/_mcp.py`
- **make_cached_client()** (4 connections) — `src/ycli/yandex/_mcp.py`
- **app_config()** (3 connections) — `src/ycli/yandex/_mcp.py`
- **.__call__()** (2 connections) — `src/ycli/yandex/_mcp.py`
- **.cache_clear()** (1 connections) — `src/ycli/yandex/_mcp.py`
- **Shared FastMCP tool annotations + the cached per-domain client/config providers.** (1 connections) — `src/ycli/yandex/_mcp.py`
- **Typed zero-arg provider wrapping ``functools.cache`` — exposes ``cache_clear()``** (1 connections) — `src/ycli/yandex/_mcp.py`
- **Build (once) the process-wide app config for MCP tools.** (1 connections) — `src/ycli/yandex/_mcp.py`
- **Return a ``@cache``d zero-arg provider building ``client_cls`` from the env.** (1 connections) — `src/ycli/yandex/_mcp.py`

## Relationships

- [[App Config and Server]] (6 shared connections)
- [[CLI Command Groups]] (1 shared connections)

## Source Files

- `src/ycli/yandex/_mcp.py`

## Audit Trail

- EXTRACTED: 24 (89%)
- INFERRED: 3 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*