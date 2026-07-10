"""Model tests for Tracker board columns — full fixture, nested statuses, typed inputs."""

from ycli.yandex.tracker.columns.models import (
    Column,
    ColumnCreate,
    ColumnList,
    ColumnStatus,
    ColumnUpdate,
)

COLUMN = {
    "self": "https://api.tracker.yandex.net/v3/boards/73/columns/1",
    "id": 1,
    "name": "Open",
    "statuses": [
        {
            "self": "https://api.tracker.yandex.net/v3/statuses/1",
            "id": "1",
            "key": "open",
            "display": "Open",
        }
    ],
}


def test_column_parses_full_fixture_with_typed_statuses():
    column = Column.model_validate(COLUMN)
    assert column.id == 1 and column.name == "Open"
    assert column.self_url.endswith("/boards/73/columns/1")  # ty: ignore[unresolved-attribute]
    assert isinstance(column.statuses[0], ColumnStatus)
    assert column.statuses[0].key == "open" and column.statuses[0].display == "Open"


def test_column_list_is_flat_root_model():
    columns = ColumnList.model_validate([COLUMN, {"id": 2, "name": "Closed"}])
    assert isinstance(columns, ColumnList)
    assert [c.name for c in columns.root] == ["Open", "Closed"]


def test_column_defaults_when_fields_absent():
    column = Column.model_validate({"id": 9})
    assert column.name is None and column.statuses == []


def test_column_create_dumps_body():
    dumped = ColumnCreate(name="Approve", statuses=["needInfo"]).model_dump(
        by_alias=True, exclude_none=True
    )
    assert dumped == {"name": "Approve", "statuses": ["needInfo"]}


def test_column_update_dumps_only_supplied_fields():
    dumped = ColumnUpdate(name="Pause").model_dump(by_alias=True, exclude_none=True)
    assert dumped == {"name": "Pause"}
