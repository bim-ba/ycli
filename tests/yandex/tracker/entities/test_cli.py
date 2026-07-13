"""TDD for `tracker entities` CLI — every subcommand branch.

NOTE: these invoke the ROOT app (``cli.app``), so they pass only after the integrator mounts
the resource (``app.add_typer(entities_app)`` in tracker/cli.py). The producer self-validates
test_client / test_models / test_mcp only.
"""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

runner = CliRunner()


def _invoke(*args):
    return runner.invoke(cli.app, ["--format", "json", "tracker", "entities", *args])


# ---- core --------------------------------------------------------------------------------


@responses.activate
def test_get():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f",
        json={"id": "655f", "fields": {"summary": "Q4"}},
        status=200,
    )
    res = _invoke("get", "project", "655f", "--fields", "summary", "--expand", "attachments")
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == "655f"


@responses.activate
def test_create_assembles_typed_fields_body():
    responses.add(responses.POST, f"{BASE}/entities/goal", json={"id": "1"}, status=200)
    res = _invoke(
        "create",
        "goal",
        "--summary",
        "Ship",
        "--lead",
        "u1",
        "--parent",
        "67f",
        "--team-user",
        "u2",
        "--tag",
        "q4",
        "--field",
        "entityStatus=at_risk",
    )
    assert res.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {
        "fields": {
            "summary": "Ship",
            "lead": "u1",
            "teamUsers": ["u2"],
            "tags": ["q4"],
            "parentEntity": {"primary": "67f"},
            "entityStatus": "at_risk",
        }
    }


@responses.activate
def test_edit_with_fields_and_comment():
    responses.add(responses.PATCH, f"{BASE}/entities/project/655f", json={"id": "655f"}, status=200)
    res = _invoke("edit", "project", "655f", "--summary", "New", "--comment", "done")
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "fields": {"summary": "New"},
        "comment": "done",
    }


@responses.activate
def test_edit_comment_only_omits_fields():
    responses.add(responses.PATCH, f"{BASE}/entities/project/655f", json={"id": "655f"}, status=200)
    res = _invoke("edit", "project", "655f", "--comment", "note")
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {"comment": "note"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete_with_board():
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f", status=204)
    res = _invoke("delete", "project", "655f", "--with-board")
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "deleted project 655f"}


@responses.activate
def test_delete_plain():
    responses.add(responses.DELETE, f"{BASE}/entities/goal/1", status=204)
    res = _invoke("delete", "goal", "1")
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "deleted goal 1"}


@responses.activate
def test_search_all_options():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/_search",
        json={"values": [{"id": "1"}]},
        status=200,
    )
    res = _invoke(
        "search",
        "project",
        "--input",
        "Q4",
        "--filter",
        "entityStatus=in_progress",
        "--order-by",
        "entityStatus",
        "--order-asc",
        "--root-only",
    )
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "1"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "input": "Q4",
        "filter": {"entityStatus": "in_progress"},
        "orderBy": "entityStatus",
        "orderAsc": True,
        "rootOnly": True,
    }


@responses.activate
def test_history():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/events/_relative",
        json={"events": [{"id": "e1"}], "hasNext": False},
        status=200,
    )
    res = _invoke("history", "project", "655f", "--limit", "5")
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "e1"


@responses.activate
def test_permissions():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/extendedPermissions",
        json={"acl": {"READ": {"roles": ["OWNER"]}}},
        status=200,
    )
    res = _invoke("permissions", "project", "655f")
    assert res.exit_code == 0 and json.loads(res.stdout)["acl"]["READ"]["roles"] == ["OWNER"]


@responses.activate
def test_set_permissions_sends_grant_action():
    # The live API accepts only grant/revoke actions inside acl (LEVEL=… top-level keys 422).
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/extendedPermissions",
        json={"acl": {"READ": {"users": [{"id": "800"}]}}},
        status=200,
    )
    res = _invoke("set-permissions", "project", "655f", "--acl", 'grant={"READ":{"users":["800"]}}')
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "acl": {"grant": {"READ": {"users": ["800"]}}}
    }


