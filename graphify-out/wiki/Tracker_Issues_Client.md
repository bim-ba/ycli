# Tracker Issues Client

> 20 nodes · cohesion 0.14

## Key Concepts

- **IssuesClient** (10 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **.update()** (5 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **.create()** (4 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **.get()** (4 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **.search()** (4 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **Body** (4 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **.count()** (3 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **.get_raw()** (3 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **Issue** (3 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **Path** (3 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **Declarative Tracker /issues client (uplink) — transport ONLY.  NOTE: do NOT add** (1 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **Declarative HTTP for ``/issues`` (get, search, count, create, update).** (1 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **``GET /issues/{key}`` → a single ``Issue`` (raises on non-2xx).          Example** (1 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **``GET /issues/{key}`` → raw JSON dict (no pydantic pruning).          Bare ``dic** (1 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **``POST /issues/_search`` → list of issues.          ``body`` is ``{"filter": …}`** (1 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **``POST /issues/_count`` → a bare integer count.          Example:             >>** (1 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **``POST /issues/`` — create from a ready body. Returns the created ``Issue``.** (1 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **``PATCH /issues/{key}`` — update fields. Returns the updated ``Issue``.** (1 connections) — `src/ycli/yandex/tracker/issues/client.py`
- **IssueList** (1 connections) — `src/ycli/yandex/tracker/issues/client.py`

## Relationships

- [[Tracker Me Client]] (1 shared connections)
- [[Tracker Issue Types Client]] (1 shared connections)

## Source Files

- `src/ycli/yandex/tracker/issues/client.py`

## Audit Trail

- EXTRACTED: 53 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*