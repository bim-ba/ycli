"""The demo render harness emits real CLI output from committed fixtures (leak-free)."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RENDER = REPO / "docs" / "demo" / "render.py"

pytestmark = pytest.mark.integration


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RENDER), *args],
        capture_output=True,
        text=True,
        cwd=REPO,
    )


def test_render_tracker_issue_get_is_pretty_and_flat():
    proc = _run(["tracker", "issues", "get", "DEMO-42"])
    assert proc.returncode == 0, proc.stderr
    assert "DEMO-42" in proc.stdout
    # the demo shows the pretty table, not raw JSON (a presentation, not a pipe)
    assert not proc.stdout.lstrip().startswith("{")
    # refs render flat (model-layer flattening), not as nested {"key": ...}
    assert "inProgress" in proc.stdout
    assert '{"key"' not in proc.stdout


def test_render_wiki_page_get_emits_markdown_body():
    proc = _run(["wiki", "pages", "get", "onboarding"])
    assert proc.returncode == 0, proc.stderr
    assert "Welcome to the team" in proc.stdout  # raw markdown body of the page