@responses.activate
def test_bulk():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/bulkchange/_update",
        json={"id": "656", "status": "CREATED"},
        status=200,
    )
    res = _invoke(
        "bulk",
        "project",
        "--entity",
        "1",
        "--entity",
        "2",
        "--comment",
        "done",
        "--field",
        "lead=u1",
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["status"] == "CREATED"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "metaEntities": ["1", "2"],
        "values": {"fields": {"lead": "u1"}, "comment": "done"},
    }


@responses.activate
def test_bulk_status():
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/656",
        json={"id": "656", "status": "COMPLETE"},
        status=200,
    )
    res = _invoke("bulk-status", "656")
    assert res.exit_code == 0 and json.loads(res.stdout)["status"] == "COMPLETE"


@responses.activate
def test_create_report_builds_typed_body():
    responses.add(
        responses.POST,
        f"{BASE}/entities/report/",
        json={"id": "68f", "entityType": "report"},
        status=200,
    )
    res = _invoke(
        "create-report",
        "--summary",
        "Export",
        "--query",
        "Queue: SUPPORT",
        "--field",
        "key",
        "--field",
        "summary",
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["entityType"] == "report"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "fields": {
            "summary": "Export",
            "parameters": {
                "type": "issueFilterExport",
                "format": "xlsx",
                "filter": {"query": "Queue: SUPPORT"},
                "fields": ["key", "summary"],
            },
        }
    }


# ---- comments ----------------------------------------------------------------------------


@responses.activate
def test_comments_list():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/comments",
        json=[{"id": 22, "text": "hi"}],
        status=200,
    )
    res = _invoke("comments", "list", "project", "655f")
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["text"] == "hi"


@responses.activate
def test_comments_list_all_drains_relative():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/comments/_relative",
        json={"comments": [{"id": 22, "longId": "lc1"}], "hasNext": False},
        status=200,
    )
    res = _invoke("comments", "list", "project", "655f", "--all", "--limit", "10")
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == 22


@responses.activate
def test_comments_get():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/comments/22",
        json={"id": 22, "text": "hi"},
        status=200,
    )
    res = _invoke("comments", "get", "project", "655f", "22")
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 22


@responses.activate
def test_comments_create():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/comments",
        json={"id": 22, "text": "Готово"},
        status=200,
    )
    res = _invoke("comments", "create", "project", "655f", "--text", "Готово", "--summon", "u1")
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {"text": "Готово", "summonees": ["u1"]}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_comments_edit_patches_per_comment_route():
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/comments/22",
        json={"id": 22, "text": "fixed"},
        status=200,
    )
    res = _invoke("comments", "edit", "project", "655f", "22", "--text", "fixed")
    assert res.exit_code == 0
    assert responses.calls[0].request.url == f"{BASE}/entities/project/655f/comments/22"
    assert json.loads(responses.calls[0].request.body) == {"text": "fixed"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_comments_delete():
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f/comments/22", status=204)
    res = _invoke("comments", "delete", "project", "655f", "22")
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "deleted comment 22 on project 655f"}


# ---- checklists --------------------------------------------------------------------------


@responses.activate
def test_checklists_create():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/checklistItems",
        json={"id": "655f"},
        status=200,
    )
    res = _invoke("checklists", "create", "project", "655f", "--text", "a", "--text", "b")
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == [{"text": "a"}, {"text": "b"}]  # ty: ignore[invalid-argument-type]


@responses.activate
def test_checklists_edit():
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/checklistItems",
        json={"id": "655f"},
        status=200,
    )
    res = _invoke("checklists", "edit", "project", "655f", "--item", "5f=renamed")
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == [{"id": "5f", "text": "renamed"}]  # ty: ignore[invalid-argument-type]


