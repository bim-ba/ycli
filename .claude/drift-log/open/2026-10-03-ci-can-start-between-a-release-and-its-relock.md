---
date: 2026-10-03
status: OPEN
priority: MEDIUM
trigger: [8]
session_context: closing milestone E3 (#104-#108, #119, #145) with seven PRs merged in one evening, each triggering an automatic release

affected_source:
  - CLAUDE.md
  - .github/workflows/release.yml
---

## What diverged

CLAUDE.md says a stale `uv.lock` after a release blocks every merge and that the release
workflow's gated "Re-lock and commit uv.lock" step prevents it. During E3 a PR's CI started
in the window between the release commit (`0.35.0`, version bumped in `pyproject.toml`) and the
`build: re-lock uv.lock for 0.35.0` commit that followed it a few seconds later. GitHub tested
the PR merged onto the intermediate `main`, `uv sync --locked` failed on every matrix leg and on
`live`, and the PR looked broken although nothing in it was. Rebasing after the re-lock landed
turned it green.

## Why it seemed better

The generic failure: any check that reads a base branch while a two-commit update is half
applied sees a tree that never existed as a whole. Here it is CI on a PR; the same window reaches
a local `git pull && uv sync --locked` and a Dependabot or Renovate rebase. Recognising the
window (base at a bare `X.Y.Z` commit, lock error only) avoids debugging a red run that the PR did
not cause.

## Proposed change

1. CLAUDE.md, Release & safety: one line — "A PR whose CI fails only at `uv sync --locked` with
   its base at a bare `X.Y.Z` release commit raced the re-lock: rebase onto `main` once the
   `build: re-lock` commit lands; do not change the lock in the PR."
2. Removing the window: make the version bump and the lock one commit. PSR can add files to the
   release commit (`build_command` plus `assets`), but the PSR action runs in its own container
   without `uv`; check whether `uv lock` can run there (or the action can be replaced by the PSR
   CLI on the runner) before changing `release.yml`.

## Resolution
