# ycli Repository Showcase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the public `bim-ba/ycli` GitHub repo modern, inviting, and discoverable — a great first impression and a low barrier to entry — without misrepresenting the project.

**Architecture:** Presentation + metadata only; zero changes to `src/` behavior. Work proceeds: LICENSE → CI → demo asset → community files → README (consumes demo + CI badge) → repo metadata. Each task ends with an independently verifiable deliverable.

**Tech Stack:** Markdown, shields.io badges, GitHub Actions (`astral-sh/setup-uv`), `uv`, a terminal recorder (`agg`/`termtosvg`/`asciinema`), `gh` CLI for metadata.

## Global Constraints

- README language: **English**, single `README.md`.
- License: **MIT**, `Copyright (c) 2026 Sava Znatnov`.
- Truthful only: every badge/claim must be backed by reality (CI badge requires the real workflow; `100%` coverage is the real `--cov-fail-under=100` gate).
- No real Yandex org data in any committed artifact (demo uses baked/safe output; no token/org-id committed).
- Owner/repo for all URLs: `bim-ba/ycli`.
- Use the **validated coverage matrix** in `docs/superpowers/specs/2026-06-27-repo-showcase-design.md` (appendix) verbatim — do not paraphrase capabilities.
- Don't touch `src/`, tests, or `.env`. Don't commit `.env`/`.mcp.json` (already gitignored).
- Commit after each task. Branch off `main` first (do not commit showcase work directly to `main` without a branch unless the user already approved).

---

### Task 1: LICENSE + package license metadata

**Files:**
- Create: `LICENSE`
- Modify: `pyproject.toml` (add `license` + classifier)

**Interfaces:**
- Produces: a `LICENSE` file at repo root (GitHub auto-detects it) and `license = "MIT"` in package metadata that the README License badge will reference.

- [ ] **Step 1: Create the LICENSE file**

Create `LICENSE` with the standard MIT text:

```text
MIT License

Copyright (c) 2026 Sava Znatnov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Add license metadata to pyproject.toml**

In `pyproject.toml`, under `[project]` (after the `description`/`readme` lines), add:

```toml
license = "MIT"
license-files = ["LICENSE"]
```

- [ ] **Step 3: Verify the build metadata is valid**

Run: `uv run python -c "import tomllib,pathlib; tomllib.loads(pathlib.Path('pyproject.toml').read_text()); print('pyproject OK')"`
Expected: `pyproject OK`

Run: `uv build 2>&1 | tail -3`
Expected: builds a wheel/sdist with no license error (SPDX `MIT` accepted by hatchling). If `license-files` causes a hatchling error on the installed version, fall back to `license = { text = "MIT" }` and re-run.

- [ ] **Step 4: Commit**

```bash
git add LICENSE pyproject.toml
git commit -m "chore: add MIT license"
```

---

### Task 2: CI workflow (real test badge)

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: a workflow named `CI` (file `ci.yml`) whose status badge URL is
  `https://img.shields.io/github/actions/workflow/status/bim-ba/ycli/ci.yml?branch=main&style=for-the-badge` — consumed by the README in Task 5.

- [ ] **Step 1: Create the workflow**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: uv sync --locked --dev
      - name: Run tests
        run: uv run pytest
```

- [ ] **Step 2: Validate the workflow YAML locally**

Run: `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('ci.yml valid')"`
Expected: `ci.yml valid` (if PyYAML is unavailable, `python -c "import json,sys; ..."` is not applicable — instead inspect indentation manually).

- [ ] **Step 3: Confirm the test command actually passes locally (the CI proxy)**

