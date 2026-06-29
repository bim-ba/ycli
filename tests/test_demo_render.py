"""The demo render harness emits real CLI output from committed fixtures (leak-free)."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RENDER = REPO / "docs" / "demo" / "render.py"

pytestmark = pytest.mark.integration


def _run(args):
    return subprocess.run(
        [sys.executable, str(RENDER), *args],
        capture_output=True,
        text=True,
        cwd=REPO,
    )


def test_render_tracker_issue_get_emits_fixture_key():
    proc = _run(["tracker", "issues", "get", "TRACKER-1"])
    assert proc.returncode == 0, proc.stderr
    assert "TRACKER-1" in proc.stdout


def test_render_wiki_page_get_emits_fixture_title():
    proc = _run(["wiki", "pages", "get", "onboarding"])
    assert proc.returncode == 0, proc.stderr
    assert "onboarding" in proc.stdout
