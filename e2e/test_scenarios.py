"""One live test per scenario file; ``smoke: true`` scenarios carry the ``smoke`` marker."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from e2e.catalog import load, scenario_paths
from e2e.conftest import RETRIED_STEPS, SKIPPED_STEPS
from e2e.recording import InProcessDriver
from e2e.runner import CliDriver, run_scenario

if TYPE_CHECKING:
    from e2e.models import Scenario
    from e2e.recording import Recorder
    from e2e.surfaces import ThreeSurfaces


def _parameters() -> list[object]:
    parameters: list[object] = []
    for path in scenario_paths():
        scenario = load(path)
        marks = [pytest.mark.smoke] if scenario.smoke else []
        parameters.append(pytest.param(scenario, id=scenario.name, marks=marks))
    return parameters


@pytest.mark.live
@pytest.mark.parametrize("scenario", _parameters())
def test_scenario(
    scenario: Scenario,
    variables: dict[str, str],
    recorder: Recorder | None,
    surfaces: ThreeSurfaces | None,
    request: pytest.FixtureRequest,
) -> None:
    print(f"RUN={variables['RUN']}")  # shown on failure: every object of this run carries it
    read = None if recorder is None else recorder.read
    if recorder is None and surfaces is None:
        skipped = run_scenario(scenario, CliDriver(), variables, retried=RETRIED_STEPS)
    elif surfaces is None:
        driver = InProcessDriver(request.config.getoption("--record-pause"))
        skipped = run_scenario(scenario, driver, variables, read=read, retried=RETRIED_STEPS)
    else:
        from e2e.surfaces import fail_on_data

        seen = len(surfaces.report.data())
        skipped = run_scenario(scenario, surfaces, variables, read=read, retried=RETRIED_STEPS)
        if request.config.getoption("--surfaces") == "strict":
            fail_on_data(surfaces.report, seen)
    SKIPPED_STEPS.extend(skipped)
    if len(skipped) == len(scenario.steps):
        pytest.skip("; ".join(skipped))
