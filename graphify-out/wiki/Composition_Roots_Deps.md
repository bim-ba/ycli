# Composition Roots Deps

> 13 nodes · cohesion 0.15

## Key Concepts

- **TrackerClient** (8 connections) — `src/ycli/yandex/tracker/client.py`
- **WikiClient** (8 connections) — `src/ycli/yandex/wiki/client.py`
- **_mcp.py (RO, app_config, make_cached_client)** (6 connections) — `src/ycli/yandex/_mcp.py`
- **scripts/new_endpoint.py** (4 connections) — `scripts/new_endpoint.py`
- **forms/_deps.py** (2 connections) — `src/ycli/yandex/forms/_deps.py`
- **tracker/_deps.py** (2 connections) — `src/ycli/yandex/tracker/_deps.py`
- **wiki/_deps.py** (2 connections) — `src/ycli/yandex/wiki/_deps.py`
- **client.py** (2 connections) — `src/ycli/yandex/tracker/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/wiki/client.py`
- **TrackerClient — composition root over the tracker resource clients (one shared s** (1 connections) — `src/ycli/yandex/tracker/client.py`
- **Holds the per-resource tracker clients, all sharing one authed ``requests.Sessio** (1 connections) — `src/ycli/yandex/tracker/client.py`
- **WikiClient — composition root over the wiki resource clients (one shared session** (1 connections) — `src/ycli/yandex/wiki/client.py`
- **Holds the per-resource wiki clients, all sharing one authed ``requests.Session``** (1 connections) — `src/ycli/yandex/wiki/client.py`

## Relationships

- [[CLI Commands and Auth]] (6 shared connections)
- [[App Config and Server]] (4 shared connections)
- [[Architecture and Docs]] (2 shared connections)
- [[Forms Answers Client]] (1 shared connections)
- [[Wiki User Page Models]] (1 shared connections)
- [[Tracker Issue Types Client]] (1 shared connections)
- [[Wiki Attachments Comments Client]] (1 shared connections)

## Source Files

- `scripts/new_endpoint.py`
- `src/ycli/yandex/_mcp.py`
- `src/ycli/yandex/forms/_deps.py`
- `src/ycli/yandex/tracker/_deps.py`
- `src/ycli/yandex/tracker/client.py`
- `src/ycli/yandex/wiki/_deps.py`
- `src/ycli/yandex/wiki/client.py`

## Audit Trail

- EXTRACTED: 36 (90%)
- INFERRED: 4 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*