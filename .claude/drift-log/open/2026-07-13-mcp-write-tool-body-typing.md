---
date: 2026-07-13
status: OPEN
priority: MEDIUM
trigger: 8
session_context: adding MCP write tools across tracker/wiki/forms to mirror the SDK (drop ARCH-3 read-only)
affected_source:
  - docs/conventions/resources.md
  - ARCHITECTURE.md
---

## What diverged

When three parallel agents added ~136 MCP write tools, they split on how a write
tool declares its request body. The wiki and forms agents typed the parameter as the
existing pydantic request model (`body: KeysetCreate`, `body: GridUpdate`, …), so
fastmcp derives a rich input schema and validates the agent's payload before the
call. The tracker agent typed ~25 tools as raw `body: dict` (bulk, comments, issues,
entities, import, worklog, links, checklists, dashboards, remotelinks), pushing the
payload shape into the docstring prose and degrading each tool's MCP input schema to a
bare `object`. Both pass every existing check (ARCH-3 annotation honesty, 100%
coverage, snapshots) — nothing in the codified conventions says which to use.

The CLI has never had this ambiguity: every CLI write command builds the typed model
(`BulkUpdate(...)`) and the client method accepts it (uplink serializes pydantic
models). So the typed model already exists and is already the client's contract for
every one of these operations — the `dict` variant is strictly a lost schema.

## Why it seemed better

`body: dict` is faster to write and mirrors the client's `uplink.Body` signature
literally, so an agent scaffolding many tools quickly reaches for it. It "works" —
the request still serializes — which is why no test caught it. The cost is invisible
until an LLM client tries to call the tool and gets `{"type": "object"}` with no field
names, types, or aliases, and must reconstruct the payload from the docstring (which
can then drift from the model as fields are added).

## Proposed change

Codify in `docs/conventions/resources.md` §MCP (and reference it from the
`/new-endpoint` scaffold and `ARCHITECTURE.md` §ARCH-3): **an MCP write tool's body
parameter MUST be the resource's typed pydantic request model, never `dict`** — the
same model the CLI command builds — so the tool's input schema is self-documenting and
validated. Binary payloads are the only exception (`Annotated[Base64Bytes, …]` for
uploads; raw byte downloads stay CLI/SDK-only). Consider an enforcement check: fail if
a `@mcp.tool`-decorated function has a parameter annotated `dict`/`dict[...]` other
than the documented binary/`Annotated` forms. Backfill the ~25 existing `body: dict`
tracker tools (tracked as follow-up #1 in
`docs/superpowers/specs/2026-07-12-improvement-roadmap.md`).
