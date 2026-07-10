"""Model behaviour for grids — typed write bodies dump correctly; reads parse; validation bites."""

import pytest
from pydantic import ValidationError

from ycli.yandex.wiki.grids.models import (
    CellsUpdate,
    ColumnsAdd,
    ColumnsMove,
    ColumnsRemove,
    Grid,
    GridActionResult,
    GridClone,
    GridCloneOperation,
    GridCreate,
    GridList,
    GridRow,
    GridUpdate,
    NewColumnSchema,
    PageIdentity,
    RowsAdd,
    RowsMove,
    RowsRemove,
    UpdateCellSchema,
)


def test_grid_create_dumps_page_by_slug():
    body = GridCreate(title="Roadmap", page=PageIdentity(slug="data/x")).model_dump(
        exclude_none=True
    )
    assert body == {"title": "Roadmap", "page": {"slug": "data/x"}}


def test_grid_create_dumps_page_by_id():
    body = GridCreate(title="Roadmap", page=PageIdentity(id=42)).model_dump(exclude_none=True)
    assert body == {"title": "Roadmap", "page": {"id": 42}}


def test_grid_create_rejects_empty_title():
    with pytest.raises(ValidationError):
        GridCreate(title="", page=PageIdentity(slug="data/x"))


def test_grid_update_dumps_only_set_fields():
    assert GridUpdate(revision="3", title="New").model_dump(exclude_none=True) == {
        "revision": "3",
        "title": "New",
    }


def test_grid_update_with_default_sort():
    body = GridUpdate(
        revision="3",
        default_sort=[{"slug": "a", "direction": "asc"}],  # ty: ignore[invalid-argument-type]
    ).model_dump(exclude_none=True)
    assert body["default_sort"][0]["direction"] == "asc"


def test_rows_add_dumps_rows_and_revision():
    assert RowsAdd(revision="3", rows=[{"name": "x"}], position=0).model_dump(
        exclude_none=True
    ) == {
        "revision": "3",
        "rows": [{"name": "x"}],
        "position": 0,
    }


def test_rows_remove_requires_at_least_one_id():
    with pytest.raises(ValidationError):
        RowsRemove(revision="3", row_ids=[])


def test_rows_move_dumps_selected_fields():
    assert RowsMove(revision="3", row_id="r1", position=2).model_dump(exclude_none=True) == {
        "revision": "3",
        "row_id": "r1",
        "position": 2,
    }


def test_columns_add_nested_new_column_dump():
    body = ColumnsAdd(revision="3", columns=[NewColumnSchema(title="C", type="string")]).model_dump(
        exclude_none=True
    )
    assert body == {"revision": "3", "columns": [{"title": "C", "type": "string"}]}


def test_new_column_rejects_bad_type():
    with pytest.raises(ValidationError):
        NewColumnSchema(title="C", type="bogus")  # ty: ignore[invalid-argument-type]


def test_columns_remove_and_move_dump():
    assert ColumnsRemove(revision="3", column_slugs=["name"]).model_dump(exclude_none=True) == {
        "revision": "3",
        "column_slugs": ["name"],
    }
    assert ColumnsMove(revision="3", column_slug="name", columns_count=2).model_dump(
        exclude_none=True
    ) == {"revision": "3", "column_slug": "name", "columns_count": 2}


def test_cells_update_nested_dump():
    body = CellsUpdate(
        revision="3", cells=[UpdateCellSchema(row_id=1, column_slug="name", value="x")]
    ).model_dump(exclude_none=True)
    assert body == {
        "revision": "3",
        "cells": [{"row_id": 1, "column_slug": "name", "value": "x"}],
    }


def test_grid_clone_defaults_with_data_false():
    assert GridClone(target="data/y").model_dump(exclude_none=True) == {
        "target": "data/y",
        "with_data": False,
    }


def test_grid_clone_rejects_empty_title():
    with pytest.raises(ValidationError):
        GridClone(target="data/y", title="")


def test_grid_parses_structure_and_rows():
    grid = Grid.model_validate(
        {
            "id": "g1",
            "revision": "3",
            "structure": {"columns": [{"slug": "name", "type": "string"}]},
            "rows": [{"id": "r1", "row": [1, "x"]}],
        }
    )
    assert grid.structure is not None and grid.structure.columns[0].slug == "name"
    assert grid.rows[0].row == [1, "x"]


def test_grid_row_defaults_empty():
    assert GridRow().row == []


def test_grid_action_result_ok_default():
    assert GridActionResult(grid_id="g1", action="delete").ok is True


def test_grid_clone_operation_parses_identity():
    op = GridCloneOperation.model_validate(
        {"operation": {"type": "clone_inline_grid", "id": "task-1"}}
    )
    assert op.operation is not None and op.operation.id == "task-1"


def test_grid_list_wraps_flat_root():
    assert GridList([Grid(id="g1")]).root[0].id == "g1"
