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