Run: `uv run pytest -q`
Expected: all tests pass, coverage gate `--cov-fail-under=100` satisfied (it's in `pyproject.toml`).

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions test workflow (uv + pytest, py3.12/3.13)"
```

> Note: the badge turns green only after this is pushed and the workflow runs on GitHub. Task 6 / final verification confirms the run succeeded before claiming the badge is real.

---

### Task 3: Demo asset (terminal SVG, no data leak)

**Files:**
- Create: `docs/demo/demo.sh` (deterministic driver — real `--help` + baked safe data)
- Create: `docs/demo/demo.tape` OR `docs/demo/demo.cast` (recorder source, tool-dependent)
- Create: `docs/assets/demo.svg` (or `.gif`) — the committed visual

**Interfaces:**
- Produces: `docs/assets/demo.svg` referenced by the README hero in Task 5.

- [ ] **Step 1: Pick the lightest recorder available, install it**

Try in order; stop at the first that installs cleanly (no `ttyd` required):
1. `agg` (asciinema gif gen) + `asciinema`: `uv tool install asciinema` then install `agg` via `cargo install --git https://github.com/asciinema/agg` **or** a release binary.
2. `termtosvg`: `uv tool install termtosvg` (records a PTY session directly to animated SVG).

If neither installs in this environment, fall back to Step 4b (hand-authored static terminal SVG). Record which path was taken in the commit message.

- [ ] **Step 2: Write the deterministic driver script**

Create `docs/demo/demo.sh`. It must NOT call the live API. Real, no-creds help output is genuine; data lines are baked. Example:

```bash
#!/usr/bin/env bash
# Deterministic ycli demo. Real --help output; baked sample data (no network, no creds).
set -euo pipefail
ps1() { printf '\033[38;5;203m❯\033[0m %s\n' "$1"; }

ps1 "ycli --help"
uv run ycli --help

ps1 "ycli tracker issues get TRACKER-1"
cat <<'OUT'
TRACKER-1  ·  Set up project scaffolding
status:    In Progress      assignee: alice
priority:  Normal           updated:  2026-06-20
OUT

ps1 "ycli wiki pages get onboarding"
cat <<'OUT'
onboarding  ·  Team Onboarding Guide
author: bob   revision: 7   children: 4
OUT

ps1 "ycli-mcp   # read-only MCP server: wiki_*, tracker_*, forms_* tools"
```

Make it executable: `chmod +x docs/demo/demo.sh`.

- [ ] **Step 3: Verify the driver leaks no real data and runs**

Run: `bash docs/demo/demo.sh | head -40`
Expected: clean output, real help text, baked sample lines. No real org id / token / private content.

Run: `grep -nEi "$(printf '%s' "$(sed -n 's/^YANDEX_ID_ORGANIZATION_ID=//p' .env)")" docs/demo/demo.sh docs/assets/* 2>/dev/null || echo "no org id present"`
Expected: `no org id present` (guard against accidentally baking the real org id).

- [ ] **Step 4a: Record to the committed asset (recorder path)**

- `agg` path: `asciinema rec --command "bash docs/demo/demo.sh" docs/demo/demo.cast` then `agg docs/demo/demo.cast docs/assets/demo.gif`.
- `termtosvg` path: `termtosvg docs/assets/demo.svg --command "bash docs/demo/demo.sh" --still-frames` (use animated SVG output).

- [ ] **Step 4b: Fallback — hand-authored static terminal SVG (only if Step 1 found no tool)**

Create `docs/assets/demo.svg` as a styled static terminal card (dark window chrome, the same prompt/output text as `demo.sh`). Keep it < 30 KB and crisp on GitHub light/dark.

- [ ] **Step 5: Verify the asset exists and is sane**

Run: `ls -la docs/assets/ && file docs/assets/demo.* `
Expected: a committed `demo.svg` or `demo.gif`, non-empty, reasonable size (< ~1.5 MB for a gif).

- [ ] **Step 6: Commit**

```bash
git add docs/demo/ docs/assets/
git commit -m "docs: add deterministic terminal demo asset (no live data)"
```

---

### Task 4: Community files

**Files:**
- Create: `CONTRIBUTING.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `CHANGELOG.md`

**Interfaces:**
- Produces: `CONTRIBUTING.md` linked from the README footer (Task 5).

- [ ] **Step 1: Write CONTRIBUTING.md**

Distill (do not copy) the project conventions that matter to outside contributors:

```markdown
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

## Layout

Per-domain SDK lives under `src/ycli/yandex/<domain>/` — each resource group has
`client.py` (uplink SDK), `cli.py` (Typer), `mcp.py` (FastMCP), `models.py` (pydantic).
The distributable Claude Code plugin is under `plugins/yandex-360/`.

See [`docs/api-coverage.md`](docs/api-coverage.md) for the current coverage gap analysis
and roadmap — a great place to find a first contribution.
```

- [ ] **Step 2: Write the issue templates**

`.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Something in ycli (CLI / MCP / SDK / plugin) doesn't work as expected
labels: bug
---

**Surface:** CLI / MCP server / Python SDK / Claude Code plugin

**What happened**
A clear description of the bug.

**Command / code**
```
# the exact command or snippet (redact tokens & org id!)
```

**Expected vs actual**

**Environment:** ycli version, Python version, OS.
```

`.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature request
about: Suggest a service, endpoint, or improvement
labels: enhancement
---

**Service / endpoint**
Tracker / Wiki / Forms / other — which capability is missing?
(Check `docs/api-coverage.md` — it may already be on the roadmap.)

**Use case**
What are you trying to automate?

**Surfaces needed:** SDK / CLI / MCP (reads ship to all three; writes to SDK + CLI).
```

- [ ] **Step 3: Write the PR template**

`.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## What

Brief description of the change.

## Checklist

- [ ] `uv run pytest` passes (coverage stays at 100%)
- [ ] Reads ship across SDK + CLI + MCP; writes across SDK + CLI only
- [ ] No MCP write tool added (server is read-only by design)
- [ ] No secrets / real org data committed
- [ ] Docs updated if behavior or coverage changed
```

- [ ] **Step 4: Write CHANGELOG.md**

```markdown
# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-06-27

### Added
- Initial release: Yandex 360 toolkit for **Tracker**, **Wiki**, and **Forms**.
- Four surfaces from one codebase: Typer **CLI** (`ycli`), FastMCP **server** (`ycli-mcp`,
  read-only), importable **Python SDK** (`ycli.yandex.*`), and a **Claude Code plugin**
  (`plugins/yandex-360/`).
- Test suite at 100% coverage with `responses`-stubbed HTTP.
```

- [ ] **Step 5: Verify all files are well-formed**

Run: `ls -la CONTRIBUTING.md CHANGELOG.md .github/ISSUE_TEMPLATE/ .github/PULL_REQUEST_TEMPLATE.md`
Expected: all five files present and non-empty.

- [ ] **Step 6: Commit**

```bash
git add CONTRIBUTING.md CHANGELOG.md .github/ISSUE_TEMPLATE/ .github/PULL_REQUEST_TEMPLATE.md
git commit -m "docs: add CONTRIBUTING, changelog, issue/PR templates"
```

---

### Task 5: README rewrite

**Files:**
- Modify: `README.md` (full rewrite)

**Interfaces:**
- Consumes: `docs/assets/demo.svg` (Task 3), CI badge URL (Task 2), CONTRIBUTING.md (Task 4), validated coverage matrix (spec appendix).
- Produces: the public landing page.

- [ ] **Step 1: Replace README.md with the full content below**

Write `README.md` exactly as follows (adjust the demo asset extension to whatever Task 3 produced — `.svg` or `.gif`):

````markdown
<div align="center">

# ycli

**One Yandex 360 toolkit — four ways to use it.**
Drive **Tracker**, **Wiki**, and **Forms** from a CLI, an MCP server, a Python SDK,
or a Claude Code plugin. Built for AI agents first — pleasant for humans too.

[![CI](https://img.shields.io/github/actions/workflow/status/bim-ba/ycli/ci.yml?branch=main&style=for-the-badge)](https://github.com/bim-ba/ycli/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=for-the-badge)](https://github.com/bim-ba/ycli)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-7c3aed?style=for-the-badge)](https://modelcontextprotocol.io/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-d97757?style=for-the-badge)](plugins/yandex-360/)

<img src="docs/assets/demo.svg" alt="ycli in action" width="760">

</div>

## Why ycli

- 🧩 **One SDK, four surfaces** — write logic once, use it as a CLI, an MCP server, a Python
  library, or a Claude Code plugin.
- 🤖 **Agent-native** — the MCP server exposes read-only `tracker_*`, `wiki_*`, `forms_*`
  tools so agents explore safely; writes stay in the CLI/SDK.
- 🛡️ **Trustworthy** — typed pydantic models, the real Yandex API quirks handled for you,
  and a test suite kept at **100% coverage**.
- ⚡ **Zero-friction start** — `uv sync`, two env vars, go.

## Quick start

Pick the surface that fits how you work.

<details open>
<summary><b>CLI</b></summary>

```bash
uv sync
uv run ycli --help
uv run ycli tracker issues get TRACKER-1
uv run ycli wiki pages get onboarding
```
</details>

<details>
<summary><b>MCP server</b> (read-only)</summary>

Run it over stdio:

```bash
uv run ycli-mcp
```

Point an MCP client at it (tools are namespaced `tracker_*`, `wiki_*`, `forms_*`):

```json
{
  "mcpServers": {
    "ycli": {
      "command": "uv",
      "args": ["run", "ycli-mcp"],
      "cwd": "/path/to/ycli",
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "...",
        "YANDEX_ID_ORGANIZATION_ID": "..."
      }
    }
  }
}
```
</details>

<details>
<summary><b>Python SDK</b></summary>

```python
from ycli.yandex.tracker.client import TrackerClient

