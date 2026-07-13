# Base-cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reach a clean base before the Spec-as-Code track by shipping the validated 24-item tech-debt inventory (T0–T4) as 10 focused, gate-green PRs.

**Architecture:** Harness-first — land the T1 conformance checks before the T2 shape refactors so they catch regressions. Each PR is a branch → PR → approval (no direct push to `main`); every merge auto-releases via PSR. Independent PRs (A, B, C, D, J) run in parallel via git worktrees; the dependent chain is D → E → {F, G, H} → I.

**Tech Stack:** Python ≥3.12, uv, uplink+requests, typer (CLI), fastmcp (MCP), pydantic, loguru; pytest + `responses`; ruff, ty, import-linter; python-semantic-release.

**Source of truth:** [`docs/superpowers/specs/2026-07-13-base-cleanup-design.md`](../specs/2026-07-13-base-cleanup-design.md).

## Global Constraints

- Python ≥3.12; add deps only via `uv add` / `uv add --dev` — never hand-edit `pyproject.toml` dependency lists.
- Spell identifiers/env-vars in full — never abbreviate (`config` not `cfg`).
- 100% coverage gate: `uv run pytest` enforces `--cov-fail-under=100`; new code ships with tests.
- Conventional Commits; **NEVER** a skip-ci token (`[skip ci]`/`[ci skip]`/`[no ci]`/`skip-checks:`); every commit ends with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- Branch → PR → explicit approval; `main` cannot be pushed directly; required checks `test (3.12)` · `test (3.13)` · `gitleaks`.
- Mirror **every** CI step before claiming green: `uv run pytest` · `uv run ruff check` · `uv run ruff format --check` · `uv run ty check` · `uv run lint-imports`.
- MCP write-tool body param MUST be the resource's typed pydantic model, never `dict` (only exception: `Base64Bytes`/`Annotated` binary uploads).
- ARCH-1..11 stay green; to change an invariant, edit `ARCHITECTURE.md` **and** its check in the same PR.
- STATE.md is gitignored working state — edit locally, never in a PR; update it as tranches land.

## Waves & ordering

```
Wave 1 (parallel, independent files):  A   B   C   D   J
Wave 2 (dependent chain):              D → E → { F , G , H } → I
```

**Detail policy:** Wave 1 tasks are fully specified below (knowable now). Wave 2 tasks (E–I) are precise **task contracts** (files, enumeration, interfaces, per-item test requirement, acceptance, one worked exemplar); their bite-sized steps are expanded just-in-time against post-Wave-1 code before each is executed — deliberate, because their exact edits depend on earlier waves landing and on reading each of 33/40 target files. This is a methodology note, not a placeholder.

---

## WAVE 1

### Task A: negative-`--limit` floor + fastmcp lock bump  (PR-A, `fix:`)

**Files:**
- Modify: `src/ycli/cli/typedefs.py:14` (LimitOption)
- Modify: `src/ycli/yandex/pagination.py:21-37` (resolve_cap)
- Modify: `uv.lock` (fastmcp 3.4.2 → 3.4.3)
- Test: `tests/yandex/test_pagination.py` (resolve_cap), `tests/cli/` limit-option test

**Interfaces:**
- Produces: `resolve_cap(limit, max_items, *, all_=False)` unchanged signature; new guarantee — a negative `limit` resolves to `max_items` (never a negative slice).

- [ ] **A1.1 Write failing test** — `resolve_cap` floors negatives:
```python
def test_resolve_cap_floors_negative_to_default():
    from ycli.yandex.pagination import resolve_cap
    assert resolve_cap(-5, 500) == 500   # was -5 → items[:-5]
    assert resolve_cap(0, 500) == 500
    assert resolve_cap(10, 500) == 10
```
- [ ] **A1.2 Run → FAIL** `uv run pytest tests/yandex/test_pagination.py -k floors_negative -v` (expect `assert -5 == 500`).
- [ ] **A1.3 Implement** — `src/ycli/yandex/pagination.py:37`:
```python
    return None if all_ else (limit if limit > 0 else max_items)
```
- [ ] **A1.4 Run → PASS**.
- [ ] **A1.5 CLI errors on negative** — add `min=0` to the option in `typedefs.py:14`:
```python
LimitOption = Annotated[int, typer.Option(min=0, help="Max items to fetch; 0 uses the default cap.")]
```
  Add a CLI test asserting `--limit -5` exits non-zero on any `list` command; run → PASS.
