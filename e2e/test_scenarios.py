"""One live test per scenario file; ``smoke: true`` scenarios carry the ``smoke`` marker."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from e2e.catalog import load, scenario_paths
from e2e.recording import InProcessDriver
from e2e.runner import CliDriver, run_scenario

if TYPE_CHECKING:
    from e2e.models import Scenario
    from e2e.recording import Recorder


def _parameters() -> list[object]:
    parameters: list[object] = []
    for path in scenario_paths():
        scenario = load(path)
        marks = [pytest.mark.smoke] if scenario.smoke else []
        parameters.append(pytest.param(scenario, id=scenario.name, marks=marks))
    return parameters


@pytest.mark.live
@pytest.mark.parametrize("scenario", _parameters())
def test_scenario(scenario: Scenario, variables: dict[str, str], recorder: Recorder | None) -> None:
    print(f"RUN={variables['RUN']}")  # shown on failure: every object of this run carries it
    if recorder is None:
        run_scenario(scenario, CliDriver(), variables)
    else:
        run_scenario(scenario, InProcessDriver(), variables, read=recorder.read)
