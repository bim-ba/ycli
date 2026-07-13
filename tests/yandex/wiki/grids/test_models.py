"""Model behaviour for grids — typed write bodies dump correctly; reads parse; validation bites."""

import pytest
from pydantic import ValidationError

from ycli.yandex.wiki.grids.models import (
    CellsUpdate,
    ColumnsAdd,
    ColumnsMove,
    ColumnsRemove,
    Grid,
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


def test_grid_update_default_sort_write_shape():
    """The API's write shape is ``[{"<column_slug>": "asc"|"desc"}]`` — dumped verbatim."""
    body = GridUpdate(
        revision="3",
        default_sort=[{"a": "asc"}, {"b": "desc"}],  # ty: ignore[invalid-argument-type]
    ).model_dump(exclude_none=True)
    assert body == {"revision": "3", "default_sort": [{"a": "asc"}, {"b": "desc"}]}


def test_grid_update_default_sort_rejects_read_shape():
    """The ``{slug, title, direction}`` READ shape must fail loudly, not get stripped to [{}]."""
    with pytest.raises(ValidationError):
        GridUpdate(
            revision="3",
            default_sort=[{"slug": "a", "direction": "asc"}],  # ty: ignore[invalid-argument-type]
        )


def test_grid_update_default_sort_rejects_bad_direction():
    with pytest.raises(ValidationError):
        GridUpdate(revision="3", default_sort=[{"a": "ascending"}])  # ty: ignore[invalid-argument-type]


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
    assert body == {
        "revision": "3",
        "columns": [{"title": "C", "type": "string", "slug": "c", "required": False}],
    }


def test_new_column_rejects_bad_type():
    with pytest.raises(ValidationError):
        NewColumnSchema(title="C", type="bogus")  # ty: ignore[invalid-argument-type]


def test_new_column_derives_slug_from_title():
    """The live API rejects a slug-less column, so ``slug`` defaults from the title —
    lowercased, non-word runs collapsed to ``_``, edge underscores stripped."""
    assert NewColumnSchema(title="Count", type="number").slug == "count"
    assert NewColumnSchema(title="My Col! (v2)", type="string").slug == "my_col_v2"


def test_new_column_derives_unicode_slug_from_cyrillic_title():
    """A Cyrillic title (the Wiki's primary audience) derives a Cyrillic slug, not an error."""
    assert NewColumnSchema(title="Количество", type="number").slug == "количество"
    assert NewColumnSchema(title="Дата начала", type="date").slug == "дата_начала"


def test_new_column_keeps_explicit_slug():
    assert NewColumnSchema(title="Count", type="number", slug="cnt").slug == "cnt"


def test_new_column_underivable_title_needs_explicit_slug():
    """A title with no word characters at all cannot yield a slug — clear error, not a 400 later."""
    with pytest.raises(ValidationError, match="pass an explicit slug"):
        NewColumnSchema(title="!!! ---", type="number")
    assert NewColumnSchema(title="!!! ---", type="number", slug="count").slug == "count"


def test_columns_add_always_serializes_required():
    """Bug 3: the API requires ``required`` on every column, so it must survive ``exclude_none``."""
    body = ColumnsAdd(revision="3", columns=[{"title": "C", "type": "string"}]).model_dump(  # ty: ignore[invalid-argument-type]
        exclude_none=True
    )
    assert body["columns"][0]["required"] is False


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


def test_grid_clone_operation_parses_identity():
    op = GridCloneOperation.model_validate(
        {"operation": {"type": "clone_inline_grid", "id": "task-1"}}
    )
    assert op.operation is not None and op.operation.id == "task-1"


def test_grid_list_wraps_flat_root():
    assert GridList([Grid(id="g1")]).root[0].id == "g1"
