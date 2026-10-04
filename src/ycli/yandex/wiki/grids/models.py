"""Pydantic v2 models for Yandex Wiki dynamic tables (``/grids``) — reads + typed write bodies.

Grids are the modern dynamic tables attached to a page. Every mutating call carries a
``revision`` string for optimistic locking: read the grid, send its current ``revision`` with the
write, and the API rejects the write (409) if another edit landed first — so ``revision`` threads
through :class:`GridUpdate`, the row/column add/remove/move bodies and :class:`CellsUpdate`. The
two exceptions are :class:`GridCreate` (a brand-new grid has no prior revision) and
:class:`GridClone` (an async trigger). Clone is deferred: it returns a :class:`AsyncOperation`
you poll through the ``operations`` resource.

Replies keep unknown fields (:class:`~ycli.yandex.models.APIModel`); request bodies refuse them.
"""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import Field, RootModel, model_validator

from ycli.yandex.models import APIModel, RequestBody, SortDirection
from ycli.yandex.wiki.models import PageIdentity

#: Sort order of a column in the grid's default sort.
#: A column's value type.
ColumnType = (
    Literal["string", "number", "date", "select", "staff", "checkbox", "ticket", "ticket_field"]
    | str
)
#: Unit a column width is expressed in.
WidthUnits = Literal["%", "px"] | str
#: Edge a column is pinned to.
ColumnPinType = Literal["left", "right"] | str
#: Background colour of a column or row.
BGColor = (
    Literal[
        "blue",
        "yellow",
        "pink",
        "red",
        "green",
        "mint",
        "grey",
        "orange",
        "magenta",
        "purple",
        "copper",
        "ocean",
    ]
    | str
)
#: Rich-text format of a text column / grid body.
TextFormat = Literal["yfm", "wom", "plain"] | str
#: Tracker issue field a ``ticket_field`` column mirrors.
TicketField = (
    Literal[
        "assignee",
        "components",
        "created_at",
        "deadline",
        "description",
        "end",
        "estimation",
        "fixversions",
        "followers",
        "last_comment_updated_at",
        "original_estimation",
        "parent",
        "pending_reply_from",
        "priority",
        "project",
        "queue",
        "reporter",
        "resolution",
        "resolved_at",
        "sprint",
        "start",
        "status",
        "status_start_time",
        "status_type",
        "storypoints",
        "subject",
        "tags",
        "type",
        "updated_at",
        "votes",
    ]
    | str
)


class ColumnSortSchema(APIModel):
    """One entry of a grid's default sort as the API *reads* it back (``{slug, title, direction}``).

    Read shape only — a grid update must send :class:`ColumnSortWrite` instead (the API's write
    shape is a plain ``{"<column_slug>": "asc"|"desc"}`` mapping and 400s on this read shape).

    Examples:
        >>> ColumnSortSchema(slug="priority", direction="desc").direction
        'desc'
    """

    slug: str | None = Field(default=None, description="Slug of the column to sort by.")
    title: str | None = Field(default=None, description="Human-readable column title.")
    direction: SortDirection | None = Field(
        default=None, description="Sort direction: ``asc`` or ``desc``."
    )


class ColumnSortWrite(RootModel[dict[str, SortDirection]]):
    """One default-sort entry as the API *writes* it — ``{"<column_slug>": "asc"|"desc"}``.

    The write shape differs from the read shape: reads return ``[{slug, title, direction}]``
    (:class:`ColumnSortSchema`), but ``POST /grids/{id}`` accepts only a list of single-key
    ``column_slug → direction`` mappings and rejects the read shape with a 400
    (``type_error.enum``).

    Examples:
        >>> ColumnSortWrite({"priority": "desc"}).model_dump()
        {'priority': 'desc'}
    """

    root: dict[str, SortDirection]


