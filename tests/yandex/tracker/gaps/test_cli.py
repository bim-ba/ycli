"""`tracker gaps create`: a malformed or incomplete absence is refused, anything else is sent."""

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

WINDOW = ["--date-from", "2026-07-01T00:00Z", "--date-to", "2026-07-02T00:00Z"]


def test_a_malformed_gap_is_a_usage_error(api):
    result = CliRunner().invoke(cli.app, ["tracker", "gaps", "create", "--gap", "{oops"])
    assert result.exit_code == 2
    assert api.calls == []


@pytest.mark.parametrize(
    ("argv", "missing"),
    [
        (["--user", "ann", *WINDOW], {"workflow"}),
        (["--workflow", "trip", *WINDOW], {"user"}),
        (["--user", "ann", "--workflow", "trip", "--date-from", "2026-07-01T00:00Z"], {"to"}),
    ],
    ids=["no workflow", "no user", "no end"],
)
def test_an_incomplete_absence_is_refused_by_the_model_before_sending(api, argv, missing):
    result = CliRunner().invoke(cli.app, ["tracker", "gaps", "create", *argv])
    assert isinstance(result.exception, ValidationError)
    errors = result.exception.errors()
    assert {error["type"] for error in errors} == {"missing"}
    assert {error["loc"][0] for error in errors} == missing
    assert api.calls == []


def test_no_absence_at_all_is_sent_as_an_empty_list(api):
    api.add("POST", f"{BASE}/gaps", json={"gaps": []})
    result = CliRunner().invoke(cli.app, ["tracker", "gaps", "create"])
    assert result.exit_code == 0
    assert api.body() == {"gaps": []}
