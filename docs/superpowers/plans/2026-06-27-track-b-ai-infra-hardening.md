# Track B — AI-infra Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make it impossible for an agent to silently reintroduce the two failures this project has hit (a `[skip ci]` token cancelling the PyPI release; secrets reaching a commit), and move the release/authoring conventions into versioned, discoverable surfaces.

**Architecture:** Four independent deliverables, each its own task: (B1) a stdlib-only Claude Code `PreToolUse` hook that denies skip-ci-carrying git/gh commands before they run; (B2) gitleaks wired into the existing pre-commit pipeline and CI; (B5) a bundled plugin `.mcp.json` that auto-wires the read-only MCP server; (B3) expanded `CLAUDE.md` plus a new skills/commands conventions doc. No `src/ycli/` code changes.

**Tech Stack:** Python 3.12+ stdlib (hook), pytest (`responses`-free unit + subprocess tests), pre-commit + gitleaks (secret scanning), GitHub Actions, Claude Code hooks/plugins, `uv`.

## Global Constraints

- No hand-edited `pyproject.toml` dependency lists — runtime deps via `uv add`, dev via `uv add --dev`. (gitleaks/pre-commit are a pre-commit repo + a GitHub Action, NOT Python deps — they do not go through `uv add`.)
- No literal secrets anywhere. Config/tests reference env vars as `${VAR}`. Skip-ci test fixtures contain skip-ci strings only — **no** token-shaped strings.
- Architecture invariants stay green: `uv run lint-imports`, `tests/test_architecture.py`, `tests/test_snapshots.py`. Track B touches `.claude/`, `docs/`, `plugins/`, CI, pre-commit config — none of `src/ycli/`, so no surface-snapshot changes are expected.
- Conventional Commits per task (`feat:`/`docs:`/`chore:`); the branch squash-merges as **`feat:`** → v0.4.0.
- 100% coverage gate stays green. Coverage measures `source = ["ycli"]` only, so `.claude/hooks/git_guard.py` (outside the package) does not enter the gate; the rest of the suite stays at 100%.
- Work on branch `feat/track-b-ai-infra` (already created). Branch → PR → explicit approval before merge. Never put a skip-ci token in any commit message.
- Pinned action versions in CI use `vX.Y.Z` tags (project convention), not SHAs or bare major tags.

---

### Task 1: B1 — skip-ci PreToolUse hook

**Files:**
- Create: `.claude/hooks/git_guard.py`
- Create: `tests/test_git_guard.py`
- Modify: `.claude/settings.json` (add a `PreToolUse` entry alongside the existing `Stop` hook)

**Interfaces:**
- Produces: `git_guard.decide(command: str) -> dict | None` — returns a PreToolUse deny payload `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": str}}` for a skip-ci-carrying `git commit`/`git merge`/`gh pr merge`/`gh pr create`, else `None`. And `git_guard.main()` — reads stdin JSON, writes the deny payload (if any) to stdout, exits 0.

- [ ] **Step 1: Write the failing test**

Create `tests/test_git_guard.py`:

```python
"""Tests for the skip-ci PreToolUse guard (.claude/hooks/git_guard.py).

The hook lives outside the ``ycli`` package (it is repo tooling, not shipped), so
it is loaded by path and is not measured by the coverage gate. These tests assert
its decision logic and its stdin->stdout/exit contract.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

_HOOK = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "git_guard.py"


def _load():
    spec = importlib.util.spec_from_file_location("git_guard", _HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


git_guard = _load()


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m 'fix: x [skip ci]'",
        "gh pr merge 7 --squash -b 'feat: y [ci skip]'",
        "gh pr create -t z -b 'body [no ci]'",
        "git commit -m 'FIX: case [SKIP CI]'",
        "git merge feature -m 'merge [skip actions]'",
    ],
)
def test_skip_ci_commands_are_denied(command):
    decision = git_guard.decide(command)
    assert decision is not None
    out = decision["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse"
    assert out["permissionDecision"] == "deny"
    assert "skip-ci" in out["permissionDecisionReason"]


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m 'fix: clean message'",
        "git log --oneline",
        "rg '[skip ci]' docs/",
        "echo '[skip ci]' > note.txt",
    ],
)
def test_safe_commands_are_allowed(command):
    assert git_guard.decide(command) is None


def test_subprocess_contract_deny():
    payload = {"tool_name": "Bash", "tool_input": {"command": "git commit -m 'x [skip ci]'"}}
    proc = subprocess.run(
        [sys.executable, str(_HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_subprocess_contract_allow():
    payload = {"tool_name": "Bash", "tool_input": {"command": "git status"}}
    proc = subprocess.run(
        [sys.executable, str(_HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_git_guard.py -q --no-cov`