@responses.activate
def test_checklists_edit_item():
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/checklistItems/5f",
        json={"id": "655f"},
        status=200,
    )
    res = _invoke(
        "checklists",
        "edit-item",
        "project",
        "655f",
        "5f",
        "--text",
        "x",
        "--checked",
        "--assignee",
        "u1",
        "--deadline",
        "2025-12-01T00:00:00.000+0000",
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "text": "x",
        "checked": True,
        "assignee": "u1",
        "deadline": {"date": "2025-12-01T00:00:00.000+0000", "deadlineType": "date"},
    }


@responses.activate
def test_checklists_delete_item():
    responses.add(
        responses.DELETE,
        f"{BASE}/entities/project/655f/checklistItems/5f",
        json={"id": "655f"},
        status=200,
    )
    res = _invoke("checklists", "delete-item", "project", "655f", "5f")
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == "655f"


@responses.activate
def test_checklists_delete_all():
    responses.add(
        responses.DELETE,
        f"{BASE}/entities/project/655f/checklistItems",
        json={"id": "655f"},
        status=200,
    )
    res = _invoke("checklists", "delete", "project", "655f")
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == "655f"


@responses.activate
def test_checklists_move():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/checklistItems/5f/_move",
        json={"id": "655f"},
        status=200,
    )
    res = _invoke("checklists", "move", "project", "655f", "5f", "--before", "6a")
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {"before": "6a"}  # ty: ignore[invalid-argument-type]


# ---- links -------------------------------------------------------------------------------


@responses.activate
def test_links_list():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/links",
        json=[{"type": "relates"}],
        status=200,
    )
    res = _invoke("links", "list", "project", "655f")
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["type"] == "relates"


@responses.activate
def test_links_create():
    responses.add(responses.POST, f"{BASE}/entities/project/655f/links", status=200)
    res = _invoke(
        "links", "create", "project", "655f", "--relationship", "relates", "--entity", "658"
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {
        "ok": True,
        "detail": "linked project 655f -> 658 (relates)",
    }
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "relationship": "relates",
        "entity": "658",
    }


@responses.activate
def test_links_delete():
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f/links", status=200)
    res = _invoke("links", "delete", "project", "655f", "658")
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "unlinked project 655f -> 658"}


# ---- attachments -------------------------------------------------------------------------


@responses.activate
def test_attachments_list():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/attachments",
        json=[{"id": "3", "name": "Shops.csv"}],
        status=200,
    )
    res = _invoke("attachments", "list", "project", "655f")
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["name"] == "Shops.csv"


@responses.activate
def test_attachments_get():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/attachments/5",
        json={"id": "5", "name": "flowers.jpg"},
        status=200,
    )
    res = _invoke("attachments", "get", "project", "655f", "5")
    assert res.exit_code == 0 and json.loads(res.stdout)["name"] == "flowers.jpg"


@responses.activate
def test_attachments_download_writes_bytes(tmp_path):
    responses.add(
        responses.GET, f"{BASE}/attachments/5/flowers.jpg", body=b"\xff\xd8jpg", status=200
    )
    out = tmp_path / "flowers.jpg"
    res = runner.invoke(
        cli.app,
        [
            "tracker",
            "entities",
            "attachments",
            "download",
            "5",
            "flowers.jpg",
            "--output",
            str(out),
        ],
    )
    assert res.exit_code == 0 and out.read_bytes() == b"\xff\xd8jpg"


@responses.activate
def test_attachments_attach():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/attachments/tmp9",
        json={"id": "655f"},
        status=200,
    )
    res = _invoke("attachments", "attach", "project", "655f", "tmp9")
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == "655f"


@responses.activate
def test_attachments_delete_serializes_ack_on_empty_body():
    # The live API answers 200 with an EMPTY body — parsing it as JSON crashed (regression).
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f/attachments/5", status=200)
    res = _invoke("attachments", "delete", "project", "655f", "5")
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {
        "ok": True,
        "detail": "deleted attachment 5 on project 655f",
    }