class ColumnSchema(APIModel):
    """A column in a grid's structure (``structure.columns[]`` on a read).

    Examples:
        >>> ColumnSchema.model_validate({"slug": "name", "type": "string"}).type
        'string'
    """

    id: str | None = Field(default=None, description="The column's identifier.")
    slug: str | None = Field(default=None, description="Machine slug used to address the column.")
    title: str | None = Field(default=None, description="Human-readable column header.")
    type: ColumnType | None = Field(default=None, description="Value type of the column.")
    required: bool | None = Field(default=None, description="Whether a value is mandatory.")
    width: int | None = Field(default=None, description="Column width in ``width_units``.")
    width_units: WidthUnits | None = Field(
        default=None, description="Unit of ``width``: ``%`` or ``px``."
    )
    pinned: ColumnPinType | None = Field(
        default=None, description="Edge the column is pinned to (``left``/``right``)."
    )
    color: BGColor | None = Field(default=None, description="Background colour of the column.")
    multiple: bool | None = Field(
        default=None, description="For ``select``/``staff``: allow multiple values."
    )
    format: TextFormat | None = Field(
        default=None, description="For text columns: rich-text format (``None`` = plain)."
    )
    ticket_field: TicketField | None = Field(
        default=None, description="For ``ticket_field`` columns: the mirrored Tracker field."
    )
    select_options: list[str] | None = Field(
        default=None, description="For ``select`` columns: the allowed choices."
    )
    mark_rows: bool | None = Field(
        default=None, description="For ``checkbox`` columns: mark the row done when ticked."
    )
    description: str | None = Field(default=None, description="Free-text column description.")


class GridStructureSchema(APIModel):
    """A grid's structure — its columns and default sort.

    Examples:
        >>> GridStructureSchema(columns=[ColumnSchema(slug="a")]).columns[0].slug
        'a'
    """

    columns: list[ColumnSchema] = Field(
        default_factory=list, description="Ordered columns of the grid."
    )
    default_sort: list[ColumnSortSchema] = Field(
        default_factory=list, description="Default row sort applied when the grid is opened."
    )


class GridRow(APIModel):
    """One row of a grid (``rows[]`` on a read) — an ordered list of cell values.

    ``row`` is positional (aligned to ``structure.columns``) and heterogeneous: a cell may be a
    scalar, a string list, a ticket ref, or a user object, so it is typed permissively.

    Examples:
        >>> GridRow.model_validate({"id": "r1", "row": [1, "x"], "pinned": True}).row
        [1, 'x']
    """

    id: str | None = Field(default=None, description="The row's identifier.")
    row: list[Any] = Field(
        default_factory=list, description="Positional cell values aligned to the grid's columns."
    )
    pinned: bool | None = Field(default=None, description="Whether the row is pinned.")
    color: BGColor | None = Field(default=None, description="Background colour of the row.")


class GridAttributes(APIModel):
    """Extra grid attributes (``fields=attributes``) — creation / modification timestamps.

    Examples:
        >>> GridAttributes(created_at="2025-01-01T00:00:00Z").created_at
        '2025-01-01T00:00:00Z'
    """

    created_at: str | None = Field(default=None, description="ISO-8601 creation timestamp.")
    modified_at: str | None = Field(
        default=None, description="ISO-8601 last-modification timestamp."
    )


class Grid(APIModel):
    """A full dynamic table (``POST /grids`` / ``GET /grids/{id}``) — structure, rows, revision.

    ``revision`` is the optimistic-lock token: pass it back on the next write. ``attributes`` and
    ``user_permissions`` are only present when requested via ``fields=``.

    Examples:
        >>> Grid.model_validate({"id": "g-uuid", "title": "Roadmap", "revision": "3"}).revision
        '3'
    """

    id: str | int | None = Field(default=None, description="The grid's identifier (uuid4 or int).")
    created_at: str | None = Field(default=None, description="ISO-8601 creation timestamp.")
    title: str | None = Field(default=None, description="Human-readable grid title.")
    page: PageIdentity | None = Field(default=None, description="Page the grid belongs to.")
    structure: GridStructureSchema | None = Field(
        default=None, description="Columns and default sort of the grid."
    )
    rich_text_format: TextFormat | None = Field(
        default=None, description="Rich-text format of the grid body, if any."
    )
    rows: list[GridRow] = Field(default_factory=list, description="The grid's rows.")
    revision: str | None = Field(
        default=None, description="Optimistic-lock token — echo it back on the next write."
    )
    user_permissions: list[str] | None = Field(
        default=None, description="Caller's permissions on the owning page (``fields=`` only)."
    )
    attributes: GridAttributes | None = Field(
        default=None, description="Extra attributes (only present with ``fields=attributes``)."
    )
    template_id: int | None = Field(
        default=None, description="Id of the template the grid was created from, if any."
    )


class RevisionResult(APIModel):
    """The common ``{revision}`` reply of a grid write (update / remove / move / columns add).

    Carries the grid's new optimistic-lock token; feed it to the next write.

    Examples:
        >>> RevisionResult.model_validate({"revision": "4"}).revision
        '4'
    """

    revision: str | None = Field(default=None, description="The grid's revision after the write.")


