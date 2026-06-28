# Round-3: Architecture, Tooling & Conventions — Design Spec

**Date:** 2026-06-29
**Status:** Draft for review
**Predecessor:** Round-2 (PR #10 — raw-arg DI, Serializer, pagination strategies, ARCH-7..10)
**Target version:** v0.8.0 (after round-2 ships v0.7.0)

## Goal

Tighten `ycli`'s internals one more turn: pay down the duplication and altitude debt
that round-2 surfaced, give the project the strict formatter/linter/type-checker it never
had, finish the CLI/MCP surface so every entry point follows the resource pattern, close
two enforcement gaps (ARCH-4 `json.dumps`, the Tracker-deeplink ARCH-5 leak), and add the
agent-facing infrastructure (code graph, drift log, helper commands, doc hygiene).

This is **one spec** delivered as six workstreams (A–F). Each workstream is internally
staged; the riskiest churn (the formatter) lands first so later semantic diffs are not
buried in reformatting noise.

## Architecture (approach)

The enforced four-surface `yandex/<domain>/<resource>/{client,cli,mcp,models}.py` tree is
the project's core value and stays intact. Round-3 makes **surgical** moves around it, not a
reorganization: two top-level files swap homes (`models.py` → `yandex/`, `settings.py` →
top-level), one file is renamed (`auth.py` → `status.py`), one is deleted (`mcp_launcher.py`),
and a new `mcp_cli.py` joins the roots. Shared construction logic is hoisted into factories;
the strategy/serializer patterns established in round-2 are the bar the rest of the code is
brought up to.

## Tech stack

Python ≥3.12 · uv · uplink+requests (sync HTTP) · pydantic v2 + pydantic-settings · typer ·
fastmcp 3.4.2 (read-only MCP) · rich · loguru. **New dev tooling:** ruff (lint+format+isort),
ty (Astral type checker, beta). **New external agent tooling:** graphify (installed via
`uv tool install`, output under `.graphify/`).

---

## Global Constraints

Copied verbatim from CLAUDE.md / ARCHITECTURE.md / project memory — every task inherits these:

- **Auto-release on push to main.** Each merged PR cuts a release via python-semantic-release.
  Use Conventional-Commit prefixes; never write a skip-ci token (`[skip ci]`/`[ci skip]`/
  `[no ci]`/`[skip actions]`/`[actions skip]`) or `skip-checks` trailer in any commit/squash.
- **After each release:** `uv lock` + a `build:` commit (PSR bumps pyproject, not the lock).
- **100% coverage gate** (`uv run pytest --cov-fail-under=100`). New code ships with tests.
- **Dependencies via `uv add` / `uv add --dev`** — never hand-edit `pyproject.toml` dep lists.
  (`[tool.*]` config sections ARE hand-edited; only dependency arrays are off-limits.)
- **No hardcoded credentials.** Env via composition roots only. Pre-authenticated session
  injection stays rejected by design.
- **MCP server stays read-only** (ARCH-3) — this milestone does not add writes.
- **Reproducible generated artifacts** — the README gif is regenerated from `docs/demo/demo.tape`,
  never hand-authored (the demo.svg incident).
- **Full self-documenting names** — never abbreviate identifiers/env vars.
- **Changing an ARCH invariant** edits `ARCHITECTURE.md` AND its enforcing check in the SAME PR,
  and is flagged in the PR body.
- Commits end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Branch → PR → explicit approval before merge. No direct pushes to main.

---

## Decisions log (forks resolved)

| # | Decision | Rationale |
|---|----------|-----------|
| Scope | One big round-3 spec → plan → SDD | User choice |
| П8 reorg | **Surgical only**, NOT full reorg | Full reorg breaks ARCH-1 + both import-linter contracts + most of `test_architecture.py`; L/high risk churn |
| settings.py | **Hoist to top-level `ycli/settings.py`** | App-wide config should be visible at the top namespace (`ycli.settings`); `APIModel` (API-layer) goes the other way into `yandex/` |
| П3 auth | **Seam, not Strategy ABC** | OAuth↔IAM delta is one header string, no algorithm; IAM real (per vendored docs) but not roadmapped. Promote to Strategy when IAM actually lands |
| П1 `@validate_call` | **Declined** | Breaks Typer (reads `Annotated` itself) and uplink (reads annotations eagerly); codebase has ~no manual validation to shrink. The one good idea (issue-key `StringConstraints` alias) is a *feature*, out of scope |
| П5a deeplinks | **Remove now**, defer general design | Tracker-only hardcoded URL violates ARCH-5; a per-model deeplink mechanism is a separate future design |
| П15 graph | **Full graphify + GLM-5.2 semantics**, output under `.graphify/` | User choice; cost is cents at this scale. Tool already installed via `uv tool install` |
| AppContext | **Stays a concrete class** (not a Protocol) | No second implementation; Protocol buys nothing; `from_typer_context` is the idiomatic typer `ctx.obj` accessor |

---

## Workstream A — Strict tooling (ruff + ty)

**Why:** the repo has zero formatting/style-lint/type-check today. ruff and ty are not even
installed; the 37 `# ty: ignore` markers are checked by nothing. The user wants strong, strict,
auto-applied rules.

**Design.** Adopt the Astral toolchain (matches the uv-centric stack): ruff for
format + lint + import-sorting (retires any need for black/isort), ty for type checking.

`[tool.ruff]` — `target-version = "py312"`, `line-length` measured against current de-facto
width before locking, `src = ["src","tests","scripts"]`.

`[tool.ruff.lint] select` (strict-but-sane families): `E, W, F, I, N, UP, B, A, C4, SIM, PTH,
RUF, ANN, TC, PT`. `ignore = ["ANN401"]` (uplink/dynamic dicts legitimately need `Any`).
Per-file-ignores: tests drop `ANN`/naming pedantry; `scripts/**` drop `ANN`; the uplink
`yandex/**/client.py` stubs get a scoped `ANN` carve-out. `[tool.ruff.lint.isort]
known-first-party = ["ycli"]`. Hold the maximalist families (`D, PL, ERA, FBT, S, EM, TRY,
COM`) for a later ratchet — highest noise, some conflict with the formatter.

`[tool.ruff.format]` — Black-compatible: `quote-style="double"`, `docstring-code-format=true`
(verify it leaves the scaffolder's *string-literal* templates untouched — only true docstrings
are formatted).

`[tool.ty]` — `python-version="3.12"`, `error-on-warning=true`, selectively tightened rules
(`possibly-unresolved-reference="error"`, `unused-ignore-comment="warn"` to catch stale
suppressions). **ty is beta (0.0.x, unstable API)** — pin the exact version, run it
**advisory** (`continue-on-error` in CI) at first, promote to a hard gate once green.

pre-commit: add `astral-sh/ruff-pre-commit` (`ruff --fix` + `ruff-format`) before the existing
`architecture-tests` hook, and `astral-sh/ty-pre-commit`; pinned `rev`s bumped in lockstep with
the dev-dep versions. CI: a single-interpreter `ruff check` + `ruff format --check` step, plus
an advisory `ty check`.

**Internal staging (within this workstream — each its own commit, reviewable in isolation):**
1. Formatter only — `uv add --dev ruff`, `ruff format`, wire format hook + `--check` CI. Huge
   but mechanical/deterministic diff; lands alone so semantic diffs that follow are readable.
2. Lint autofix — conservative `select` (autofix-heavy families), `ruff check --fix`,
   per-file-ignores, hand-resolve the residue.
3. Annotations ratchet — add `ANN` + `TC`; this is where the uplink pattern bites (hence the
   client.py carve-out).
4. ty advisory — `uv add --dev ty`, config, hooks, advisory CI; validate the 37 suppressions
   still match ty's codes.

**Files:** `pyproject.toml` (`[tool.ruff*]`, `[tool.ty*]`), `.pre-commit-config.yaml`,
`.github/workflows/ci.yml`, `uv.lock`, broad mechanical edits across `src/`+`tests/`+`scripts/`.
**ARCH/snapshot/coverage:** no invariant or snapshot impact; coverage unaffected (formatting +
annotations don't change branches).

---

## Workstream B — Composition & DI

**Why:** the client-construction block (`Credentials()`/`AppConfig()`/`<Domain>Client(...)`) is
duplicated **4×** (`context.py` + three `_deps.py`) — the single largest DRY violation. Config
is read inconsistently (cached client config vs on-the-fly `AppConfig()` in tool bodies).

**Design.**
- **B1 — Move `APIModel`** from `src/ycli/models.py` → `src/ycli/yandex/models.py`. Sweep ~28
  imports + the scaffold template (`scripts/new_endpoint.py`) + `ARCHITECTURE.md` Layout lines.
  No shim (a dead top-level file contradicts "few thin roots"). Falls outside the `yandex.**.models`
  import-linter glob, so no contract breaks.
- **B2 — Hoist settings** from `src/ycli/yandex/settings.py` → `src/ycli/settings.py`. Update
  imports (`Credentials`/`AppConfig` consumers), and **ARCH-8** (`test_architecture.py:123`
  `settings = YANDEX/"settings.py"` → top-level path) + the ARCH-5/ARCH-8 wording in
  `ARCHITECTURE.md` (same-PR invariant-change rule).
- **B3 — Extract a `ClientFactory`** that owns the per-domain construction, consumed by BOTH
  `AppContext` and the three `_deps.py`. `AppContext` shrinks to presentation state
  (`output_format`, `console`, `strategy`) + delegation; the `# type: ignore[return-value]`
  lazy-property smell goes away. `AppContext` stays a concrete class; `from_typer_context`
  stays. Sketch:
  ```python
  # src/ycli/yandex/factory.py  (or folded into a composition root)
  class ClientFactory:
      """Builds a domain client from app config + credentials — the single construction site."""
      @staticmethod
      def build(client_cls, credentials, config):
          return client_cls(
              oauth_token=credentials.oauth_token,
              organization_id=credentials.organization_id,
              timeout_seconds=int(config.timeout_seconds),
              retries=config.retries,
          )
  ```
  The three `_deps.py` `@cache` factories and `AppContext`'s lazy client properties both call
  `ClientFactory.build(...)`. (Pairs with Workstream D's `_deps.py` collapse — see D2.)
- **B4 — Config-injection rule** (codified, applied):
  - MCP: add a `@cache def app_config() -> AppConfig` provider beside the client factory; tools
    needing config take `cfg: AppConfig = Depends(app_config)` and read `cfg.max_items`
    (`Depends` hides it from the tool schema → no snapshot impact).
  - CLI: expose `AppContext.config`; command bodies read `app_ctx.config.max_items`.
  - Sole allowed bare read: `AppConfig().log_level` at the two `main()` roots (`cli.py`,
    `mcp.py`), which run before any DI context exists.
  - Touch sites: `forms/answers/{mcp,cli}.py`, `wiki/pages/{mcp,cli}.py`.

**Files:** `src/ycli/models.py`→`yandex/models.py`; `yandex/settings.py`→`src/ycli/settings.py`;
new `yandex/factory.py`; `context.py`; three `_deps.py`; four leaf `{mcp,cli}.py`; scaffold;
`ARCHITECTURE.md`; `test_architecture.py` (ARCH-8 path). **ARCH/snapshot/coverage:** reinforces
ARCH-7/8; ARCH-8 path edited deliberately; no snapshot impact; new factory + `app_config` +
`AppContext.config` each need a covering test.

---

## Workstream C — Transport / status / auth

**Why:** `_raise_typed` floats at module scope; `auth.py` overclaims (it only checks status);
auth scheme is inlined and would be awkward to extend.

**Design.**
- **C1 — `_raise_typed` → `@staticmethod` on `Transport`.** It is a `requests`
  `session.hooks["response"]` callback — `requests` invokes any callable, so module scope is
  arbitrary. Register as `session.hooks["response"].append(Transport._raise_typed)` (same
  function object → byte-identical behavior). Update the one test import
  (`tests/yandex/test_transport.py`). Keeps the typed-error mapping inside the `Transport`
  boundary — ARCH-9 preserved/strengthened.
- **C2 — Rename `yandex/auth.py` → `yandex/status.py`**, keep the Typer `name="auth"` and the
  `status` command so **`ycli auth status` is unchanged** (no snapshot churn). Update the
  `cli.py` import. Internal models (`ServiceAuthStatus`/`AuthReport`) may be renamed to
  `ServiceStatus`/`StatusReport`.
- **C3 — Simplify the probe loop** into a small `ServiceProbe` class (class-level table +
  `run(credentials)`), removing the free-floating `_PROBES`/`_probe`. The per-service identity
  extractor **stays** — tracker `.login` / wiki `.username` / forms `.email` are genuinely
  different fields on different models; collapsing below "one extractor per service" would
  require editing three domain models (out of scope). Honest framing: this is *housing*, not
  *elimination*.
- **C4 — Auth-scheme seam (NOT an ABC).** Localize the `Authorization`-header build (currently
  inline `f"OAuth {oauth_token}"` in `transport.py`) into a single private helper in
  `transport.py` (respecting ARCH-5's "header strings live in transport.py"). The `auth.py`
  module name is left free for a future real Strategy. No `scheme` parameter is added to the
  public client constructors yet (that would widen the ARCH-10 signature-defaults surface for a
  capability nothing uses) — the seam is purely the extracted helper, so adding IAM later is a
  one-branch, localized change.

**Files:** `transport.py`; `yandex/auth.py`→`yandex/status.py`; `cli.py`; transport+status tests.
**ARCH/snapshot/coverage:** ARCH-9 preserved; ARCH-5 respected (header build stays in transport);
no snapshot change (CLI command name preserved); existing except-branch tests retained.

---

## Workstream D — Dedup, conventions & the ARCH-4 gap

**Why:** ~100 lines of triplicated boilerplate; several resource inconsistencies; a real
ARCH-4 enforcement hole.

**Design.**
- **D1 — Close the ARCH-4 `json.dumps` hole.** `tracker/issues/cli.py` (`full`) and
  `tracker/transitions/cli.py` (`execute`) render via `json.dumps(...)` directly, bypassing
  `Serializer` and ignoring `--format`. The ARCH-4 check only forbids `model_dump_json`/
  `yaml.safe_dump`, so `json.dumps` slips through. Fix: wrap the dict/list in a `RootModel` at
  the CLI boundary and route through `Serializer.serialize` (so `--format` works). Then **tighten
  the ARCH-4 check** to also forbid `json.dumps` outside `output.py` (bare `print(int)` for
  scalar `count` stays fine). Same-PR `ARCHITECTURE.md` ARCH-4 wording edit (invariant-change rule).
  - `get_raw` stays a raw dict (deliberate "unpruned" escape hatch) — only its *rendering* changes.
- **D2 — Model `transitions execute`.** Currently returns `builtins.list` (a shadowing hack
  forced by uplink eager-eval). Define a `RootModel`-based type (reuse `Transition`/
  `TransitionList`) so it returns a model, the hack disappears, and `--format` is honored.
  *Verify the response shape against `docs/references/yandex/` + a live response before committing.*
  Note: changes the SDK public return type (a real public-surface change for SDK consumers,
  though ARCH-6 locks names not signatures — call it out in the PR).
- **D3 — Collapse triplicated `_deps.py`** (tracker/wiki/forms are byte-identical but for the
  client class + `TAGS` literal) into one parametrized factory in `yandex/_mcp.py`
  (`make_cached_client(client_cls, tags)`), each producing a **distinct `@cache`d callable** (the
  autouse `cache_clear` fixture must still reset each). Reconcile the `RO` import path
  (scaffold imports from `_mcp`, resources from `_deps`) — pick one and align both.
- **D4 — Collapse the single-page `list` wrappers.** `wiki/attachments`, `wiki/comments`,
  `forms/surveys` share a near-identical `SinglePageStrategy(extract=…).collect(…)` + `RootModel`
  wrap. Hoist the *pure* post-processing into a shared helper (the uplink `_list_page` HTTP
  methods stay per-client — ARCH-1 + uplink eager-eval forbid moving them).
- **D5 — Convention cleanups:** the two `me` models that use bare `BaseModel`
  (`tracker/me`, `wiki/me`) → inherit `APIModel`; delete the dead tombstone `forms/_models.py`;
  rename `forms/surveys`' `SurveyList`(envelope)/`SurveyCollection`(flat) to match the
  `XList = flat RootModel` convention used everywhere else.
- **D6 — Write `docs/conventions/resources.md`** capturing the naming/shape rules ARCHITECTURE.md
  omits: all models inherit `APIModel` (incl. `me`); list-model naming; `RO` import path; when a
  `_raw`/`full` accessor is offered.
- **D7 (optional) — Align the `count` CLI/MCP asymmetry** (CLI accepts query OR filters; MCP tool
  accepts only `query`) — align deliberately or document the divergence. Low priority.

**Files:** the two cli.py + `output.py` (RootModel wrap path); `transitions/{client,models}.py`;
`yandex/_mcp.py` + three `_deps.py`; three single-page clients + a shared helper; two `me/models.py`;
delete `forms/_models.py`; `forms/surveys/models.py`; new `docs/conventions/resources.md`;
`ARCHITECTURE.md` + `test_architecture.py` (ARCH-4). **Snapshot:** model renames don't touch
names; the `count` alignment (if done) changes an MCP tool's params not its name → no snapshot trip
but an MCP-surface behavior change to flag. **Coverage:** existing raw-dump tests updated to expect
Serializer output.

---

## Workstream E — CLI / MCP / output surface (snapshot-changing)

**Why:** `mcp_launcher.py` breaks the resource pattern; the Tracker deeplink leaks a hardcoded
URL; `PrettyStrategy` is hard to read; MCP metadata is good but unwritten.

**Design.**
- **E1 — `mcp` as a Typer sub-app; delete `mcp_launcher.py`.** New `src/ycli/mcp_cli.py`
  (`name="mcp"`) with `start()` (runs the server, lazy-imports `ycli.mcp.main`, friendly error if
  the `[mcp]` extra is missing) and `methods()` (lists tools via an in-memory `fastmcp.Client`,
  like the snapshot test). `cli.py` mounts it via `app.add_typer`; remove the bare-command
  registration. ARCH-3 holds — `mcp_cli.py` lazy-imports `ycli.mcp` (an `mcp.py`-named module),
  not `fastmcp` directly, and is not in the ARCH-3 forbidden-source list.
  - **Public-surface change (deliberate, ARCH-6):** CLI tree gains `mcp start` + `mcp methods`,
    loses bare `mcp`. Regenerate `tests/snapshots/cli_tree.txt`. Update the plugin
    `plugins/yandex-360/.mcp.json` args `["…","ycli","mcp"]` → `["…","ycli","mcp","start"]` and
    its test. Update `test_yandex_cli.py` (`["mcp"]`→`["mcp","start"]`).
- **E2 — Remove the Tracker deeplink.** Delete `_KEY_RE` + the
  `https://tracker.yandex.ru/{key}` link build in `output.py` (ARCH-5 leak; Tracker-only).
  Update `tests/test_output_links.py` + `tests/test_output_strategies.py` to expect bare keys.
  Note in CLAUDE.md that a general per-model deeplink mechanism is deferred.
- **E3 — Decompose `PrettyStrategy`.** Introduce small `RichCell` / `RichTableBuilder` helpers
  and split `_list_table` (CC=5) into `_list_of_dicts_table` / `_list_of_scalars_table`. Behavior
  identical; helpers are unit-testable in isolation. ARCH-4 unchanged (still confined to
  `output.py`).
- **E4 — Write the MCP metadata standard** (already met by all 25 tools): every tool sets `name`,
  a one-line-first docstring (→ `description`), a concrete return type (→ `output_schema`),
  `annotations={**RO,"title":…}`, `tags`. `description`/`output_schema` are auto-derived — never
  set by hand. Add a clarifying comment to the scaffold MCP template; optionally a `test_architecture`
  check asserting every tool has a non-empty description + output schema. (Snapshots track names
  only, so metadata tuning is snapshot-free.)

**Files:** new `mcp_cli.py`; delete `mcp_launcher.py`; `cli.py`; `output.py`; `plugins/yandex-360/.mcp.json`;
snapshots; output + cli + plugin tests; scaffold; `CLAUDE.md`. **Snapshot:** **regenerated on
purpose** (ARCH-6) for the `mcp` sub-app. **Coverage:** new `mcp_cli` commands + Rich helpers need
tests.

---

## Workstream F — Infra, meta & docs (final step: README)

**Why:** live doc drift, loud badges, missing agent tooling, recurring footguns that no command
encodes.

**Design.**
- **F1 — Code graph (graphify).** graphify is installed via `uv tool install`. Run it over `src/`
  with **GLM-5.2** for the semantic pass; place all output + config under `.graphify/`
  (gitignored vs committed — decide in plan; if committed, it's a reproducible artifact regenerated
  via a `/codegraph-regen`-style command, never hand-edited). Validate the claimed integration
  (slash commands / MCP / hook) during planning. Pin the model + prompt so re-runs are stable.
- **F2 — Drift log.** `.claude/drift-log/` is wired but empty. Capture this session's recurring
  conventions (composition-root DI, serialization confinement, the `from_env` purge, the `@cache`
  MCP factory, naming, snapshot discipline) as entries; add a CLAUDE.md line nudging future
  sessions to capture drift before ending.
- **F3 — Helper commands.** `/snapshot-regen` (wraps the snapshot regeneration + diff;
  ARCH-6 hinges on "regenerate on purpose" but no command exists). `/release-checklist` (encodes
  the `uv lock`+`build:` post-release step and the never-skip-ci rule — covers the GitHub-UI
  squash-title blind spot the `git_guard` hook can't see).
- **F4 — Optional doc-drift guard (ARCH-11 candidate).** A grep-test asserting purged idioms
  (`from_env`, `@uplink.timeout`, …) don't appear in `README.md`/`docs/` code blocks. Would have
  caught the line-104 bug. Decide in plan whether to enforce or keep as a command.
- **F5 — Badges.** Replace the 6 `for-the-badge` badges with a minimal `flat-square` set, one
  neutral grey (`555`), add the DeepWiki badge + a PyPI-version badge, drop the loud
  MCP/Claude-Code marketing badges from the row.
- **F6 — README + all-docs audit (LAST).** After everything else is merged and green:
  - Fix the **`from_env` drift** (`README.md:104` still shows `TrackerClient.from_env()` — purged
    by ARCH-7).
  - **Regenerate the demo gif** from `docs/demo/demo.tape` via the committed `.github/workflows/demo.yml`
    path (vhs) — never hand-author. The CLI surface changed (`mcp start`), so the tape may need a
    line updated first, then regenerate.
  - Sweep `README.md` + all other `.md` files for stale commands, flags, examples, and
    inconsistencies introduced by round-2 + round-3.

**Files:** `.graphify/*`; `.claude/drift-log/*`; new `.claude/commands/*`; `README.md`;
`docs/**/*.md`; `docs/demo/demo.tape`; badges. **ARCH/snapshot/coverage:** F6 must run after all
surface changes so the docs reflect final state; gif is a reproducible artifact.

---

## Sequencing (within the single spec)

1. **A1 formatter** first (mechanical, isolates later diffs).
2. **A2–A4** lint/annotations/ty.
3. **B** composition (B1 move models, B2 hoist settings, B3 factory, B4 config rule).
4. **C** transport/status/auth.
5. **D** dedup + ARCH-4 + conventions (depends on B3 factory for D3).
6. **E** surface (snapshot regen happens here, once).
7. **F1–F5** infra/meta.
8. **F6 README + docs audit LAST** — after every surface change is final.

Rationale: tooling before code churn; structural moves (B) before the dedup that builds on them
(D); the single snapshot regeneration isolated in E; all docs last so they describe the final state.

## Out of scope / deferred

- Full module reorg (П8) — rejected; only the two surgical moves (B1/B2) are done.
- Auth Strategy ABC — deferred until IAM is actually implemented (seam only, C4).
- `@validate_call` — declined; the issue-key `StringConstraints` alias is a separate future feature.
- General per-model deeplink mechanism — deferred (E2 only removes the Tracker leak).
- `settings.py` is hoisted but NOT split; `count` CLI/MCP alignment (D7) is optional.
- Maximalist ruff families (`D/PL/S/…`) and promoting ty to a hard gate — a later ratchet.

## Risks

- **Formatter blast radius** (~220 files) — mitigated by landing A1 alone, deterministic diff.
- **ty beta volatility** — pinned + advisory, never a release blocker this round.
- **D2 `transitions execute` API shape** — verify against vendored docs + a live response.
- **E1 plugin `.mcp.json` change** — a breaking change for plugin users; intentional, documented.
- **graphify external dependency** — keep its artifacts out of the 100%-coverage path; validate
  integration before committing to it.
- **Auto-release per merge** — each workstream that merges cuts a release; keep each green and run
  the `uv lock` + `build:` follow-up.
