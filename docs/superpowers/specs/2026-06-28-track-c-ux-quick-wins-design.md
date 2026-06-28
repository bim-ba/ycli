# Track C — UX quick-wins — Design

> Status: approved design, ready for an implementation plan.
> Third track after A (architecture guardrails, v0.3.0) and B (AI-infra hardening, v0.4.0).
> Companion to `docs/superpowers/specs/2026-06-27-architecture-guardrails-and-polish-design.md`.

## Goal

A batch of user- and agent-facing quality wins across the CLI, the MCP server, and the SDK
— now that the guardrails (Track A) make feature work safe from silent drift. Every item
ships with a test (TDD) and respects the six ARCH invariants (HTTP only in `client.py`, CLI
output only via `ycli.output.render`, MCP read-only, four-surface symmetry, etc.).

## Scope

In scope: **C1, metadata enrichment, C3, C4, C5, C6** (the user chose the full batch). No
`C7` extras (`--format csv`, `--web`, `$PAGER`) this pass — deferred.

## Global constraints (every task inherits these)

- **No hand-edited dependency lists.** Runtime deps via `uv add`, dev via `uv add --dev`.
  (This track likely needs none — stdlib `difflib`, existing `rich`/`requests`/`fastmcp`.)
- **ARCH invariants hold** (`tests/test_architecture.py`, `lint-imports`, `tests/test_snapshots.py`):
  HTTP only in `client.py`; no `requests`/`uplink` in cli/mcp/models; `fastmcp` only in mcp;
  CLI output only via `render`; MCP tools read-only (verb in the allow-list + `readOnlyHint`);
  every resource dir has the five canonical files; `model_dump_json` only in `output.py`.
- **New resources via `/new-endpoint`.** The `myself` resource is scaffolded with
  `scripts/new_endpoint.py tracker myself`, then filled in — do not hand-build the five files.
- **Snapshots are intentional.** C1, the `myself` resource, and `auth status` change the CLI
  tree and/or MCP tool list; regenerate `tests/snapshots/` with
  `uv run python -m tests.snapshots --update` and treat the diff as a reviewed artifact (ARCH-6).
- **100% coverage stays green.** Every new branch ships with a test.
- **Conventional Commits.** Branch squash-merges as **`feat:`** → minor bump to **v0.5.0**.
- **Branch → PR → explicit approval before merge.** Never write a CI-skip token / `skip-checks`
  trailer in any commit or squash message.
- **Post-release chore:** after v0.5.0 publishes, run `uv lock` + a `build:` commit to resync
  the lockfile (PSR leaves it behind — see the memory `ycli-uvlock-drifts-after-each-release`).

## Items

### C6 — SDK typed exception hierarchy (retries already exist)

**Finding:** `transport.py` already mounts a `urllib3.Retry` (total=3, backoff, forcelist
`429/500/502/503/504`, GET/HEAD/OPTIONS only) and urllib3 honors `Retry-After` by default —
so the "transparent retries" half is **done**. The real gap: client docstrings say "raises on
non-2xx", but uplink does **not** raise — only `forms/answers/client.py` calls
`raise_for_status` manually; everywhere else a 401/404 parses error JSON into an empty/garbage
model with no error. C6 closes that.

**Design:**

- New `src/ycli/yandex/errors.py` — **pure** exception classes (no `requests`/`uplink` import,
  so cli/mcp may import them under ARCH-2):

  ```python
  class YandexError(Exception):
      """Base for all Yandex API errors. Carries the HTTP status and the response text."""
      def __init__(self, message: str, *, status: int | None = None, url: str | None = None) -> None:
          super().__init__(message)
          self.status = status
          self.url = url

  class YandexAuthError(YandexError): ...        # 401, 403
  class YandexNotFoundError(YandexError): ...    # 404
  class YandexRateLimitError(YandexError): ...   # 429 (after retries exhausted)
  class YandexServerError(YandexError): ...      # 5xx (after retries exhausted)
  class YandexClientError(YandexError): ...      # other 4xx
  ```

