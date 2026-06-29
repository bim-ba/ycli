---
date: 2026-06-29
status: APPLIED
disposition: applied
applied_date: 2026-06-29
applied_in: CLAUDE.md
priority: MEDIUM
trigger: 3
session_context: round-2 internals-cleanup / round-3 arch-tooling refactor sessions
affected_source:
  - CLAUDE.md
---

## What diverged

The user holds and consistently enforces an authoritative naming convention: identifiers and
environment variable names must be spelled out in full — never abbreviated. Examples: use
`YANDEX_ID_OAUTH_TOKEN`, `timeout_seconds`, `organization_id`; never `YCLI_TIMEOUT_S`,
`org_id`, or `tok`. This rule was introduced during the round-2 internals-cleanup track
(v0.6.0) and has been reinforced in every subsequent session. However, it lives only in
the user's personal agent memory (`MEMORY.md`) — it is not present in the committed
`CLAUDE.md` that a fresh agent or a human contributor would read.

As a result, any contributor (human or agent) who does not happen to have the memory
injected could introduce abbreviated identifiers that pass linting and tests but violate
the project's actual naming standard. The gap was noticed when reviewing new `_deps.py`
files during round-3: none of the freshly scaffolded symbols used abbreviations, but only
because the author had the convention in memory — not because any project-level rule
prevented it.

## Why it seemed better

Keeping the rule in personal memory is lower friction at authoring time — no PR is needed
to add it, and it applies instantly across all projects the user works on. For a single-author
project this is usually enough. The oversight only surfaces when onboarding a new agent or
contributor who starts from `CLAUDE.md` alone.

## Proposed change

Add one line to the "Project-Specific Conventions" section of `CLAUDE.md`:

```
- **Naming:** spell identifiers and env-var names out in full — never abbreviate
  (`timeout_seconds` not `timeout_s`, `organization_id` not `org_id`,
  `YANDEX_ID_OAUTH_TOKEN` is already correct).
```

## Resolution

Added the **Naming** bullet to the "Project-Specific Conventions" section of `CLAUDE.md`
(verbatim from the proposed change). The convention is now visible to any agent or human
contributor reading `CLAUDE.md` alone, not only to sessions with the personal memory injected.
