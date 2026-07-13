# Contributing to ycli

Thanks for helping improve **ycli**! This project wraps Yandex 360 services and exposes
them four ways (CLI, MCP server, Python SDK, Claude Code plugin) from one codebase.

## Setup

```bash
uv sync --all-extras   # install runtime + dev deps + the optional `mcp` extra
uv run pytest          # run the test suite
```

`--all-extras` matters: `fastmcp` lives in the optional `mcp` extra and the 100%-coverage
test suite imports it, so a plain `uv sync` leaves you with a red suite. CI installs the
same way (`uv sync --locked --all-extras --dev`).

You need Python ≥ 3.12. Dependencies are managed with `uv` — add them with
`uv add <pkg>` (runtime) or `uv add --dev <pkg>`; never hand-edit `pyproject.toml`
dependency lists.

The committed `.claude/settings.json` grants only a conservative, scoped baseline (broad
reads + a mostly-read-only `Bash` allowlist); it never grants unscoped `Write`/`Edit`/`Bash`.
Put any broader personal permissions in the gitignored `.claude/settings.local.json` instead
of widening the committed file.

### Architecture guardrails

The structure in [`ARCHITECTURE.md`](ARCHITECTURE.md) is enforced. Install the local hooks once:

```bash
uv run pre-commit install
```

They run import-linter + the architecture/snapshot tests on commit. CI runs the same. If you
change the public surface on purpose, regenerate snapshots: `uv run python -m tests.snapshots --update`.

## Conventions

- **Tests:** `uv run pytest`. The suite must stay at **100% coverage** (`--cov-fail-under=100`).
  HTTP is stubbed with `responses` — no live network. Mark CLI/MCP wiring tests with
  `@pytest.mark.integration`. Async MCP tests rely on `asyncio_mode = "auto"`.
- **MCP server is read/write with honest annotations** (ARCH-3): reads carry
  `readOnlyHint=True` (the `RO` set); writes carry explicit `destructiveHint` /
  `idempotentHint` (the `WRITE` / `WRITE_IDEMPOTENT` / `DESTRUCTIVE` sets in
  `ycli.yandex.mcp`) plus the `write` tag. `ycli mcp start --read-only` serves the
  reads-only view.
- **New endpoints:** ship every operation across SDK + CLI + MCP (writes included, with
  honest annotations). Each surface gets a test (TDD).
- **Auth:** credentials (`YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID`) are read
  from the environment once, at the composition root — `Credentials()` / `AppConfig()` in
  `AppContext` for the CLI, or each domain's cached `dependencies` factory for MCP — and
  passed to clients as explicit `oauth_token` / `organization_id` constructor arguments.
  Clients themselves never read the environment (ARCH-7; there is no `from_env`). Never
  hardcode credentials. The transport sends one canonical `X-Org-Id` org header for every
  service (case-insensitive per RFC 9110).
- **Secrets:** `.env` and `.mcp.json` are gitignored. Keep real tokens out of commits;
  use `.env.example` / `.mcp.example.json` placeholders.

## Commits & releases

This project uses [Conventional Commits](https://www.conventionalcommits.org/) —
they drive **automated releases** via [python-semantic-release](https://python-semantic-release.readthedocs.io/).
On every push to `main`, the version, `CHANGELOG.md`, git tag, GitHub Release, and the
PyPI upload are produced automatically from the commit messages:

- `fix: …` → patch release (`0.1.0` → `0.1.1`)
- `feat: …` → minor release (`0.1.0` → `0.2.0`)
- `feat!: …` / a `BREAKING CHANGE:` footer → major (kept at `0.x` until 1.0)
- `docs: … / chore: … / ci: … / refactor: … / test: …` → no release

So write the commit (or the squash-merge title) as the change it makes. No manual version
bumps or changelog edits.

## Demo GIF

The README demo (`docs/assets/demo.gif`) is generated from `docs/demo/demo.tape` with
[VHS](https://github.com/charmbracelet/vhs) — never hand-edited. The tape types real
`ycli` commands; the shims in `docs/demo/bin/` serve the genuine `--help` and leak-free
baked sample data (no network, no credentials). Regenerate it with:

```bash
vhs docs/demo/demo.tape    # needs vhs + ttyd + ffmpeg on PATH
```

CI (`.github/workflows/demo.yml`) is **report-only**: whenever `docs/demo/**` changes it
re-renders the GIF, reports any drift against the committed one, and uploads the fresh
render as a workflow artifact — it never pushes. If it flags drift, regenerate locally
with the command above and commit the result yourself.

## Layout

Per-domain SDK lives under `src/ycli/yandex/<domain>/` — each resource group has
`client.py` (uplink SDK), `cli.py` (Typer), `mcp.py` (FastMCP), `models.py` (pydantic).
The distributable Claude Code plugin is under `plugins/yandex-360/`.

The [README Coverage section](README.md#coverage) is generated from the code and is the
source of truth for what's wrapped. A few Yandex features have **no public REST API** and are
deliberately not wrapped — please don't try to add them:

- **Tracker** — `DELETE /issues/{key}`, `GET /issues` (bulk list), `PATCH /queues/{id}`
  (phantom paths that appear only in the navigation-only doc tree, not the API reference).
- **Wiki** — full-text search and page history/versions listing (UI-only).
- **Forms** — appearance/themes and analytics/charts (UI-only).

Everything else that the api-ref documents is fair game — add it with `/new-endpoint`.