class RowsAddResult(APIModel):
    """Reply of ``POST /grids/{id}/rows`` — the new ``revision`` plus the created rows.

    Examples:
        >>> RowsAddResult.model_validate({"revision": "5", "results": [{"id": "r1"}]}).results[0].id
        'r1'
    """

    revision: str | None = Field(default=None, description="The grid's revision after adding rows.")
    results: list[GridRow] = Field(default_factory=list, description="The rows that were created.")


class CellSchema(APIModel):
    """A single updated cell in a ``cells update`` reply (``row_id``, ``column_slug``, ``value``).

    Examples:
        >>> CellSchema.model_validate({"row_id": "r1", "column_slug": "name", "value": 1}).value
        1
    """

    row_id: str | None = Field(default=None, description="Id of the row the cell belongs to.")
    column_slug: str | None = Field(default=None, description="Slug of the cell's column.")
    value: Any = Field(default=None, description="The cell's value after the update.")


class CellsUpdateResult(APIModel):
    """Reply of ``POST /grids/{id}/cells`` — the new ``revision`` plus the updated cells.

    Examples:
        >>> CellsUpdateResult.model_validate({"revision": "6", "cells": []}).revision
        '6'
    """

    revision: str | None = Field(
        default=None, description="The grid's revision after updating cells."
    )
    cells: list[CellSchema] = Field(
        default_factory=list, description="The cells that were updated."
    )


class NewColumnSchema(RequestBody):
    """Typed body for one new column in a ``columns add`` request.

    ``title`` and ``type`` are required; the remaining fields shape a specific column type
    (``select_options`` for ``select``, ``ticket_field`` for ``ticket_field``, …). The live API
    requires a ``slug`` on every column (400 ``value_error.missing`` without one), so when
    ``slug`` is omitted it is derived from ``title``: lowercased, with every run of non-word
    characters collapsed to a single ``_`` and edge underscores stripped (``"Owner"`` →
    ``"owner"``, ``"My Col!"`` → ``"my_col"``). The derivation is Unicode-aware, so a Cyrillic
    title yields a Cyrillic slug (``"Владелец"`` → ``"владелец"``); only a title with no word
    characters at all (pure punctuation) needs an explicit ``slug``.

    Examples:
        >>> NewColumnSchema(title="Owner", type="staff", multiple=True).model_dump(
        ...     exclude_none=True
        ... )
        {'title': 'Owner', 'type': 'staff', 'slug': 'owner', 'required': False, 'multiple': True}
    """

    title: str = Field(min_length=1, max_length=255, description="Column header (non-empty).")
    type: ColumnType = Field(description="Value type of the new column.")
    slug: str | None = Field(
        default=None,
        description="Machine slug of the column — required by the API; derived from ``title`` "
        "when omitted (lowercased, non-``a-z0-9`` runs collapsed to ``_``).",
    )
    required: bool = Field(
        default=False,
        description="Whether a value is mandatory. The API requires this on every column, so it "
        "defaults to ``False`` (never ``None``) to survive ``exclude_none`` serialization.",
    )
    width: int | None = Field(default=None, description="Column width in ``width_units``.")
    width_units: WidthUnits | None = Field(default=None, description="Unit of ``width``.")
    pinned: ColumnPinType | None = Field(default=None, description="Edge to pin the column to.")
    color: BGColor | None = Field(default=None, description="Background colour of the column.")
    multiple: bool | None = Field(
        default=None, description="For ``select``/``staff``: allow multiple values."
    )
    format: TextFormat | None = Field(
        default=None, description="For text columns: rich-text format."
    )
    ticket_field: TicketField | None = Field(
        default=None, description="For ``ticket_field`` columns: the mirrored Tracker field."
    )
    select_options: list[str] | None = Field(
        default=None, description="For ``select`` columns: the allowed choices."
    )
    mark_rows: bool | None = Field(
        default=None, description="For ``checkbox`` columns: mark the row done when ticked."
    )
    description: str | None = Field(
        default=None, max_length=1024, description="Free-text column description."
    )

    @model_validator(mode="after")
    def _derive_slug_from_title(self) -> NewColumnSchema:
        r"""Default ``slug`` from ``title`` — the live API rejects slug-less columns (400).

        ``\W+`` is Unicode-aware, so a Cyrillic title (the Wiki's primary audience) derives a
        Cyrillic slug rather than collapsing to empty; only a title with no word characters at
        all (pure punctuation) needs an explicit slug.
        """
        if self.slug is None:
            derived = re.sub(r"\W+", "_", self.title.lower()).strip("_")
            if not derived:
                raise ValueError(
                    f"cannot derive a column slug from title {self.title!r} "
                    "(no word characters); pass an explicit slug"
                )
            self.slug = derived
        return self


