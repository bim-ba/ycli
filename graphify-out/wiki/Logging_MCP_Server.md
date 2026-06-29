# Logging MCP Server

> 8 nodes · cohesion 0.29

## Key Concepts

- **log.py** (4 connections) — `src/ycli/log.py`
- **configure()** (4 connections) — `src/ycli/log.py`
- **mcp.py** (4 connections) — `src/ycli/mcp.py`
- **main()** (4 connections) — `src/ycli/mcp.py`
- **Central loguru configuration — one sink to stderr, idempotent.  ``configure()``** (1 connections) — `src/ycli/log.py`
- **Install a single stderr sink at ``level`` (idempotent — safe to call repeatedly)** (1 connections) — `src/ycli/log.py`
- **Root Yandex 360 FastMCP server — mounts the per-domain subservers.  Run over std** (1 connections) — `src/ycli/mcp.py`
- **Run the root server over stdio (the console-script entry point).      Example:** (1 connections) — `src/ycli/mcp.py`

## Relationships

- [[CLI Command Groups]] (2 shared connections)
- [[App Config and Server]] (2 shared connections)

## Source Files

- `src/ycli/log.py`
- `src/ycli/mcp.py`

## Audit Trail

- EXTRACTED: 20 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*