- [ ] **A2.1 Bump fastmcp lock** — `uv lock --upgrade-package fastmcp`; verify `uv pip show fastmcp` / grep `uv.lock` shows `3.4.3`.
- [ ] **A2.2 Verify** — `uv run pytest -k mcp` green; full CI-mirror green.
- [ ] **A3 Commit** — `fix: floor negative --limit to default cap; bump fastmcp lock to 3.4.3`. Release-note: negative `--limit` now errors at the CLI and never tail-truncates.

**Acceptance:** `resolve_cap(-5, 500) == 500`; `--limit -5` exits non-zero; `uv.lock` fastmcp `3.4.3`; all CI steps green.

---

### Task B: committable docs (README count, plugin version, social-preview, drift-pointer)  (PR-B, `docs:`)

**Files:**
- Modify: `README.md:210` (221 → 222)
- Modify: `plugins/yandex-360/.claude-plugin/plugin.json:4` (version)
- Modify: `CONTRIBUTING.md` (social-preview regen note)
- Verify only: `.claude/drift-log/applied/2026-07-13-mcp-write-tool-body-typing.md` (dead STATE.md pointer)
- Local-only (NOT in PR): `STATE.md` stale lines 9, 10-11, 57, 76-77

- [ ] **B1** README: change "plus **221** MCP tools" → "plus **222** MCP tools (221 domain + the cross-cutting `status` tool)". Run `uv run python scripts/gen_coverage.py --check` (expect exit 0 — the intro line is prose, not generated; confirm no test pins "221").
- [ ] **B2** `plugin.json` version `0.1.0` → `0.13.0` (align with the package release that shipped the full read/write surface). Run `plugin-validator` if available; confirm marketplace.json still resolves.
- [ ] **B3** CONTRIBUTING: add a one-line "regenerate `social-preview.png` from `social-preview.svg` with `<tool>`" note. **First determine the actual rasterizer** (grep repo/history for `rsvg`/`inkscape`/`resvg`); if none found, document the chosen tool.
- [ ] **B4** Drift-pointer: the applied entry is **immutable** (core drift-log policy) and references gitignored STATE.md. Do NOT edit the applied entry. Instead confirm the committed spec (this cleanup's design doc) already supersedes the pointer — the dead reference is mooted by a committed follow-up existing. Record this in the PR description. (If the drift-log policy permits a pointer-only correction, repoint `INDEX-2026-07.md:16` to the committed spec.)
- [ ] **B5** Local housekeeping (separate, not committed): fix STATE.md lines 9 (231), 10-11 (restructure shipped — prune branch note), 57 (CONTRIBUTING done), 76-77 (`applied/` path). 
- [ ] **B6 Commit** — `docs: correct MCP-tool count, bump plugin version, document social-preview regen`.

**Acceptance:** README says 222 with explanation; `plugin.json` bumped; social-preview regen documented; `gen_coverage --check` = 0; PR description explains the drift-pointer disposition.

---

### Task C: `cfg` → `config` rename  (PR-C, `refactor:`)

**Files:** 14 `mcp.py` files under `src/ycli/yandex/**` (35 occurrences of `cfg`). Test: `tests/test_snapshots.py` is the guard (param is internal DI, not MCP-exposed).

- [ ] **C1.1** Enumerate: `rg -nw cfg src/` → expect 35 hits across 14 files.
- [ ] **C1.2** Rename `cfg` → `config` in each (parameter name + `.max_items` accesses). Preserve the type (`config: AppConfig`).
- [ ] **C1.3** Guard: `uv run python -m tests.snapshots --check` (or the snapshot test) — MCP tool schemas MUST be unchanged (the param is a DI injection, not an agent-facing field). If snapshot changes, the rename touched an exposed surface — stop and investigate.
- [ ] **C1.4** `rg -nw cfg src/` → 0 hits. Full CI-mirror green.
- [ ] **C2 Commit** — `refactor: rename cfg MCP-tool param to config (no abbreviations)`.

**Acceptance:** 0 `cfg` identifiers in `src/`; snapshots byte-identical; suite green.

---

### Task D: harness hardening (T1)  (PR-D, `test:`/`chore:`)

Each sub-task adds/strengthens a check **and** a failing-case test proving it bites. Read the current `tests/test_architecture.py` before editing.

**Files:**
- Modify: `tests/test_architecture.py` (ARCH-1 `:67-74`, ARCH-3 `:141-179`, ARCH-4 `:182-191`)
- Modify: `ARCHITECTURE.md:62-68` (ARCH-4 carve-out (c))
- Modify: `pyproject.toml:74-77` (addopts + markers)
- Modify: `.pre-commit-config.yaml:17-22` (files filter)
- Possibly modify: ~92 `test_mcp.py`/`test_cli.py` files (integration-marker backfill — see D4)

- [ ] **D1 — ARCH-4 bare-`print(` guard + carve-out.** Extend the ARCH-4 check to fail on any bare `print(` in a `cli.py` except an explicit allowlist: `tracker/issues/cli.py` (scalar count) and `wiki/pages/cli.py:32` (demo-pinned raw dump). Add carve-out (c) to `ARCHITECTURE.md:62-68` documenting the wiki dump. Failing-case: assert the checker flags a synthetic `print(model)` sample. 
- [ ] **D2 — ARCH-1 operation-level parity.** Extend ARCH-1 beyond directory symmetry: assert every client public method has a CLI **and** MCP wrapper, driven by `scripts/gen_coverage.py`'s per-operation surface map, with a committed allowlist for intentional asymmetries (e.g. `images.upload` no-MCP; the 231→222 deltas). Failing-case: a synthetic unwrapped method trips the check. This is the codegen conformance keystone — the generator must not silently drop a surface.
- [ ] **D3 — ARCH-3 helper-indirection.** Strengthen the AST backstop (`:141-179`) so a read tool calling a module-level `_helper()` has that helper's body walked for write-method calls (resolve bare-`ast.Name` calls to module-level defs). Failing-case: a read tool laundering a write through `_helper()` trips.
- [ ] **D4 — `--strict-markers` + integration policy (DECISION: enforce).** Add `--strict-markers` to `addopts`. Enforce the CLAUDE.md rule: add a test that every `test_mcp.py`/`test_cli.py` wiring file carries `@pytest.mark.integration`, then backfill the marker across the ~92 wiring files (mechanical). Verify `uv run pytest -m "not integration"` now deselects the wiring suite meaningfully. *(If the owner prefers, the alternative is deleting the rule from CLAUDE.md — but enforce aligns with the harness goal.)*
- [ ] **D5 — ARCH-11 pre-commit docs trigger.** Widen `.pre-commit-config.yaml:17-22` so `architecture-tests` also runs when README/CLAUDE.md/ARCHITECTURE.md change (ARCH-11 doc-drift is otherwise CI-only).
- [ ] **D6 Commit(s)** — one commit per sub-task (D1..D5), e.g. `test: enforce ARCH-1 operation-level surface parity`. Full CI-mirror green after each.

**Acceptance:** each check has a proven failing case; `-m "not integration"` is meaningful; docs edits trigger ARCH tests locally; suite green.

---

### Task J: AI-environment ergonomics (T4)  (PR-J, `chore:`)

**Files:**
- Modify: `.claude/settings.json:3-10` (allow), `:72-89` (graphify hooks)
- Modify: `.claude/skills/graphify/SKILL.md` (project-local update guard)
- Modify: `.claude/hooks/git_guard.py:17-26,48-51` (+ new test)

- [ ] **J1 — scope committed permissions.** Move the blanket `Bash`/`Write`/`Edit` allows out of committed `.claude/settings.json` into `.claude/settings.local.json` (gitignored) so clones don't inherit auto-approve; keep committed settings minimal/scoped. Verify `.claude/settings.local.json` is gitignored.
- [ ] **J2 — throttle graphify tip-hook.** Read the hook command at `:72-89`; make it idempotent per session (write/check a sentinel in the session tmp dir; no-op on subsequent fires) so the tip injects ≤1×/session instead of on every Read/grep.
- [ ] **J3 — graphify-update guard into skill.** Add a project-local note to `.claude/skills/graphify/SKILL.md`: "In this repo do NOT run `graphify update .` — use `.graphify/rebuild.sh` (see CLAUDE.md)."
- [ ] **J4 — git_guard robustness.** Normalize whitespace before token matching (catch `[skip  ci]`, `skip-checks:  true`); avoid false-positive when a token appears only in prose quoting. Add `tests/test_git_guard.py` (or extend hooks tests) covering: blocks `-m "[skip ci]"`, blocks whitespace variant, allows a normal message. 
- [ ] **J5 Commit(s)** — e.g. `chore: scope committed permissions and throttle graphify hook`.

**Acceptance:** committed settings ship no blanket auto-approve; graphify tip ≤1×/session; skill carries the update guard; git_guard tests green.

---

## WAVE 2 (task contracts — steps expanded just-in-time)

### Task E: typed MCP write-tool bodies + fail-closed check  (PR-E, `refactor:`) — depends on D

**Files:** Modify the ~33 `body: dict` write-tool params under `src/ycli/yandex/tracker/**/mcp.py`; add the ARCH check to `tests/test_architecture.py`; regenerate `tests/snapshots/mcp_tools.txt`.

**Interfaces:** each converted tool's `body` param becomes the SAME typed pydantic request model the CLI already builds (e.g. `CommentCreate`, `BulkUpdate`, `IssueCreate`).

**Contract:**
1. Enumerate exactly: `rg -n 'body: dict' src/ycli/yandex/tracker` → the authoritative list (expect ≈33). Cross-check each against its `cli.py` to find the typed model it builds.
2. Per tool: replace `body: dict` with `body: <TypedModel>`; keep the docstring; the client already accepts the model (uplink serializes pydantic).
3. Add ARCH check: fail if a `@mcp.tool` function has a param annotated `dict`/`dict[...]` other than documented `Base64Bytes`/`Annotated` forms.
4. Regenerate the MCP-tools snapshot; the diff should show richer input schemas.

**Worked exemplar** (`tracker/comments/mcp.py`, add-comment): `async def comments_add(..., body: dict)` → `body: CommentCreate`; snapshot for `tracker_comments_add` gains the typed fields.

**Per-item test:** the tool's existing `test_mcp.py` still passes; snapshot delta reviewed. **Acceptance:** 0 `body: dict` in `@mcp.tool` (new check green); snapshot reflects typed schemas; wiki `pages_update` inline-dict (spec N3) also converted.

---

### Task F: centralize `Ack.detail`, retire `*ActionResult`  (PR-F, `refactor:`) — depends on E

**Files:** the 36 `detail=` sites (CLI + MCP) + the 4 `*ActionResult` wrappers (`Survey/File/Question/GridActionResult`); shared `Ack` model.

**Contract:** produce each write's `detail` from ONE source (client bodyless writes return the `Ack`, or a single detail-builder keyed by operation), eliminating the ≥6 CLI/MCP drifts; replace the 4 `*ActionResult` wrappers with the shared `Ack`.

**Worked exemplar:** worklog delete — today `mcp.py:145` "worklog record" vs `cli.py:139` "worklog" → one builder yields one string used by both.

**Per-item test:** each affected CLI+MCP test asserts the SAME detail string. **Acceptance:** detail from one source; 0 `*ActionResult`; suite green.

---

### Task G: pagination clamp + `_drain_relative` fold + QuestionMove + all-optional guard  (PR-G, `refactor:`/`fix:`) — depends on E

**Files:** the 7 relative-cursor drains (`comments/changelog/worklog/boards/users/client.py`, `entities/client.py:155,296`); a new `TrackerResource._drain_relative` helper; `forms/questions/models.py:580-589`; a shared not-found guard helper + its ~10 call sites in `**/mcp.py`.

**Contract:**
- Clamp: pass `per_page=min(100, limit)` into the drains (fetch fewer rows when `limit` is small).
- Fold the 7 build-collect-wrap copies into `TrackerResource._drain_relative(...)`; the helper accepts both `str|None` and `int|str|None` id extractors (spec: not a bug, just a shared signature).
- QuestionMove: stop defaulting `page=1` inside the validator; either raise when only `position` is given, or default visibly at the CLI boundary (**release-note** — no longer silently re-pages).
- All-optional guard: add one `require_found(model, name)`-style helper; replace the ~10 hand-rolled not-found guards.

**Per-item test:** clamp test (small `limit` → single small request); drain-fold parity tests unchanged; QuestionMove raises/visible-defaults test; guard-helper test. **Acceptance:** 7 copies → 1 helper; QuestionMove behavior explicit; guards centralized; suite green.

---

### Task H: split `tracker/entities` god-resource  (PR-H, `refactor:`) — depends on E

**Files:** `src/ycli/yandex/tracker/entities/{client,mcp,cli,models}.py` (626/627/738/1033 LOC) → sub-resource modules for comments/checklists/links/attachments, mirroring how standalone resources are structured.

**Contract:** split the 40-method client into cohesive sub-resources; **preserve the public CLI/MCP surface** (snapshot-stable) unless an intentional surface change is documented in `ARCHITECTURE.md`. Keep ARCH-1 (now operation-level, from D2) green throughout.

**Per-item test:** `tests/test_snapshots.py` (cli_tree + mcp_tools) unchanged; existing entities tests pass against the new module layout. **Acceptance:** no god-node; surface snapshot-stable; suite + import-linter green. *(Largest task — will be sub-decomposed at JIT expansion.)*

---

### Task I: conftest fixture dedup  (PR-I, `test:`) — runs last

**Files:** `tests/conftest.py` (add shared fixtures) + remove `creds` (×100) / `BASE` (×144) in-file copies across the test tree.

**Contract:** add shared `credentials` and `base_url` fixtures to the root conftest; delete the per-file duplicates. Mechanical but touches the whole tree — do after E/F/G/H so it rebases once.

**Per-item test:** the full suite is the guard (100% coverage must hold). **Acceptance:** 0 in-file `creds`/`BASE` duplicates; suite green; coverage 100%.

---

## Self-Review

**Spec coverage:** T0 → A,B,C; T1 → D (#8 D2, #9 D3, #10 D1, #11 E, #12 D4, #13 D5); T2 → E (#14),F (#15),G (#16,#17,#18); T3 → H (#19),I (#20); T4 → J (#21-24). Unverified bugs (grid-cell-null, cursor-guard) → folded into G/verify-then-fix. All 24 items mapped. ✅

**Placeholder scan:** Wave-1 tasks carry real code/commands; Wave-2 are labeled task-contracts with a stated JIT-expansion methodology (not TBD). The only genuinely-unknown value — the social-preview rasterizer (B3) — is flagged "determine actual tool," not assumed. ✅

**Type consistency:** `resolve_cap` signature preserved (A); `config: AppConfig` type kept (C); typed models in E are the CLI's existing models; `_drain_relative` signature stated in G. ✅

## Execution Handoff

Two execution options — **subagent-driven (recommended)**: fresh subagent per task, two-stage review between tasks, matches the orchestrator/cycles model. **Inline**: batch execution with checkpoints. Wave-1 tasks (A/B/C/D/J) can dispatch in parallel via worktrees; Wave-2 runs the D→E→{F,G,H}→I chain.
