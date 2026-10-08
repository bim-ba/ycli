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
from e2e.settings import missing_credentials, optional_variables, sandbox_queue
from ycli.yandex.registry import SERVICES

if TYPE_CHECKING:
    from collections.abc import Iterator

    from e2e.models import Scenario
    from e2e.surfaces import ThreeSurfaces

# Never collected: ``--doctest-modules`` would import it, and it imports fastmcp, which comes
# with the `mcp` extra a plain run does not have. Only the ``surfaces`` fixture imports it.
collect_ignore = ["surfaces.py"]

# A file every scenario appends its run name to, when set (see ``e2e/janitor.py --runs-file``).
RUNS_FILE_ENV = "YCLI_E2E_RUNS_FILE"


# The steps this run did not run because a variable they need is not set, said at the end.
SKIPPED_STEPS: list[str] = []


# The steps this run ran again on the failure they name, said at the end: a retry that passed
# is still a refusal of the service.
RETRIED_STEPS: list[str] = []


def pytest_terminal_summary(terminalreporter: pytest.TerminalReporter) -> None:
    if RETRIED_STEPS:
        terminalreporter.section("steps run again: the service refused and asked to retry")
        for step in RETRIED_STEPS:
            terminalreporter.line(step)
    if SKIPPED_STEPS:
        terminalreporter.section("steps skipped: a variable they need is not set")
        for step in SKIPPED_STEPS:
            terminalreporter.line(step)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--service",
        default=None,
        help="Run only the scenarios of this service (tracker, wiki, forms, datalens): the "
        "nightly run is one job per service.",
    )
    parser.addoption(
        "--permanent",
        action="store_true",
        help="Also run the scenarios that leave objects the API cannot delete (a status, a "
        "field, a trigger). On purpose and by hand: every such run adds them for good.",
    )
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
        "--record-pause",
        type=float,
        default=1.0,
        help="Seconds to wait before each command of a recording run: a command in this "
        "process follows the one before faster than Tracker settles after a write.",
    )
    parser.addoption(
        "--surfaces",
        choices=("report", "strict"),
        default=None,
        help="Run the CLI in this process and repeat every read through MCP and the SDK (needs "
        "the `mcp` extra): `report` lists where the replies differ, `strict` also fails on it.",
    )
    parser.addoption(
        "--writes-through",
        choices=("cli", "mcp", "sdk"),
        default="cli",
        help="With --surfaces: the surface that carries out every write of the run. The step's "
        "expectations are checked against its answer; a write still runs once.",
    )
    parser.addoption(
        "--surfaces-report",
        type=Path,
        default=Path(tempfile.gettempdir()) / "ycli-surfaces-report.txt",
        help="Where the report of a --surfaces run goes, besides the end of the log.",
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


@pytest.fixture(scope="session")
def surfaces(
    request: pytest.FixtureRequest, recorder: Recorder | None
) -> Iterator[ThreeSurfaces | None]:
    """The driver of a ``--surfaces`` run, ``None`` otherwise; its report ends the log.

    After ``recorder``: it listens over a recording run's transport, not under it.
    """
    if request.config.getoption("--surfaces") is None:
        yield None
        return
    # Here, not at the top: fastmcp comes with the `mcp` extra, and a plain run has none.
    from e2e.recording import InProcessDriver
    from e2e.surfaces import ThreeSurfaces, listening

    with pytest.MonkeyPatch.context() as monkeypatch, listening(monkeypatch) as listener:
        through = request.config.getoption("--writes-through")
        driver = ThreeSurfaces(
            InProcessDriver(request.config.getoption("--record-pause")),
            listener,
            writes_through=None if through == "cli" else through,
        )
        yield driver
        driver.close()
        text = driver.report.text()
        request.config.getoption("--surfaces-report").write_text(text, encoding="utf-8")
        request.config.get_terminal_writer().line(f"\n{text}")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "live: calls the real Yandex 360 test organization")
    config.addinivalue_line("markers", "smoke: the live subset that also runs on pull requests")


def kept_out(scenario: Scenario, *, permanent: bool) -> str | None:
    """Why ``scenario`` does not run in this run, whatever the credentials; ``None`` when it may.

    ``kept_out(Scenario(name="t/x", permanent=True, steps=...), permanent=False)`` ->
    ``"leaves objects the API cannot delete: run it on purpose with --permanent"``.
    """
    if scenario.permanent and not permanent:
        return "leaves objects the API cannot delete: run it on purpose with --permanent"
    return None


def _skip_reason(service: str | None) -> str | None:
    """Why a live test of ``service`` does not run here; ``None`` when it does.

    Each service is asked for what its own profile takes, so one run reaches the services
    its credentials fit and skips the others with the reason: DataLens takes no OAuth token
    and a Yandex Cloud organization, the three services of Yandex 360 the other way round.
    """
    if os.environ.get("YCLI_E2E") != "1":
        return "live e2e is opt-in: set YCLI_E2E=1"
    profiles = {known.name: known.profile for known in SERVICES}
    if service not in profiles:
        return None
    lacking = missing_credentials(profiles[service])
    return f"{service}: {lacking}" if lacking else None


def of_service(scenario_name: str, service: str | None) -> bool:
    """Whether a scenario belongs to ``service``; every scenario does when none is named.

    ``of_service("wiki/page-lifecycle", "wiki") -> True``: a scenario is named after the
    directory of its service.
    """
    return service is None or scenario_name.split("/")[0] == service


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    service = config.getoption("--service")
    dropped = [
        item
        for item in items
        if (callspec := getattr(item, "callspec", None)) is not None
        and "scenario" in callspec.params
        and not of_service(callspec.params["scenario"].name, service)
    ]
    if dropped:
        config.hook.pytest_deselected(items=dropped)
        items[:] = [item for item in items if item not in dropped]
    for item in items:
        if "live" not in item.keywords:
            continue
        scenario = getattr(getattr(item, "callspec", None), "params", {}).get("scenario")
        reason = _skip_reason(scenario.name.split("/")[0] if scenario is not None else None)
        if scenario is not None:
            reason = kept_out(scenario, permanent=config.getoption("--permanent")) or reason
        if reason is not None:
            item.add_marker(pytest.mark.skip(reason=reason))


@pytest.fixture
def variables() -> dict[str, str]:
    """``RUN`` names every object a scenario creates: ``e2e-<unix seconds>-<4 hex>``.

    ``TAG`` is its four hex digits alone.

    The janitor reads the age back from the stamp, so it needs no per-object metadata call.
    """
    run = f"e2e-{int(time.time())}-{secrets.token_hex(2)}"
    # The janitor of this run removes only what the runs listed here named.
    if runs_file := os.environ.get(RUNS_FILE_ENV):
        with Path(runs_file).open("a", encoding="utf-8") as listed:
            listed.write(f"{run}\n")
    return {
        "RUN": run,
        # The last part of the run's name, for a key that takes no dash (a status, a field).
        "TAG": run.rsplit("-", 1)[1],
        "QUEUE": sandbox_queue(),
        "FILES": str(Path(__file__).parent / "files"),
        **optional_variables(),
    }