tracker = TrackerClient.from_env()
issue = tracker.issues.get("TRACKER-1")
print(issue.summary)
```
</details>

<details>
<summary><b>Claude Code plugin</b></summary>

```
/plugin marketplace add bim-ba/ycli
/plugin install yandex-360@ycli
```

Teaches an agent to drive Yandex 360 through `ycli` — including the real API quirks.
See [`plugins/yandex-360/`](plugins/yandex-360/).
</details>

## Skills (Claude Code plugin)

| Skill | Use for |
|-------|---------|
| `yandex-360` | Entry point — install + auth, pick a surface (CLI/MCP/SDK), route to a domain |
| `yandex-360-tracker` | Issues, epics, comments, transitions, links, worklog, changelog |
| `yandex-360-wiki` | Wiki pages, page tree, comments, attachments, YFM authoring |
| `yandex-360-forms` | Forms, questions/schema, responses, pagination |

The skills encode the read/write commands **and** the gnarly Yandex API quirks
(epic-vs-parent, transition discovery, permanent wiki slugs, `fields=` rules, Forms
host/header traps, answers pagination).

## What's covered

Reads ship across **SDK + CLI + MCP**; writes across **SDK + CLI** only (the MCP server is
read-only by design).

### Tracker

| Resource | Operations | SDK | CLI | MCP |
|----------|-----------|:---:|:---:|:---:|
| issues | get · full · search · list · count | ✅ | ✅ | ✅ |
| issues | create · update | ✅ | ✅ | — |
| comments | list | ✅ | ✅ | ✅ |
| comments | add | ✅ | ✅ | — |
| links | list | ✅ | ✅ | ✅ |
| links | add | ✅ | ✅ | — |
| transitions | list | ✅ | ✅ | ✅ |
| transitions | execute | ✅ | ✅ | — |
| worklog · changelog · priorities · issuetypes · linktypes | list | ✅ | ✅ | ✅ |

### Wiki

| Resource | Operations | SDK | CLI | MCP |
|----------|-----------|:---:|:---:|:---:|
| pages | get · descendants | ✅ | ✅ | ✅ |
| pages | meta (metadata-only) | — | — | ✅ |
| pages | create · update | ✅ | ✅ | — |
| comments | list | ✅ | ✅ | ✅ |
| attachments | list | ✅ | ✅ | ✅ |

### Forms (read-only today)

| Resource | Operations | SDK | CLI | MCP |
|----------|-----------|:---:|:---:|:---:|
| me | get (whoami) | ✅ | ✅ | ✅ |
| surveys | list · get | ✅ | ✅ | ✅ |
| questions | list | ✅ | ✅ | ✅ |
| answers | list (drains all pages) | ✅ | ✅ | ✅ |

> **Mail and more — coming.** See [`docs/api-coverage.md`](docs/api-coverage.md) for the full
> gap analysis and prioritized roadmap.

## Configure

```bash
cp .env.example .env
```

```bash
YANDEX_ID_OAUTH_TOKEN=...        # get one at https://oauth.yandex.ru/
YANDEX_ID_ORGANIZATION_ID=...    # from the Yandex 360 admin panel
```

Header casing differs per service (Tracker `X-Org-ID`, Wiki/Forms `X-Org-Id`) — ycli
handles it for you.

## Project layout

```text
src/ycli/
├── cli.py              # root Typer CLI  → `ycli`
├── mcp.py              # root FastMCP server → `ycli-mcp` (read-only)
├── log.py              # central loguru config
└── yandex/
    ├── tracker/        # per-domain SDK …
    ├── wiki/           #   each resource group has:
    └── forms/          #   client.py · cli.py · mcp.py · models.py