class GridCreate(RequestBody):
    """Typed body for ``POST /grids`` — create a new grid as a resource of a page.

    A new grid has no prior revision, so this body carries none. Columns and rows are added
    afterwards via the ``columns``/``rows`` calls.

    Examples:
        >>> GridCreate(title="Roadmap", page=PageIdentity(slug="data/x")).model_dump(
        ...     exclude_none=True
        ... )
        {'title': 'Roadmap', 'page': {'slug': 'data/x'}}
    """

    title: str = Field(min_length=1, max_length=255, description="Title of the new grid.")
    page: PageIdentity = Field(description="Page the grid is created under (by id or slug).")


class GridUpdate(RequestBody):
    """Typed body for ``POST /grids/{id}`` — rename or re-sort a grid (POST, not PATCH).

    ``revision`` is required (optimistic lock); ``title`` and ``default_sort`` are the editable
    fields. ``default_sort`` takes the API's *write* shape — a list of single-key
    ``{"<column_slug>": "asc"|"desc"}`` mappings (:class:`ColumnSortWrite`), **not** the
    ``{slug, title, direction}`` read shape a grid ``get`` returns.

    Examples:
        >>> GridUpdate(revision="3", title="New").model_dump(exclude_none=True)
        {'revision': '3', 'title': 'New'}
        >>> GridUpdate(revision="3", default_sort=[{"col": "asc"}]).model_dump(exclude_none=True)
        {'revision': '3', 'default_sort': [{'col': 'asc'}]}
    """

    revision: str = Field(description="Current grid revision (optimistic lock).")
    title: str | None = Field(
        default=None, min_length=1, max_length=255, description="New grid title."
    )
    default_sort: list[ColumnSortWrite] | None = Field(
        default=None,
        description='New default row sort — write shape ``[{"<column_slug>": "asc"|"desc"}]``.',
    )


class RowsAdd(RequestBody):
    """Typed body for ``POST /grids/{id}/rows`` — insert rows at a position.

    Each item of ``rows`` maps a column slug to its cell value. ``position`` /
    ``after_row_id`` place the new rows; omit both to append.

    Examples:
        >>> RowsAdd(revision="3", rows=[{"name": "x"}]).model_dump(exclude_none=True)
        {'revision': '3', 'rows': [{'name': 'x'}]}
    """

    revision: str = Field(description="Current grid revision (optimistic lock).")
    rows: list[dict[str, Any]] = Field(
        description="Rows to insert; each maps a column slug to its cell value."
    )
    position: int | None = Field(default=None, description="Zero-based index to insert at.")
    after_row_id: str | None = Field(
        default=None, description="Insert after this row id (alternative to ``position``)."
    )


class RowsRemove(RequestBody):
    """Typed body for ``DELETE /grids/{id}/rows`` — delete rows by id.

    Examples:
        >>> RowsRemove(revision="3", row_ids=["r1"]).model_dump(exclude_none=True)
        {'revision': '3', 'row_ids': ['r1']}
    """

    revision: str = Field(description="Current grid revision (optimistic lock).")
    row_ids: list[str] = Field(
        min_length=1, description="Ids of the rows to delete (at least one)."
    )


class RowsMove(RequestBody):
    """Typed body for ``POST /grids/{id}/rows/move`` — move a run of rows to a position.

    Examples:
        >>> RowsMove(revision="3", row_id="r1", position=0).model_dump(exclude_none=True)
        {'revision': '3', 'row_id': 'r1', 'position': 0}
    """

    revision: str = Field(description="Current grid revision (optimistic lock).")
    row_id: str | None = Field(default=None, description="Id of the first row to move.")
    after_row_id: str | None = Field(
        default=None, description="Move to just after this row id (alternative to ``position``)."
    )
    position: int | None = Field(default=None, description="Zero-based destination index.")
    rows_count: int | None = Field(
        default=None, description="How many consecutive rows to move (default 1)."
    )


