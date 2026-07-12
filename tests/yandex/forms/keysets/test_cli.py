"""TDD for `forms keysets` CLI (needs the resource mounted by the integrator to pass)."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"
KID = 7
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_list_dumps_keysets():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/keysets",
        json=[{"id": 7, "name": "Q1"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "keysets", "list", SID])
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["id"] == 7


@responses.activate
def test_get_dumps_keyset():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/keysets/{KID}",
        json={"id": KID, "name": "Q1"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "keysets", "get", SID, str(KID)])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == KID


@responses.activate
def test_create_sends_typed_body():
    responses.add(
        responses.POST, f"{BASE}/surveys/{SID}/keysets", json={"id": KID, "name": "Q1"}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "keysets",
            "create",
            SID,
            "--name",
            "Q1",
            "--total",
            "250",
            "--enabled",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Q1",
        "total": 250,
        "is_enabled": True,
    }


@responses.activate
def test_create_requires_enabled_flag():
    """The live API rejects a create without ``is_enabled``, so the CLI requires
    --enabled/--disabled — omitting it is a usage error before any request is sent."""
    responses.add(responses.POST, f"{BASE}/surveys/{SID}/keysets", json={}, status=200)
    res = runner.invoke(
        cli.app, ["forms", "keysets", "create", SID, "--name", "Q1", "--total", "250"]
    )
    assert res.exit_code != 0
    assert len(responses.calls) == 0  # rejected at arg-parse; no is_enabled-less body was sent


@responses.activate
def test_modify_sends_full_record():
    """PATCH replaces the whole key set, so modify sends name + total + is_enabled together."""
    responses.add(
        responses.PATCH,
        f"{BASE}/surveys/{SID}/keysets/{KID}",
        json={"id": KID, "name": "Q2", "total": 300, "is_enabled": False},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "keysets",
            "modify",
            SID,
            str(KID),
            "--name",
            "Q2",
            "--total",
            "300",
            "--disabled",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Q2",
        "total": 300,
        "is_enabled": False,
    }


@responses.activate
def test_modify_requires_full_record():
    """The API rejects a partial PATCH (name+total+is_enabled all required), so the CLI requires
    every field — omitting one is a usage error before any request is sent (no partial PATCH)."""
    responses.add(responses.PATCH, f"{BASE}/surveys/{SID}/keysets/{KID}", json={}, status=200)
    res = runner.invoke(cli.app, ["forms", "keysets", "modify", SID, str(KID), "--name", "Q2"])
    assert res.exit_code != 0
    assert len(responses.calls) == 0  # rejected at arg-parse; no partial body was ever sent


@responses.activate
def test_delete_keyset():
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}/keysets/{KID}", status=200)
    res = runner.invoke(cli.app, ["--format", "json", "forms", "keysets", "delete", SID, str(KID)])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {
        "ok": True,
        "detail": f"deleted keyset {KID} on survey {SID}",
    }


@responses.activate
def test_download_writes_bytes_to_output(tmp_path):
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/keysets/{KID}/download",
        body=b"key1,link1\n",
        status=200,
    )
    target = tmp_path / "keys.csv"
    res = runner.invoke(
        cli.app,
        ["forms", "keysets", "download", SID, str(KID), "--output", str(target)],
    )
    assert res.exit_code == 0
    assert target.read_bytes() == b"key1,link1\n"
