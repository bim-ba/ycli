"""TDD for `tracker bulk` CLI (wiring-dependent — run by the integrator after mount).

Covers the ``--wait`` poll path end-to-end: ``time.sleep`` is monkeypatched to a no-op so the
CREATED → COMPLETE sequence resolves instantly.
"""

import json
import time

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@pytest.fixture(autouse=True)
def _patch_sleep(monkeypatch):
    """No real waiting in the --wait poll."""
    monkeypatch.setattr(time, "sleep", lambda *_: None)


@responses.activate
def test_update_no_wait_prints_created_change():
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_update",
        json={"id": "1ab", "status": "CREATED"},
        status=201,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "bulk",
            "update",
            "--issue",
            "TEST-1",
            "-F",
            "priority=blocker",
            "--no-wait",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["status"] == "CREATED"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "issues": ["TEST-1"],
        "values": {"priority": "blocker"},
    }


@responses.activate
def test_update_wait_polls_to_terminal():
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_update",
        json={"id": "1ab", "status": "CREATED"},
        status=201,
    )
    responses.add(
        responses.GET, f"{BASE}/bulkchange/1ab", json={"id": "1ab", "status": "CREATED"}, status=200
    )
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab",
        json={"id": "1ab", "status": "COMPLETE"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "bulk",
            "update",
            "--query",
            "Queue: TEST",
            "-F",
            "priority=blocker",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["status"] == "COMPLETE"
    assert json.loads(responses.calls[0].request.body)["issues"] == "Queue: TEST"  # ty: ignore[invalid-argument-type]


@responses.activate
def test_move_command():
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_move",
        json={"id": "2cd", "status": "COMPLETE"},
        status=201,
    )
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/2cd",
        json={"id": "2cd", "status": "COMPLETE"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "bulk",
            "move",
            "CHECK",
            "--issue",
            "TEST-1",
            "--move-all-fields",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "queue": "CHECK",
        "issues": ["TEST-1"],
        "moveAllFields": True,
    }


@responses.activate
def test_transition_command():
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_transition",
        json={"id": "3ef", "status": "COMPLETE"},
        status=201,
    )
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/3ef",
        json={"id": "3ef", "status": "COMPLETE"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "bulk",
            "transition",
            "close",
            "--issue",
            "TEST-1",
            "-F",
            "resolution=fixed",
            "--no-wait",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "transition": "close",
        "issues": ["TEST-1"],
        "values": {"resolution": "fixed"},
    }


@responses.activate
def test_get_command():
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab",
        json={"id": "1ab", "status": "COMPLETE"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "bulk", "get", "1ab"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["status"] == "COMPLETE"


@responses.activate
def test_issues_command():
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab/issues",
        json=[{"issue": {"key": "TEST-1"}, "status": "FAILED"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "bulk", "issues", "1ab"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["status"] == "FAILED"
