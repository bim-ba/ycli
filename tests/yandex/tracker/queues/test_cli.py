"""TDD for the `tracker queues` CLI (runs after the integrator mounts the resource)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

runner = CliRunner()


@responses.activate
def test_queues_list():
    responses.add(responses.GET, f"{BASE}/queues/", json=[{"id": "3", "key": "TEST"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "TEST"


@responses.activate
def test_queues_list_all_flag():
    responses.add(responses.GET, f"{BASE}/queues/", json=[{"key": "TEST"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "list", "--all"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "TEST"


@responses.activate
def test_queues_get_with_expand():
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST",
        json={"id": "3", "key": "TEST", "name": "Test"},
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "queues", "get", "TEST", "--expand", "all"]
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "TEST"
    assert responses.calls[0].request.params["expand"] == "all"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_queues_get_without_expand():
    responses.add(responses.GET, f"{BASE}/queues/TEST", json={"id": "3", "key": "TEST"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "get", "TEST"])
    assert res.exit_code == 0
    assert "expand" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]


@responses.activate
def test_queues_tags():
    responses.add(responses.GET, f"{BASE}/queues/TEST/tags", json=["tag1"], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "tags", "TEST"])
    assert res.exit_code == 0 and json.loads(res.stdout) == ["tag1"]


@responses.activate
def test_queues_versions():
    responses.add(
        responses.GET, f"{BASE}/queues/TEST/versions", json=[{"id": 1, "name": "v0.1"}], status=200
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "versions", "TEST"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["name"] == "v0.1"


@responses.activate
def test_queues_fields():
    responses.add(responses.GET, f"{BASE}/queues/TEST/fields", json=[{"id": "myfield"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "fields", "TEST"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "myfield"


@responses.activate
def test_queues_create():
    responses.add(responses.POST, f"{BASE}/queues/", json={"key": "DESIGN"}, status=201)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "queues",
            "create",
            "--key",
            "DESIGN",
            "--name",
            "Design",
            "--lead",
            "u",
            "--default-type",
            "task",
            "--default-priority",
            "normal",
            "--issue-type-config",
            '{"issueType":"task","workflow":"oicn"}',
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "DESIGN"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["key"] == "DESIGN"
    assert sent["issueTypesConfig"] == [{"issueType": "task", "workflow": "oicn"}]


@responses.activate
def test_queues_delete():
    responses.add(responses.DELETE, f"{BASE}/queues/TEST", status=204)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "delete", "TEST"])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "deleted queue TEST"}


@responses.activate
def test_queues_restore():
    responses.add(responses.POST, f"{BASE}/queues/TEST/_restore", json={"key": "TEST"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "restore", "TEST"])
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "TEST"


@responses.activate
def test_queues_permissions():
    responses.add(
        responses.PATCH, f"{BASE}/queues/TEST/permissions", json={"version": 11}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "queues",
            "permissions",
            "TEST",
            "--grant",
            '{"roles": {"add": ["author"]}}',
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["version"] == 11
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "grant": {"roles": {"add": ["author"]}}
    }


@responses.activate
def test_queues_tag_remove():
    responses.add(responses.POST, f"{BASE}/queues/TEST/tags/_remove", status=204)
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "queues", "tag-remove", "TEST", "obsolete"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {
        "ok": True,
        "detail": "removed tag 'obsolete' from queue TEST",
    }
    assert json.loads(responses.calls[0].request.body) == {"tag": "obsolete"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_queues_version_create():
    responses.add(responses.POST, f"{BASE}/versions/", json={"id": 1, "name": "v0.1"}, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "queues",
            "version-create",
            "--queue",
            "TEST",
            "--name",
            "v0.1",
            "--start-date",
            "2023-10-03",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["name"] == "v0.1"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "queue": "TEST",
        "name": "v0.1",
        "startDate": "2023-10-03",
    }
