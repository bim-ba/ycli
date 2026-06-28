"""ARCH-6: the public surface changes only via an intentional snapshot update."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.snapshots._surface import cli_tree, mcp_tool_names

HERE = Path(__file__).resolve().parent / "snapshots"
HINT = "run `uv run python -m tests.snapshots --update` to accept the new surface"


@pytest.mark.parametrize(
    ("filename", "current"),
    [("cli_tree.txt", cli_tree), ("mcp_tools.txt", mcp_tool_names)],
)
def test_public_surface_matches_snapshot(filename, current):
    expected = (HERE / filename).read_text(encoding="utf-8").splitlines()
    assert current() == expected, f"public surface drifted ({filename}); {HINT}"
