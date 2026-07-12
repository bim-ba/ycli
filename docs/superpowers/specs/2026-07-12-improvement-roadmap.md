# ycli improvement roadmap (post-audit, 2026-07-12)

**Status:** proposal for owner review · **Sources:** five-agent research wave (session
archaeology `f8cba46e`, coverage audit, tech-debt audits ×2, ARCH-3 change map) plus the
full-surface live test of all 230 SDK methods against org 8526809 (237 OK / 7 ycli bugs —
all fixed on `feat/mcp-read-write`).

## 1. Specification-as-Code (YAML → codegen) — the big one

**Recommendation: adopt Strategy S1 (in-repo YAML → Jinja build-time codegen), evolve
toward S4 (YAML → OpenAPI-ish IR → fan-out). Do NOT adopt runtime metaprogramming (S3)
or an external toolchain (S2/Fern).**

Evidence base (two independent measurements agree):

| Layer | files | LOC | structural duplication |
|---|---|---|---|
| client.py | 54 | 3,757 | 75% |
| cli.py | 54 | 4,491 | 81% |
| mcp.py | 55 | 1,631 | 71% |
| models.py | 52 | 4,925 | 65% |
| tests | 213 | 13,415 | 79% |

- ~89% of `src/` is the mechanical per-resource quartet; a generator could produce
  **~65–75% of src and ~75–80% of tests** (31 of 50 resources are ≤400-line pure
  get/list plumbing — near-100% generatable).
- Prior session (2026-07-10) verified: no off-the-shelf YAML→SDK+CLI+MCP+tests tool
  exists; Fern was spiked hands-on and rejected (SDK-only under free/local, foreign
  model identity, inverted ownership); Stainless is sunsetting; datamodel-code-generator
  is the one reusable in-repo component. POC: 23 authored YAML lines → 6 valid files
  (~5.9× compression) with the generated model validating a real fixture.
- The repo is already "one step" from spec-driven: `scripts/new_endpoint.py` is a
  str.format generator; pagination is a strategy registry; ARCH-1 symmetry + ARCH-6
  snapshots + the 100% gate form a ready-made conformance harness for a generator.

Phasing (each phase keeps the gate green):
1. Define the YAML spec schema (one endpoint = one YAML; per-tool `description` field
   preserves the hand-tuned agent-facing MCP docstrings; write verbs carry their
   WRITE/WRITE_IDEMPOTENT/DESTRUCTIVE class explicitly — the ARCH-3 maps become spec
   fields).
2. Grow `scripts/new_endpoint.py` into the Jinja generator; generate into the SAME
   committed file layout (no runtime magic; py.typed, coverage, import-linter all keep
   working; diffs stay reviewable).
3. Migrate the tracker domain first (largest win), resource by resource; a
   `--check` mode in CI asserts generated files match their specs (same pattern as
   `gen_coverage.py --check`).
4. Evolve the bespoke YAML toward an OpenAPI-compatible IR (S4) only when a second
   consumer appears (docs generation, TypeScript SDK, …).

Open owner decisions: bespoke YAML vs OpenAPI-split as the authoring format;
"fewer authored lines" vs "fewer repo files" as the success metric.

## 2. API coverage backlog (43 documented, unimplemented endpoints)

Priority order (impact-first):
1. **Tracker attachments upload chain** — `POST /v3/attachments/` (temp upload),
   `POST /v3/issues/{id}/attachments/`, delete. Closes the shipped dead-end:
   `entities.attachments_attach` requires a `temp_file_id` ycli cannot produce
   (live-confirmed; with a raw-curl-seeded id the ycli command works).
2. **Tracker permission reads** — 4 `GET queues|components/…/permissions` endpoints
   (ycli has the writes but cannot read back).
3. **Wiki page ACL** — 4 `pages/{idx}/access` endpoints (api-coverage.md's "UI-only"
   claim was stale).
4. **Wiki comment thread GET** — server-side `…/comments/{id}/thread` (ycli currently
   reconstructs threads client-side).
5. **Tracker workflows read** — `GET /v3/workflows` is not wrapped, yet
   `queues create` de-facto requires a `*PresetWorkflow` id from it (live finding).
6. **Forms hooks** — 24 endpoints (hook groups/subscriptions/conditions CRUD,
   variables, notification history, answer views, show-errors). Big but mechanical;
   ideal first candidate for the S1 generator.
7. **Tracker Projects API v3** — 6 endpoints; entities overlap but don't replace it.
8. Tracker dashboards delete (live testing had to raw-curl it away).

## 3. Architecture decisions to revisit

- **`tracker/entities` god-resource** (2,579 LOC, ~40-method client, graphify god-node
  #3): split sub-resources (comments/checklists/links/attachments) the way standalone
  resources already work. 1–2 days.
- **All-optional models**: every field `X | None` forces 10 hand-rolled not-found guards
  in mcp.py and phantom all-None objects elsewhere; add a shared guard helper (½ day).
- **Test fixture duplication**: `creds` fixture ×86, `BASE` URL ×129 with a 16-line root
  conftest — consolidate into conftest fixtures (~1 day, mechanical; also shrinks the
  future generator's test templates).
- **`@pytest.mark.integration` policy**: 7 markers vs ~109 wiring-test files — either
  enforce (a lint) or drop the CLAUDE.md rule; today `-m "not integration"` is
  meaningless.
- **`wiki pages get` raw-markdown print**: deliberate cat-like dump pinned by the demo
  test, but formally outside ARCH-4's carve-outs — either add carve-out (c) to
  ARCHITECTURE.md or route through the Serializer with a `--raw` escape.
- **ARCH-4 grep**: extend the enforcement to flag bare `print(` in `cli.py` (the 17
  converted sites had no guard preventing regression).
- **`.claude/settings.json` ergonomics** (owner call, not changed): committed blanket
  Bash/Edit/Write allows apply to every clone; the graphify tip-hook fires on every
  .md/.py read (dozens of times per session) — consider once-per-session.

## 4. Stack verdicts (validated against current sources, 2026-07)

- **Keep `uplink` + `requests` for now** — the 320 structural `ty: ignore`s are the cost;
  S1 codegen changes the calculus later (generated clients could target httpx directly).
  No migration before the generator decision.
- **`ty` adopted and now blocking in CI** (was advisory; pre-commit already blocked).
- **fastmcp 3.4.2 dict-annotations** confirmed current; MCP-spec default
  `destructiveHint=true` for unannotated tools is why ARCH-3 demands explicit hints.
- No new runtime dependencies warranted by any audited need.
