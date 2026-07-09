"""TDD for SprintsClient — list a board's sprints + get one sprint by id."""

import requests
import responses

from ycli.yandex.tracker.sprints.client import SprintsClient
from ycli.yandex.tracker.sprints.models import Sprint, SprintList

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
