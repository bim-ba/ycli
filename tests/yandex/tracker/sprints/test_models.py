"""Model tests for Tracker sprints — full fixture, board ref, ref-flattening, flat list."""

from ycli.yandex.tracker.sprints.models import Sprint, SprintBoardRef, SprintList

SPRINT = {
    "self": "https://api.tracker.yandex.net/v3/sprints/4405",
    "id": 4405,
    "version": 1435288720018,
    "name": "Sprint 1",
    "board": {
        "self": "https://api.tracker.yandex.net/v3/boards/3",
        "id": "3",
        "display": "My board",
    },
    "status": "in_progress",
    "archived": False,
    "createdBy": {"id": "33", "display": "Ivan Ivanov"},
    "createdAt": "2015-06-23T17:03:24.799+0000",
    "startDate": "2015-06-01",
    "endDate": "2015-06-14",
    "startDateTime": "2015-06-01T07:00:00.000+0000",
    "endDateTime": "2015-06-14T07:00:00.000+0000",
}


def test_sprint_parses_full_fixture_and_flattens_created_by():
    sprint = Sprint.model_validate(SPRINT)
    assert sprint.id == 4405 and sprint.version == 1435288720018 and sprint.name == "Sprint 1"
    assert sprint.self_url.endswith("/sprints/4405")  # ty: ignore[unresolved-attribute]
    assert sprint.status == "in_progress" and sprint.archived is False
    assert sprint.created_by == "Ivan Ivanov"  # createdBy flattened to display
    assert sprint.created_at.startswith("2015-06-23")  # ty: ignore[unresolved-attribute]
    assert sprint.start_date == "2015-06-01" and sprint.end_date == "2015-06-14"
    assert sprint.start_date_time.startswith("2015-06-01T07")  # ty: ignore[unresolved-attribute]
    assert sprint.end_date_time.startswith("2015-06-14T07")  # ty: ignore[unresolved-attribute]


def test_sprint_board_ref_is_typed():
    sprint = Sprint.model_validate(SPRINT)
    assert isinstance(sprint.board, SprintBoardRef)
    assert sprint.board.id == "3" and sprint.board.display == "My board"


def test_sprint_list_is_flat_root_model():
    sprints = SprintList.model_validate([SPRINT, {"id": 4406, "name": "Sprint 2"}])
    assert isinstance(sprints, SprintList)
    assert [s.name for s in sprints.root] == ["Sprint 1", "Sprint 2"]


def test_sprint_defaults_when_fields_absent():
    sprint = Sprint.model_validate({"id": 7})
    assert sprint.name is None and sprint.board is None and sprint.created_by is None
    assert sprint.archived is None and sprint.start_date is None
