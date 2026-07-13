"""TDD for ChecklistsClient — get (array) + create/edit/delete/clear (issue wrapper)."""

import json

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.checklists.client import ChecklistsClient
from ycli.yandex.tracker.checklists.models import Checklist, ChecklistItemList


def _client() -> ChecklistsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return ChecklistsClient(session=s)


@responses.activate
def test_get_returns_item_list():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/checklistItems",
        json=[
            {
                "id": "5f",
                "text": "step 1",
                "checked": False,
                "assignee": {"display": "Сава"},
                "deadline": {"date": "2021-05-09T00:00:00.000+0000", "deadlineType": "date"},
                "checklistItemType": "standard",
            }
        ],
        status=200,
    )
    out = _client().get("DE-1")
    assert isinstance(out, ChecklistItemList)
    item = out.root[0]
    assert item.text == "step 1" and item.assignee == "Сава"
    assert item.deadline is not None and item.deadline.deadline_type == "date"


@responses.activate
def test_create_posts_body_returns_wrapper():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/checklistItems",
        json={
            "key": "DE-1",
            "checklistItems": [{"id": "5f", "text": "step 1"}],
            "checklistTotal": 1,
        },
        status=200,
    )
    out = _client().create("DE-1", body={"text": "step 1"})
    assert isinstance(out, Checklist) and out.key == "DE-1"
    assert out.checklist_items[0].text == "step 1" and out.checklist_total == 1
    assert responses.calls[0].request.method == "POST"
    assert json.loads(responses.calls[0].request.body) == {"text": "step 1"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_edit_patches_item():
    responses.add(
        responses.PATCH,
        f"{BASE}/issues/DE-1/checklistItems/5f",
        json={"key": "DE-1", "checklistItems": [{"id": "5f", "checked": True}]},
        status=200,
    )
    out = _client().edit("DE-1", "5f", body={"checked": True})
    assert isinstance(out, Checklist) and out.checklist_items[0].checked is True
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"checked": True}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete_item_returns_wrapper():
    responses.add(
        responses.DELETE,
        f"{BASE}/issues/DE-1/checklistItems/5f",
        json={"key": "DE-1", "checklistTotal": 0},
        status=200,
    )
    out = _client().delete("DE-1", "5f")
    assert isinstance(out, Checklist) and out.checklist_total == 0
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_clear_deletes_whole_checklist():
    responses.add(
        responses.DELETE,
        f"{BASE}/issues/DE-1/checklistItems",
        json={"key": "DE-1"},
        status=200,
    )
    out = _client().clear("DE-1")
    assert isinstance(out, Checklist) and out.checklist_items == []
    assert responses.calls[0].request.method == "DELETE"
