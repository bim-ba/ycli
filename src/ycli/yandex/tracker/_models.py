"""Shared pydantic sub-models for Tracker resources (lenient; key/id/display refs).

``_Lenient`` ignores extra fields and accepts population by name OR alias. The three
ref models flatten the API's ``{key}`` / ``{id}`` / ``{display}`` wrapper objects that
recur across issues, links, changelog, etc. See each class's own ``Example`` below.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Lenient(BaseModel):
    """Base model: extra fields silently ignored, population by name OR alias allowed."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class _KeyRef(_Lenient):
    """A reference object carrying a ``key`` string.

    Example:
        >>> _KeyRef.model_validate({"key": "task"}).key
        'task'
    """

    key: str | None = None


class _IdRef(_Lenient):
    """A reference object carrying an ``id`` string.

    Example:
        >>> _IdRef.model_validate({"id": "relates"}).id
        'relates'
    """

    id: str | None = None


class _DisplayRef(_Lenient):
    """A reference object carrying a ``display`` string.

    Example:
        >>> _DisplayRef.model_validate({"display": "Сава"}).display
        'Сава'
    """

    display: str | None = None
