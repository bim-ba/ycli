# Track B — AI-infra hardening — Design

> Status: approved design, ready for an implementation plan.
> Companion to `docs/superpowers/specs/2026-06-27-architecture-guardrails-and-polish-design.md`
> (the five-track strategy). Track A shipped as v0.3.0; this is Track B.

## Goal

Harden the **agent + release workflow** so AI agents (and humans) cannot silently
reintroduce the two failures this project has actually hit — a `[skip ci]` token that
cancels the PyPI release, and secrets reaching a commit — and so the project's
conventions (release rules, skill/command authoring) live in versioned, discoverable
surfaces instead of personal memory. Same philosophy as Track A: prefer an executable
guard or an existing tool over prose alone.

## Scope

In scope this pass: **B1, B2, B3, B5**.

- **B4 (scoped Bash allowlist) — dropped** by decision: the blanket `"Bash"` grant in
  `.claude/settings.json` stays. Not worth the prompt friction.
- **B6 (extra plugin slash-commands, researcher subagent, drift-log seed) — deferred**
  to its own pass. The B3 conventions doc written here is the spec B6 will build against.

## Global constraints (every task inherits these)

- **No hand-edited dependency lists.** Runtime deps via `uv add`, dev deps via
  `uv add --dev`. Never hand-edit `pyproject.toml` `[project.dependencies]` /
  `[dependency-groups]`. (gitleaks/pre-commit are *not* Python deps — they are a
  pre-commit repo + a GitHub Action, so they do not go through `uv add`.)
- **No literal secrets anywhere.** Config and tests reference env vars as `${VAR}` /
  read from env; never embed a real `YANDEX_ID_OAUTH_TOKEN` value. Test fixtures for the
  skip-ci hook contain skip-ci strings only — **no** token-shaped strings (so gitleaks
  stays green and ARCH-5 is unaffected).
- **Architecture invariants hold.** Track A's checks (`tests/test_architecture.py`,
  `lint-imports`, `tests/test_snapshots.py`) must stay green. Track B touches `.claude/`,
  `docs/`, `plugins/`, CI, and pre-commit config — none of `src/ycli/` — so no surface
  snapshot changes are expected.
- **Conventional Commits.** Each task commits with a `feat:` / `fix:` / `docs:` / `chore:`
  prefix. The branch merges as **`feat:`** → minor bump to **v0.4.0**.
- **100% coverage gate stays green.** Coverage measures `source = ["ycli"]` only, so the
  out-of-package hook script does not enter the gate; the rest of the suite must remain at
  100%.
- **Branch → PR → explicit approval before merge.** No direct pushes to main.

## Items

### B1 — skip-ci PreToolUse hook (`.claude/hooks/git_guard.py`)

**Why custom:** no off-the-shelf tool blocks `[skip ci]` in a commit/merge message, and
the worst past incident was the token in a **squash-merge body** passed to `gh pr merge`
— a commit created on GitHub, never locally, so neither the Track A `no-skip-ci`
pre-commit hook nor gitleaks can see it. A Claude Code `PreToolUse` hook intercepts the
`gh`/`git` command *before it runs*, with a reason returned to the agent. This is the
third, earliest layer over (1) the prose rule in CLAUDE.md/memory and (2) the git-level
`no-skip-ci` pre-commit hook.

**Design:**

- Stdlib-only Python (no `uv`/third-party imports → fast cold start). Lives in repo
  `.claude/hooks/` — **not** bundled in the plugin (end users of the plugin are not
  releasing ycli).
- Pure decision function, easily unit-tested:

  ```python
  SKIP_CI_TOKENS = ("[skip ci]", "[ci skip]", "[no ci]", "[skip actions]", "[actions skip]")
  COMMIT_CMD_RE = re.compile(r"\bgit\s+(commit|merge)\b|\bgh\s+pr\s+(merge|create)\b")

  def decide(command: str) -> dict | None:
      """Return a PreToolUse deny payload, or None to allow."""
      if not COMMIT_CMD_RE.search(command):
          return None
      low = command.lower()
      if any(tok in low for tok in SKIP_CI_TOKENS):
          return _deny(
              "This git/gh command carries a skip-ci token "
              f"({', '.join(SKIP_CI_TOKENS)}). GitHub scans the whole commit/squash "
              "message and silently cancels the python-semantic-release run, so the "
              "PyPI release never ships. Remove the token from the message."
          )
      return None

  def _deny(reason: str) -> dict:
      return {"hookSpecificOutput": {
          "hookEventName": "PreToolUse",
          "permissionDecision": "deny",
          "permissionDecisionReason": reason,
      }}
  ```

