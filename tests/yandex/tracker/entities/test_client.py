"""TDD for EntitiesClient — responses stub + session DI.

Covers every method: core CRUD/search/history/permissions/bulk, comments, checklists, links and
attachments (JSON reads, typed write bodies, the ``_relative`` drains and the binary download).
"""

import json
from urllib.parse import parse_qs, urlparse

import requests
import responses

from ycli.yandex.tracker.entities.client import EntitiesClient
from ycli.yandex.tracker.entities.models import (
    Attachment,
    AttachmentList,
    BulkChangeOperation,
    Comment,
    CommentList,
    Entity,
    EntityEventList,
    EntityList,
    ExtendedPermissions,
    LinkList,
)

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> EntitiesClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return EntitiesClient(session=session)


# ---- core --------------------------------------------------------------------------------


@responses.activate
def test_create_posts_body_and_returns_entity():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project",
        json={"id": "655f", "entityType": "project", "fields": {"summary": "Q4"}},
        status=200,
    )
    out = _client().create("project", body={"fields": {"summary": "Q4"}})
    assert isinstance(out, Entity)
    assert out.id == "655f" and out.fields is not None and out.fields.summary == "Q4"
    assert json.loads(responses.calls[0].request.body) == {"fields": {"summary": "Q4"}}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_get_returns_entity_with_expand_and_fields_query():
    responses.add(
        responses.GET,
        f"{BASE}/entities/goal/1",
        json={
            "id": "1",
            "entityType": "goal",
            "fields": {"summary": "Ship", "keyResultItems": [{"id": "k1", "type": "binary"}]},
        },
        status=200,
    )
    out = _client().get("goal", "1", expand="attachments", fields="keyResultItems")
    assert out.entity_type == "goal"
    assert out.fields is not None and out.fields.key_result_items[0].type == "binary"
    params = parse_qs(urlparse(responses.calls[0].request.url).query)  # ty: ignore[invalid-argument-type]
    assert params["expand"] == ["attachments"] and params["fields"] == ["keyResultItems"]


@responses.activate
def test_edit_patches_body():
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f",
        json={"id": "655f", "fields": {"summary": "New"}},
        status=200,
    )
    out = _client().edit("project", "655f", body={"fields": {"summary": "New"}})
    assert out.fields is not None and out.fields.summary == "New"
    assert responses.calls[0].request.method == "PATCH"


@responses.activate
def test_delete_with_board_sends_query():
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f", status=204)
    assert _client().delete("project", "655f", with_board=True) is None
    assert parse_qs(urlparse(responses.calls[0].request.url).query)["withBoard"] == ["True"]  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete_without_board_omits_query():
    responses.add(responses.DELETE, f"{BASE}/entities/goal/1", status=204)
    assert _client().delete("goal", "1") is None
    assert "withBoard" not in urlparse(responses.calls[0].request.url).query  # ty: ignore[unsupported-operator]


@responses.activate
def test_search_unwraps_values_to_entity_list():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/_search",
        json={"hits": 2, "pages": 1, "values": [{"id": "1"}, {"id": "2"}]},
        status=200,
    )
    out = _client().search("project", {"filter": {"entityStatus": "in_progress"}})
    assert isinstance(out, EntityList)
    assert [e.id for e in out.root] == ["1", "2"]
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "filter": {"entityStatus": "in_progress"}
    }


@responses.activate
def test_search_defaults_to_empty_body():
    responses.add(responses.POST, f"{BASE}/entities/goal/_search", json={"values": []}, status=200)
    out = _client().search("goal")
    assert out.root == []
    assert json.loads(responses.calls[0].request.body) == {}  # ty: ignore[invalid-argument-type]


def _history_callback(request):
    """Two-page relative history: page 1 → last event id e2, page 2 (from=e2) empty."""
    params = parse_qs(urlparse(request.url).query)
    if "from" not in params:
        body = {"events": [{"id": "e1"}, {"id": "e2"}], "hasNext": True}
    else:
        body = {"events": [], "hasNext": False}
    return (200, {}, json.dumps(body))


@responses.activate
def test_history_drains_relative_pages():
    responses.add_callback(
        responses.GET,
        f"{BASE}/entities/project/655f/events/_relative",
        callback=_history_callback,
        content_type="application/json",
    )
    out = _client().history("project", "655f")
    assert isinstance(out, EntityEventList)
    assert [e.id for e in out.root] == ["e1", "e2"]
    assert len(responses.calls) == 2
    assert "from=e2" in responses.calls[1].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_history_respects_limit():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/events/_relative",
        json={"events": [{"id": "e1"}, {"id": "e2"}, {"id": "e3"}], "hasNext": True},
        status=200,
    )
    out = _client().history("project", "655f", limit=2)
    assert [e.id for e in out.root] == ["e1", "e2"]
    assert len(responses.calls) == 1


