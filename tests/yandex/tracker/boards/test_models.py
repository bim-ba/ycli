"""Model tests for Tracker boards — full fixture, ref-flattening, flat list shape."""

from ycli.yandex.tracker.boards.models import (
    Board,
    BoardColumn,
    BoardColumnInput,
    BoardCreate,
    BoardList,
    BoardUpdate,
    Calendar,
)

BOARD = {
    "self": "https://api.tracker.yandex.net/v3/boards/1",
    "id": 1,
    "version": 3,
    "name": "My board",
    "createdAt": "2026-01-22T09:02:18.647+0000",
    "updatedAt": "2026-01-23T09:02:18.647+0000",
    "createdBy": {"id": "username", "display": "Ivan Ivanov"},
    "columns": [
        {
            "self": "https://api.tracker.yandex.net/v3/boards/1/columns/1",
            "id": "1",
            "display": "Open",
        }
    ],
    "useRanking": False,
    "estimateBy": {"id": "storyPoints", "display": "Story Points"},
    "country": {"id": "1", "display": "Russia"},
    "calendar": {"id": 6},
    "autoFilterSettings": {"addFilterSettings": {"queue": "DEV"}},
}


def test_board_parses_full_fixture_and_flattens_refs():
    board = Board.model_validate(BOARD)
    assert board.id == 1 and board.version == 3 and board.name == "My board"
    assert board.self_url.endswith("/boards/1")  # ty: ignore[unresolved-attribute]
    assert board.created_at is not None and board.updated_at is not None
    assert board.created_at.startswith("2026-01-22")
    assert board.updated_at.startswith("2026-01-23")
    assert board.created_by == "Ivan Ivanov"  # createdBy flattened to display
    assert board.use_ranking is False
    assert board.estimate_by == "Story Points" and board.country == "Russia"
    assert board.auto_filter_settings == {"addFilterSettings": {"queue": "DEV"}}


def test_board_columns_and_calendar_are_typed():
    board = Board.model_validate(BOARD)
    assert isinstance(board.columns[0], BoardColumn)
    assert board.columns[0].id == "1" and board.columns[0].display == "Open"
    assert isinstance(board.calendar, Calendar) and board.calendar.id == 6


def test_board_list_is_flat_root_model():
    boards = BoardList.model_validate([BOARD, {"id": 2, "name": "Second"}])
    assert isinstance(boards, BoardList)
    assert [b.name for b in boards.root] == ["My board", "Second"]


def test_board_defaults_when_fields_absent():
    board = Board.model_validate({"id": 9})
    assert board.name is None and board.columns == [] and board.calendar is None
    assert board.created_by is None and board.auto_filter_settings is None


def test_board_create_dumps_alias_cased_body_dropping_none():
    body = BoardCreate(
        name="Testing",
        owner="username",
        board_permissions_template="private",
        backlog_available=True,
        sprints_available=False,
        columns=[BoardColumnInput(name="To Do", statuses=["new", "open"], limit=5)],
    )
    dumped = body.model_dump(by_alias=True, exclude_none=True)
    assert dumped == {
        "name": "Testing",
        "owner": "username",
        "boardPermissionsTemplate": "private",
        "backlogAvailable": True,
        "sprintsAvailable": False,
        "columns": [{"name": "To Do", "statuses": ["new", "open"], "limit": 5}],
    }


def test_board_create_omits_unset_optionals():
    dumped = BoardCreate(name="Bare").model_dump(by_alias=True, exclude_none=True)
    assert dumped == {"name": "Bare"}


def test_board_update_dumps_only_supplied_fields():
    dumped = BoardUpdate(name="New name", sprints_available=True).model_dump(
        by_alias=True, exclude_none=True
    )
    assert dumped == {"name": "New name", "sprintsAvailable": True}
