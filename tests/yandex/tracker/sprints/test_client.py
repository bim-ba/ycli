"""TDD for SprintsClient — list/get reads + create/edit/delete/start/archive writes."""

import json

import requests
import responses

from ycli.yandex.tracker.sprints.client import SprintsClient
from ycli.yandex.tracker.sprints.models import (
    Sprint,
    SprintBoardInput,
    SprintCreate,
    SprintList,
    SprintUpdate,
)

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> SprintsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return SprintsClient(session=s)


@responses.activate
def test_list_returns_board_sprints():
    responses.add(
        responses.GET,
        f"{BASE}/boards/3/sprints",
        json=[{"id": 4405, "name": "Sprint 1", "status": "in_progress"}],
        status=200,
    )
    out = _client().list(board_id=3)
    assert isinstance(out, SprintList)
    assert out.root[0].name == "Sprint 1" and out.root[0].status == "in_progress"
    assert responses.calls[0].request.url == f"{BASE}/boards/3/sprints"


@responses.activate
def test_get_returns_sprint_with_board_ref():
    responses.add(
        responses.GET,
        f"{BASE}/sprints/4405",
        json={
            "id": 4405,
            "name": "Sprint 1",
            "status": "in_progress",
            "board": {"id": "3", "display": "My board"},
        },
        status=200,
    )
    sprint = _client().get(sprint_id=4405)
    assert isinstance(sprint, Sprint) and sprint.id == 4405
    assert sprint.board.id == "3" and sprint.board.display == "My board"


@responses.activate
def test_create_posts_typed_body_with_nested_board():
    responses.add(responses.POST, f"{BASE}/sprints", json={"id": 4405, "name": "New"}, status=201)
    sprint = _client().create(
        SprintCreate(
            name="New Sprint",
            board=SprintBoardInput(id="1"),
            start_date="2018-10-21",
            end_date="2018-10-24",
        )
    )
    assert isinstance(sprint, Sprint) and sprint.id == 4405
    assert responses.calls[0].request.method == "POST"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "New Sprint",
        "board": {"id": "1"},
        "startDate": "2018-10-21",
        "endDate": "2018-10-24",
    }


@responses.activate
def test_edit_patches_only_supplied_fields_with_version_query():
    responses.add(
        responses.PATCH, f"{BASE}/sprints/4405", json={"id": 4405, "name": "Updated"}, status=200
    )
    sprint = _client().edit(4405, SprintUpdate(name="Updated", status="in_progress"), version=1)
    assert sprint.name == "Updated"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Updated",
        "status": "in_progress",
    }


@responses.activate
def test_edit_without_version_omits_query():
    responses.add(
        responses.PATCH, f"{BASE}/sprints/4405", json={"id": 4405, "name": "Updated"}, status=200
    )
    _client().edit(4405, SprintUpdate(name="Updated"))
    assert "version" not in (responses.calls[0].request.url or "")


@responses.activate
def test_delete_issues_delete_and_returns_response():
    responses.add(responses.DELETE, f"{BASE}/sprints/4405", status=204)
    resp = _client().delete(sprint_id=4405)
    assert resp.status_code == 204
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_start_posts_to_start_action_with_version_query():
    responses.add(
        responses.POST,
        f"{BASE}/sprints/4405/_start",
        json={"id": 4405, "status": "in_progress"},
        status=200,
    )
    sprint = _client().start(sprint_id=4405, version=1)
    assert sprint.status == "in_progress"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/sprints/4405/_start?version=1"


@responses.activate
def test_archive_posts_to_archive_action_with_version_query():
    responses.add(
        responses.POST,
        f"{BASE}/sprints/4405/_archive",
        json={"id": 4405, "status": "archived", "archived": True},
        status=200,
    )
    sprint = _client().archive(sprint_id=4405, version=2)
    assert sprint.status == "archived" and sprint.archived is True
    assert responses.calls[0].request.url == f"{BASE}/sprints/4405/_archive?version=2"