@responses.activate
def test_permissions_returns_acl():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/extendedPermissions",
        json={"acl": {"READ": {"roles": ["OWNER"]}}, "permissionSources": [{"id": "67f"}]},
        status=200,
    )
    out = _client().permissions("project", "655f")
    assert isinstance(out, ExtendedPermissions)
    assert out.acl is not None and out.acl.read is not None and out.acl.read.roles == ["OWNER"]
    assert out.permission_sources[0].id == "67f"


@responses.activate
def test_set_permissions_patches_body():
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/extendedPermissions",
        json={"acl": {"WRITE": {"roles": ["MEMBER"]}}},
        status=200,
    )
    out = _client().set_permissions(
        "project", "655f", body={"acl": {"WRITE": {"roles": ["MEMBER"]}}}
    )
    assert out.acl is not None and out.acl.write is not None and out.acl.write.roles == ["MEMBER"]
    assert responses.calls[0].request.method == "PATCH"


@responses.activate
def test_bulk_update_posts_and_returns_operation():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/bulkchange/_update",
        json={"id": "656", "status": "CREATED"},
        status=200,
    )
    out = _client().bulk_update(
        "project", body={"metaEntities": ["1"], "values": {"comment": "done"}}
    )
    assert isinstance(out, BulkChangeOperation) and out.status == "CREATED"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "metaEntities": ["1"],
        "values": {"comment": "done"},
    }


@responses.activate
def test_bulk_status_reads_operation():
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/656",
        json={"id": "656", "status": "COMPLETE"},
        status=200,
    )
    out = _client().bulk_status("656")
    assert out.status == "COMPLETE"


# ---- comments ----------------------------------------------------------------------------


@responses.activate
def test_comments_list_returns_list():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/comments",
        json=[{"id": 22, "text": "Готово"}],
        status=200,
    )
    out = _client().comments_list("project", "655f")
    assert isinstance(out, CommentList) and out.root[0].text == "Готово"


def _comments_callback(request):
    """Two-page relative comments: page 1 → last longId lc2, page 2 (from=lc2) empty."""
    params = parse_qs(urlparse(request.url).query)
    if "from" not in params:
        body = {
            "comments": [
                {"id": 22, "longId": "lc1"},
                {"id": 23, "longId": "lc2"},
            ],
            "hasNext": True,
        }
    else:
        body = {"comments": [], "hasNext": False}
    return (200, {}, json.dumps(body))


@responses.activate
def test_comments_relative_drains_pages():
    responses.add_callback(
        responses.GET,
        f"{BASE}/entities/project/655f/comments/_relative",
        callback=_comments_callback,
        content_type="application/json",
    )
    out = _client().comments_relative("project", "655f")
    assert [c.id for c in out.root] == [22, 23]
    assert len(responses.calls) == 2
    assert "from=lc2" in responses.calls[1].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_comments_get_returns_comment():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/comments/22",
        json={"id": 22, "longId": "lc1", "text": "hi"},
        status=200,
    )
    out = _client().comments_get("project", "655f", "22")
    assert isinstance(out, Comment) and out.long_id == "lc1"


@responses.activate
def test_comments_create_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/comments",
        json={"id": 22, "text": "Готово"},
        status=200,
    )
    out = _client().comments_create("project", "655f", body={"text": "Готово"})
    assert out.id == 22
    assert json.loads(responses.calls[0].request.body) == {"text": "Готово"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_comments_edit_patches_body_with_id():
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/comments",
        json={"id": 22, "text": "fixed"},
        status=200,
    )
    out = _client().comments_edit("project", "655f", body={"id": 22, "text": "fixed"})
    assert out.text == "fixed"
    assert json.loads(responses.calls[0].request.body) == {"id": 22, "text": "fixed"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_comments_delete_returns_none():
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f/comments/22", status=204)
    assert _client().comments_delete("project", "655f", "22") is None
    assert responses.calls[0].request.method == "DELETE"


# ---- checklists --------------------------------------------------------------------------


@responses.activate
def test_checklists_create_posts_array():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/checklistItems",
        json={"id": "655f", "fields": {"checklistItems": [{"id": "5f", "text": "step"}]}},
        status=200,
    )
    out = _client().checklists_create("project", "655f", body=[{"text": "step"}])
    assert isinstance(out, Entity)
    assert out.fields is not None and out.fields.checklist_items[0].text == "step"
    assert json.loads(responses.calls[0].request.body) == [{"text": "step"}]  # ty: ignore[invalid-argument-type]


