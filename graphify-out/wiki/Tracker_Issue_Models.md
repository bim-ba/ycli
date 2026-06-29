# Tracker Issue Models

> 20 nodes · cohesion 0.10

## Key Concepts

- **Issue** (10 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **models.py** (3 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **.assignee_display()** (2 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **.epic_key()** (2 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **.parent_key()** (2 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **.priority_key()** (2 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **.queue_key()** (2 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **.status_key()** (2 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **.type_key()** (2 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **IssueList** (2 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **Pydantic models for Tracker /issues (Issue + IssueList root model).** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **A Yandex Tracker issue (``/issues/{key}`` response).      Nested ``type``/``stat** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **``type.key`` or ``None``.** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **``status.key`` or ``None``.** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **``priority.key`` or ``None``.** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **``epic.key`` or ``None``.** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **``parent.key`` or ``None``.** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **``queue.key`` or ``None``.** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **``assignee.display`` or ``None``.** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`
- **A bare JSON array of issues (``POST /issues/_search`` response).      Example:** (1 connections) — `src/ycli/yandex/tracker/issues/models.py`

## Relationships

- [[Wiki User Page Models]] (1 shared connections)

## Source Files

- `src/ycli/yandex/tracker/issues/models.py`

## Audit Trail

- EXTRACTED: 39 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*