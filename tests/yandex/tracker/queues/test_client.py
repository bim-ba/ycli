"""TDD for QueuesClient — list drains page/perPage pages; get returns one Queue."""

import json

import requests
import responses

from ycli.yandex.tracker.queues.client import QueuesClient
from ycli.yandex.tracker.queues.models import (
    Queue,
    QueueCreate,
    QueueFieldList,
    QueueList,
    QueuePermissions,
    QueuePermissionScope,
    QueuePermissionsUpdate,
    QueueTagList,
    QueueTagRemove,
    QueueVersionCreate,
    QueueVersionInfo,
    QueueVersionInfoList,
)

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> QueuesClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return QueuesClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/queues/",
        json=[{"id": "3", "key": "TEST"}, {"id": "4", "key": "DEMO"}],
        status=200,
    )
    out = _client().list()
    assert isinstance(out, QueueList)
    assert [q.key for q in out.root] == ["TEST", "DEMO"]
    assert responses.calls[0].request.params["page"] == "1"  # ty: ignore[unresolved-attribute]
    assert responses.calls[0].request.params["perPage"] == "50"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_drains_two_offset_pages():
    full_page = [{"id": str(index), "key": f"Q{index}"} for index in range(50)]  # exactly page_size
    responses.add(responses.GET, f"{BASE}/queues/", json=full_page, status=200)
    responses.add(responses.GET, f"{BASE}/queues/", json=[{"id": "50", "key": "TAIL"}], status=200)
    out = _client().list()
    assert len(out.root) == 51 and out.root[-1].key == "TAIL"  # both pages drained
    assert len(responses.calls) == 2
    assert responses.calls[1].request.params["page"] == "2"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_respects_limit_without_extra_fetch():
    responses.add(
        responses.GET,
        f"{BASE}/queues/",
        json=[{"key": "A"}, {"key": "B"}, {"key": "C"}],
        status=200,
    )
    out = _client().list(limit=2)
    assert [q.key for q in out.root] == ["A", "B"]  # truncated to the cap
    assert len(responses.calls) == 1


@responses.activate
def test_get_returns_single_queue_with_expand():
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST",
        json={
            "id": "3",
            "key": "TEST",
            "name": "Test",
            "version": 5,
            "lead": {"id": "11", "display": "Ivan"},
            "defaultType": {"key": "task", "display": "Task"},
            "assignAuto": False,
            "issueTypes": [{"key": "task"}, {"key": "bug"}],
            "workflows": {"dev": [{"key": "task"}]},
        },
        status=200,
    )
    q = _client().get("TEST", expand="all")
    assert isinstance(q, Queue)
    assert q.key == "TEST" and q.version == 5
    assert q.lead.display == "Ivan"
    assert q.default_type.key == "task"
    assert [t.key for t in q.issue_types] == ["task", "bug"]
    assert q.workflows["dev"][0].key == "task"
    assert responses.calls[0].request.params["expand"] == "all"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_get_without_expand_sends_no_query():
    responses.add(responses.GET, f"{BASE}/queues/TEST", json={"id": "3", "key": "TEST"}, status=200)
    q = _client().get("TEST")
    assert q.key == "TEST"
    assert "expand" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]


@responses.activate
def test_tags_returns_flat_string_list():
    responses.add(responses.GET, f"{BASE}/queues/TEST/tags", json=["tag1", "tag2"], status=200)
    out = _client().tags("TEST")
    assert isinstance(out, QueueTagList)
    assert out.root == ["tag1", "tag2"]


@responses.activate
def test_versions_returns_version_list():
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST/versions",
        json=[{"id": 1, "name": "v0.1", "released": False, "queue": {"key": "TEST"}}],
        status=200,
    )
    out = _client().versions("TEST")
    assert isinstance(out, QueueVersionInfoList)
    assert out.root[0].name == "v0.1" and out.root[0].queue.key == "TEST"


@responses.activate
def test_fields_returns_field_list():
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST/fields",
        json=[{"id": "myfield", "name": "My field", "schema": {"type": "string"}, "order": 222}],
        status=200,
    )
    out = _client().fields("TEST")
    assert isinstance(out, QueueFieldList)
    assert out.root[0].id == "myfield" and out.root[0].field_schema == {"type": "string"}


@responses.activate
def test_create_posts_typed_body():
    responses.add(
        responses.POST, f"{BASE}/queues/", json={"id": "111", "key": "DESIGN"}, status=201
    )
    q = _client().create(
        QueueCreate(
            key="DESIGN",
            name="Design",
            lead="username",
            default_type="task",
            default_priority="normal",
        )
    )
    assert isinstance(q, Queue) and q.key == "DESIGN"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "key": "DESIGN",
        "name": "Design",
        "lead": "username",
        "defaultType": "task",
        "defaultPriority": "normal",
    }


@responses.activate
def test_create_includes_issue_types_config():
    responses.add(responses.POST, f"{BASE}/queues/", json={"key": "DESIGN"}, status=201)
    _client().create(
        QueueCreate(
            key="DESIGN",
            name="Design",
            lead="u",
            default_type="task",
            default_priority="normal",
            issue_types_config=[  # ty: ignore[invalid-argument-type]
                {"issueType": "task", "workflow": "oicn", "resolutions": ["wontFix"]}
            ],
        )
    )
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["issueTypesConfig"] == [
        {"issueType": "task", "workflow": "oicn", "resolutions": ["wontFix"]}
    ]


@responses.activate
def test_delete_issues_delete_and_returns_response():
    responses.add(responses.DELETE, f"{BASE}/queues/TEST", status=204)
    resp = _client().delete("TEST")
    assert resp.status_code == 204
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_restore_returns_queue():
    responses.add(
        responses.POST, f"{BASE}/queues/TEST/_restore", json={"id": "3", "key": "TEST"}, status=200
    )
    q = _client().restore("TEST")
    assert isinstance(q, Queue) and q.key == "TEST"
    assert responses.calls[0].request.method == "POST"


@responses.activate
def test_set_permissions_patches_typed_body():
    responses.add(
        responses.PATCH,
        f"{BASE}/queues/TEST/permissions",
        json={"self": "x", "version": 11},
        status=200,
    )
    perms = _client().set_permissions(
        "TEST", QueuePermissionsUpdate(create=QueuePermissionScope(roles=["author"]))
    )
    assert isinstance(perms, QueuePermissions) and perms.version == 11
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "create": {"roles": ["author"]}
    }


@responses.activate
def test_tag_remove_posts_tag_body():
    responses.add(responses.POST, f"{BASE}/queues/TEST/tags/_remove", status=204)
    resp = _client().tag_remove("TEST", QueueTagRemove(tag="obsolete"))
    assert resp.status_code == 204
    assert json.loads(responses.calls[0].request.body) == {"tag": "obsolete"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_version_create_posts_body_to_versions():
    responses.add(responses.POST, f"{BASE}/versions/", json={"id": 1, "name": "v0.1"}, status=200)
    version = _client().version_create(QueueVersionCreate(queue="TEST", name="v0.1"))
    assert isinstance(version, QueueVersionInfo) and version.name == "v0.1"
    assert responses.calls[0].request.url == f"{BASE}/versions/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "queue": "TEST",
        "name": "v0.1",
    }
