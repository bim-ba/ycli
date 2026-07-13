"""CLI wiring for `tracker fields` (list + get)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@responses.activate
def test_fields_list():
    responses.add(
        responses.GET,
        f"{BASE}/fields",
        json=[{"id": "ruName", "key": "ruName", "schema": {"type": "string"}}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "fields", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "ruName"


@responses.activate
def test_fields_get():
    responses.add(
        responses.GET,
        f"{BASE}/fields/ruName",
        json={"id": "ruName", "name": "Field"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "fields", "get", "ruName"])
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == "ruName"


@responses.activate
def test_fields_create():
    responses.add(responses.POST, f"{BASE}/fields", json={"id": "myField"}, status=201)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "fields",
            "create",
            "--id",
            "myField",
            "--type",
            "StringFieldType",
            "--category",
            "1",
            "--name-ru",
            "Поле",
            "--option",
            "a",
            "--option",
            "b",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == "myField"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {
        "name": {"ru": "Поле"},
        "id": "myField",
        "category": "1",
        "type": "StringFieldType",
        "optionsProvider": {"type": "FixedListOptionsProvider", "values": ["a", "b"]},
    }


@responses.activate
def test_fields_edit_sends_version():
    responses.add(responses.PATCH, f"{BASE}/fields/ruName", json={"id": "ruName"}, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "fields",
            "edit",
            "ruName",
            "--name-ru",
            "Имя",
            "--version",
            "3",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == "ruName"
    assert "version=3" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_fields_category_create():
    responses.add(
        responses.POST, f"{BASE}/fields/categories", json={"id": "604f99", "version": 1}, status=201
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "fields",
            "category-create",
            "--name-ru",
            "Своя",
            "--order",
            "400",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == "604f99"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": {"ru": "Своя"}, "order": 400}


@responses.activate
def test_fields_category_edit_sends_version():
    responses.add(
        responses.PATCH,
        f"{BASE}/fields/categories/604f99",
        json={"id": "604f99", "version": 2},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "fields",
            "category-edit",
            "604f99",
            "--order",
            "500",
            "--version",
            "1",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["version"] == 2
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
