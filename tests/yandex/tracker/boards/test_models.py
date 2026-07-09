"""Model tests for Tracker boards — full fixture, ref-flattening, flat list shape."""

from ycli.yandex.tracker.boards.models import Board, BoardColumn, BoardList, Calendar

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
