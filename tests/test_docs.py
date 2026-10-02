"""Live docs stay in step with the code: no idiom the code has dropped is shown as usage."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# User-facing doc files and globs to scan for purged idioms.
# Historical / rule-defining files are intentionally excluded:
#   PROMPT.md            — historical transcript
#   CHANGELOG.md         — historical release notes
#   ARCHITECTURE.md      — DEFINES the forbidden idioms as rules
#   .venv/** / .git/**   — not user-facing docs
_LIVE_DOC_GLOBS = [
    "README.md",
    "CLAUDE.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/conventions/**/*.md",
    "docs/en/**/*.md",
    "plugins/**/*.md",
]

# Patterns whose mere presence in a live doc signals a purged idiom — either the CALL/USAGE
# syntax of a decommissioned API, or a decommissioned literal string.
# Rationale: `.from_env(` and `session_from_env(` match invocation; prose like "no from_env"
# does not match because it lacks the trailing `(`. `X-Org-ID` (capital D) is the wrong-cased
# org header from the old "casing differs per service" gotcha — the transport emits one
# canonical `X-Org-Id` for every service (case-insensitive per RFC 9110), so the correct
# `X-Org-Id` must never regress to `X-Org-ID`. The substring differs in the final letter, so
# the correct casing is not matched.
_PURGED_CALL_PATTERNS = [
    ".from_env(",
    "session_from_env(",
    "X-Org-ID",
]


def _live_doc_files() -> list[Path]:
    """Return the list of tracked user-facing doc files to scan."""
    files: list[Path] = []
    for glob_pattern in _LIVE_DOC_GLOBS:
        matched = sorted(ROOT.glob(glob_pattern))
        files.extend(p for p in matched if p.is_file())
    return files


def test_live_docs_show_no_purged_idioms():
    """User-facing docs must not show call idioms the code no longer has (ARCH-5, ARCH-7).

    Scanned files: README.md, CLAUDE.md, AGENTS.md, CONTRIBUTING.md, SECURITY.md,
    docs/conventions/**/*.md, the documentation site (docs/en/**/*.md), plugins/**/*.md.
    Excluded (historical/rule-defining): PROMPT.md, CHANGELOG.md,
    ARCHITECTURE.md (it defines the forbidden idioms as rules), .venv/**, .git/**.
    Patterns checked: .from_env(  session_from_env(  X-Org-ID
    """
    doc_files = _live_doc_files()
    assert doc_files, "expected at least one live doc file to scan; glob list may be broken"
    offenders: list[str] = []
    for doc_file in doc_files:
        text = doc_file.read_text(encoding="utf-8")
        for pattern in _PURGED_CALL_PATTERNS:
            if pattern in text:
                rel = doc_file.relative_to(ROOT)
                offenders.append(f"{rel}: contains purged call pattern {pattern!r}")
    assert not offenders, (
        "Purged idioms found in live docs — remove the call-site example or update the doc. "
        f"Offenders: {offenders}"
    )
