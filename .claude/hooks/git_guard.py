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
import shlex
import sys

SKIP_CI_TOKENS = (
    "[skip ci]",
    "[ci skip]",
    "[no ci]",
    "[skip actions]",
    "[actions skip]",
    "skip-checks: true",
    "skip-checks:true",
)
COMMIT_CMD_RE = re.compile(r"\bgit\s+(?:commit|merge)\b|\bgh\s+pr\s+(?:merge|create)\b")

# Flags whose next shell token is message-bearing text (git -m/-b, gh --title/--body/--trailer).
_MESSAGE_FLAGS = frozenset({"-m", "--message", "-b", "--body", "-t", "--title", "--trailer"})
# GNU-style --flag=value forms of the long flags above.
_MESSAGE_FLAG_EQUALS = tuple(f"{flag}=" for flag in _MESSAGE_FLAGS if flag.startswith("--"))
_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_whitespace(text: str) -> str:
    """Collapse any run of whitespace to a single space, so a bracket token or the
    ``skip-checks:`` trailer written with extra internal spacing (e.g. a doubled space)
    still matches its single-space form in ``SKIP_CI_TOKENS``."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def _message_bearing_text(command: str) -> str:
    """Extract the text carried by -m/-b/-t/--message/--body/--title/--trailer args.

    Falls back to the raw command if it can't be shell-tokenized (malformed quoting) so a
    broken command is still scanned rather than silently skipped. Scoping the match to these
    args (instead of the whole command string) avoids flagging a token that only appears in
    an unrelated part of the command, e.g. a filename or a `--` pathspec.
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return command
    parts = []
    take_next = False
    for token in tokens:
        if take_next:
            parts.append(token)
            take_next = False
            continue
        if token in _MESSAGE_FLAGS:
            take_next = True
            continue
        for flag_equals in _MESSAGE_FLAG_EQUALS:
            if token.startswith(flag_equals):
                parts.append(token[len(flag_equals) :])
                break
    return " ".join(parts)


def _deny(reason: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def decide(command: str) -> dict | None:
    """Return a PreToolUse deny payload for a skip-ci commit/merge, else None.

    Scope: this inspects the message-bearing args of the command STRING only (see
    ``_message_bearing_text``). A token supplied out-of-band — ``git commit -F msg.txt``,
    ``gh pr merge --body-file b.txt``, ``--amend --no-edit`` — is invisible here and falls
    through to the other two layers (the no-skip-ci pre-commit hook and the human merge
    step). The common agent path (``-m``/``-b``) is fully covered, including variants that
    add extra internal whitespace around a bracket token or the ``skip-checks:`` trailer
    (GitHub still honors those).
    """
    if not COMMIT_CMD_RE.search(command):
        return None
    text = _normalize_whitespace(_message_bearing_text(command)).lower()
    if any(token in text for token in SKIP_CI_TOKENS):
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
        sys.stdout.write("\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
