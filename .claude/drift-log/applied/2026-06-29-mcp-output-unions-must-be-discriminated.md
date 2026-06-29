---
date: 2026-06-29
status: APPLIED
disposition: applied
applied_date: 2026-06-29
applied_in: src/ycli/yandex/status/models.py, src/ycli/yandex/status/reporter.py, docs/conventions/resources.md (§5)
priority: MEDIUM
trigger: 8
session_context: round-4 follow-up — status_get me-union mis-hydration found in final review
affected_source:
  - docs/conventions/resources.md
  - src/ycli/yandex/status/models.py
---

## What diverged

The `status_get` MCP tool returns an `AuthReport` whose per-service `me` field was typed as an
**undiscriminated** union — `TrackerMe | WikiMe | FormsMe | None`. Because all three `me`
models are fully optional and ignore extra keys (`APIModel` is `extra="ignore"`), every payload
validates against every member of that union. That is harmless on the CLI/SDK path, where the
real model instance is carried through and serialized directly.

It is **not** harmless across MCP. fastmcp rebuilds `CallToolResult.data` from the tool's output
JSON schema, and for an undiscriminated `anyOf` it picks the *first* branch that validates. A
wiki payload (`{"username": ...}`) was therefore reconstructed into the **tracker** shape
(`{uid, login, display, email}`) and its fields — including `username` — were silently dropped.
The on-the-wire `structured_content` stayed correct, so the data loss only showed up when a
Python consumer read `result.data`. The repo had no rule against undiscriminated unions in MCP
tool outputs, and `docs/conventions/resources.md` did not mention the constraint, so the next
heterogeneous MCP result would have hit the same trap.

## Why it seemed better

A bare union reads naturally and needed no extra scaffolding: each service's probe just stored
its native `me` model, and `extra="ignore"` made every payload "just validate". The ambiguity
is invisible in unit tests that assert against the freshly-built Python object or against
`structured_content` — only the fastmcp `result.data` reconstruction exposes it, which is an
easy seam to overlook.

## Proposed change

1. Type heterogeneous MCP-tool-output unions as **discriminated** unions: give each member a
   `Literal` tag field and annotate the union with `Field(discriminator=...)`. For `AuthReport`,
   split `ServiceAuthStatus` into `TrackerAuthStatus | WikiAuthStatus | FormsAuthStatus` keyed on
   a `Literal` `service` tag. This makes the output schema self-describing and loss-free across
   the fastmcp round-trip.
2. Add a short convention to `docs/conventions/resources.md` (MCP section):

   ```
   ### Heterogeneous MCP output unions must be discriminated

   fastmcp rebuilds `result.data` from the tool's output JSON schema and picks the first
   matching branch of an undiscriminated `anyOf` — silently reshaping one member into another
   and dropping fields. Any union returned by an MCP tool must carry a `Literal` discriminator
   tag (`Field(discriminator="...")`). The CLI/SDK path is unaffected, but MCP consumers are not.
   ```

## Resolution

`ServiceAuthStatus` was split into `TrackerAuthStatus | WikiAuthStatus | FormsAuthStatus`,
each carrying a `Literal` `service` tag and its own typed `me`, combined as
`Annotated[…, Field(discriminator="service")]` in `src/ycli/yandex/status/models.py`. The
shared fields live on a `_ServiceAuthStatus` base; the subclasses override `service`/`me`
so field order is preserved. `StatusReporter._probe` now routes each probe through a
`TypeAdapter(ServiceAuthStatus)` (the discriminator is the single source of truth for
service→model), so no separate name→class map is needed. A fastmcp round-trip test in
`tests/yandex/status/test_mcp.py` now asserts `wiki.me.username` survives on `result.data`
(previously it had to read `structured_content` because the undiscriminated union dropped it).
The convention is documented in `docs/conventions/resources.md` §5 and listed in the
enforcement table. The CLI/SDK path is unchanged — it still carries the bare native `me` model.