Expected: FAIL/ERROR — `.claude/hooks/git_guard.py` does not exist (import/exec error at collection).

- [ ] **Step 3: Write the hook**

Create `.claude/hooks/git_guard.py`:

```python
"""PreToolUse guard: deny git/gh commands that carry a skip-ci token.

GitHub scans the entire commit (and squash-merge) message for [skip ci] / [ci skip]
/ [no ci] and silently cancels the workflow run — which cancels the
python-semantic-release publish, so the PyPI release never ships. This hook denies
such a command before it runs. Skip-ci has no off-the-shelf scanner, and the
squash-merge body never produces a local commit, so neither gitleaks nor the
no-skip-ci pre-commit hook can catch that path — only a PreToolUse block can.

Stdlib only (fast cold start). Registered on PreToolUse with matcher "Bash".
"""
import json
import re
import sys

SKIP_CI_TOKENS = (
    "[skip ci]",
    "[ci skip]",
    "[no ci]",
    "[skip actions]",
    "[actions skip]",
)
COMMIT_CMD_RE = re.compile(r"\bgit\s+(?:commit|merge)\b|\bgh\s+pr\s+(?:merge|create)\b")


def _deny(reason: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def decide(command: str) -> dict | None:
    """Return a PreToolUse deny payload for a skip-ci commit/merge, else None."""
    if not COMMIT_CMD_RE.search(command):
        return None
    low = command.lower()
    if any(token in low for token in SKIP_CI_TOKENS):
        return _deny(
            "This git/gh command carries a skip-ci token "
            f"({', '.join(SKIP_CI_TOKENS)}). GitHub scans the whole commit/squash "
            "message and silently cancels the python-semantic-release run, so the "
            "PyPI release never ships. Remove the token from the message."
        )
    return None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    command = payload.get("tool_input", {}).get("command", "")
    decision = decide(command)
    if decision is not None:
        json.dump(decision, sys.stdout)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_git_guard.py -q --no-cov`
Expected: PASS — 11 cases (5 deny + 4 allow parametrized, + 2 subprocess).

- [ ] **Step 5: Register the hook in settings**

Modify `.claude/settings.json` — add a top-level `PreToolUse` array inside the existing `"hooks"` object (which currently holds only `"Stop"`); keep `Stop` unchanged. The `"hooks"` object becomes:

```json
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/git_guard.py\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$CLAUDE_PROJECT_DIR\" && uv run lint-imports >/dev/null 2>&1 && uv run pytest tests/test_architecture.py tests/test_snapshots.py -q --no-cov >/dev/null 2>&1 || echo '⚠️ architecture guardrails failing — run: uv run pytest tests/test_architecture.py tests/test_snapshots.py --no-cov && uv run lint-imports'"
          }
        ]
      }
    ]
  }
```

- [ ] **Step 6: Verify settings JSON is valid**

Run: `uv run python -c "import json,pathlib; json.loads(pathlib.Path('.claude/settings.json').read_text()); print('ok')"`
Expected: `ok`

- [ ] **Step 7: Run the full suite to confirm nothing else broke**

Run: `uv run pytest -q`
Expected: PASS, coverage 100% (the new hook is outside `source = ["ycli"]`, the new test file is collected and green).

- [ ] **Step 8: Commit**

```bash
git add .claude/hooks/git_guard.py tests/test_git_guard.py .claude/settings.json
git commit -m "feat: block skip-ci tokens before commit via PreToolUse hook"
```

---

### Task 2: B2 — gitleaks secret scanning (pre-commit + CI)

**Files:**
- Modify: `.pre-commit-config.yaml` (append a gitleaks repo block)
- Modify: `.github/workflows/ci.yml` (add a `gitleaks` job)

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: a `gitleaks` pre-commit hook id and a CI `gitleaks` job. No Python symbols.

- [ ] **Step 1: Confirm the gitleaks + action versions to pin**

Run: `gh api repos/gitleaks/gitleaks/releases/latest --jq .tag_name` (expected `v8.30.1` or newer) and `gh api repos/gitleaks/gitleaks-action/releases/latest --jq .tag_name` (a `v2.x.y` tag, e.g. `v2.3.9`).
Use the actual returned tags in the steps below — `v8.30.1` and the latest `gitleaks-action` `v2.x.y` are the values to use unless `gh` returns newer ones.

