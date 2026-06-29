# Architecture and Docs

> 48 nodes · cohesion 0.08

## Key Concepts

- **Transport** (18 connections) — `src/ycli/yandex/transport.py`
- **YandexAuthError** (17 connections) — `src/ycli/yandex/errors.py`
- **YandexClientError** (11 connections) — `src/ycli/yandex/errors.py`
- **YandexNotFoundError** (11 connections) — `src/ycli/yandex/errors.py`
- **YandexRateLimitError** (11 connections) — `src/ycli/yandex/errors.py`
- **YandexServerError** (11 connections) — `src/ycli/yandex/errors.py`
- **_TimeoutAdapter** (11 connections) — `src/ycli/yandex/transport.py`
- **tests/test_architecture.py** (9 connections) — `tests/test_architecture.py`
- **._raise_typed()** (9 connections) — `src/ycli/yandex/transport.py`
- **Response** (7 connections) — `src/ycli/yandex/transport.py`
- **Retry** (7 connections) — `src/ycli/yandex/transport.py`
- **Any** (7 connections) — `src/ycli/yandex/transport.py`
- **errors.py** (7 connections) — `src/ycli/yandex/errors.py`
- **PreparedRequest** (6 connections) — `src/ycli/yandex/transport.py`
- **Session** (6 connections) — `src/ycli/yandex/transport.py`
- **ARCH-11 Doc-drift guard** (5 connections) — `ARCHITECTURE.md`
- **.session()** (5 connections) — `src/ycli/yandex/transport.py`
- **.send()** (4 connections) — `src/ycli/yandex/transport.py`
- **ARCH-10 No shadowing of configurable values** (3 connections) — `ARCHITECTURE.md`
- **ARCH-4 Serialization confinement** (3 connections) — `ARCHITECTURE.md`
- **ARCHITECTURE.md** (3 connections) — `ARCHITECTURE.md`
- **CONTRIBUTING.md** (3 connections) — `CONTRIBUTING.md`
- **transport.py** (3 connections) — `src/ycli/yandex/transport.py`
- **._authorization()** (3 connections) — `src/ycli/yandex/transport.py`
- **ARCH-7 Composition-root DI** (2 connections) — `ARCHITECTURE.md`
- *... and 23 more nodes in this community*

## Relationships

- [[App Config and Server]] (16 shared connections)
- [[Forms Answers Client]] (2 shared connections)
- [[Composition Roots Deps]] (2 shared connections)
- [[CLI Commands and Auth]] (1 shared connections)
- [[Tracker Issue Types Client]] (1 shared connections)
- [[Wiki Attachments Comments Client]] (1 shared connections)

## Source Files

- `.superpowers/sdd/progress.md`
- `ARCHITECTURE.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- `README.md`
- `SECURITY.md`
- `src/ycli/output.py`
- `src/ycli/yandex/errors.py`
- `src/ycli/yandex/transport.py`
- `tests/test_architecture.py`

## Audit Trail

- EXTRACTED: 104 (49%)
- INFERRED: 107 (51%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*