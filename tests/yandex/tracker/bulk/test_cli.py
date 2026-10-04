"""`tracker bulk … --wait` (the default) polls the started operation to a terminal status."""

import json
import time

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.errors import YandexTimeoutError


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """The poll waits between reads through ``time.sleep``; tests never wait."""
    monkeypatch.setattr(time, "sleep", lambda *_: None)


@pytest.mark.parametrize(
    ("argv", "trigger"),
    [
        (["update", "--query", "Queue: TEST", "-F", "priority=blocker"], "_update"),
        (["move", "CHECK", "--issue", "TEST-1"], "_move"),
        (["transition", "close", "--issue", "TEST-1"], "_transition"),
    ],
)
def test_wait_polls_until_the_status_is_terminal(api, argv, trigger):
    api.add("POST", f"{BASE}/bulkchange/{trigger}", json={"id": "1ab", "status": "CREATED"})
    api.add("GET", f"{BASE}/bulkchange/1ab", json={"id": "1ab", "status": "CREATED"})
    api.add("GET", f"{BASE}/bulkchange/1ab", json={"id": "1ab", "status": "COMPLETE"})
    res = CliRunner().invoke(cli.app, ["-o", "json", "tracker", "bulk", *argv])
    assert res.exit_code == 0, res.output
    assert json.loads(res.stdout)["status"] == "COMPLETE"
    assert [(call.method, call.url.path) for call in api.calls] == [
        ("POST", f"/v3/bulkchange/{trigger}"),
        ("GET", "/v3/bulkchange/1ab"),
        ("GET", "/v3/bulkchange/1ab"),
    ]


def test_wait_without_an_operation_id_prints_the_answer(api):
    api.add("POST", f"{BASE}/bulkchange/_update", json={"status": "FAILED"})
    res = CliRunner().invoke(
        cli.app, ["-o", "json", "tracker", "bulk", "update", "--issue", "TEST-1"]
    )
    assert res.exit_code == 0, res.output
    assert json.loads(res.stdout)["status"] == "FAILED"
    assert len(api.calls) == 1


def test_wait_gives_up_after_the_configured_seconds(api, monkeypatch):
    """``YCLI__HTTP__MAX_WAIT_SECONDS`` is how long ``--wait`` polls (#301)."""
    slept: list[float] = []
    monkeypatch.setattr(time, "sleep", slept.append)
    monkeypatch.setenv("YCLI__HTTP__MAX_WAIT_SECONDS", "1")
    api.add("POST", f"{BASE}/bulkchange/_update", json={"id": "1ab", "status": "CREATED"})
    for _ in range(3):
        api.add("GET", f"{BASE}/bulkchange/1ab", json={"id": "1ab", "status": "CREATED"})
    res = CliRunner().invoke(cli.app, ["tracker", "bulk", "update", "--issue", "TEST-1"])
    assert isinstance(res.exception, YandexTimeoutError)
    assert str(res.exception) == "operation did not finish within 1 s"
    assert slept == [0.5, 0.5]