- `main()` reads stdin JSON, extracts `tool_input.command` (default `""`), calls
  `decide`; on a deny payload it prints the JSON to stdout and exits `0`; otherwise exits
  `0` silently. (Exit-0 + `permissionDecision: "deny"` is the structured block; the reason
  is shown to the agent.)
- **Matcher scope:** only commands matching `COMMIT_CMD_RE` are ever denied, so a
  `rg "[skip ci]" docs/` search or a file edit is never blocked.

**Registration** — `.claude/settings.json`, add a `PreToolUse` entry **alongside** the
existing `Stop` hook (do not replace it):

```json
"PreToolUse": [
  {
    "matcher": "Bash",
    "hooks": [
      { "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/git_guard.py\"" }
    ]
  }
]
```

**Tests** — `tests/test_git_guard.py` (loads the module by path via `importlib`; the file
is outside the coverage source so it does not affect the 100% gate, but tests assert
correctness):

- `decide("git commit -m 'fix: x [skip ci]'")` → deny
- `decide("gh pr merge 7 --squash -b 'feat: y [ci skip]'")` → deny
- `decide("gh pr create -t z -b 'body [no ci]'")` → deny
- `decide("git commit -m 'FIX: case [SKIP CI]'")` → deny (case-insensitive)
- `decide("git commit -m 'fix: clean message'")` → None
- `decide("git log --oneline")` → None
- `decide("rg '[skip ci]' docs/")` → None (not a commit/merge command)
- One subprocess smoke test: pipe a deny-case JSON to `python3 .claude/hooks/git_guard.py`,
  assert exit `0` and stdout parses to a JSON payload with
  `hookSpecificOutput.permissionDecision == "deny"`; pipe an allow-case JSON, assert empty
  stdout.

### B2 — gitleaks secret scanning (pre-commit + CI)

**Why off-the-shelf:** gitleaks is the mature, maintained standard for secret detection;
reinventing it as a hook is exactly the kind of custom code to avoid. Secrets are a
*git-content* concern, so the natural layers are the existing pre-commit pipeline and CI —
not a Claude PreToolUse hook.

**Design:**

- Add to `.pre-commit-config.yaml` (alongside the Track A local hooks):

  ```yaml
    - repo: https://github.com/gitleaks/gitleaks
      rev: v8.24.2   # pin to the actual latest tag at implementation time
      hooks:
        - id: gitleaks
  ```

  Pin `rev` to whatever `gitleaks` tag is current at implementation (verify via
  `gh api repos/gitleaks/gitleaks/releases/latest`), not blindly to `v8.24.2`.

- Add a CI step to `.github/workflows/ci.yml` using `gitleaks/gitleaks-action@v2` with a
  full-history checkout (`fetch-depth: 0`) and `GITHUB_TOKEN`. Confirm at implementation
  that the action needs **no** `GITLEAKS_LICENSE` for this repo (free for personal/public
  repos; the license requirement is org-only). If licensing is a problem, fall back to
  running the gitleaks binary directly in a `run:` step (`gitleaks dir . --no-banner`).
- **Baseline triage (implementation step):** run gitleaks once over the repo before
  wiring it in. Expected clean — `.env`/`.mcp.json` are gitignored and `.env.example` /
  `.mcp.example.json` hold `${...}` placeholders. If gitleaks flags any committed fixture
  or example, resolve with a narrow `.gitleaksignore` entry or an inline `gitleaks:allow`
  comment, and note why. Do **not** broaden rules to silence a real finding.

No unit test (config + external tool); the pre-commit run and CI job are the verification.

### B3 — Documentation: release rules + skill/command conventions

Two deliverables.

**(a) Expand `CLAUDE.md`** with a `## Release & safety` section capturing rules currently
only in private memory / CONTRIBUTING:

- Auto-release: every push to `main` runs python-semantic-release → publishes to PyPI.
  Use Conventional Commits; the merge title becomes the release.