class ColumnsAdd(RequestBody):
    """Typed body for ``POST /grids/{id}/columns`` — add columns at a position.

    Examples:
        >>> ColumnsAdd(
        ...     revision="3", columns=[NewColumnSchema(title="C", type="string")]
        ... ).model_dump(exclude_none=True)["columns"]
        [{'title': 'C', 'type': 'string', 'slug': 'c', 'required': False}]
    """

    revision: str = Field(description="Current grid revision (optimistic lock).")
    columns: list[NewColumnSchema] = Field(description="Columns to add (in order).")
    position: int | None = Field(default=None, description="Zero-based index to insert at.")


class ColumnsRemove(RequestBody):
    """Typed body for ``DELETE /grids/{id}/columns`` — delete columns by slug.

    Examples:
        >>> ColumnsRemove(revision="3", column_slugs=["name"]).model_dump(exclude_none=True)
        {'revision': '3', 'column_slugs': ['name']}
    """

    revision: str = Field(description="Current grid revision (optimistic lock).")
    column_slugs: list[str] = Field(description="Slugs of the columns to delete.")


class ColumnsMove(RequestBody):
    """Typed body for ``POST /grids/{id}/columns/move`` — move a run of columns to a position.

    Examples:
        >>> ColumnsMove(revision="3", column_slug="name", position=0).model_dump(exclude_none=True)
        {'revision': '3', 'column_slug': 'name', 'position': 0}
    """

    revision: str = Field(description="Current grid revision (optimistic lock).")
    column_slug: str | None = Field(default=None, description="Slug of the first column to move.")
    position: int | None = Field(default=None, description="Zero-based destination index.")
    columns_count: int | None = Field(
        default=None, description="How many consecutive columns to move (default 1)."
    )


class UpdateCellSchema(RequestBody):
    """Typed body for one cell in a ``cells update`` request (``row_id``, ``column_slug``, value).

    Examples:
        >>> UpdateCellSchema(row_id=1, column_slug="name", value="x").model_dump()
        {'row_id': 1, 'column_slug': 'name', 'value': 'x'}
    """

    row_id: int = Field(description="Numeric id of the row whose cell is updated.")
    column_slug: str = Field(description="Slug of the cell's column.")
    value: Any = Field(default=None, description="New cell value (scalar, list, or user ref).")


class CellsUpdate(RequestBody):
    """Typed body for ``POST /grids/{id}/cells`` — set the value of individual cells.

    Examples:
        >>> CellsUpdate(
        ...     revision="3", cells=[UpdateCellSchema(row_id=1, column_slug="name", value="x")]
        ... ).model_dump(exclude_none=True)
        {'revision': '3', 'cells': [{'row_id': 1, 'column_slug': 'name', 'value': 'x'}]}
    """

    revision: str = Field(description="Current grid revision (optimistic lock).")
    cells: list[UpdateCellSchema] = Field(description="The cells to update.")