@responses.activate
def test_checklists_edit_patches_array():
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/checklistItems",
        json={"id": "655f", "fields": {"checklistItems": [{"id": "5f", "text": "renamed"}]}},
        status=200,
    )
    out = _client().checklists_edit("project", "655f", body=[{"id": "5f", "text": "renamed"}])
    assert out.fields is not None and out.fields.checklist_items[0].text == "renamed"
    assert json.loads(responses.calls[0].request.body) == [{"id": "5f", "text": "renamed"}]  # ty: ignore[invalid-argument-type]


@responses.activate
def test_checklists_edit_item_patches():
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/checklistItems/5f",
        json={"id": "655f", "fields": {"checklistItems": [{"id": "5f", "checked": True}]}},
        status=200,
    )
    out = _client().checklists_edit_item("project", "655f", "5f", body={"checked": True})
    assert out.fields is not None and out.fields.checklist_items[0].checked is True


@responses.activate
def test_checklists_delete_returns_entity():
    responses.add(
        responses.DELETE,
        f"{BASE}/entities/project/655f/checklistItems",
        json={"id": "655f", "fields": {"checklistItems": []}},
        status=200,
    )
    out = _client().checklists_delete("project", "655f")
    assert isinstance(out, Entity) and out.fields is not None and out.fields.checklist_items == []


@responses.activate
def test_checklists_delete_item_returns_entity():
    responses.add(
        responses.DELETE,
        f"{BASE}/entities/project/655f/checklistItems/5f",
        json={"id": "655f"},
        status=200,
    )
    out = _client().checklists_delete_item("project", "655f", "5f")
    assert out.id == "655f"


@responses.activate
def test_checklists_move_posts_before():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/checklistItems/5f/_move",
        json={"id": "655f"},
        status=200,
    )
    out = _client().checklists_move("project", "655f", "5f", body={"before": "6a"})
    assert out.id == "655f"
    assert json.loads(responses.calls[0].request.body) == {"before": "6a"}  # ty: ignore[invalid-argument-type]


# ---- links -------------------------------------------------------------------------------


@responses.activate
def test_links_list_returns_links():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/links",
        json=[{"type": "relates", "linkFieldValues": {"summary": "Other", "id": "658"}}],
        status=200,
    )
    out = _client().links_list("project", "655f")
    assert isinstance(out, LinkList)
    assert out.root[0].type == "relates"
    assert out.root[0].link_field_values is not None
    assert out.root[0].link_field_values.summary == "Other"


@responses.activate
def test_links_create_posts_body_returns_none():
    responses.add(responses.POST, f"{BASE}/entities/project/655f/links", status=200)
    result = _client().links_create(
        "project", "655f", body={"relationship": "relates", "entity": "658"}
    )
    assert result is None
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "relationship": "relates",
        "entity": "658",
    }


@responses.activate
def test_links_delete_sends_right_query():
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f/links", status=200)
    assert _client().links_delete("project", "655f", "658") is None
    assert parse_qs(urlparse(responses.calls[0].request.url).query)["right"] == ["658"]  # ty: ignore[invalid-argument-type]


# ---- attachments -------------------------------------------------------------------------


@responses.activate
def test_attachments_list_returns_list():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/attachments",
        json=[{"id": "3", "name": "Shops.csv", "size": 559, "mimetype": "text/csv"}],
        status=200,
    )
    out = _client().attachments_list("project", "655f")
    assert isinstance(out, AttachmentList) and out.root[0].name == "Shops.csv"


@responses.activate
def test_attachments_get_returns_metadata():
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/attachments/5",
        json={"id": "5", "name": "flowers.jpg", "metadata": {"size": "236x295"}},
        status=200,
    )
    out = _client().attachments_get("project", "655f", "5")
    assert isinstance(out, Attachment)
    assert out.name == "flowers.jpg"
    assert out.metadata is not None and out.metadata.size == "236x295"


@responses.activate
def test_attachment_download_returns_raw_bytes():
    responses.add(
        responses.GET, f"{BASE}/attachments/5/flowers.jpg", body=b"\xff\xd8\xff\xe0jpg", status=200
    )
    out = _client().attachment_download("5", "flowers.jpg")
    assert out == b"\xff\xd8\xff\xe0jpg"


@responses.activate
def test_attachments_attach_posts_and_returns_entity():
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/attachments/tmp9",
        json={"id": "655f", "entityType": "project"},
        status=200,
    )
    out = _client().attachments_attach("project", "655f", "tmp9")
    assert isinstance(out, Entity) and out.id == "655f"
    assert responses.calls[0].request.method == "POST"


@responses.activate
def test_attachments_delete_returns_entity():
    responses.add(
        responses.DELETE,
        f"{BASE}/entities/project/655f/attachments/5",
        json={"id": "655f"},
        status=200,
    )
    out = _client().attachments_delete("project", "655f", "5")
    assert out.id == "655f"
    assert responses.calls[0].request.method == "DELETE"
