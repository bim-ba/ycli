"""Live tests run only on purpose: ``YCLI_E2E=1`` plus the test organization's credentials."""

from __future__ import annotations

import os
import secrets
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from e2e.recording import REPLIES, Recorder, recording
from e2e.runner import CREDENTIAL_VARIABLES
from e2e.settings import sandbox_queue

if TYPE_CHECKING:
    from collections.abc import Iterator

# A file every scenario appends its run name to, when set (see ``e2e/janitor.py --runs-file``).
RUNS_FILE_ENV = "YCLI_E2E_RUNS_FILE"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--record",
        action="store_true",
        help="Run the CLI in this process and keep each operation's real reply as a fixture.",
    )
    parser.addoption(
        "--record-to",
        type=Path,
        default=REPLIES,
        help="Where the fixtures go (the committed ones by default).",
    )
    parser.addoption(
        "--record-report",
        type=Path,
        default=Path(tempfile.gettempdir()) / "ycli-record-report.txt",
        help="Where the names of failed reads and unknown keys go: a file outside the repository.",
    )


@pytest.fixture(scope="session")
def recorder(request: pytest.FixtureRequest) -> Iterator[Recorder | None]:
    """The recorder of a ``--record`` run, ``None`` otherwise; its report is printed at the end."""
    if not request.config.getoption("--record"):
        yield None
        return
    directory = request.config.getoption("--record-to")
    with pytest.MonkeyPatch.context() as monkeypatch, recording(monkeypatch, directory) as recorder:
        yield recorder
        report: Path = request.config.getoption("--record-report")
        report.write_text(recorder.details(), encoding="utf-8")
        terminal = request.config.get_terminal_writer()
        terminal.line(f"\n{recorder.summary()}\nthe names are in {report}")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "live: calls the real Yandex 360 test organization")
    config.addinivalue_line("markers", "smoke: the live subset that also runs on pull requests")


def _skip_reason() -> str | None:
    if os.environ.get("YCLI_E2E") != "1":
        return "live e2e is opt-in: set YCLI_E2E=1"
    missing = [name for name in CREDENTIAL_VARIABLES if not os.environ.get(name)]
    if missing:
        return "missing credentials: " + ", ".join(missing)
    return None


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    reason = _skip_reason()
    if reason is None:
        return
    for item in items:
        if "live" in item.keywords:
            item.add_marker(pytest.mark.skip(reason=reason))


@pytest.fixture
def variables() -> dict[str, str]:
    """``RUN`` names every object a scenario creates: ``e2e-<unix seconds>-<4 hex>``.

    The janitor reads the age back from the stamp, so it needs no per-object metadata call.
    """
    run = f"e2e-{int(time.time())}-{secrets.token_hex(2)}"
    # The janitor of this run removes only what the runs listed here named.
    if runs_file := os.environ.get(RUNS_FILE_ENV):
        with Path(runs_file).open("a", encoding="utf-8") as listed:
            listed.write(f"{run}\n")
    return {"RUN": run, "QUEUE": sandbox_queue(), "FILES": str(Path(__file__).parent / "files")}