- [ ] **Step 2: Add gitleaks to the pre-commit config**

Modify `.pre-commit-config.yaml` — append this block as a new top-level entry under `repos:` (after the existing `- repo: local` block; same indentation as it):

```yaml
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
```

(Use the tag from Step 1 if newer than `v8.30.1`.)

- [ ] **Step 3: Run the baseline scan**

Run: `uv run pre-commit run gitleaks --all-files`
Expected: PASS (`Passed`). The repo's secrets live in gitignored `.env`/`.mcp.json`; `.env.example`/`.mcp.example.json` hold `${...}` placeholders; the Task 1 fixtures carry no tokens.
If gitleaks reports a finding on a committed fixture/example (a false positive), add a narrow entry to a new `.gitleaksignore` file (one `<commit-sha>:<path>:<rule>:<line>` fingerprint per line, copied from the gitleaks output) OR an inline `gitleaks:allow` comment on the offending line, and note which in the commit body. Do NOT broaden rules to silence a real secret — if it is real, stop and report it.

- [ ] **Step 4: Add the CI job**

Modify `.github/workflows/ci.yml` — add a second job `gitleaks` under `jobs:` (sibling of `test`, same indentation):

```yaml
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.0
        with:
          fetch-depth: 0
      - name: Scan for secrets
        uses: gitleaks/gitleaks-action@v2.3.9
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

(Use the `gitleaks-action` tag from Step 1. `fetch-depth: 0` gives gitleaks the full history to scan. No `GITLEAKS_LICENSE` is needed — that is required only for organization accounts, and this is a personal/public repo. The top-level `permissions: contents: read` already in the file covers this job.)

- [ ] **Step 5: Verify the workflow YAML parses**

Run: `uv run python -c "import yaml,pathlib; yaml.safe_load(pathlib.Path('.github/workflows/ci.yml').read_text()); print('ok')"`
Expected: `ok` (PyYAML is a runtime dependency, already installed).

- [ ] **Step 6: Confirm the full suite still passes**

Run: `uv run pytest -q`
Expected: PASS, 100% coverage (no code changed; this is a guard against accidental edits).

- [ ] **Step 7: Commit**

```bash
git add .pre-commit-config.yaml .github/workflows/ci.yml
git add .gitleaksignore 2>/dev/null || true
git commit -m "chore: scan for secrets with gitleaks in pre-commit and CI"
```

---

### Task 3: B5 — bundle the plugin MCP config

**Files:**
- Create: `plugins/yandex-360/.mcp.json`
- Create: `tests/test_plugin_mcp.py`
- Modify: `plugins/yandex-360/README.md` (document the auto-wired server)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `plugins/yandex-360/.mcp.json` declaring an `mcpServers["yandex-360"]` entry with `command == "uvx"`, `args == ["--from", "yandex-cli[mcp]", "ycli", "mcp"]`, and an `env` mapping whose values are all `${...}` references.

- [ ] **Step 1: Write the failing test**

Create `tests/test_plugin_mcp.py`:

```python
"""The bundled plugin MCP config auto-wires the read-only server without leaking secrets.

Installing the yandex-360 plugin should register the MCP server with no hand-copied
JSON. This locks the command form and guarantees credentials are passed by env-var
reference, never as literal values.
"""
from __future__ import annotations

import json
from pathlib import Path

_MCP = Path(__file__).resolve().parent.parent / "plugins" / "yandex-360" / ".mcp.json"


def test_plugin_mcp_declares_readonly_server():
    config = json.loads(_MCP.read_text(encoding="utf-8"))
    servers = config["mcpServers"]
    assert "yandex-360" in servers
    server = servers["yandex-360"]
    assert server["command"] == "uvx"
    assert server["args"] == ["--from", "yandex-cli[mcp]", "ycli", "mcp"]


