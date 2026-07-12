# ycli

> Baseline agent behavior is provided by spark/core (injected each session via the SessionStart hook); add only project-specific rules here.

## Project Overview

`ycli` interacts with Yandex 360 services (Tracker, Wiki, Forms; more to come) and exposes
the same SDK four ways: a Typer **CLI** (`ycli` / `yandex-cli`), a FastMCP **server**
(`ycli mcp start`, optional `[mcp]` extra), an importable **Python SDK** (`ycli.yandex.*`), and a
Claude Code **plugin** under `plugins/yandex-360/`. Published on PyPI as `yandex-cli`.

- **Stack:** Python ≥3.12, managed with `uv`. `requests` + `uplink` (HTTP/SDK), `typer`
  (CLI), `fastmcp` (MCP), `pydantic` (models), `loguru` (logging).
- **Layout:** root entry-point packages `src/ycli/cli/` (CLI, `app.py`) and `src/ycli/mcp/` (MCP server, `server.py`); per-domain SDK
  under `src/ycli/yandex/<domain>/` (each has `client.py`, `cli.py`, `mcp.py`, models). Vendored
  external docs live under `references/` (not `docs/`, which is the repo's own docs):
  `references/yandex-360/` holds the 360/dev-hub docs — git-ignored, local-only, regenerated with
  `scripts/fetch_docs.py` (yandex.ru is not open-licensed); `references/yandex-cloud/` is a git
  submodule of `github.com/yandex-cloud/docs` (CC BY 4.0, fetched on demand). The distributable
  plugin (skills + instructions) lives in `plugins/yandex-360/`, listed by the repo-root
  `.claude-plugin/marketplace.json`.
- **Output:** every CLI command honors a global `--format/-o` flag (`auto` · `json` · `yaml`
  · `pretty`); rendering goes through `output.Serializer.serialize` (`src/ycli/cli/output.py`, ARCH-4). No output surface
  hardcodes a service UI URL (ARCH-5); a general per-model deeplink mechanism is deferred.
- **Typing:** the package ships a PEP 561 `py.typed` marker, so downstream type checkers
  see ycli's types. The MCP server is the `ycli mcp start` subcommand (optional `[mcp]` extra).

## Project-Specific Conventions

- **Dependencies:** add with `uv add <pkg>` (runtime) / `uv add --dev <pkg>` (dev) — never
  hand-edit `pyproject.toml` dependency lists.
- **Naming:** spell identifiers and env-var names out in full — never abbreviate
  (`timeout_seconds` not `timeout_s`, `organization_id` not `org_id`; `YANDEX_ID_OAUTH_TOKEN`
  is already correct).
- **Tests:** `uv run pytest`. Async MCP tests rely on `asyncio_mode = "auto"`; HTTP is stubbed
  with `responses` (no live network). Mark CLI/MCP wiring tests with `@pytest.mark.integration`.
- **Auth:** credentials (`YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID`) are read once
  at the composition root — `Credentials()` / `AppConfig()` in `AppContext` for the CLI, or
  the `dependencies` cached factory in each domain's MCP module — and passed as raw `oauth_token` /
  `organization_id` constructor arguments to each client. There is no `from_env` or
  `session_from_env`; never hardcode credentials. The transport sends one canonical
  `X-Org-Id` org header for every service (HTTP header names are case-insensitive per
  RFC 9110), so there is no per-service casing to track.
- **MCP server is read/write** (ARCH-3 annotation honesty: reads carry `readOnlyHint=True`,
  writes carry explicit `destructiveHint`/`idempotentHint`); `ycli mcp start --read-only`
  serves the reads-only view.
- **Secrets:** `.env` and `.mcp.json` are gitignored — keep real tokens out of committed files
  (`.env.example` / `.mcp.example.json` hold placeholders).

## Release & safety

- **Auto-release on push to main.** Every push to `main` runs python-semantic-release (PSR),
  which versions from Conventional Commits and publishes to PyPI (OIDC trusted publishing).
  Use `feat:` / `fix:` / `docs:` / `chore:` … prefixes; the squash-merge title becomes the
  release. PSR pushes the release commit + tag back to `main` with a short-lived **GitHub App**
  installation token (App ID `4175048`; secrets `RELEASE_APP_CLIENT_ID` /
  `RELEASE_APP_PRIVATE_KEY`, minted in `release.yml`) — the default `GITHUB_TOKEN` cannot bypass
  the branch-protection ruleset below, so the App token is what lets a release land. After a
  release, `uv.lock`'s own version lags `pyproject` until you re-lock (see the gate bullet).
- **Never write a skip-ci token.** `[skip ci]` / `[ci skip]` / `[no ci]` / `[skip actions]` /
  `[actions skip]`, or a `skip-checks: true` commit trailer, anywhere in a commit **or
  squash-merge** message makes GitHub silently cancel the workflow run — and with it the
  release. The `git_guard` PreToolUse hook (`.claude/hooks/`) blocks all of these in the
  `git`/`gh` commit/merge command string (its one blind spot: a message passed via file,
  e.g. `git commit -F`); the `no-skip-ci` pre-commit hook additionally catches `[skip ci]` /
  `[ci skip]` written into staged file *content*; this rule covers what neither can see (a
  message typed in the GitHub UI).
- **Secrets never reach a commit.** gitleaks runs in pre-commit and CI. Credentials come
  from the env (`YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID`); the root `.env` /
  `.mcp.json` are gitignored. The one committed `.mcp.json` (the bundled plugin config)
  holds only `${VAR}` references — config and tests never embed literal values.
- **Reproducible artifacts.** Generated demos/tables come from a committed source —
  regenerate, never hand-author (the `demo.svg` incident).
- **Branch → PR → explicit approval before merge — enforced.** `main` is protected by a
  repository ruleset (`Protect main — require CI`): the checks `test (3.12)` · `test (3.13)` ·
  `gitleaks` are **required** before any merge, and `main` cannot be force-pushed or deleted.
  No direct pushes to `main`; only the release GitHub App (ID `4175048`) bypasses, so PSR can
  land the release commit. **Consequence:** any red required check — including a stale `uv.lock`
  after a release, where `uv sync --locked` fails — now *blocks every merge*, not just reds CI.
  Re-lock (`uv lock`) and ship a `build:` commit immediately after each release. **Emergency
  rollback:** set the ruleset to `disabled` (GitHub → Settings → Rules), fix, re-enable.
- **100% coverage gate.** `uv run pytest` enforces `--cov-fail-under=100`; new code ships
  with tests that keep it green.
- **New resources via `/new-endpoint`**, respecting the invariants in
  [`ARCHITECTURE.md`](ARCHITECTURE.md) and the model/naming/import conventions in
  [`docs/conventions/resources.md`](docs/conventions/resources.md). Authoring skills/commands follows
  [`docs/conventions/skills-and-commands.md`](docs/conventions/skills-and-commands.md).

## Working notes

- **Drift log:** when a session reveals a convention the codebase doesn't yet enforce, capture it via `core:creating-drift-logs` before ending.

## Architecture invariants (enforced)

The repo's structure is enforced by executable checks — see [`ARCHITECTURE.md`](ARCHITECTURE.md)
for the eleven invariants (ARCH-1..11). They are verified by `tests/test_architecture.py`,
import-linter (`uv run lint-imports`), and `tests/test_snapshots.py`. Do **not** route around
them: HTTP only in `client.py`; CLI output only via `output.Serializer.serialize`; MCP tools read-only;
new resources via `/new-endpoint`. To change an invariant, edit `ARCHITECTURE.md` **and** its
enforcing check in the **same** PR and flag it.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing (it's git-ignored/local — regenerate for free with `graphify export wiki` if absent).
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- **Do NOT run `graphify update .` here.** It ignores the curated `--exclude` set in `.graphify/rebuild.sh` and re-scans the vendored `references/yandex-cloud/` submodule (~90k files), exploding the graph from ~5.3k to ~560k nodes. Treat the committed graph as a periodically-rebuilt snapshot: refresh it only by re-running `.graphify/rebuild.sh` (a full GLM-5.2 rebuild that costs API credits), and accept minor staleness (e.g. a just-deleted symbol) between rebuilds.
