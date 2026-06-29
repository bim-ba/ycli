# Tracker Me Client

> 11 nodes · cohesion 0.18

## Key Concepts

- **TrackerResource** (13 connections) — `src/ycli/yandex/tracker/_base.py`
- **MeClient** (4 connections) — `src/ycli/yandex/tracker/me/client.py`
- **.get()** (3 connections) — `src/ycli/yandex/tracker/me/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/tracker/me/client.py`
- **_base.py** (2 connections) — `src/ycli/yandex/tracker/_base.py`
- **Me** (1 connections) — `src/ycli/yandex/tracker/me/client.py`
- **Declarative Tracker /myself client (uplink) — transport ONLY.** (1 connections) — `src/ycli/yandex/tracker/me/client.py`
- **Declarative HTTP for ``/myself``.** (1 connections) — `src/ycli/yandex/tracker/me/client.py`
- **``GET /myself`` → the authenticated ``Me`` (a safe auth probe).** (1 connections) — `src/ycli/yandex/tracker/me/client.py`
- **Per-domain base — carries the Tracker API base_url; resource clients inherit it.** (1 connections) — `src/ycli/yandex/tracker/_base.py`
- **Base for every Tracker resource client (inherits session DI via constructor).** (1 connections) — `src/ycli/yandex/tracker/_base.py`

## Relationships

- [[Wiki Attachments Comments Client]] (1 shared connections)
- [[Tracker Changelog Client]] (1 shared connections)
- [[Tracker Issues Client]] (1 shared connections)
- [[Tracker Issue Types Client]] (1 shared connections)
- [[Tracker Links Client]] (1 shared connections)
- [[Tracker Link Types Client]] (1 shared connections)
- [[Tracker Priorities Client]] (1 shared connections)
- [[Tracker Comments Client]] (1 shared connections)
- [[Tracker Transitions Client]] (1 shared connections)
- [[Tracker Worklog Client]] (1 shared connections)

## Source Files

- `src/ycli/yandex/tracker/_base.py`
- `src/ycli/yandex/tracker/me/client.py`

## Audit Trail

- EXTRACTED: 29 (97%)
- INFERRED: 1 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*