def test_plugin_mcp_passes_secrets_by_reference():
    config = json.loads(_MCP.read_text(encoding="utf-8"))
    env = config["mcpServers"]["yandex-360"]["env"]
    assert set(env) == {"YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID"}
    for value in env.values():
        assert value.startswith("${") and value.endswith("}")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_plugin_mcp.py -q --no-cov`
Expected: FAIL — `plugins/yandex-360/.mcp.json` does not exist (`FileNotFoundError`).

- [ ] **Step 3: Create the bundled config**

Create `plugins/yandex-360/.mcp.json`:

```json
{
  "mcpServers": {
    "yandex-360": {
      "command": "uvx",
      "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp"],
      "env": {
        "YANDEX_ID_OAUTH_TOKEN": "${YANDEX_ID_OAUTH_TOKEN}",
        "YANDEX_ID_ORGANIZATION_ID": "${YANDEX_ID_ORGANIZATION_ID}"
      }
    }
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_plugin_mcp.py -q --no-cov`
Expected: PASS (2 tests).

- [ ] **Step 5: Document it in the plugin README**

Modify `plugins/yandex-360/README.md` — replace the final `## Requires` section with the following (keeps the requirement text, adds the auto-wiring note):

```markdown
## MCP server (auto-wired)

This plugin bundles `.mcp.json`, so installing it registers the **read-only** Yandex 360
MCP server automatically — no hand-copied config. The server launches via
`uvx --from "yandex-cli[mcp]" ycli mcp`, so you need [`uv`](https://docs.astral.sh/uv/)
on `PATH` but no global `ycli` install. Writes stay on the CLI/SDK; the MCP surface is
read-only.

## Requires

[`uv`](https://docs.astral.sh/uv/) on `PATH` (for the bundled MCP server) and two
environment variables, read from your shell: `YANDEX_ID_OAUTH_TOKEN`,
`YANDEX_ID_ORGANIZATION_ID`. The `yandex-360` skill walks through setup. For direct CLI/SDK
use, install the package with `uv add 'yandex-cli[mcp]'`.
```

- [ ] **Step 6: Run the full suite**

Run: `uv run pytest -q`
Expected: PASS, 100% coverage.

- [ ] **Step 7: Commit**

```bash
git add plugins/yandex-360/.mcp.json plugins/yandex-360/README.md tests/test_plugin_mcp.py
git commit -m "feat: auto-wire read-only MCP server via bundled plugin .mcp.json"
```

---

### Task 4: B3 — release/safety rules + skills/commands conventions

**Files:**
- Modify: `CLAUDE.md` (add `## Release & safety`; freshness fixes; link the new doc)
- Create: `docs/conventions/skills-and-commands.md`

**Interfaces:**
- Consumes: the deliverables of Tasks 1–3 (the hook, gitleaks, the bundled MCP) are referenced by name in the prose.
- Produces: documentation only — no code symbols.

- [ ] **Step 1: Create the conventions doc**

Create `docs/conventions/skills-and-commands.md`:

```markdown
# Skills & commands conventions

How to name and author Claude Code skills (shipped in the `yandex-360` plugin) and
slash-commands (repo-local, under `.claude/commands/`). New skills/commands MUST follow
this; it is the spec the architecture review and any future authoring pass check against.

## Naming

- **Plugin skills** live in `plugins/yandex-360/skills/<name>/SKILL.md`. Names are
  `yandex-360` (the umbrella entry point) and `yandex-360-<domain>` per service —
  `yandex-360-tracker`, `yandex-360-wiki`, `yandex-360-forms`. A new domain skill follows
  the same `yandex-360-<domain>` pattern.
- **Repo slash-commands** live in `.claude/commands/<name>.md`. Names are kebab-case
  `verb-noun` — the existing `/new-endpoint` and `/arch-review` are the worked examples. A
  new command names the action first (`generate-…`, `check-…`, `review-…`).

## Frontmatter

- `SKILL.md` requires YAML frontmatter with `name` and `description`. The `description`
  starts with "Use when …" and names the triggering situation, so the agent can match it
  (e.g. "Use when creating, reading, or transitioning Yandex Tracker issues …").
- A slash-command `.md` requires a `description:` frontmatter line — one sentence, present
  tense, stating what the command does (see `.claude/commands/arch-review.md`).

## Directory layout (skills)

A skill directory contains:

- `SKILL.md` — the entry point (always loaded when the skill activates).
- `rules/NN-*.md` (optional) — **always-on** behavior, numbered for order
  (`01-workflow.md`). Use `rules/` only for guidance the agent must follow every time the
  skill is active.
- `references/*.md` (optional) — **on-demand** lookups the agent reads when it needs them
  (quick-reference tables, API quirk catalogues). Use `references/` for material that is
  too large or situational to always load.

Rule of thumb: if the agent must obey it on every task, it is a `rule`; if it looks it up
when relevant, it is a `reference`.

## Placement

- Repo-only developer tooling (generators, review gates) → `.claude/commands/`. These are
  not distributed with the plugin.
- User-facing domain capability (driving Tracker/Wiki/Forms) → `plugins/yandex-360/skills/`.

## Authoring checklist

Before committing a new skill or command, confirm:

- [ ] Name follows the scheme above (`yandex-360-<domain>` skill, or kebab `verb-noun` command).
- [ ] Frontmatter is complete; the description starts with "Use when …" (skills) or states the action (commands).
- [ ] It is in the correct place (repo command vs plugin skill).
- [ ] `rules/` holds only always-on behavior; situational material is in `references/`.
- [ ] A new plugin skill is listed in the plugin README's skills table and routed from the `yandex-360` umbrella skill where relevant.
```

- [ ] **Step 2: Expand CLAUDE.md with the Release & safety section**

Modify `CLAUDE.md` — insert a new section immediately after the `## Project-Specific Conventions` section (before `## Architecture invariants (enforced)`):

```markdown
## Release & safety

- **Auto-release on push to main.** Every push to `main` runs python-semantic-release,
  which versions from Conventional Commits and publishes to PyPI. Use `feat:` / `fix:` /
  `docs:` / `chore:` … prefixes; the squash-merge title becomes the release.
- **Never write a skip-ci token.** `[skip ci]` / `[ci skip]` / `[no ci]` anywhere in a
  commit **or squash-merge** message makes GitHub silently cancel the workflow run — and
  with it the release. This is enforced three ways: the `git_guard` PreToolUse hook
  (`.claude/hooks/`), the `no-skip-ci` pre-commit hook, and this rule.
- **Secrets never reach a commit.** gitleaks runs in pre-commit and CI. Credentials come
  from the env (`YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID`); `.env` / `.mcp.json`
  are gitignored. Config and tests reference `${VAR}`, never literal values.
- **Reproducible artifacts.** Generated demos/tables come from a committed source —
  regenerate, never hand-author (the `demo.svg` incident).
- **Branch → PR → explicit approval before merge.** No direct pushes to `main`.
- **100% coverage gate.** `uv run pytest` enforces `--cov-fail-under=100`; new code ships
  with tests that keep it green.
- **New resources via `/new-endpoint`**, respecting the six invariants in
  [`ARCHITECTURE.md`](ARCHITECTURE.md). Authoring skills/commands follows
  [`docs/conventions/skills-and-commands.md`](docs/conventions/skills-and-commands.md).
```

- [ ] **Step 3: Apply the freshness fixes to CLAUDE.md**

Modify the `## Project Overview` bullet list in `CLAUDE.md`. Append these two bullets to the existing list under Project Overview (after the **Layout** bullet):

```markdown
- **Output:** every CLI command honors a global `--format/-o` flag (`auto` · `json` · `yaml`
  · `pretty`); rendering goes through `ycli.output.render` (ARCH-4).
- **Typing:** the package ships a PEP 561 `py.typed` marker, so downstream type checkers
  see ycli's types. The MCP server is the `ycli mcp` subcommand (optional `[mcp]` extra).
```

- [ ] **Step 4: Verify the docs render and links resolve**

Run:
```bash
test -f docs/conventions/skills-and-commands.md && \
grep -q "skills-and-commands.md" CLAUDE.md && \
grep -q "Release & safety" CLAUDE.md && \
grep -q "py.typed" CLAUDE.md && echo ok
```
Expected: `ok`

- [ ] **Step 5: Run the full suite (guards against accidental code edits)**

Run: `uv run pytest -q`
Expected: PASS, 100% coverage.

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md docs/conventions/skills-and-commands.md
git commit -m "docs: codify release/safety rules and skills/commands conventions"
```

---

## Final verification (after all tasks)

- [ ] Full suite: `uv run pytest -q` → PASS, 100% coverage.
- [ ] Architecture intact: `uv run lint-imports` → clean; `uv run pytest tests/test_architecture.py tests/test_snapshots.py -q --no-cov` → PASS.
- [ ] Secret scan clean: `uv run pre-commit run gitleaks --all-files` → Passed.
- [ ] Hook live: `echo '{"tool_input":{"command":"git commit -m \"x [skip ci]\""}}' | python3 .claude/hooks/git_guard.py` → prints a deny payload.
- [ ] Then: PR → review → merge as `feat:` → verify v0.4.0 ships to PyPI.

## Spec coverage map

- B1 → Task 1. B2 → Task 2. B5 → Task 3. B3 (CLAUDE.md + conventions doc) → Task 4.
- B4 dropped, B6 deferred (per spec "Out of scope").