plugins/yandex-360/     # distributable Claude Code plugin (skills + instructions)
docs/references/        # vendored Yandex API reference docs
```

## Development

```bash
uv sync
uv run pytest          # 100% coverage gate; HTTP stubbed with `responses` (no live network)
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions. Contributions welcome — the
[coverage roadmap](docs/api-coverage.md) is a good place to find a first issue.

## License

[MIT](LICENSE) © 2026 Sava Znatnov
````

- [ ] **Step 2: Verify links and the demo asset reference resolve**

Run: `grep -oE '\]\(([^)]+)\)' README.md | sed -E 's/\]\(|\)//g' | grep -vE '^https?:|^#' | while read p; do [ -e "$p" ] && echo "OK  $p" || echo "MISSING  $p"; done`
Expected: every local path prints `OK` (LICENSE, plugins/yandex-360/, docs/api-coverage.md, CONTRIBUTING.md, docs/assets/demo.svg, .env.example). Fix any `MISSING`.

- [ ] **Step 3: Verify every CLI command shown actually exists**

Run: `uv run ycli tracker issues --help >/dev/null && uv run ycli wiki pages --help >/dev/null && echo "commands exist"`
Expected: `commands exist` (confirms `tracker issues get` and `wiki pages get` are real).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: modern README — hero, quick-starts, coverage matrix, layout"
```

---

### Task 6: Repo metadata

**Files:**
- No repo files. Uses `gh` CLI against `bim-ba/ycli`.
- Create (only if social-preview rasterizer is unavailable): `docs/assets/social-preview.svg`

**Interfaces:**
- Consumes: nothing in-repo (runs after README so positioning is final).

- [ ] **Step 1: Set description + topics + homepage**

```bash
gh repo edit bim-ba/ycli \
  --description "Yandex 360 toolkit — Tracker, Wiki & Forms via CLI, MCP server, Python SDK & Claude Code plugin ✨" \
  --homepage "https://github.com/bim-ba/ycli#readme" \
  --add-topic yandex --add-topic yandex-360 --add-topic yandex-tracker \
  --add-topic yandex-wiki --add-topic yandex-forms --add-topic cli \
  --add-topic mcp --add-topic mcp-server --add-topic claude-code \
  --add-topic ai-agents --add-topic python --add-topic sdk \
  --add-topic typer --add-topic fastmcp
