# Tracker Worklog Client

> 8 nodes · cohesion 0.25

## Key Concepts

- **WorklogClient** (5 connections) — `src/ycli/yandex/tracker/worklog/client.py`
- **.list()** (4 connections) — `src/ycli/yandex/tracker/worklog/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/tracker/worklog/client.py`
- **Path** (1 connections) — `src/ycli/yandex/tracker/worklog/client.py`
- **WorklogList** (1 connections) — `src/ycli/yandex/tracker/worklog/client.py`
- **Declarative Tracker worklog client (uplink) — transport ONLY.  NOTE: no ``from _** (1 connections) — `src/ycli/yandex/tracker/worklog/client.py`
- **Declarative HTTP for ``/issues/{key}/worklog``.** (1 connections) — `src/ycli/yandex/tracker/worklog/client.py`
- **``GET /issues/{key}/worklog`` → worklog listing.          Example:             >** (1 connections) — `src/ycli/yandex/tracker/worklog/client.py`

## Relationships

- [[Tracker Me Client]] (1 shared connections)
- [[Tracker Issue Types Client]] (1 shared connections)

## Source Files

- `src/ycli/yandex/tracker/worklog/client.py`

## Audit Trail

- EXTRACTED: 15 (94%)
- INFERRED: 1 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*