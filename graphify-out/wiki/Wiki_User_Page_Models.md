# Wiki User Page Models

> 23 nodes · cohesion 0.11

## Key Concepts

- **APIModel** (46 connections) — `src/ycli/yandex/models.py`
- **models.py** (8 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **PageDetails** (4 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **models.py** (4 connections) — `src/ycli/yandex/wiki/me/models.py`
- **DescendantsResponse** (3 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **PageAttributes** (3 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **PageRef** (3 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **Me** (3 connections) — `src/ycli/yandex/wiki/me/models.py`
- **Identity** (2 connections) — `src/ycli/yandex/wiki/me/models.py`
- **Organization** (2 connections) — `src/ycli/yandex/wiki/me/models.py`
- **_Owner** (2 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **_OwnerUser** (2 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **PageRefList** (2 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **The authenticated Wiki user (``GET /v1/users/me``) — a safe auth probe.** (1 connections) — `src/ycli/yandex/wiki/me/models.py`
- **.owner_username()** (1 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **Pydantic v2 models for Yandex Wiki /pages responses (extra='ignore').** (1 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **Optional page metadata (``fields=attributes``) — timestamps, draft flag.      Ex** (1 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **A single wiki page (``GET /pages?slug=``) — id, slug, title, optional content.** (1 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **A lightweight ``{id, slug}`` reference (``/pages/descendants`` item).      Examp** (1 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **``/pages/descendants`` — a paginated listing of ``{id, slug}`` refs.      ``next** (1 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **A drained, flat list of descendant page refs (no cursor — pagination is internal** (1 connections) — `src/ycli/yandex/wiki/pages/models.py`
- **Pydantic models for Wiki /users/me (the authenticated user).** (1 connections) — `src/ycli/yandex/wiki/me/models.py`
- **Base for all Yandex API models: ignore unknown fields, allow name-or-alias popul** (1 connections) — `src/ycli/yandex/models.py`

## Relationships

- [[Forms Questions Models]] (3 shared connections)
- [[Wiki Comments Models]] (3 shared connections)
- [[Tracker Reference Models]] (3 shared connections)
- [[Forms Answers Models]] (2 shared connections)
- [[Forms Surveys Models]] (2 shared connections)
- [[Wiki Attachments Models]] (2 shared connections)
- [[Tracker Changelog Models]] (2 shared connections)
- [[Tracker Link Models]] (2 shared connections)
- [[Tracker Transition Models]] (2 shared connections)
- [[App Config and Server]] (2 shared connections)
- [[Console Rendering]] (1 shared connections)
- [[Forms Answers MCP]] (1 shared connections)

## Source Files

- `src/ycli/yandex/models.py`
- `src/ycli/yandex/wiki/me/models.py`
- `src/ycli/yandex/wiki/pages/models.py`

## Audit Trail

- EXTRACTED: 94 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*