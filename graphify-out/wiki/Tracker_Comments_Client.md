# Tracker Comments Client

> 12 nodes · cohesion 0.18

## Key Concepts

- **.add()** (5 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **CommentsClient** (5 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **.list()** (4 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **client.py** (2 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **Path** (2 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **Comment** (1 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **Declarative HTTP for ``/issues/{key}/comments``.** (1 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **``GET /issues/{key}/comments`` → comment listing.          Example:** (1 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **``POST /issues/{key}/comments/`` — add a comment. Returns it.          Example:** (1 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **Body** (1 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **CommentList** (1 connections) — `src/ycli/yandex/tracker/comments/client.py`
- **Declarative Tracker issue-comments client (uplink) — transport ONLY.  NOTE: no `** (1 connections) — `src/ycli/yandex/tracker/comments/client.py`

## Relationships

- [[Tracker Me Client]] (1 shared connections)

## Source Files

- `src/ycli/yandex/tracker/comments/client.py`

## Audit Trail

- EXTRACTED: 25 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*