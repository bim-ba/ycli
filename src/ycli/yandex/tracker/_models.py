"""Shared pydantic sub-models for Tracker resources (key/id/display refs).

The three ref models flatten the API's ``{key}`` / ``{id}`` / ``{display}`` wrapper
objects that recur across issues, links, changelog, etc. See each class's own
``Example`` below.
"""

from __future__ import annotations

from ycli.models import APIModel


class _KeyRef(APIModel):
    """A reference object carrying a ``key`` string.

    Example:
        >>> _KeyRef.model_validate({"key": "task"}).key
        'task'
    """

    key: str | None = None


class _IdRef(APIModel):
    """A reference object carrying an ``id`` string.

    Example:
        >>> _IdRef.model_validate({"id": "relates"}).id
        'relates'
    """

    id: str | None = None


class _DisplayRef(APIModel):
    """A reference object carrying a ``display`` string.

    Example:
        >>> _DisplayRef.model_validate({"display": "Сава"}).display
        'Сава'
    """

    display: str | None = None
