"""Pydantic models for Tracker queue macros (Macro + refs + write bodies).

Mirrors ``GET /queues/{id}/macros`` (list) and ``.../macros/{macro_id}`` (single). A macro runs
a canned comment plus field updates on an issue. Note the asymmetry the API exposes: the
``issueUpdate`` block is a *list* of field/update objects on the way out, but a plain *object*
of field→value on the way in (see :class:`MacroCreate`).
"""

from __future__ import annotations

from typing import Any

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class MacroQueueRef(APIModel):
    """The queue a macro belongs to (``queue`` object).

    Example:
        >>> MacroQueueRef.model_validate({"key": "TEST", "display": "My queue"}).key
        'TEST'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the queue.",
    )
    id: str | None = Field(default=None, description="Identifier of the queue.")
    key: str | None = Field(default=None, description="Key of the queue (e.g. TEST).")
    display: str | None = Field(default=None, description="Human-readable name of the queue.")


class MacroField(APIModel):
    """A task-field reference inside a macro's ``issueUpdate`` row.

    Example:
        >>> MacroField.model_validate({"id": "tags", "display": "Tags"}).id
        'tags'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the task field.",
    )
    id: str | None = Field(default=None, description="Identifier of the task field.")
    display: str | None = Field(default=None, description="Human-readable name of the task field.")


class MacroFieldUpdate(APIModel):
    """One field-update row in a macro's ``issueUpdate`` list.

    Example:
        >>> MacroFieldUpdate.model_validate(
        ...     {"field": {"id": "tags"}, "update": {"add": ["tag 1"]}}
        ... ).field.id
        'tags'
    """

    field: MacroField | None = Field(
        default=None, description="The task field this row updates when the macro runs."
    )
    update: Any = Field(
        default=None, description="The change applied to the field (e.g. {'add': [...]})."
    )


class Macro(APIModel):
    """A queue macro (``GET /queues/{id}/macros`` item and ``.../macros/{macro_id}``).

    Example:
        >>> Macro.model_validate({"id": 3, "name": "My macro"}).name
        'My macro'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns the macro's parameters.",
    )
    id: int | None = Field(default=None, description="Unique identifier of the macro.")
    queue: MacroQueueRef | None = Field(
        default=None, description="Queue whose issues the macro applies to."
    )
    name: str | None = Field(default=None, description="Human-readable name of the macro.")
    body: str | None = Field(
        default=None, description="Comment text created when the macro is executed."
    )
    issue_update: list[MacroFieldUpdate] = Field(
        default_factory=list,
        alias="issueUpdate",
        description="Field updates the macro applies to the issue.",
    )


class MacroList(RootModel[list[Macro]]):
    """A bare JSON array of macros — the flat public shape of ``macros.list()``.

    Example:
        >>> MacroList.model_validate([{"id": 3, "name": "My macro"}]).root[0].name
        'My macro'
    """


class MacroCreate(APIModel):
    """Typed request body for ``macros.create`` (``POST /queues/{id}/macros``).

    ``issue_update`` here is a field→value *object* (not the list the read side returns),
    e.g. ``{"tags": {"add": "Новый тег"}, "resolution": None}``.

    Example:
        >>> MacroCreate(name="Test macro", body="Hi {{issue.author}}").name
        'Test macro'
    """

    name: str = Field(description="Name of the new macro.")
    body: str | None = Field(default=None, description="Comment text created when the macro runs.")
    issue_update: dict[str, Any] | None = Field(
        default=None,
        serialization_alias="issueUpdate",
        description="Field→value object of issue changes the macro applies.",
    )


class MacroUpdate(APIModel):
    """Typed request body for ``macros.edit`` (``PATCH /queues/{id}/macros/{macro_id}``).

    Every field is optional; only the fields you set are sent.

    Example:
        >>> MacroUpdate(name="Renamed").name
        'Renamed'
    """

    name: str | None = Field(default=None, description="New name of the macro.")
    body: str | None = Field(
        default=None, description="New comment text created when the macro runs."
    )
    issue_update: dict[str, Any] | None = Field(
        default=None,
        serialization_alias="issueUpdate",
        description="Replacement field→value object of issue changes the macro applies.",
    )
