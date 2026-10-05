"""Contract cases for Wiki ``/grids`` (see tests/contract.py)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.wiki.grids.models import (
    CellsUpdate,
    ColumnsAdd,
    ColumnsMove,
    ColumnsRemove,
    ColumnSuggest,
    ColumnUpdate,
    GridClone,
    GridCreate,
    GridUpdate,
    RowsAdd,
    RowsMove,
    RowsRemove,
    RowUpdate,
)

G1 = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
G2 = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a02"
G3 = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a03"
GRID = {"id": G1, "title": "Roadmap", "revision": "12", "rows": [{"id": "r1", "row": ["x"]}]}


def _revision(value: str) -> Reply:
    return Reply(json={"revision": value})


ROWS = [{"name": "Launch", "owner": "vera"}, {"name": "Review", "owner": "ivan"}]
COLUMNS_SENT = [
    {"title": "Due Date", "type": "date", "slug": "due_date", "required": False},
    {"title": "Stage", "type": "select", "slug": "stage", "required": True,
     "select_options": ["todo", "done"]},
]  # fmt: skip
CELLS = [
    {"row_id": 101, "column_slug": "name", "value": "Launch v2"},
    {"row_id": 102, "column_slug": "owner", "value": ["vera", "ivan"]},
]

COLUMN_UPDATE = {
    "revision": "19",
    "title": "Stage 2",
    "description": "workflow stage",
    "required": True,
    "width": 30,
    "width_units": "%",
    "pinned": "left",
    "color": "mint",
    "select_options": ["todo", "doing", "done"],
}
COLUMN_UPDATE_EXTRA = {
    "revision": "30",
    "format": "yfm",
    "multiple": True,
    "ticket_field": "assignee",
    "mark_rows": False,
}

CASES = [
    Case(
        "wiki.grids.get",
        args=(G1,),
        kwargs={
            "fields": "attributes,user_permissions",
            "row_filter": "[owner] ~ vera",
            "only_cols": "name,owner",
            "only_rows": "r1,r2",
            "revision": "9",
            "sort": "-name",
        },
        cli=[
            "wiki",
            "grids",
            "get",
            G1,
            "--fields",
            "attributes,user_permissions",
            "--row-filter",
            "[owner] ~ vera",
            "--only-cols",
            "name,owner",
            "--only-rows",
            "r1,r2",
            "--revision",
            "9",
            "--sort",
            "-name",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "GET",
                    f"grids/{G1}",
                    {
                        "fields": "attributes,user_permissions",
                        "filter": "[owner] ~ vera",
                        "only_cols": "name,owner",
                        "only_rows": "r1,r2",
                        "revision": "9",
                        "sort": "-name",
                    },
                ),
                Reply(json=GRID),
            )
        ],
    ),
    Case(
        "wiki.grids.get",
        args=(G2,),
        kwargs={
            "fields": "attributes",
            "row_filter": "[stage] = done",
            "only_cols": "stage",
            "only_rows": "r7",
            "sort": "stage",
        },
        cli=[
            "wiki",
            "grids",
            "get",
            G2,
            "--fields",
            "attributes",
            "--row-filter",
            "[stage] = done",
            "--only-cols",
            "stage",
            "--only-rows",
            "r7",
            "--sort",
            "stage",
        ],
        mcp=(
            "wiki_grids_get",
            {
                "grid_id": G2,
                "fields": "attributes",
                "row_filter": "[stage] = done",
                "only_cols": "stage",
                "only_rows": "r7",
                "sort": "stage",
            },
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    f"grids/{G2}",
                    {
                        "fields": "attributes",
                        "filter": "[stage] = done",
                        "only_cols": "stage",
                        "only_rows": "r7",
                        "sort": "stage",
                    },
                ),
                Reply(json={**GRID, "id": G2}),
            )
        ],
    ),
    Case(
        "wiki.grids.get",
        args=(G3,),
        cli=["wiki", "grids", "get", G3],
        mcp=("wiki_grids_get", {"grid_id": G3}),
        exchanges=[(Sent("GET", f"grids/{G3}"), Reply(json={**GRID, "id": G3}))],
    ),
    Case(
        "wiki.grids.create",
        args=(GridCreate.model_validate({"title": "Hiring plan", "page": {"slug": "hr/hiring"}}),),
        cli=["wiki", "grids", "create", "--title", "Hiring plan", "--page-slug", "hr/hiring"],
        mcp=(
            "wiki_grids_create",
            {"body": {"title": "Hiring plan", "page": {"slug": "hr/hiring"}}},
        ),
        exchanges=[
            (
                Sent("POST", "grids", json={"title": "Hiring plan", "page": {"slug": "hr/hiring"}}),
                Reply(json={**GRID, "title": "Hiring plan"}),
            )
        ],
    ),
    Case(
        "wiki.grids.create",
        args=(GridCreate.model_validate({"title": "Budget", "page": {"id": 6101}}),),
        cli=["wiki", "grids", "create", "--title", "Budget", "--page-id", "6101"],
        mcp=("wiki_grids_create", {"body": {"title": "Budget", "page": {"id": 6101}}}),
        exchanges=[
            (
                Sent("POST", "grids", json={"title": "Budget", "page": {"id": 6101}}),
                Reply(json={**GRID, "title": "Budget"}),
            )
        ],
    ),
    Case(
        "wiki.grids.update",
        args=(
            G1,
            GridUpdate.model_validate(
                {"revision": "12", "title": "Roadmap 2027", "default_sort": [{"due": "desc"}]}
            ),
        ),
        cli=[
            "wiki",
            "grids",
            "update",
            G1,
            "--revision",
            "12",
            "--title",
            "Roadmap 2027",
            "--default-sort",
            json.dumps([{"due": "desc"}]),
        ],
        mcp=(
            "wiki_grids_update",
            {
                "grid_id": G1,
                "body": {
                    "revision": "12",
                    "title": "Roadmap 2027",
                    "default_sort": [{"due": "desc"}],
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G1}",
                    json={
                        "revision": "12",
                        "title": "Roadmap 2027",
                        "default_sort": [{"due": "desc"}],
                    },
                ),
                _revision("13"),
            )
        ],
        effect="idempotent_write",
    ),
    Case(
        "wiki.grids.update",
        args=(G2, GridUpdate.model_validate({"revision": "4", "title": "Renamed"})),
        cli=["wiki", "grids", "update", G2, "--revision", "4", "--title", "Renamed"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", f"grids/{G2}", json={"revision": "4", "title": "Renamed"}),
                _revision("5"),
            )
        ],
        effect="idempotent_write",
    ),
    Case(
        "wiki.grids.delete",
        output={"ok": True, "detail": f"deleted grid {G3}"},
        args=(G3,),
        cli=["wiki", "grids", "delete", G3],
        mcp=("wiki_grids_delete", {"grid_id": G3}),
        exchanges=[(Sent("DELETE", f"grids/{G3}"), Reply(status=204))],
    ),
    Case(
        "wiki.grids.rows_create",
        args=(
            G1,
            RowsAdd.model_validate(
                {"revision": "13", "rows": ROWS, "position": 2, "after_row_id": "r9"}
            ),
        ),
        cli=[
            "wiki",
            "grids",
            "rows",
            "create",
            G1,
            "--revision",
            "13",
            "--rows",
            json.dumps(ROWS),
            "--position",
            "2",
            "--after-row-id",
            "r9",
        ],
        mcp=(
            "wiki_grids_rows_create",
            {
                "grid_id": G1,
                "body": {"revision": "13", "rows": ROWS, "position": 2, "after_row_id": "r9"},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G1}/rows",
                    json={"revision": "13", "rows": ROWS, "position": 2, "after_row_id": "r9"},
                ),
                Reply(json={"revision": "14", "results": [{"id": "r10", "row": ["Launch"]}]}),
            )
        ],
    ),
    Case(
        "wiki.grids.rows_create",
        args=(G2, RowsAdd.model_validate({"revision": "5", "rows": [{"name": "Solo"}]})),
        cli=[
            "wiki",
            "grids",
            "rows",
            "create",
            G2,
            "--revision",
            "5",
            "--rows",
            '[{"name": "Solo"}]',
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST", f"grids/{G2}/rows", json={"revision": "5", "rows": [{"name": "Solo"}]}
                ),
                Reply(json={"revision": "6", "results": []}),
            )
        ],
    ),
    Case(
        "wiki.grids.rows_delete",
        args=(G1, RowsRemove.model_validate({"revision": "14", "row_ids": ["r1", "r2"]})),
        cli=[
            "wiki",
            "grids",
            "rows",
            "delete",
            G1,
            "--revision",
            "14",
            "--row-id",
            "r1",
            "--row-id",
            "r2",
        ],
        mcp=(
            "wiki_grids_rows_delete",
            {"grid_id": G1, "body": {"revision": "14", "row_ids": ["r1", "r2"]}},
        ),
        exchanges=[
            (
                Sent(
                    "DELETE", f"grids/{G1}/rows", json={"revision": "14", "row_ids": ["r1", "r2"]}
                ),
                _revision("15"),
            )
        ],
    ),
    Case(
        "wiki.grids.rows_move",
        args=(
            G1,
            RowsMove.model_validate(
                {
                    "revision": "15",
                    "row_id": "r3",
                    "after_row_id": "r5",
                    "position": 4,
                    "rows_count": 2,
                }
            ),
        ),
        cli=[
            "wiki",
            "grids",
            "rows",
            "move",
            G1,
            "--revision",
            "15",
            "--row-id",
            "r3",
            "--after-row-id",
            "r5",
            "--position",
            "4",
            "--rows-count",
            "2",
        ],
        mcp=(
            "wiki_grids_rows_move",
            {
                "grid_id": G1,
                "body": {
                    "revision": "15",
                    "row_id": "r3",
                    "after_row_id": "r5",
                    "position": 4,
                    "rows_count": 2,
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G1}/rows/move",
                    json={
                        "revision": "15",
                        "row_id": "r3",
                        "after_row_id": "r5",
                        "position": 4,
                        "rows_count": 2,
                    },
                ),
                _revision("16"),
            )
        ],
    ),
    Case(
        "wiki.grids.rows_move",
        args=(G2, RowsMove.model_validate({"row_id": "r1"})),
        cli=["wiki", "grids", "rows", "move", G2, "--row-id", "r1"],
        mcp=None,
        exchanges=[(Sent("POST", f"grids/{G2}/rows/move", json={"row_id": "r1"}), _revision("7"))],
    ),
    Case(
        "wiki.grids.columns_create",
        args=(
            G1,
            ColumnsAdd.model_validate({"revision": "16", "columns": COLUMNS_SENT, "position": 1}),
        ),
        cli=[
            "wiki",
            "grids",
            "columns",
            "create",
            G1,
            "--revision",
            "16",
            "--columns",
            json.dumps(COLUMNS_SENT),
            "--position",
            "1",
        ],
        mcp=(
            "wiki_grids_columns_create",
            {"grid_id": G1, "body": {"revision": "16", "columns": COLUMNS_SENT, "position": 1}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G1}/columns",
                    json={"revision": "16", "columns": COLUMNS_SENT, "position": 1},
                ),
                _revision("17"),
            )
        ],
    ),
    Case(
        "wiki.grids.columns_delete",
        args=(
            G1,
            ColumnsRemove.model_validate({"revision": "17", "column_slugs": ["stage", "due_date"]}),
        ),
        cli=[
            "wiki",
            "grids",
            "columns",
            "delete",
            G1,
            "--revision",
            "17",
            "--column-slug",
            "stage",
            "--column-slug",
            "due_date",
        ],
        mcp=(
            "wiki_grids_columns_delete",
            {"grid_id": G1, "body": {"revision": "17", "column_slugs": ["stage", "due_date"]}},
        ),
        exchanges=[
            (
                Sent(
                    "DELETE",
                    f"grids/{G1}/columns",
                    json={"revision": "17", "column_slugs": ["stage", "due_date"]},
                ),
                _revision("18"),
            )
        ],
    ),
    Case(
        "wiki.grids.columns_move",
        args=(
            G1,
            ColumnsMove.model_validate(
                {"revision": "18", "column_slug": "owner", "position": 0, "columns_count": 3}
            ),
        ),
        cli=[
            "wiki",
            "grids",
            "columns",
            "move",
            G1,
            "--revision",
            "18",
            "--column-slug",
            "owner",
            "--position",
            "0",
            "--columns-count",
            "3",
        ],
        mcp=(
            "wiki_grids_columns_move",
            {
                "grid_id": G1,
                "body": {
                    "revision": "18",
                    "column_slug": "owner",
                    "position": 0,
                    "columns_count": 3,
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G1}/columns/move",
                    json={
                        "revision": "18",
                        "column_slug": "owner",
                        "position": 0,
                        "columns_count": 3,
                    },
                ),
                _revision("19"),
            )
        ],
    ),
    Case(
        "wiki.grids.columns_move",
        args=(G2, ColumnsMove.model_validate({"column_slug": "owner", "position": 0})),
        cli=["wiki", "grids", "columns", "move", G2, "--column-slug", "owner", "--position", "0"],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G2}/columns/move",
                    json={"column_slug": "owner", "position": 0},
                ),
                _revision("8"),
            )
        ],
    ),
    Case(
        "wiki.grids.cells_update",
        args=(G1, CellsUpdate.model_validate({"revision": "19", "cells": CELLS})),
        cli=[
            "wiki",
            "grids",
            "cells",
            "update",
            G1,
            "--revision",
            "19",
            "--cells",
            json.dumps(CELLS),
        ],
        mcp=(
            "wiki_grids_cells_update",
            {"grid_id": G1, "body": {"revision": "19", "cells": CELLS}},
        ),
        exchanges=[
            (
                Sent("POST", f"grids/{G1}/cells", json={"revision": "19", "cells": CELLS}),
                Reply(
                    json={
                        "revision": "20",
                        "cells": [{"row_id": "101", "column_slug": "name", "value": "Launch v2"}],
                    }
                ),
            )
        ],
        effect="idempotent_write",
    ),
    Case(
        "wiki.grids.clone",
        args=(
            G1,
            GridClone.model_validate(
                {"target": "eng/roadmap-copy", "title": "Roadmap copy", "with_data": True}
            ),
        ),
        cli=[
            "wiki",
            "grids",
            "clone",
            G1,
            "--target",
            "eng/roadmap-copy",
            "--title",
            "Roadmap copy",
            "--with-data",
            "--no-wait",
        ],
        mcp=(
            "wiki_grids_clone",
            {
                "grid_id": G1,
                "body": {"target": "eng/roadmap-copy", "title": "Roadmap copy", "with_data": True},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G1}/clone",
                    json={"target": "eng/roadmap-copy", "title": "Roadmap copy", "with_data": True},
                ),
                Reply(json={"operation": {"type": "clone_inline_grid", "id": "task-6201"}}),
            )
        ],
    ),
    Case(
        "wiki.grids.clone",
        args=(G2, GridClone.model_validate({"target": "eng/shape-only"})),
        cli=["wiki", "grids", "clone", G2, "--target", "eng/shape-only", "--no-wait"],
        mcp=("wiki_grids_clone", {"grid_id": G2, "body": {"target": "eng/shape-only"}}),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G2}/clone",
                    json={"target": "eng/shape-only"},
                ),
                Reply(json={"operation": {"type": "clone_inline_grid", "id": "task-6202"}}),
            )
        ],
    ),
    # POST /grids/{id}/columns/suggest (undocumented) only reads, whatever its method says.
    Case(
        "wiki.grids.columns_suggest",
        args=(G2, ColumnSuggest.model_validate({"title": "Due date"})),
        cli=["wiki", "grids", "columns", "suggest", G2, "--title", "Due date"],
        mcp=("wiki_grids_columns_suggest", {"grid_id": G2, "body": {"title": "Due date"}}),
        effect="read",
        exchanges=[
            (
                Sent("POST", f"grids/{G2}/columns/suggest", json={"title": "Due date"}),
                Reply(json={"slug": "due-date", "occupied": False, "suggest": []}),
            )
        ],
    ),
    Case(
        "wiki.grids.columns_suggest",
        args=(G3, ColumnSuggest.model_validate({"slug": "stage"})),
        cli=["wiki", "grids", "columns", "suggest", G3, "--slug", "stage"],
        mcp=None,
        effect="read",
        exchanges=[
            (
                Sent("POST", f"grids/{G3}/columns/suggest", json={"slug": "stage"}),
                Reply(json={"slug": "stage", "occupied": True, "suggest": ["stage-2", "stage-1"]}),
            )
        ],
    ),
    # POST /grids/{id}/column/{slug} (undocumented; the path says "column", singular).
    Case(
        "wiki.grids.columns_update",
        effect="idempotent_write",
        args=(G1, "stage", ColumnUpdate.model_validate(COLUMN_UPDATE)),
        cli=[
            "wiki",
            "grids",
            "columns",
            "update",
            G1,
            "stage",
            "--revision",
            "19",
            "--title",
            "Stage 2",
            "--description",
            "workflow stage",
            "--required",
            "--width",
            "30",
            "--width-units",
            "%",
            "--pinned",
            "left",
            "--color",
            "mint",
            "--select-option",
            "todo",
            "--select-option",
            "doing",
            "--select-option",
            "done",
        ],
        mcp=(
            "wiki_grids_columns_update",
            {"grid_id": G1, "column_slug": "stage", "body": COLUMN_UPDATE},
        ),
        exchanges=[
            (
                Sent("POST", f"grids/{G1}/column/stage", json=COLUMN_UPDATE),
                Reply(
                    json={
                        "revision": "20",
                        "column": {
                            "id": "2",
                            "slug": "stage",
                            "title": "Stage 2",
                            "type": "select",
                            "required": True,
                            "width": 30,
                            "width_units": "%",
                            "pinned": "left",
                            "color": "mint",
                            "select_options": ["todo", "doing", "done"],
                            "description": "workflow stage",
                        },
                    }
                ),
            )
        ],
    ),
    Case(
        "wiki.grids.columns_update",
        effect="idempotent_write",
        args=(G2, "note", ColumnUpdate.model_validate({"title": "Remarks", "required": False})),
        cli=[
            "wiki",
            "grids",
            "columns",
            "update",
            G2,
            "note",
            "--title",
            "Remarks",
            "--no-required",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G2}/column/note",
                    json={"title": "Remarks", "required": False},
                ),
                Reply(
                    json={
                        "revision": "4",
                        "column": {"slug": "note", "title": "Remarks", "required": False},
                    }
                ),
            )
        ],
    ),
    # The fields the CLI has no flag for: SDK and MCP only.
    Case(
        "wiki.grids.columns_update",
        effect="idempotent_write",
        args=(G3, "assignee", ColumnUpdate.model_validate(COLUMN_UPDATE_EXTRA)),
        cli=None,
        mcp=(
            "wiki_grids_columns_update",
            {"grid_id": G3, "column_slug": "assignee", "body": COLUMN_UPDATE_EXTRA},
        ),
        exchanges=[
            (
                Sent("POST", f"grids/{G3}/column/assignee", json=COLUMN_UPDATE_EXTRA),
                Reply(
                    json={
                        "revision": "31",
                        "column": {
                            "slug": "assignee",
                            "title": "Assignee",
                            "type": "ticket_field",
                            "format": "yfm",
                            "multiple": True,
                            "ticket_field": "assignee",
                            "mark_rows": False,
                        },
                    }
                ),
            )
        ],
    ),
    # POST /grids/{id}/rows/{row_id} (undocumented): pin or colour a row.
    Case(
        "wiki.grids.rows_update",
        effect="idempotent_write",
        args=(
            G1,
            "103",
            RowUpdate.model_validate({"revision": "22", "pinned": True, "color": "orange"}),
        ),
        cli=[
            "wiki",
            "grids",
            "rows",
            "update",
            G1,
            "103",
            "--revision",
            "22",
            "--pinned",
            "--color",
            "orange",
        ],
        mcp=(
            "wiki_grids_rows_update",
            {
                "grid_id": G1,
                "row_id": "103",
                "body": {"revision": "22", "pinned": True, "color": "orange"},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"grids/{G1}/rows/103",
                    json={"revision": "22", "pinned": True, "color": "orange"},
                ),
                Reply(json={"status": "ok"}),
            )
        ],
    ),
    Case(
        "wiki.grids.rows_update",
        effect="idempotent_write",
        args=(G2, "207", RowUpdate.model_validate({"pinned": False})),
        cli=["wiki", "grids", "rows", "update", G2, "207", "--no-pinned"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", f"grids/{G2}/rows/207", json={"pinned": False}),
                Reply(json={}),  # what the live API sends, whatever its spec says
            )
        ],
    ),
]