- **skip-ci footgun:** never place `[skip ci]` / `[ci skip]` / `[no ci]` anywhere in a
  commit **or squash-merge** message — GitHub scans the whole message and silently cancels
  the release. (Also blocked by the `git_guard` PreToolUse hook and the `no-skip-ci`
  pre-commit hook.)
- **Reproducible artifacts:** generated demos/tables come from a committed source —
  regenerate, never hand-author (the `demo.svg` incident).
- Flow: branch → PR → wait for explicit approval before merge.
- 100% coverage gate; new resources scaffolded via `/new-endpoint` respecting
  `ARCHITECTURE.md`.

Plus **freshness fixes** to the existing prose: mention the global `--format/-o`
(auto/json/yaml/pretty) output flag, the `ycli mcp` subcommand (`[mcp]` extra), and the
shipped `py.typed` (PEP 561) marker.

**(b) New `docs/conventions/skills-and-commands.md`** — naming standard **plus** an
authoring checklist, linked from `CLAUDE.md`. Contents:

- **Naming.** Plugin skills: `yandex-360` (umbrella) and `yandex-360-<domain>` per domain
  (`-tracker`, `-wiki`, `-forms`) — matches the existing tree. Repo slash-commands:
  kebab-case `verb-noun` (`new-endpoint`, `arch-review`). State the rule once and cite the
  existing names as the worked examples.
- **Frontmatter.** `SKILL.md` requires `name` + `description`; the description starts with
  "Use when …" and names the triggering situation. Command `.md` files require a
  `description` line.
- **Directory layout.** A skill dir = `SKILL.md` + optional `rules/NN-*.md` (always-loaded
  behavior, numbered) + `references/*.md` (on-demand lookups). When to use `rules/` vs
  `references/`.
- **Placement.** Repo-only developer tooling → `.claude/commands/` (e.g. `/new-endpoint`,
  `/arch-review`). User-facing domain capability → `plugins/yandex-360/skills/`.
- **Authoring checklist** (the template a new skill/command must satisfy): name follows the
  scheme; description is "Use when …"; frontmatter complete; correct placement
  (repo-command vs plugin-skill); `rules/` only for always-on behavior; referenced from the
  umbrella skill or CLAUDE.md where applicable.

Link the new doc from `CLAUDE.md` (e.g. in the conventions section). Prose only — no test.

### B5 — Bundle `plugins/yandex-360/.mcp.json`

Today every user hand-copies MCP JSON to use the read-only server; bundling it in the
plugin auto-wires the server on install.

**Design** — create `plugins/yandex-360/.mcp.json` at the plugin root:

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

- `uvx --from "yandex-cli[mcp]" ycli mcp` → reproducible, pulls the `[mcp]` extra, needs
  no global install (only `uv`). Chosen over a bare `ycli mcp` (PATH-dependent) and over a
  `${CLAUDE_PLUGIN_ROOT}/bin/...` path (the plugin ships no binary).
- Env vars passed **by reference** from the user's shell — never literal values. Document
  in the plugin README that `YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID` must be
  set in the user's environment, and that the server is read-only.

**Test** — `tests/test_plugin_mcp.py`: the file is valid JSON; declares a `yandex-360`
server; `command == "uvx"` with args including `yandex-cli[mcp]`, `ycli`, `mcp`; every
value under `env` is a `${...}` reference (no literal token, no value containing a digit
that looks like a real credential).

## Sequencing (for the plan)

On a `feat/track-b-ai-infra` branch, subagent-driven like Track A:

1. **B1** — `git_guard.py` + `tests/test_git_guard.py` + `.claude/settings.json`
   registration. (Self-contained; the hook governs the rest of the work too.)
2. **B2** — gitleaks in `.pre-commit-config.yaml` + CI step + baseline triage.
3. **B5** — `plugins/yandex-360/.mcp.json` + README note + `tests/test_plugin_mcp.py`.
4. **B3** — `CLAUDE.md` expansion + `docs/conventions/skills-and-commands.md` (docs last,
   so they describe the final state).

Then PR → review → merge as `feat:` → v0.4.0 → verify the PyPI release.

## Out of scope

- B4 (scoped Bash allowlist) — dropped.
- B6 (extra slash-commands, researcher subagent, drift-log seed) — deferred; will follow
  the conventions doc from B3.
- Any `src/ycli/` change — Track C owns feature/UX work.