- `transport.py` gains a response hook installed on the session that maps a final non-2xx
  response to the right class and raises it (this keeps HTTP/`requests` knowledge in the
  transport boundary; `errors.py` stays import-pure). Status → class:
  `401/403 → YandexAuthError`, `404 → YandexNotFoundError`, `429 → YandexRateLimitError`,
  `5xx → YandexServerError`, other `4xx → YandexClientError`. The message includes the status,
  the request URL, and a trimmed snippet of the response body. The hook runs after retries
  (Retry has `raise_on_status=False`), so only the final response raises.

- Reconcile call sites: `issues/mcp.py` `get` keeps its empty-body `key is None` guard (covers a
  2xx-with-empty-body); the redundant manual `raise_for_status` in `forms/answers/client.py`
  is removed (the hook now covers it). Docstrings claiming "raises on non-2xx" become true.

- **CLI presentation:** the console entry wraps `app()` so an uncaught `YandexError` prints a
  one-line friendly message (`Error: <message>`) and exits non-zero, instead of a traceback.
  (MCP already surfaces raised exceptions as tool errors — no change needed there.)

**Tests:** unit-test the status→exception mapping with a stubbed `requests.Response` (or via
`responses`): 401→Auth, 404→NotFound, 429→RateLimit, 503→Server, 418→Client, 200→no raise.
A CLI test asserts a 404 prints the friendly line and exits non-zero (no traceback).

### Metadata enrichment (annotations + instructions + per-tool titles)

Our tools already return pydantic models, so FastMCP auto-generates output schemas +
`structuredContent` — that part is done. What's missing:

