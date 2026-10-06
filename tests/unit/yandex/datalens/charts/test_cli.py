"""`datalens charts data-get`: what a chart that gives no data answers with."""

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.cli.errors import format_cli_error
from ycli.yandex.errors import YandexClientError

DATA = "https://api.datalens.tech/rpc/getChartData"
# Two refusals measured live (2026-10-06): a source that cannot be reached, and a pivot table.
UNREACHABLE = {"code": "ERR.CHARTS.DATA_FETCHING_ERROR", "message": "Failed to retrieve chart data"}
PIVOT = {
    "code": "UNSUPPORTED_CHART_DATA_VISUALIZATION",
    "message": "Data retrieval is not supported for this visualization type. "
    "Pivot tables are not supported.",
}


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


@pytest.mark.parametrize(("status", "body"), [(427, UNREACHABLE), (422, PIVOT)])
def test_a_chart_that_gives_no_data_says_why(api, status, body):
    """427 is a status of DataLens's own: it is an error of the request like any other 4xx."""
    api.add("POST", DATA, json=body, status=status)
    result = CliRunner().invoke(cli.app, ["datalens", "charts", "data-get", "ch1"])
    assert result.exit_code == 1
    assert isinstance(result.exception, YandexClientError) and result.exception.status == status
    assert f"{body['code']}: {body['message']}" in format_cli_error(result.exception)
