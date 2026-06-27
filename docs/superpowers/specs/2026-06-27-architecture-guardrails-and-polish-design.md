# Architecture Guardrails & Repo Polish — Design

**Status:** design (brainstorming output) — awaiting user review before `writing-plans`.

**Goal:** Make `ycli` resistant to silent architectural drift by AI agents, by turning its
load-bearing invariants into *executable* artifacts (tests, linters, generators, hooks), and
fold in the agreed AI-infra, UX, and discoverability improvements — guardrails first, since
they protect every later change.

**Architecture (of this effort):** Five-layer "architecture-as-executable-contract" spine
(Track A) + three polish tracks (B/C/D) + one flagship net-new direction (Track E). The plan
that follows this spec sequences Track A first.

**Tech Stack:** Python ≥3.12, uv, pydantic, typer, fastmcp, uplink, rich, loguru;
import-linter (new dev dep), pre-commit (new dev tooling), python-semantic-release (existing),
GitHub Actions (existing).

## Global Constraints

- Keep the 100%-coverage gate (`--cov-fail-under=100`) green; new tests count toward it.
- Conventional Commits drive PSR auto-release on push to `main`. Never place a skip-ci token
  (`[skip ci]`/`[ci skip]`) anywhere in a commit OR squash-merge message (GitHub scans the
  whole message) — it silently cancels the release. Only the `demo.yml` GIF commit may skip.
- Branch → PR → green CI → explicit confirm before merge/publish. Dependencies via `uv add`.
- MCP server stays read-only. Reads ship SDK+CLI+MCP; writes ship SDK+CLI only.
- **Guardrails must stay few and load-bearing (YAGNI).** Over-constraining makes agents and
  humans fight the linter — that is its own drift. ~6 enforced invariants, not 20 aspirational.
- An invariant change is deliberate: edit `ARCHITECTURE.md` + its enforcing test in the SAME
  PR and call it out in the PR body. The enforcement must make a silent change impossible.

---

## Established facts (verified against source, 2026-06-27)

These ground the invariants — they all hold *today*, so enforcement locks in the status quo:

- **Resource symmetry:** 16 resource dirs under `src/ycli/yandex/{tracker,wiki,forms}/<resource>/`,
  each with `client.py` · `cli.py` · `mcp.py` · `models.py` · `__init__.py`.
- **Shared layer:** `src/ycli/yandex/base.py`, `transport.py`, and per-domain `_base.py`,
  `_deps.py`, `_clideps.py`, `client.py`, `cli.py`, `mcp.py`, `_models.py`.
- **HTTP confinement:** `requests`/`uplink` imported only in `*/client.py`, `base.py`,
  `transport.py` — never in `cli.py`/`mcp.py`/`models.py`.
- **MCP confinement:** `fastmcp` imported only in modules named `mcp.py`. Every tool already
  carries `annotations=RO` where `RO = {"readOnlyHint": True}` (`*/_deps.py`).
- **Output chokepoint:** `model_dump_json` appears in exactly one place — `src/ycli/output.py`.
  CLI raw/scalar passthroughs (`json.dumps(raw)`, `print(count)`, `.content or ""`) are
  intentional and stay allowed.
- **Single sources of truth:** version via `importlib.metadata.version("yandex-cli")`
  (`src/ycli/__init__.py`); org/auth headers centralized in `transport.py`.

---

## Track A — Architecture as an executable contract (the spine)

### Layer 0 — Name the invariants: `ARCHITECTURE.md` (repo root)

A short numbered list; the single source of truth. CLAUDE.md links to it. Each invariant names
its enforcement so a reader knows it is real, not aspirational:

- **ARCH-1 Four-surface symmetry.** Every `yandex/<domain>/<resource>/` dir contains exactly
  `client.py`, `cli.py`, `mcp.py`, `models.py`, `__init__.py`. *(test_architecture)*
- **ARCH-2 HTTP confinement / layering.** `cli.py`, `mcp.py`, `models.py` must not import
  `requests` or `uplink`; all HTTP lives in `client.py`/`base.py`/`transport.py`. *(import-linter)*
- **ARCH-3 MCP is read-only.** `fastmcp` imported only in `mcp.py` modules; every `@mcp.tool`
  carries `readOnlyHint` and wraps a read (no create/update/add/execute verbs). *(import-linter + test_architecture)*
- **ARCH-4 Output discipline.** `model_dump_json` / pydantic-result serialization for CLI
  output goes through `ycli.output.render`; `model_dump_json` may appear only in `output.py`.
  *(test_architecture)*
- **ARCH-5 Single sources of truth.** No hardcoded version, OAuth token, or org id in `src/`;
  version from `importlib.metadata`; org/auth headers only in `transport.py`. *(test_architecture)*
