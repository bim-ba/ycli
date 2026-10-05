"""Docstring examples render as code on the documentation site."""

from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
SINGULAR = re.compile(r"^\s*Example:\s*$", re.MULTILINE)


def singular_example_sections(root: Path) -> list[str]:
    """Files under ``root`` with an ``Example:`` section instead of ``Examples:``."""
    return [
        str(path.relative_to(root))
        for path in sorted(root.rglob("*.py"))
        if SINGULAR.search(path.read_text(encoding="utf-8"))
    ]


def test_example_sections_are_titled_examples():
    """Mkdocstrings reads ``Examples:`` as code and ``Example:`` as prose, which mangles ``>>>``."""
    assert singular_example_sections(SRC) == []


def test_the_check_bites(tmp_path):
    (tmp_path / "module.py").write_text('"""Summary.\n\nExample:\n    >>> 1\n    1\n"""\n')
    assert singular_example_sections(tmp_path) == ["module.py"]