class ColumnSuggest(RequestBody):
    """Typed body for ``POST /grids/{id}/columns/suggest`` — check a column slug (undocumented).

    Give a ``slug`` to see whether it is taken, or a ``title`` to have it turned into a slug first:
    exactly one of them (the API answers 400 for neither or both). The call only reads: it changes
    nothing in the grid.

    Examples:
        >>> ColumnSuggest(title="Due date").model_dump(exclude_none=True)
        {'title': 'Due date'}
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Column title to turn into a slug and check.",
    )
    slug: str | None = Field(default=None, description="Column slug to check.")

    @model_validator(mode="after")
    def _exactly_one_of_title_and_slug(self) -> ColumnSuggest:
        """The API answers 400 unless exactly one of ``title`` and ``slug`` is given."""
        if (self.title is None) == (self.slug is None):
            raise ValueError("give exactly one of title and slug")
        return self


class ColumnSuggestion(APIModel):
    """Reply of ``POST /grids/{id}/columns/suggest`` — the checked slug and free alternatives.

    Examples:
        >>> ColumnSuggestion.model_validate(
        ...     {"slug": "name", "occupied": True, "suggest": ["name_1"]}
        ... ).suggest
        ['name_1']
    """

    slug: str | None = Field(default=None, description="The slug that was checked.")
    occupied: bool | None = Field(
        default=None, description="Whether a column already has that slug."
    )
    suggest: list[str] = Field(
        default_factory=list, description="Free slugs to use instead when it is occupied."
    )


class ColumnUpdate(RequestBody):
    """Typed body for ``POST /grids/{id}/column/{slug}`` — edit a column in place (undocumented).

    Every field is optional and only the ones sent change. The column ``type`` and ``slug`` cannot
    be edited. Unlike the other grid writes this one does not enforce ``revision``: a live check
    accepted a stale revision and none at all. Every call moves the grid's revision on.

    Examples:
        >>> ColumnUpdate(revision="3", title="Owner", width=40, width_units="%").model_dump(
        ...     exclude_none=True
        ... )
        {'revision': '3', 'title': 'Owner', 'width': 40, 'width_units': '%'}
    """

    revision: str | None = Field(
        default=None, description="Grid revision; this endpoint accepts a stale or missing one."
    )
    title: str | None = Field(
        default=None, min_length=1, max_length=255, description="New column header."
    )
    description: str | None = Field(
        default=None, max_length=1024, description="New free-text column description."
    )
    required: bool | None = Field(default=None, description="Whether a value is mandatory.")
    width: int | None = Field(default=None, description="Column width in ``width_units``.")
    width_units: WidthUnits | None = Field(default=None, description="Unit of ``width``.")
    format: TextFormat | None = Field(
        default=None, description="For text columns: rich-text format."
    )
    pinned: ColumnPinType | None = Field(default=None, description="Edge to pin the column to.")
    color: BGColor | None = Field(default=None, description="Background colour of the column.")
    multiple: bool | None = Field(
        default=None, description="For ``select``/``staff``: allow multiple values."
    )
    ticket_field: TicketField | None = Field(
        default=None, description="For ``ticket_field`` columns: the mirrored Tracker field."
    )
    select_options: list[str] | None = Field(
        default=None, description="For ``select`` columns: the allowed choices."
    )
    mark_rows: bool | None = Field(
        default=None, description="For ``checkbox`` columns: mark the row done when ticked."
    )


class ColumnUpdateResult(APIModel):
    """Reply of ``POST /grids/{id}/column/{slug}`` — the new ``revision`` and the column as saved.

    Examples:
        >>> ColumnUpdateResult.model_validate(
        ...     {"revision": "5", "column": {"slug": "owner", "title": "Owner"}}
        ... ).column.title
        'Owner'
    """

    revision: str | None = Field(default=None, description="The grid's revision after the edit.")
    column: ColumnSchema | None = Field(default=None, description="The column after the edit.")


class RowUpdate(RequestBody):
    """Typed body for ``POST /grids/{id}/rows/{row_id}`` — pin or colour a row (undocumented).

    Cell values are not part of it; set those with ``cells update``. Like ``ColumnUpdate`` it does
    not enforce ``revision`` (a stale or missing one is accepted), and every call moves the grid's
    revision on.

    Examples:
        >>> RowUpdate(revision="3", pinned=True, color="mint").model_dump(exclude_none=True)
        {'revision': '3', 'pinned': True, 'color': 'mint'}
    """

    revision: str | None = Field(
        default=None, description="Grid revision; this endpoint accepts a stale or missing one."
    )
    pinned: bool | None = Field(default=None, description="Pin the row to the top of the grid.")
    color: BGColor | None = Field(default=None, description="Background colour of the row.")


class RowUpdateResult(APIModel):
    """Reply of ``POST /grids/{id}/rows/{row_id}`` — carries no revision.

    The spec says ``{status: "ok"}``, but a live check got an empty object, so ``status`` stays
    ``None``: the 2xx is the success signal, and the new revision comes from ``grids get``.

    Examples:
        >>> RowUpdateResult.model_validate({"status": "ok"}).status
        'ok'
        >>> RowUpdateResult.model_validate({}).status is None
        True
    """

    status: str | None = Field(
        default=None, description="``ok`` when the API says so; the live API sends nothing."
    )


class GridClone(RequestBody):
    """Typed body for ``POST /grids/{id}/clone`` — copy a grid onto another page (async).

    ``target`` is the destination page slug (created if absent); ``with_data`` copies the rows as
    well as the structure. The call is deferred — see :class:`AsyncOperation`.

    Examples:
        >>> GridClone(target="data/y", with_data=True).model_dump(exclude_none=True)
        {'target': 'data/y', 'with_data': True}
    """

    target: str = Field(description="Slug of the page to copy the grid onto (created if absent).")
    title: str | None = Field(
        default=None, min_length=1, max_length=255, description="Title of the copy, if renaming."
    )
    with_data: bool = Field(default=False, description="Copy the rows too, not just the structure.")
