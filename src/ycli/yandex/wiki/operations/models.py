"""Pydantic v2 models for Yandex Wiki async operation status (``/operations``).

A page or grid *clone* is a deferred operation: the trigger (``pages clone`` / ``grids clone``)
returns an operation reference, and you re-read a status endpoint here until ``status`` reaches a
terminal value. :attr:`CloneOperationStatus.is_terminal` /
:attr:`GridCloneOperationStatus.is_terminal` are the stop predicates for
:func:`ycli.yandex.polling.poll` on the ``--wait`` CLI path.

``extra='ignore'`` via :class:`~ycli.yandex.models.APIModel`.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel

#: Lifecycle status of a clone operation.
OperationStatus = Literal["scheduled", "in_progress", "success", "failed"]
#: Statuses at which a clone operation has stopped running (poll terminates here).
TERMINAL_STATUSES = frozenset({"success", "failed"})


class OperationProgress(APIModel):
    """Progress of a running clone operation — a fraction plus an optional detail string.

    Example:
        >>> OperationProgress(percentage=0.5).percentage
        0.5
    """

    percentage: float | None = Field(
        default=None, description="Completion fraction in ``[0, 1]`` (``0.5`` = half done)."
    )
    details: str | None = Field(default=None, description="Free-text progress detail, if any.")


class PageSchema(APIModel):
    """A cloned page reference (``{id, slug}``) in a clone operation's result.

    Example:
        >>> PageSchema(id=42, slug="data/y").slug
        'data/y'
    """

    id: int | None = Field(default=None, description="Numeric id of the cloned page.")
    slug: str | None = Field(default=None, description="Slug of the cloned page.")


class PageCloneResult(APIModel):
    """Result payload of a finished page-clone operation — the cloned ``page``.

    Example:
        >>> PageCloneResult.model_validate({"page": {"id": 42, "slug": "data/y"}}).page.slug
        'data/y'
    """

    page: PageSchema | None = Field(default=None, description="The page that was cloned.")


class GridCloneResult(APIModel):
    """Result payload of a finished grid-clone operation — the new ``grid_id`` (and page).

    ``page`` is the page the grid landed on; ``grid`` is a transitional legacy-table schema.

    Example:
        >>> GridCloneResult.model_validate({"grid_id": "g2"}).grid_id
        'g2'
    """

    grid_id: str | int | None = Field(
        default=None, description="Id of the cloned grid (uuid4 or int)."
    )
    page: PageSchema | None = Field(
        default=None, description="Page the dynamic table was copied onto."
    )
    grid: PageSchema | None = Field(
        default=None, description="Transitional legacy-table schema (deprecated)."
    )


class CloneOperationStatus(APIModel):
    """Status of a page-clone operation (``GET /operations/clone/{task_id}``).

    Poll this until :attr:`is_terminal`; on ``success`` the ``result.page`` names the clone.

    Example:
        >>> CloneOperationStatus.model_validate({"status": "success"}).is_terminal
        True
    """

    status: OperationStatus | None = Field(
        default=None,
        description="Lifecycle status (``scheduled``/``in_progress``/``success``/``failed``).",
    )
    progress: OperationProgress | None = Field(
        default=None, description="Progress of the running operation."
    )
    result: PageCloneResult | None = Field(
        default=None, description="Result payload (present once ``status`` is ``success``)."
    )

    @property
    def is_terminal(self) -> bool:
        """``True`` once ``status`` reached a terminal value (see :data:`TERMINAL_STATUSES`)."""
        return self.status in TERMINAL_STATUSES


class GridCloneOperationStatus(APIModel):
    """Status of an inline-grid-clone operation (``GET /operations/clone_inline_grid/{task_id}``).

    Poll this until :attr:`is_terminal`; on ``success`` the ``result.grid_id`` names the copy.

    Example:
        >>> GridCloneOperationStatus.model_validate(
        ...     {"status": "success", "result": {"grid_id": "g2"}}
        ... ).result.grid_id
        'g2'
    """

    status: OperationStatus | None = Field(
        default=None,
        description="Lifecycle status (``scheduled``/``in_progress``/``success``/``failed``).",
    )
    progress: OperationProgress | None = Field(
        default=None, description="Progress of the running operation."
    )
    result: GridCloneResult | None = Field(
        default=None, description="Result payload (present once ``status`` is ``success``)."
    )

    @property
    def is_terminal(self) -> bool:
        """``True`` once ``status`` reached a terminal value (see :data:`TERMINAL_STATUSES`)."""
        return self.status in TERMINAL_STATUSES
