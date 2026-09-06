"""Enforce the `@pytest.mark.integration` backfill on CLI/MCP wiring test files.

CLAUDE.md: "Mark CLI/MCP wiring tests with `@pytest.mark.integration`." The wiring set is
every ``test_cli.py``/``test_mcp.py`` under ``tests/yandex/`` — a homogeneous set of
CLI/MCP smoke tests, each expected to carry a module-level ``pytestmark =
pytest.mark.integration`` (the repo's idiom for a wholly-integration file; see
``tests/test_yandex_cli.py`` / ``tests/test_demo_render.py``). Detection is AST-only (no
importing test modules — that would trigger their collection-time side effects), matching
the checker style in ``tests/test_architecture.py``.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YANDEX_TESTS = ROOT / "tests" / "yandex"

# The exact wiring glob: `test_cli.py` / `test_mcp.py` basenames under tests/yandex/ — the
# same set `rg --files -g 'test_cli.py' -g 'test_mcp.py' tests/yandex` enumerates. Sibling
# basenames (`test_login_cli.py`, `test_status.py`) and root-level aggregate files
# (`tests/test_yandex_cli.py`, `tests/test_demo_render.py`) are intentionally NOT in this
# glob — they already carry their own markers and are out of this check's scope.
_WIRING_BASENAMES = frozenset({"test_cli.py", "test_mcp.py"})


def _wiring_files() -> list[Path]:
    """Every CLI/MCP wiring test file, sorted for stable failure messages."""
    return sorted(p for p in YANDEX_TESTS.rglob("*.py") if p.name in _WIRING_BASENAMES)


def _is_pytest_mark_integration(node: ast.expr) -> bool:
    """``True`` for the attribute chain ``pytest.mark.integration``."""
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "integration"
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "mark"
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "pytest"
    )


def _has_integration_pytestmark(source: str) -> bool:
    """``True`` if ``source`` has a module-level ``pytestmark = pytest.mark.integration``.

    Detects via AST — a top-level ``Assign`` targeting a name ``pytestmark`` whose value is
    either the bare attribute chain ``pytest.mark.integration`` or a list/tuple containing
    it (pytest supports both a single marker and a sequence of markers as ``pytestmark``).
    Source is never imported, so this is safe to run against arbitrary/synthetic text.
    """
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets):
            continue
        value = node.value
        if _is_pytest_mark_integration(value):
            return True
        if isinstance(value, (ast.List, ast.Tuple)) and any(
            _is_pytest_mark_integration(elt) for elt in value.elts
        ):
            return True
    return False


def test_wiring_glob_matches_the_expected_99_files():
    """Lock the scope: exactly 99 files match the wiring glob today.

    A count drift (new resource added/removed) is expected over time — if this trips, update
    the count deliberately rather than silently widening or narrowing what's enforced below.
    """
    files = _wiring_files()
    assert len(files) == 99, (
        f"expected 99 test_cli.py/test_mcp.py wiring files under tests/yandex/, found "
        f"{len(files)}: update this count deliberately if the wiring set changed"
    )


def test_all_wiring_files_carry_module_level_integration_marker():
    """Every CLI/MCP wiring test file must carry `pytestmark = pytest.mark.integration`."""
    offenders = [
        str(p.relative_to(ROOT))
        for p in _wiring_files()
        if not _has_integration_pytestmark(p.read_text(encoding="utf-8"))
    ]
    assert not offenders, (
        "every tests/yandex/**/test_cli.py and test_mcp.py must carry a module-level "
        "`pytestmark = pytest.mark.integration` (CLAUDE.md) — missing in: " + ", ".join(offenders)
    )


def test_integration_marker_guard_bites():
    """Prove-it: the AST predicate flags a synthetic wiring source missing the marker.

    Mirrors the prove-it style in tests/test_architecture.py — the guard is exercised on
    in-memory source, not just proven to pass on today's (already-fixed) tree.
    """
    unmarked = "import pytest\n\n\ndef test_something():\n    pass\n"
    assert not _has_integration_pytestmark(unmarked)

    other_marker_only = "import pytest\n\npytestmark = pytest.mark.slow\n"
    assert not _has_integration_pytestmark(other_marker_only)

    per_function_only = (
        "import pytest\n\n\n@pytest.mark.integration\ndef test_something():\n    pass\n"
    )
    assert not _has_integration_pytestmark(per_function_only)

    bare = "import pytest\n\npytestmark = pytest.mark.integration\n"
    assert _has_integration_pytestmark(bare)

    listed = "import pytest\n\npytestmark = [pytest.mark.integration]\n"
    assert _has_integration_pytestmark(listed)

    tupled = "import pytest\n\npytestmark = (pytest.mark.integration,)\n"
    assert _has_integration_pytestmark(tupled)

    listed_with_others = (
        "import pytest\n\npytestmark = [pytest.mark.slow, pytest.mark.integration]\n"
    )
    assert _has_integration_pytestmark(listed_with_others)


def test_enforcement_file_itself_is_out_of_scope():
    """This file is neither `test_cli.py` nor `test_mcp.py`, so the glob correctly skips it —
    it is not, and must not become, one of the 99 files it enforces."""
    here = Path(__file__).resolve()
    assert here.name not in _WIRING_BASENAMES
    assert here not in _wiring_files()
