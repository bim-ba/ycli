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
    module = importlib.util.module_from_spec(spec)  # ty: ignore[invalid-argument-type]
    spec.loader.exec_module(module)  # ty: ignore[unresolved-attribute]
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
        "git commit -m 'feat: x [actions skip]'",
        "git commit -m 'fix: x' -m 'skip-checks: true'",
        "git commit --trailer skip-checks:true -m 'fix: x'",
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
        "git commit -m 'fix: normal release message, nothing to see here'",
    ],
)
def test_safe_commands_are_allowed(command):
    assert git_guard.decide(command) is None


# The bracket/trailer tokens below are built via string concatenation, never as a
# contiguous literal, so this file's own diff never carries a raw skip-ci token for
# git_guard (this repo's own PreToolUse commit guard) or the no-skip-ci pre-commit
# content check to trip on.
_SKIP = "skip"
_CI_BRACKET_ONE_SPACE = "[" + _SKIP + " ci]"
_CI_BRACKET_TWO_SPACES = "[" + _SKIP + "  ci]"
_TRAILER_TWO_SPACES = "skip-checks:" + "  true"


@pytest.mark.parametrize(
    "command",
    [
        f"git commit -m 'fix: release {_CI_BRACKET_ONE_SPACE}'",
        f"git commit -m 'fix: release {_CI_BRACKET_TWO_SPACES}'",
        f"git commit --trailer '{_TRAILER_TWO_SPACES}' -m 'fix: x'",
    ],
)
def test_whitespace_variants_are_denied(command):
    """GitHub still honors internal-whitespace variants of the bracket/trailer tokens
    (double space, tabs, ...); the hook must normalize whitespace before matching."""
    decision = git_guard.decide(command)
    assert decision is not None
    assert decision["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_token_outside_message_args_is_not_flagged():
    """Scoping the match to message-bearing args (-m/-b/...) means a token that only
    appears in an unrelated arg -- e.g. a pathspec after `--` -- is not a false positive."""
    command = f"git commit -m 'fix: rename asset' -- 'assets/{_CI_BRACKET_ONE_SPACE}.png'"
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
