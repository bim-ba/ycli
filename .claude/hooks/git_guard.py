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