- **ARCH-6 Public-surface stability.** The CLI command tree and the MCP tool list change only
  with an intentional snapshot regeneration. *(snapshot tests)*

### Layer 1 — Enforce mechanically

1. **import-linter** (`uv add --dev import-linter`), contracts in `pyproject.toml`
   `[tool.importlinter]`:
   - *Forbidden* contract: `source_modules` = the cli/mcp/models layer, `forbidden_modules`
     = `requests`, `uplink` (`include_external_packages = true`) → ARCH-2.
   - *Forbidden* contract: non-`mcp` modules → `fastmcp` → ARCH-3 (import side).
   - Run via `uv run lint-imports` in CI + pre-commit.
2. **`tests/test_architecture.py`** (in the coverage suite):
   - ARCH-1: walk `src/ycli/yandex/*/*/`, assert the 5 canonical files exist; assert no
     *extra* surface files sneak in unreviewed (allowlist the shared `_*.py`).
   - ARCH-3 (semantic): import each resource `mcp.py`, assert every registered tool's name/verb
     is a read (deny-list `create|update|add|execute|delete|set`), and `readOnlyHint` is set.
   - ARCH-4: AST-scan `src/ycli/**` — `model_dump_json` only in `output.py`.
   - ARCH-5: regex-scan `src/ycli/**` for a hardcoded version literal, `YANDEX_ID_*` token
     assignment, or org-header string outside `transport.py`.
3. **Surface snapshot tests** — `tests/snapshots/cli_tree.txt` and `tests/snapshots/mcp_tools.txt`,
   generated from the live Typer app (recursive `--help` walk) and the FastMCP tool registry.
   A test renders the current surface and diffs against the committed snapshot; drift fails with
   "run `uv run python -m tests.snapshots --update` to accept." → ARCH-6. This is the guard
   against an agent silently renaming/removing/adding a command or tool.

### Layer 2 — Channel the easy path: `/new-endpoint` generator

A scaffolding generator (a `scripts/new_endpoint.py` invoked by a `.claude/commands/new-endpoint.md`
slash command) that, given `<domain> <resource> [--write]`, emits the canonical
`client.py`/`cli.py`/`mcp.py`/`models.py` + a `tests/.../test_*.py` stub, pre-wired to the
domain `_deps`, the `render` output path, and `RO` annotations — so the path of least resistance
produces the compliant shape. This realizes the user's vision (*change `src/`, derive the rest*):
the generator **is** the derivation, and it satisfies ARCH-1/3/4 by construction.

### Layer 3 — Catch semantic drift linters can't: review gate

- **CLAUDE.md rule** making invariant changes deliberate (see Global Constraints).
- An **architecture-review rubric** — a reviewer pass (subagent dimension / a project
  `.claude/commands/arch-review.md`) keyed solely to `ARCHITECTURE.md`, run before merge.
  Catches business logic creeping into `cli.py`, a client method bypassing `transport`, etc. —
  things imports/snapshots can't see.

### Layer 4 — Fail fast & local

- **pre-commit** (`.pre-commit-config.yaml`, `uv add --dev pre-commit`): hooks for
  `lint-imports`, `pytest -k architecture` (fast subset), ruff (if adopted), and a local
  skip-ci/token guard. Documented in CONTRIBUTING.
- **`Stop` hook** in `.claude/settings.json`: on agent stop, run the architecture test subset +
  `lint-imports` and surface failures so the agent self-corrects before handing back.
- **CI:** add a `lint-imports` + architecture-tests step to `ci.yml` (already runs pytest;
  snapshot + arch tests ride along in the 100% gate).

---

## Track B — AI-infra hardening (non-architecture)

Mined from the three past sessions; each item prevents a *real* past failure or codifies a
*repeated* preference.

- **B1 skip-ci PreToolUse hook** (`.claude/`): block any `git commit` / `gh pr merge` whose
  message contains `[skip ci]`/`[ci skip]` unless it targets only `docs/assets/`. *(skip-ci
  killed a release twice; prose memory did not prevent recurrence — only a hard block will.)*
- **B2 token-leak PreToolUse hook:** block commits/staging containing `YANDEX_ID_OAUTH_TOKEN=`
  or staged `.env`/`.mcp.json`.
- **B3 Expand `CLAUDE.md`** with the load-bearing rules currently only in CONTRIBUTING /
  private memory: auto-release + skip-ci footgun; reproducible-artifacts rule (the demo.svg
  incident); branch→PR→confirm flow; 100%-coverage gate; new-endpoint surface rule; a pointer
  to `ARCHITECTURE.md`. Fix staleness: mention `--format/-o`, `ycli mcp` subcommand, shipped
  `py.typed`.
