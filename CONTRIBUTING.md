# Contributing to ycli

Thanks for helping improve **ycli**! This project wraps Yandex 360 services and exposes
them four ways (CLI, MCP server, Python SDK, Claude Code plugin) from one codebase.

## Setup

```bash
uv sync           # install runtime + dev deps
uv run pytest     # run the test suite
```

You need Python ≥ 3.12. Dependencies are managed with `uv` — add them with
`uv add <pkg>` (runtime) or `uv add --dev <pkg>`; never hand-edit `pyproject.toml`
dependency lists.

## Conventions

- **Tests:** `uv run pytest`. The suite must stay at **100% coverage** (`--cov-fail-under=100`).
  HTTP is stubbed with `responses` — no live network. Mark CLI/MCP wiring tests with
  `@pytest.mark.integration`. Async MCP tests rely on `asyncio_mode = "auto"`.
- **MCP server is read-only.** Writes live in the CLI/SDK only — never add an MCP write tool.
- **New endpoints:** ship reads across SDK + CLI + MCP; ship writes across SDK + CLI only.
  Each surface gets a test (TDD).
- **Auth:** clients read `YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID` from the
  environment. Never hardcode credentials. Header casing differs per service
  (Tracker `X-Org-ID`, Wiki/Forms `X-Org-Id`) — the transport handles this for you.
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

CI (`.github/workflows/demo.yml`) re-renders and commits it automatically whenever
`docs/demo/**` changes, so the demo always reflects the current CLI.

## Layout

Per-domain SDK lives under `src/ycli/yandex/<domain>/` — each resource group has
`client.py` (uplink SDK), `cli.py` (Typer), `mcp.py` (FastMCP), `models.py` (pydantic).
The distributable Claude Code plugin is under `plugins/yandex-360/`.

See [`docs/api-coverage.md`](docs/api-coverage.md) for the current coverage gap analysis
and roadmap — a great place to find a first contribution.
