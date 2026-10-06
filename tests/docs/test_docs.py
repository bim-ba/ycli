"""Live docs stay in step with the code: no idiom the code has dropped is shown as usage."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

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
    "docs/ru/**/*.md",
    "README.ru.md",
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
# `bim-ba.github.io` is the documentation site's former host; old links are not kept.
_PURGED_CALL_PATTERNS = [
    ".from_env(",
    "session_from_env(",
    "X-Org-ID",
    "bim-ba.github.io",
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
    docs/conventions/**/*.md, the documentation site (docs/en, docs/ru), README.ru.md,
    plugins/**/*.md.
    Excluded (historical/rule-defining): PROMPT.md, CHANGELOG.md,
    ARCHITECTURE.md (it defines the forbidden idioms as rules), .venv/**, .git/**.
    Patterns checked: .from_env(  session_from_env(  X-Org-ID  bim-ba.github.io
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


# What starts a new block, so a line beginning with it is not the continuation of a paragraph.
_BLOCK_STARTS = ("#", "|", ">", "<", "- ", "* ", "```", "[![")


def _hard_wrapped(markdown: str) -> list[int]:
    """Line numbers where a paragraph or list item continues on the next line.

    A paragraph is one line: an editor wraps it for the reader, and a hand-made break turns
    every later edit into a re-wrap of the whole paragraph. Code fences and the generated
    coverage block are skipped.
    """
    wrapped = []
    fenced = generated = continues = False
    for number, line in enumerate(markdown.splitlines(), start=1):
        stripped = line.strip()
        if "COVERAGE:" in line:
            generated = "COVERAGE:START" in line
        elif stripped.startswith("```"):
            fenced = not fenced
        text = bool(stripped) and not (fenced or generated or stripped.startswith("```"))
        if text and continues and not stripped.startswith(_BLOCK_STARTS):
            wrapped.append(number)
        # A paragraph or a list item may run on; a heading, a table row or a tag may not.
        continues = text and not stripped.startswith(("#", "|", "<", "[!["))
    return wrapped


def test_the_readmes_have_no_hard_wrapped_paragraph():
    for name in ("README.md", "README.ru.md"):
        assert _hard_wrapped((ROOT / name).read_text(encoding="utf-8")) == [], name


def test_the_hard_wrap_check_bites():
    markdown = (
        "# Title\n\nOne line.\n\nA paragraph broken\nby hand.\n\n"
        "- an item\n  that continues\n- a second item\n\n"
        "```bash\nycli a\nycli b\n```\n\n| a |\n|---|\n| b |\n"
    )
    assert _hard_wrapped(markdown) == [6, 9]