```

- [ ] **Step 2: Verify the metadata landed**

Run: `gh repo view bim-ba/ycli --json description,homepageUrl,repositoryTopics`
Expected: new description, homepage set, and all 14 topics present.

- [ ] **Step 3: Social preview image**

`gh`/the GitHub API **cannot** set the social-preview image — it must be uploaded via repo
**Settings → Social preview**. Prepare the asset:

- If a rasterizer is available (`rsvg-convert`, `resvg`, or ImageMagick `convert`): build a
  1280×640 SVG card (title `ycli`, tagline, four-surface icons) and rasterize to
  `docs/assets/social-preview.png`.
- Otherwise: commit `docs/assets/social-preview.svg` and tell the user to export+upload it
  manually (one-time, in Settings).

Commit whichever asset was produced:

```bash
git add docs/assets/social-preview.*
git commit -m "docs: add social preview card"
```

- [ ] **Step 4: Confirm CI is actually green before trusting the badge**

After pushing the branch/PR, run: `gh run list --repo bim-ba/ycli --workflow ci.yml --limit 1`
Expected: the latest run shows `completed / success`. Only then is the README CI badge truthful.

---

## Self-Review

**Spec coverage check** (against `docs/superpowers/specs/2026-06-27-repo-showcase-design.md`):
- README rewrite (Component 1) → Task 5 ✅ (hero, badges, 4 quick-starts, skills table, validated coverage matrix, folder map, install, dev, footer).
- Repo metadata (Component 2) → Task 6 ✅ (description, topics, social preview + manual-upload caveat).
- Demo visual (Component 3) → Task 3 ✅ (deterministic driver, light recorder, no data leak, fallback SVG).
- LICENSE (Component 4) → Task 1 ✅ (+ pyproject license field).
- Community files (Component 5) → Task 4 ✅ (CONTRIBUTING, issue/PR templates, CHANGELOG).
- CI (Component 6) → Task 2 ✅ (uv + pytest, py3.12/3.13, backs the badge).
- Truthfulness invariant → CI badge gated on a real run (Task 6 Step 4); coverage badge backed by the real gate; demo data baked & grepped for org id.
- Validated coverage matrix → embedded verbatim in Task 5.

**Placeholder scan:** no TBD/TODO; all file contents are complete; the only deliberately
deferred decision is the recorder tool (Task 3 Step 1) and rasterizer (Task 6 Step 3), both
with explicit fallbacks — not placeholders.

**Type/name consistency:** badge URLs, asset path (`docs/assets/demo.*`), workflow filename
(`ci.yml`), and owner/repo (`bim-ba/ycli`) are consistent across Tasks 2, 5, 6.

## Execution Handoff

Sequencing: Tasks 1, 2, 4 are independent; Task 3 is independent; Task 5 consumes 2/3/4;
Task 6 runs last. Tasks 1–4 may be parallelized; 5 then 6 are sequential.
