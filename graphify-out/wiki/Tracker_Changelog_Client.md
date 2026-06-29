# Tracker Changelog Client

> 9 nodes · cohesion 0.22

## Key Concepts

- **ChangelogClient** (5 connections) — `src/ycli/yandex/tracker/changelog/client.py`
- **.list()** (5 connections) — `src/ycli/yandex/tracker/changelog/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/tracker/changelog/client.py`
- **Declarative Tracker changelog client (uplink) — transport ONLY.  NOTE: no ``from** (1 connections) — `src/ycli/yandex/tracker/changelog/client.py`
- **Declarative HTTP for ``/issues/{key}/changelog``.** (1 connections) — `src/ycli/yandex/tracker/changelog/client.py`
- **``GET /issues/{key}/changelog`` → changelog listing (``perPage`` paging).** (1 connections) — `src/ycli/yandex/tracker/changelog/client.py`
- **ChangelogList** (1 connections) — `src/ycli/yandex/tracker/changelog/client.py`
- **Path** (1 connections) — `src/ycli/yandex/tracker/changelog/client.py`
- **Query** (1 connections) — `src/ycli/yandex/tracker/changelog/client.py`

## Relationships

- [[Tracker Me Client]] (1 shared connections)
- [[Tracker Issue Types Client]] (1 shared connections)

## Source Files

- `src/ycli/yandex/tracker/changelog/client.py`

## Audit Trail

- EXTRACTED: 17 (94%)
- INFERRED: 1 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*