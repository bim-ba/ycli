# Design: MCP read/write (drop ARCH-3 "read-only", adopt annotation honesty)

**Date:** 2026-07-12 · **Status:** approved by owner (session goal), implementing
**Driver:** owner decision — "отказаться от ARCH-3 правила и сделать MCP read/write".

## Context

ARCH-3 today: MCP tools are read-only — enforced by a fail-closed verb allow-list +
`readOnlyHint=True` on all 81 tools + a regex ban on client write calls in `mcp.py`
(`tests/test_architecture.py`), an import-linter contract, `tests/test_mcp_metadata.py`,
35 per-resource `test_mcp.py` asserts, and the ARCH-6 tool-list snapshot.
The SDK has 133 write methods (Tracker 90, Wiki 26, Forms 17; 30 destructive) that MCP
cannot reach; agents are misrouted to the CLI for every write.

## Decision

1. **Full SDK mirror.** Every public client write method gets an MCP tool in its
   resource's `mcp.py`, same naming scheme as reads (`<domain>_<resource>_<verb>`).
   Missing *read* tools found by the coverage audit are added too
   (`forms_filling_suggest`, `forms_files_verify`, `tracker_issues_suggest`,
   `tracker_worklog_global_list` — exact list per coverage inventory).
2. **ARCH-3 is replaced, not deleted** — new invariant **ARCH-3 "MCP annotation
   honesty"** (fail-closed):
   - Tool verb (trailing `_`-token(s) of the tool name, longest match wins — handles
     `abort_all`, `delete_item`) must classify into READ / WRITE / WRITE_IDEMPOTENT /
     DESTRUCTIVE maps in `tests/test_architecture.py`. Unknown verb → test fails; a new
     verb is added deliberately.
   - READ tools carry `readOnlyHint=True`; WRITE tools carry `readOnlyHint=False` and an
     explicit `destructiveHint` (False for create-style, True for delete/clear/abort);
     idempotent PATCH-style edits set `idempotentHint=True`.
   - Rationale: MCP-spec defaults for an unannotated tool are `destructiveHint=true` —
     honesty must be explicit, not defaulted.
3. **Annotation helpers** next to `RO` in `src/ycli/yandex/mcp.py`:
   `WRITE`, `WRITE_IDEMPOTENT`, `DESTRUCTIVE` dicts (fastmcp 3.4.2 dict-annotation style).
4. **`ycli mcp start --read-only`** flag: serves only `readOnlyHint=True` tools —
   the old behavior stays one flag away for cautious deployments. Default is read/write.
5. **Import-linter contract is kept** (it enforces layering, not read-only-ness),
   renamed to "fastmcp is imported only in mcp modules".
6. **Docs sweep in the same PR** (ARCHITECTURE.md §Changing-an-invariant rule):
   CLAUDE.md/AGENTS.md, README, SECURITY.md (write tools now in scope), CONTRIBUTING,
   docs/api-coverage.md (+ `scripts/gen_coverage.py` legend), docs/conventions/resources.md,
   plugin skills (`plugins/yandex-360/**`), `scripts/new_endpoint.py` template,
   `.claude/commands/arch-review.md`, `src/ycli/mcp/server.py` + domain server
   instruction strings, `ycli mcp` help text. OAuth guidance: MCP now needs write scopes.
7. **Snapshots** (`tests/snapshots/mcp_tools.txt`, cli tree unchanged) regenerated once
   after all domains land; tool count grows 81 → ~215.

## Out of scope (tracked in roadmap, not this change)

- 43 documented-but-unimplemented endpoints (Tracker attachments upload chain — the
  `entities.attachments_attach` dead-end, Forms hooks, Projects v3, Wiki ACL, permission
  reads) — implement via `/new-endpoint` later.
- YAML-spec code generation (S1→S4 strategy) — separate roadmap decision.
- MCP write E2E against the live org happens via SDK/CLI equivalence (same client
  methods); the live-test wave exercises every SDK method through the CLI.

## Testing

TDD: the rewritten architecture tests + relaxed metadata test land first (red on
missing annotations), then per-domain agents add tools + per-resource `test_mcp.py`
write-tool tests (fastmcp in-process `Client`, `responses`-stubbed HTTP, 100% coverage
gate), then snapshot regen. `/arch-review` + full CI mirror before PR.