- **Annotations** — the shared `RO` dict in the three `src/ycli/yandex/<domain>/_deps.py`
  becomes `{"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}`. Accurate:
  every tool is an idempotent read that calls the external Yandex 360 API. (Keeps `readOnlyHint`,
  so ARCH-3's check still passes.)
- **Server `instructions`** — add an `instructions=` string to the root `FastMCP("yandex")`
  ([src/ycli/mcp.py](src/ycli/mcp.py)) and to each domain subserver
  (`<domain>/mcp.py`). Content: read-only nature; env auth (`YANDEX_ID_OAUTH_TOKEN` /
  `YANDEX_ID_ORGANIZATION_ID`); writes are CLI/SDK-only; per-domain navigation hints (Tracker
  queue/issue keys + TQL; Wiki permanent page slugs; Forms ids).
- **Per-tool `title`** — every `@mcp.tool` gets a human-friendly `title` via
  `annotations={**RO, "title": "<Title>"}` (FastMCP accepts a dict or `ToolAnnotations`).
  Titles are concise and hand-authored per tool (~23), e.g. `issues_get` → "Get Tracker issue",
  `pages_descendants` → "List Wiki page descendants". Because `RO` is shared and `title` is
  per-tool, each tool spreads `RO` and adds its own `title`.

**Tests:** extend the MCP surface assertions — every tool has `readOnlyHint=True`,
`idempotentHint=True`, `openWorldHint=True`, and a non-empty `title`; the root + domain servers
expose a non-empty `instructions`. Update `tests/snapshots/` if the snapshot records annotations
(verify scope; if it records only names + `readOnlyHint`, titles/instructions don't alter it —
but the new assertions live in `tests/test_*`, not only the snapshot).

### C1 — shell completion

Drop `add_completion=False` from the root `typer.Typer(...)` in
[src/ycli/cli.py](src/ycli/cli.py). Typer then exposes `--install-completion` /
`--show-completion` (bash/zsh/fish/pwsh). Regenerate the CLI-tree snapshot (it gains the
completion options) and confirm the diff is exactly those additions.

**Test:** the CLI-tree snapshot reflects completion; an `--install-completion --show-completion`
invocation does not error (a light integration check).

### C3 — `myself` resource + `ycli auth status`

**`myself` resource** (architecture-pure validation target), scaffolded via
`scripts/new_endpoint.py tracker myself`, then filled:

- `client.py` — `MyselfClient(TrackerResource)` with `get()` → `GET myself` → `Myself`.
- `models.py` — `Myself(BaseModel)` with the `/v3/myself` fields (e.g. `uid`, `login`,
  `display`, `email`, with aliases as the API returns them).
- `cli.py` — `ycli tracker myself` → `render(tracker_client(ctx).myself.get())`.
- `mcp.py` — tool `myself_get` (verb `get` is in the read allow-list), `annotations={**RO,
  "title": "Get current Tracker user"}`.
- Register: `self.myself = MyselfClient(session=session)` in `tracker/client.py`; `add_typer`
  in `tracker/cli.py`; `mcp.mount` in `tracker/mcp.py`.

**`ycli auth status`** — a root CLI command (sibling of `ycli mcp`, not a domain resource, so
ARCH-1's four-surface rule does not apply to it). It:

1. Reads the env vars; if either is missing, reports `not configured` (naming the missing var)
   and exits non-zero — without an API call.
2. Otherwise calls `TrackerClient.from_env().myself.get()` to validate, catching the C6 typed
   errors: `YandexAuthError` → "token invalid/expired"; other `YandexError` → "reachable but
   errored: <message>".
3. Renders an `AuthStatus` pydantic model (`configured: bool`, `org_id: str`, `valid: bool`,
   `login: str | None`, `display: str | None`) through `ycli.output.render` (ARCH-4). The
   `AuthStatus` model lives in the small `auth` CLI module (a BaseModel rendered via `render`;
   no `model_dump_json` outside `output.py`).

**Tests:** with `responses` stubbing `/v3/myself`: a 200 → `valid=True` + login/display; a 401
→ `valid=False` (caught `YandexAuthError`); missing env → `configured=False`, non-zero exit, no
HTTP call. Plus the `myself` resource's own client/cli/mcp tests, mirroring a sibling resource.

### C4 — "did you mean?" for unknown subcommands

When a user types an unknown subcommand, suggest the closest valid one via
`difflib.get_close_matches`. Implement at the Typer/Click group level (a small `TyperGroup`
subclass overriding `resolve_command` / `get_command` to raise a `UsageError` whose message
appends "Did you mean '<x>'?"). Applies to the root app and the domain sub-apps. Value-level
suggestions (bad queue names) are out of scope (they need a live queue list).

**Test:** invoking `ycli wiki pagez ...` (typo) exits with usage error text containing
"Did you mean 'pages'". A correct command is unaffected.

### C5 — OSC8 hyperlinks on Tracker keys (pretty tables, TTY-gated)

In [src/ycli/output.py](src/ycli/output.py), when rendering a **pretty** table on a **TTY**,
a cell in a column/field named `key` whose value matches `^[A-Z][A-Z0-9]*-\d+$` is wrapped in a
rich link: `[link=https://tracker.yandex.ru/<key>]<key>[/link]`. The link is added only in
`_kv_table` / `_list_table` where the field name is known (not in the generic `_cell`), and only
when `console.is_terminal` — piped/JSON/YAML output is untouched (stays a plain key). This is a
small, isolated bit of domain knowledge in the renderer; the alternative (models carrying link
metadata) is more invasive for a cosmetic win.

**Test:** rendering a model with a `key="ABC-1"` field to a forced-terminal `rich.Console`
emits the OSC8 escape / link markup for that cell; rendering with `is_terminal=False` (or
`--format json`) emits the bare key, no link.

## Sequencing (for the plan)

On a `feat/track-c-ux` branch, subagent-driven like A/B. Order chosen so foundations land first:

1. **C6** — `errors.py` + transport hook + CLI wrapper (foundational; `auth status` depends on it).
2. **Metadata** — `RO` annotations + server `instructions` + per-tool `title`s (mechanical, wide).
3. **C1** — shell completion + snapshot.
4. **myself resource** — via `/new-endpoint`, filled + registered + snapshot.
5. **C3** — `ycli auth status` (depends on `myself` + C6 errors).
6. **C4** — did-you-mean group.
7. **C5** — OSC8 in `output.py`.

Then PR → review → merge as `feat:` → v0.5.0 → verify PyPI → post-release `uv lock` chore.

## Out of scope

- C7 extras (`--format csv`, `--web`, `$PAGER`) — deferred.
- Value-level did-you-mean (queue names) — needs a live queue list.
- Any write capability on the MCP server (stays read-only).
- Track D (SEO) and Track E (LangChain/OpenAI schema export) — separate tracks.
