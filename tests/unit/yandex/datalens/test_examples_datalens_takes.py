"""The examples of creating a dashboard and a report are bodies DataLens takes.

Measured through ycli (2026-10-07, `e2e/scenarios/datalens/entries_content.yaml`): DataLens
answers 400 for a new dashboard or report that lacks any of these keys, so a contract case
without one would show, in the docstring of the SDK and wherever the case is quoted, a body
the service refuses.
"""

import pytest

from tests.unit.yandex.datalens.dashboards.cases import CASES as DASHBOARDS
from tests.unit.yandex.datalens.reports.cases import CASES as REPORTS

DASHBOARD_SETTINGS = {"autoupdateInterval", "maxConcurrentRequests", "silentLoading", "expandTOC"}
TAB = {"id", "title", "items", "layout", "connections", "aliases"}
REPORT = {
    "counter",
    "salt",
    "slides",
    "slideGroups",
    "slidesOrder",
    "visualSettings",
    "slideSettings",
}


def _sent(cases: list, operation: str) -> list[dict]:
    found = [case.exchanges[0][0].json for case in cases if case.operation == operation]
    assert found, operation
    return found


@pytest.mark.parametrize("body", _sent(DASHBOARDS, "datalens.dashboards.create"))
def test_the_example_of_a_new_dashboard_is_one_datalens_takes(body):
    entry = body["entry"]
    assert isinstance(entry.get("meta"), dict)  # 400 entry.meta: expected record
    assert set(entry["data"]["settings"]) >= DASHBOARD_SETTINGS
    assert entry["data"]["tabs"] and all(set(tab) >= TAB for tab in entry["data"]["tabs"])


@pytest.mark.parametrize("body", _sent(REPORTS, "datalens.reports.create"))
def test_the_example_of_a_new_report_is_one_datalens_takes(body):
    assert set(body["data"]) >= REPORT and body["data"]["slides"]
    assert "meta" in body  # required, `null` when the report has none
