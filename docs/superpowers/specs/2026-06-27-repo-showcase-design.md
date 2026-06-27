# Design: ycli repository showcase

**Date:** 2026-06-27
**Goal:** Make the public `bim-ba/ycli` GitHub repo look modern and inviting, lower the
barrier to entry, and improve discoverability ("охваты") — without misrepresenting the
project (no fake badges, no leaked data).

## Decisions (locked)

| Topic | Decision |
|-------|----------|
| README language | **English** (single README.md) |
| Scope | README rework · repo metadata · demo visual · community files · CI |
| License | **MIT**, `Copyright (c) 2026 Sava Znatnov` |
| Demo render | **Light SVG** via `agg` (asciinema→gif) or `termtosvg` — no `ttyd`/`vhs` |
| CI | **Yes** — GitHub Actions (uv + pytest + coverage gate) for a real green badge |

## Success criteria

1. A newcomer can pick their surface (CLI / MCP / SDK / plugin) and copy-paste a working
   first command within ~30 seconds of landing on the README.
2. Every badge and claim is **truthful** (CI badge backed by a real workflow; coverage
   reflects the real 100% gate already in `pyproject.toml`).
3. The repo is discoverable: keyword-rich description + topics so GitHub search and link
   unfurls surface it.
4. No real Yandex org data leaks into any committed artifact (demo uses baked/safe output).

## Non-goals (YAGNI)

- No separate docs website / GitHub Pages.
- No CODE_OF_CONDUCT (keep community surface lean; can add later).
- No logo commission — a simple text/emoji hero + terminal SVG is enough.
- No changes to `src/` behavior. This is presentation + metadata only.

---

## Component 1 — README.md (rewrite, English)

Section order, each scaled to its weight:

1. **Hero** — H1 title, one-line tagline, badge row, demo SVG immediately under it.
2. **Pitch** — "One SDK, four surfaces": CLI · MCP server · Python SDK · Claude Code plugin
   (short bullet list with emoji icons).
3. **Quick start** — one copy-paste block **per pattern**, each independently runnable:
   - **CLI** — `uv sync` → `uv run ycli tracker issues get TRACKER-1`
   - **MCP** — `uv run ycli-mcp`; collapsible `<details>` with a sample MCP-client JSON
     config (read-only server note).
   - **SDK** — `from ycli.yandex.tracker.client import TrackerClient` short snippet.
   - **Plugin** — `/plugin marketplace add bim-ba/ycli` → `/plugin install yandex-360@ycli`.
4. **Skills table** — surface the 4 plugin skills (`yandex-360`, `-tracker`, `-wiki`,
   `-forms`) with "use for" column (mirrors `plugins/yandex-360/README.md`).
5. **Service coverage matrix** — Tracker / Wiki / Forms × capability groups, with a
   "Mail and more — coming" row. Data is **source-validated** (see appendix); use those
   exact operations/surfaces — do not paraphrase from `docs/api-coverage.md` alone.
6. **Architecture / folder map** — annotated tree (fenced block) explaining each top-level
   path and the per-domain `client.py`/`cli.py`/`mcp.py`/`models.py` pattern.
7. **Install & Configure** — `uv sync`; the two env vars; link to
   `https://oauth.yandex.ru/` for the token; note header-casing is handled for you.
8. **Development** — `uv run pytest`; mention 100% coverage gate and `@pytest.mark.integration`.
9. **Footer** — Roadmap (Mail, more services), Contributing link, License.

### Badges (truthful only)

`for-the-badge` flat style, Yandex-leaning accent color:

- CI — `github/actions/workflow/status` (from Component 6 workflow)
- Coverage — static `100%` (backed by the real `--cov-fail-under=100` gate)
- Python — `3.12+`
- License — `MIT`
- MCP — "MCP compatible"
- Claude Code — "plugin"
- PRs welcome

No "build passing" badge exists until the CI workflow is committed — order the work so the
badge is added in the same change as the workflow.

## Component 2 — Repo metadata (via `gh repo edit`)

- **description** → keyword-rich + one emoji, e.g.
  `Yandex 360 toolkit — Tracker, Wiki & Forms via CLI, MCP server, Python SDK & Claude Code plugin ✨`
- **topics** → `yandex yandex-360 yandex-tracker yandex-wiki yandex-forms cli mcp
  mcp-server claude-code ai-agents python sdk typer fastmcp`
- **social preview** (1280×640 OG image) — improves Telegram/Slack/Twitter unfurls.
  Produced as an SVG card; rasterized to PNG only if a rasterizer (`rsvg-convert`/
  ImageMagick/`resvg`) is available. If none is available, commit the SVG under
  `docs/assets/` and note that the PNG must be uploaded manually via repo Settings
  (the social-preview image cannot be set through the `gh` CLI/API).

## Component 3 — Demo visual

- Driver script: a small, deterministic demo sequence. Real, no-creds commands
  (`ycli --help`, `ycli tracker --help`) are run live; data commands print **baked safe
  output** from a fixture (no network, no real org data).
- Record with `asciinema` → render to GIF with `agg`, **or** record directly to animated
  SVG with `termtosvg`. Tools installed on demand (`uv tool install` / `cargo`/release
  binary) — chosen at implementation time, justified inline; prefer whichever installs
  cleanest without `ttyd`.
