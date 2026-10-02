"""TDD for the `tracker localfields` CLI (runs after the integrator mounts the resource)."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

pytestmark = pytest.mark.integration

runner = CliRunner()


@responses.activate
def test_localfields_list():
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields",
        json=[{"key": "loc_field_key", "name": "Loc field"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "localfields", "list", "ORG"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "loc_field_key"


@responses.activate
def test_localfields_get():
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields/loc_field_key",
        json={"key": "loc_field_key", "name": "loc_field_name", "schema": {"type": "string"}},
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "localfields", "get", "ORG", "loc_field_key"]
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "loc_field_key"


@responses.activate
def test_localfields_create():
    responses.add(responses.POST, f"{BASE}/queues/ORG/localFields", json={"key": "loc"}, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "localfields",
            "create",
            "ORG",
            "--id",
            "loc",
            "--type",
            "StringFieldType",
            "--category",
            "1",
            "--name-ru",
            "Поле",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "loc"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": {"ru": "Поле"}, "id": "loc", "category": "1", "type": "StringFieldType"}


@responses.activate
def test_localfields_create_with_options():
    responses.add(responses.POST, f"{BASE}/queues/ORG/localFields", json={"key": "loc"}, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "localfields",
            "create",
            "ORG",
            "--id",
            "loc",
            "--type",
            "StringFieldType",
            "--category",
            "1",
            "--name-en",
            "Drop",
            "--option",
            "a",
            "--option",
            "b",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "loc"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["optionsProvider"] == {"type": "FixedListOptionsProvider", "values": ["a", "b"]}


@responses.activate
def test_localfields_edit_no_version():
    responses.add(
        responses.PATCH, f"{BASE}/queues/ORG/localFields/loc", json={"key": "loc"}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "localfields",
            "edit",
            "ORG",
            "loc",
            "--order",
            "102",
            "--hidden",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "loc"
    assert "version=" not in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"order": 102, "hidden": True}


@responses.activate
def test_localfields_create_no_readonly_sends_false():
    """--no-readonly is sent as readonly=false instead of being dropped."""
    responses.add(responses.POST, f"{BASE}/queues/ORG/localFields", json={"id": "f"}, status=201)
    res = runner.invoke(
        cli.app,
        [
            "tracker",
            "localfields",
            "create",
            "ORG",
            "--id",
            "f",
            "--type",
            "StringFieldType",
            "--category",
            "1",
            "--no-readonly",
        ],
    )
    assert res.exit_code == 0, res.output
    body = responses.calls[0].request.body
    assert isinstance(body, str | bytes)
    assert json.loads(body)["readonly"] is False
