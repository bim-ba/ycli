# Base-cleanup design (pre-Spec-as-Code, 2026-07-13)

**Status:** approved scope, design for owner spec-review · **Supersedes/refines:** §3 and §5 of
`2026-07-12-improvement-roadmap.md` (validated numbers replace the roadmap's estimates).

## Goal & rationale

Reach a genuinely clean base **before** starting the Spec-as-Code (YAML→codegen) track, so the
generator codifies a clean shape and is validated by a trustworthy conformance harness — not
baking today's debt into every generated resource.

This design is the output of a five-agent validation wave (2026-07-13) that re-checked every item
in STATE.md and the 2026-07-12 roadmap against current source (branch `main`, v0.13.0) and
cross-validated the findings. **Key reframe:** the base is far cleaner than the lists implied —
no correctness landmines (`0` bare-`except`, `0` `== None`, `0` mutable-default-args), both prior
"surviving bugs" already fixed and robust, wiki thread-reconstruction correct, all 11 ARCH
invariants enforced, README coverage machine-synced, deps healthy, no committed secrets. The real
work is **shape normalization + harness hardening + small hygiene**, not repairing a broken base.

## Out of scope — validated as already-done or refuted (do NOT touch)

| Item from the lists | Reality | Evidence |
|---|---|---|
| CONTRIBUTING intentional-exclusions | already present | `CONTRIBUTING.md:93-100` |
| resources.md §4 "typed body" convention | already added | `docs/conventions/resources.md:135-152` |
| README coverage tables (231/50/153·43·35) | accurate, machine-synced | `gen_coverage.py --check` = 0 |
| ARCH-1..11 documented + enforced | all 11 confirmed | `tests/test_architecture.py`, importlinter, snapshots |
| "surviving bugs": grid `required`, forms `returns.json()` | both already fixed | `wiki/grids/models.py:397-401`; `forms/answers/client.py:107-155` |
| wiki thread reconstruction | correct (DFS + seen-guard) | `wiki/comments/client.py:54-116` |
| changelog id-guard "divergence" | not a bug — `str`-id adaptation | `changelog/client.py:40` |
| dep stack (pydantic/requests/typer/loguru/uplink) | latest, no CVE | Agent-5 external validation, 2026-07-13 |
| committed secrets / bundled `.mcp.json` | clean, only `${VAR}` | git scan; `plugins/yandex-360/.mcp.json:7-8` |

## Validated inventory (24 items, T0–T4)

Disposition: ✅ CONFIRMED-open · 🆕 NEW. Numbers are the validated counts (they correct the
roadmap's estimates — see "Corrections" below).

### T0 — quick hygiene / bugs
1. ✅ `fix` — negative `--limit=-5` silently tail-truncates (`items[:-5]`); `LimitOption` lacks
   `min=0`, `resolve_cap` uses `limit or max_items`. `src/ycli/cli/typedefs.py:14` + `pagination.py`.
2. ✅ `build` — `uv.lock` fastmcp **3.4.2 → 3.4.3** (SSRF/DNS-rebind/OAuth hardening); pin `>=` already OK.
3. 🆕 `chore` — `plugins/yandex-360/.claude-plugin/plugin.json:4` version frozen at `0.1.0` despite full read/write rewrite.
4. 🆕 `docs` — README "221 MCP tools" off-by-one; real surface is **222** (domain 221 + `status_get`). `README.md:210` vs `tests/snapshots/mcp_tools.txt` (222 lines).
5. ✅ `refactor` — `cfg`→`config`: **35** occurrences across 14 `mcp.py` (CLAUDE.md forbids abbreviations).
6. ✅ `chore` — STATE.md is gitignored yet drift-log + INDEX reference it → dead pointer in clean clones. Repoint to a committed target (this spec / roadmap). `applied/2026-07-13-mcp-write-tool-body-typing.md:52,62`.
7. ✅ `docs` — STATE.md 4 stale lines (see Corrections table).

### T1 — harness hardening (conformance safety-net for codegen) — PRECONDITION
8. 🆕 ARCH-1 four-surface symmetry is **directory-level, not operation-level**: a client method with no CLI/MCP wrapper trips nothing. `tests/test_architecture.py:67-74`. **Most consequential for the codegen bet.**
9. ✅ ARCH-3 AST backstop doesn't follow module-level helpers: a read tool calling `_helper()` that writes is unchecked. `tests/test_architecture.py:141-179`.
10. ✅ ARCH-4 doesn't flag bare `print(` in `cli.py`; `wiki pages get` dumps a string outside the documented carve-outs; the 17 converted sites have no regression fence. `wiki/pages/cli.py:32`, `tests/test_architecture.py:182-191`, `ARCHITECTURE.md:62-68`.
11. ✅ typed-body: no fail-closed check forbidding `body: dict` on `@mcp.tool` (deferred in the applied drift entry). **Lands with #14.**
12. ✅ no `--strict-markers`; `@pytest.mark.integration` = **5** markers / 3 files vs ~97 wiring files → `-m "not integration"` is meaningless; CLAUDE.md rule is aspirational. Decide: enforce (lint) or drop the rule. `pyproject.toml:74-77`.
13. 🆕 pre-commit `architecture-tests` hook doesn't fire on docs-only edits → ARCH-11 caught only in CI. `.pre-commit-config.yaml:17-22`.

### T2 — shape normalization (source-of-truth the generator will codify) — PRECONDITION
14. ✅ `body: dict` in Tracker MCP write tools: **≈33** write-tool params (rigorous count; raw grep up to 45 incl. local vars — precise enumeration at implementation) degrade the MCP input schema to bare `object`; wiki/forms already typed. `tracker/**/mcp.py`.
15. ✅ `Ack.detail`: **36** hand-written strings duplicated CLI/MCP, **≥6 already drifted**; **4** `*ActionResult` wrappers to retire in favor of shared `Ack`.
16. ✅ pagination: relative drains fetch `per_page=100` regardless of small `limit`; fold the 7 relative-cursor copies into `TrackerResource._drain_relative` (helper must accept both `str|None` and `int|str|None` id forms).
17. ✅ all-optional models (of 52 modules only 8 required fields) force ~10 hand-rolled not-found guards + phantom all-None objects → add a shared guard helper.
18. ✅ `QuestionMove` validator defaults `page=1` on bare position → can silently move a question off its page. Raise, or default visibly at the CLI boundary (behavior change → release-note). `forms/questions/models.py:580-589`.

### T3 — structural refactors
19. ✅ `tracker/entities` god-resource: client **626 LOC / 40 def / 31 public**, dir **3,025 LOC** — split sub-resources (comments/checklists/links/attachments) the way standalone resources already work.
20. ✅ test-fixture duplication: `creds` fixture ×**100**, `BASE` const ×**144** → consolidate into conftest fixtures (also shrinks future generator test templates). Root `tests/conftest.py` is 17 lines, autouse-cache-reset only.

### T4 — AI-environment ergonomics
21. ✅ committed blanket `allow: [Bash,Edit,Write,…]` in `.claude/settings.json:3-10` (no scoping) auto-approves arbitrary shell/write in every trusting clone → scope it.
22. ✅ graphify tip-hook fires on every Read/grep with no throttle (observed 4× on one batched Read) → dozens of duplicate injections/session. `.claude/settings.json:72-89`. Add once-per-session sentinel / PostToolUse throttle.
23. ✅ the "do NOT run `graphify update`" guard lives only in CLAUDE.md + `rebuild.sh`, not in the graphify skill an agent loads on `/graphify` → mirror it into the skill.
24. 🆕 `git_guard` misses whitespace variants (`[skip  ci]`, `skip-checks:  true`) and false-positives on a commit that quotes a token in prose. `.claude/hooks/git_guard.py:17-26,48-51`.

### Unverified (need live API — verify-then-fix, never blind)
- Grid cell cannot be cleared to null: `CellsUpdate.model_dump(exclude_none=True)` strips nested `value=None`. `wiki/grids/models.py:583-607`. Confirm whether the API treats absent `value` as clear vs no-op before fixing.
- `CursorStrategy`/`RelativeCursorStrategy` lack a non-advancing-cursor guard that `NextUrlStrategy` has. `pagination.py:57-67,158-170`. Safe under documented exclusive-cursor semantics; add a cheap `cursor==previous → stop` guard as hardening.

## Corrections to STATE.md / roadmap (fold into T0)

| Location | Stale | Correct |
|---|---|---|
| STATE.md:9 | "230 SDK methods" | **231** (contradicts its own line 23 + README) |
| STATE.md:10-11 | "cleanup in progress on `docs/readme-restructure`" | shipped (#41 `fbec717`); prune the branch |
| STATE.md:57 | "(belongs in CONTRIBUTING…)" as TODO | already done `CONTRIBUTING.md:93-100` |
| STATE.md:76-77 | drift ref `open/…body-typing.md` | now in `applied/` (#42); code task still open |
| roadmap §5.5 / §3 | creds ×86 / BASE ×129 | now ×**100** / ×**144** |
| roadmap §4 | 320 `ty: ignore` | now **331** |
| roadmap §3 | entities 2,579 LOC | client **626** / dir **3,025** |
| roadmap §3 | 7 integration markers | now **5** |
| roadmap §5.1 | ~25 `body: dict` tools | ≈**33** write-tool params |

## Execution approach

- **Branch → PR → explicit approval** per logical unit (ruleset forbids direct push to `main`).
- **Auto-release awareness:** every merge runs PSR. Conventional Commits strictly; **never** a skip-ci token (git_guard + CLAUDE.md). Most tranches are `refactor`/`chore`/`test`/`docs` (no minor bump); user-visible behavior (negative-limit, QuestionMove) ships as `fix`/`feat` with a release-note.
- **Gate green at every step:** 100% coverage + ARCH tests + snapshots + `ruff check` + `ruff format --check` + `ty` + `lint-imports` (mirror every CI step before claiming green).
- **Harness first:** land T1 checks before T2 shape refactors so they catch regressions. Exception: the `body: dict` fail-closed check (#11) ships **in the same PR** as the 33-tool conversion (#14) — else it's red on merge.
- **TDD** for behavior changes; **`requesting-code-review`** before each merge; snapshots/coverage updated in-PR.
- **Subagent orchestration:** independent PRs (non-overlapping files) run in parallel via git worktrees; dependent ones sequentially. The main session stays orchestrator (research → plan → act → validate → reflect).

## PR sequence (10 PRs)

| PR | Type | Tranche · items | Content | Depends on |
|---|---|---|---|---|
| A | `fix` | T0 #1,#2 | negative `--limit` floor; `uv.lock` fastmcp 3.4.2→3.4.3 | — |
| B | `docs` | T0 #3,#4,#6,#7 | STATE.md 4 lines + repoint drift-pointer; README 221→222; `plugin.json` version; social-preview regen-note | — |
| C | `refactor` | T0 #5 | `cfg`→`config` (35 sites); snapshot confirms MCP-schema unchanged | — |
| D | `test`/`chore` | **T1** #8,#9,#10,#12,#13 | ARCH-1 op-parity; ARCH-3 helper-follow; ARCH-4 print-guard + carve-out; `--strict-markers` + integration policy; ARCH-11 pre-commit docs | — |
| E | `refactor` | T2 #14 + T1 #11 | 33 `body: dict`→typed models **+** fail-closed ARCH check; snapshot MCP schemas | D |
| F | `refactor` | T2 #15 | centralize `Ack.detail`; retire 4 `*ActionResult` | E |
| G | `refactor`/`fix` | T2 #16,#17,#18 | `per_page=min(100,limit)` + `_drain_relative` fold; QuestionMove visible default; all-optional guard helper | E |
| H | `refactor` | **T3** #19 | split `tracker/entities` god-resource | E (E converts ~12 `body:dict` tools in `entities/mcp.py` — same files) |
| I | `test` | T3 #20 | `creds`/`BASE` → conftest fixtures | last (touches all tests) |
| J | `chore` | **T4** #21-24 | settings.json scoping; graphify-hook throttle; graphify-update guard→skill; git_guard whitespace | — |

Parallelizable now (non-overlapping files): A, B, C, D, J. Sequential chain: D → E → {F, G, H}. I runs near the end (touches the whole test tree).

## Acceptance criteria (per tranche)

- **Every PR:** all CI steps green locally + in CI; snapshots/coverage regenerated; code-review passed; behavior changes carry a release-note line.
- **T1:** each new/strengthened check has a failing-case test proving it bites (add a deliberately-bad fixture, assert the check fails). ARCH-1 op-parity has a documented allowlist for the known-intentional surface asymmetries (e.g. `images.upload` no-MCP).
- **T2:** `tests/snapshots/mcp_tools.txt` reflects the richer typed schemas; no `@mcp.tool` param annotated bare `dict` (except documented `Base64Bytes`); `Ack.detail` produced from one source.
- **T3:** `tracker/entities` split preserves the public CLI/MCP surface (snapshot-stable) or documents the intended surface change; conftest dedup leaves 0 in-file `creds`/`BASE` duplicates.
- **T4:** settings `allow` scoped; graphify hook fires ≤1×/session; graphify-update guard present in the skill; git_guard covers whitespace variants without false-positives on prose.

## Open notes
- Release-note candidates already shipped (roadmap §6) plus this cleanup's: negative-`--limit` now errors; QuestionMove no longer silently re-pages.
- STATE.md itself is gitignored working state — update it as tranches land (don't narrate shipped work there).
- This spec commits via a docs PR (or as the first commit of the epic branch) — not a direct push to `main`.
