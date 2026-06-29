---
date: 2026-06-29
status: APPLIED
disposition: applied
applied_date: 2026-06-29
applied_in: tests/test_architecture.py::test_arch11_no_purged_idioms_in_live_docs
priority: HIGH
trigger: 5
session_context: round-2/round-3 refactor sessions — doc audit after ARCH-7/ARCH-10 landed
affected_source:
  - README.md
  - CLAUDE.md
  - ARCHITECTURE.md
---

## What diverged

Purged idioms and stale counts have repeatedly survived in prose documentation after the
code moved on. Two concrete instances observed across multiple sessions:

1. **`from_env` in README.md** — after ARCH-7 ("Composition-root dependency injection")
   removed `from_env` from every client, `README.md` still showed usage examples like
   `TrackerClient.from_env()`. Any reader following those examples would get an
   `AttributeError` at runtime. The discrepancy was caught by manual doc review, not by
   any automated check.

2. **Stale invariant count in CLAUDE.md** — `CLAUDE.md` read "six invariants (ARCH-1..6)"
   after the set had grown to ARCH-1..10 across the round-2 refactor. A contributor reading
   `CLAUDE.md` would believe the architecture was smaller than it actually is. The count was
   hand-updated during this session but no guard prevents it drifting again.

Neither README nor prose docs are covered by the existing grep-based ARCH checks. The
architecture tests assert code-level invariants; documentation that references purged
patterns is invisible to them.

## Why it seemed better

Updating docs in the same PR as a code change feels like over-engineering — the code PR is
already large, and a doc-sync step adds cognitive load. In practice this recurs: round-2
landed ARCH-7 and ARCH-10 as code-only PRs, leaving docs to drift. The pattern repeated
across at least two independent refactor sessions, which is the trigger-5 signal.

## Proposed change

Add **ARCH-11 — Doc-drift guard** to `ARCHITECTURE.md` and a corresponding test in
`tests/test_architecture.py`:

```
- **ARCH-11 — No purged idioms in docs.** README.md, CLAUDE.md, and files under docs/
  must not reference idioms that ARCH-7..10 explicitly prohibit in code. Concretely:
  the strings `from_env`, `@uplink.timeout`, `TrackerClient.from_env`, and
  `WikiClient.from_env` must not appear in README.md or any file under docs/.
  *Check:* pytest grep assertions in test_architecture.py.
```

Note: round-3 Task F4 implements this check. Once F4 lands, this entry can be closed.

## Resolution

ARCH-11 — Doc-drift guard — was codified in `ARCHITECTURE.md` (invariants ARCH-1..11) and
enforced by `test_arch11_no_purged_idioms_in_live_docs` in `tests/test_architecture.py`.

The test scans user-facing docs (`README.md`, `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`,
`SECURITY.md`, `docs/api-coverage.md`, `docs/conventions/**/*.md`, `plugins/**/*.md`) for
call-site occurrences of `.from_env(` and `session_from_env(` — the two purged idiom patterns
that ARCH-7 eliminated from the codebase. Historical and rule-defining files (`ARCHITECTURE.md`,
`CHANGELOG.md`, `PROMPT.md`, `docs/superpowers/**`) are excluded from scanning.

The test passed immediately after implementation because Task F6 had already cleaned the live
docs. This guard prevents the idioms from silently reappearing in future PRs.