- **B4 Scope the Bash permission allowlist** in `.claude/settings.json`: replace bare `"Bash"`
  with `Bash(uv run pytest:*)`, `Bash(uv build)`, `Bash(uv sync*)`, `Bash(uv add*)`,
  `Bash(gh pr*)`, `Bash(git status:*)`, `Bash(git diff:*)`, etc. — fewer prompts *and* removes
  the blanket grant.
- **B5 Bundle `.mcp.json` in `plugins/yandex-360/`** so installing the plugin auto-wires the
  read-only MCP tools (today every user hand-copies the JSON). Document that env vars still come
  from the user's shell. *(highest end-user friction removal)*
- **B6 (polish)** plugin slash-commands (`/tracker-triage`, `/wiki-publish`), a read-only
  `yandex-360-researcher` subagent, and seed `.claude/drift-log/open/` (the `core` plugin
  expects it; currently absent) with the skip-ci and demo.svg incidents.

## Track C — UX quick-wins

- **C1 Re-enable shell completion** — remove `add_completion=False` in `cli.py` (one line;
  bash/zsh/fish/pwsh via Typer). *S*
- **C2 `openWorldHint=True`** added to the MCP `RO` annotations (calls an external API).
  *(`readOnlyHint` already shipped.)* *S*
- **C3 `ycli auth status` / `whoami`** — validate env token + report org. *S*
- **C4 "Did you mean?" error hints** — `difflib.get_close_matches` on bad queue/command names,
  raised as `typer.BadParameter` with a one-line fix suggestion. *S*
- **C5 OSC8 hyperlinks** on issue/queue keys in pretty tables (rich-native, TTY-gated). *S*
- **C6 SDK robustness** — typed exception hierarchy (`YandexError` → `YandexAuthError`(401),
  `YandexNotFoundError`(404), `YandexRateLimitError`(429), …) + transparent retries honoring
  `Retry-After` on the requests-backed transport. *S–M*
- **C7 (optional)** `--format csv`, `--web` (open in browser), `$PAGER` for long output. *S*

Each C-item ships with a test (TDD) and respects ARCH-4 (output through `render`).

## Track D — Discoverability / repo (ownership marked)

- **D1 `server.json` + MCP Registry auto-publish** (agent: file + CI job; OIDC) — the upstream
  source-of-truth that Glama/PulseMCP/mcp.so/GitHub MCP Registry crawl. *Agent.* *S/M*
- **D2 Keyword-front-load the GitHub About** ("Yandex 360 CLI + MCP server + Python SDK for
  Tracker, Wiki, Forms"). *Agent via `gh repo edit` or user.* *S*
- **D3 OpenSSF Scorecard badge** + `ossf/scorecard-action`. *Agent.* *S/M*
- **D4 PyPI downloads badge + README heading/alt-text tuning.** *Agent.* *S*
- **D5 Enable Discussions + Private Vulnerability Reporting** (SECURITY.md links the latter; the
  link 404s until enabled). *User-manual (GitHub settings).* *S*
- **D6 Directory submissions** (Glama, mcp.so, PulseMCP, Claude plugin dirs) + one genuine Habr
  walkthrough cross-posted to dev.to. *User-manual.* *S–M*
- **Avoid:** buying stars/downloads, mass cross-posting, manually spamming every sub-registry
  (publish once to the official registry; let crawlers propagate).

## Track E — Flagship net-new direction (documented; likely its own plan)

**LangChain tool + OpenAI function-schema export** — an `ycli.integrations` module that exposes
the existing pydantic models as `convert_to_openai_tool(...)` JSON and
`StructuredTool.from_function(...)` objects, so ycli plugs into the whole agent ecosystem beyond
MCP for near-zero schema work. *S, highest leverage.* Then, in later sessions: Tracker→Markdown /
Wiki backup export (*M, flagship*) and a GitHub Action + Docker image (*S–M*). Full API coverage
remains a separate project.

---

## Phasing (the plan will detail this)

1. **Track A** (guardrails) — first; protects everything after it.
2. **Track B** (AI-infra hardening) — slots into the same enforcement frame.
3. **Track C** (UX) + **Track D-agent** items — feature work, now drift-guarded.
4. **Track D-user** items — handed to the user with exact steps.
5. **Track E** — flagship net-new, its own spec/plan next.

## Out of scope

Full Yandex API coverage (Mail, more endpoints) — separate future project. Async SDK client,
Textual TUI, Homebrew, Raycast, webhooks (Yandex has only outbound queue triggers) — deferred,
lower ROI.