- Output committed under `docs/assets/demo.svg` (or `.gif`) and referenced from the README
  hero. The `.tape`/`.cast` source + driver script committed alongside for reproducibility.

## Component 4 — LICENSE

Standard MIT text, `Copyright (c) 2026 Sava Znatnov`. Also set `license = "MIT"` /
classifier in `pyproject.toml` so the package metadata matches.

## Component 5 — Community files

- `CONTRIBUTING.md` — dev setup (`uv sync`), test command, the project conventions that
  matter to outside contributors (uv-managed deps, 100% coverage gate, integration marker,
  MCP-server-is-read-only, header-casing, secrets hygiene). Distilled from `CLAUDE.md` —
  not a copy.
- `.github/ISSUE_TEMPLATE/bug_report.md` and `feature_request.md`.
- `.github/PULL_REQUEST_TEMPLATE.md`.
- `CHANGELOG.md` — Keep a Changelog format, seeded with `0.1.0`.

## Component 6 — CI workflow

`.github/workflows/ci.yml`:

- Triggers: `push` + `pull_request`.
- Uses `astral-sh/setup-uv` + `uv sync` + `uv run pytest`.
- The existing `--cov-fail-under=100` gate makes the job fail if coverage regresses.
- Matrix on Python 3.12 / 3.13 (both supported per `requires-python >=3.12`).
- Its status URL backs the CI badge in the README.

---

## Sequencing / dependencies

1. LICENSE + `pyproject.toml` license field (no deps).
2. CI workflow (must land with/before the CI badge).
3. Demo asset (tool install + record) — independent, can run in parallel with 1–2.
4. README rewrite (consumes the demo asset path + CI badge URL).
5. Community files (independent).
6. Repo metadata via `gh` (description + topics immediately; social-preview PNG may be
   manual). Done last so the description can reference the final positioning.

## Risks / open items

- **Rasterizer for social preview** may be absent → fall back to committing the SVG and a
  one-line manual upload instruction. (Confirmed: `gh` cannot set social preview.)
- **Demo tooling install** (`agg`/`termtosvg`/`asciinema`) — pick the lightest that works in
  this environment; if all fail, fall back to a hand-authored static terminal SVG card.
- All changes are presentation/metadata only; no risk to `src/` or tests.

## Verification

- `uv run pytest` still green (unchanged source).
- README links/anchors resolve; badge URLs return images.
- `gh repo view --json description,repositoryTopics` shows the new metadata.
- No real org data in committed demo artifacts (grep the fixture/cast for org id / token).
- CI workflow passes on a pushed branch before claiming the badge is real.

---

## Appendix — validated coverage matrix (source-audited 2026-06-27)

Validated by per-service source audit of `src/ycli/yandex/**` (3 parallel agents), confirming
the `docs/api-coverage.md` "Covered" claims. MCP is read-only by design — writes are SDK+CLI
only, which is correct, not a gap. Two refinements found where source has **more** than the
prior doc stated (marked ⁺). Use this table verbatim for the README matrix.

### Tracker

| Resource | Operations | SDK | CLI | MCP |
|----------|-----------|-----|-----|-----|
| issues | get, full (raw), search, list⁺, count | ✅ | ✅ | ✅ |
| issues | create, update | ✅ | ✅ | — (write) |
| comments | list | ✅ | ✅ | ✅ |
| comments | add | ✅ | ✅ | — (write) |
| links | list | ✅ | ✅ | ✅ |
| links | add | ✅ | ✅ | — (write) |
| transitions | list | ✅ | ✅ | ✅ |
| transitions | execute | ✅ | ✅ | — (write) |
| worklog | list | ✅ | ✅ | ✅ |
| changelog | list | ✅ | ✅ | ✅ |
| priorities | list | ✅ | ✅ | ✅ |
| issuetypes | list | ✅ | ✅ | ✅ |
| linktypes | list | ✅ | ✅ | ✅ |

⁺ `issues list` (filter-based) exists in source though not named in the prior doc's claim.

### Wiki

| Resource | Operations | SDK | CLI | MCP |
|----------|-----------|-----|-----|-----|
| pages | get (by slug), descendants | ✅ | ✅ | ✅ |
| pages | meta⁺ (metadata-only read) | — | — | ✅ only |
| pages | create, update | ✅ | ✅ | — (write) |
| comments | list | ✅ | ✅ | ✅ |
| attachments | list | ✅ | ✅ | ✅ |

⁺ MCP splits reads into `pages_get` (content) and `pages_meta` (metadata).

### Forms (read-only today)

| Resource | Operations | SDK | CLI | MCP |
|----------|-----------|-----|-----|-----|
| me | get (whoami) | ✅ | ✅ | ✅ |
| surveys | list, get | ✅ | ✅ | ✅ |
| questions | list | ✅ | ✅ | ✅ |
| answers | list (paginated, drains all pages) | ✅ | ✅ | ✅ |

Note: SDK exposes raw single-page `answers.list()`; CLI/MCP intentionally expose only the
paginated `list_all()` (follows `next.next_url`). No write operations yet (by design).
