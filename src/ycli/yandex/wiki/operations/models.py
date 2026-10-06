"""Pydantic v2 models for Yandex Wiki async operation status (``/operations``).

A page or grid *clone* and a page *move* are deferred operations: the trigger (``pages clone`` /
``grids clone`` / ``pages move``) returns an operation reference, and you re-read a status
endpoint here until ``status`` reaches a terminal value. :attr:`CloneOperationStatus.is_terminal`,
:attr:`GridCloneOperationStatus.is_terminal` and :attr:`MoveOperationStatus.is_terminal` are the
stop predicates for the ``--wait`` CLI path.

Replies keep unknown fields (:class:`~ycli.yandex.models.APIModel`); request bodies refuse them.
"""

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel
from ycli.yandex.wiki.models import PageIdentity

#: Lifecycle status of an async operation.
OperationStatus = Literal["scheduled", "in_progress", "success", "failed"] | str
#: Statuses at which an async operation has stopped running (poll terminates here).
TERMINAL_STATUSES = frozenset({"success", "failed"})


class OperationProgress(APIModel):
    """Progress of a running clone operation — a fraction plus an optional detail string.

    Examples:
        >>> OperationProgress(percentage=0.5).percentage
        0.5
    """

    percentage: float | None = Field(
        default=None, description="Completion fraction in ``[0, 1]`` (``0.5`` = half done)."
    )
    details: str | None = Field(default=None, description="Free-text progress detail, if any.")


class OperationState(APIModel):
    """What every status of an asynchronous Wiki operation carries: where it is and how far.

    Each operation adds its own ``result``. Poll until :attr:`is_terminal`.

    Examples:
        >>> OperationState.model_validate({"status": "in_progress"}).is_terminal
        False
    """

    status: OperationStatus | None = Field(
        default=None,
        description="Lifecycle status (``scheduled``/``in_progress``/``success``/``failed``).",
    )
    progress: OperationProgress | None = Field(
        default=None, description="Progress of the running operation."
    )

    @property
    def is_terminal(self) -> bool:
        """``True`` once ``status`` reached a terminal value (see :data:`TERMINAL_STATUSES`)."""
        return self.status in TERMINAL_STATUSES


class PageCloneResult(APIModel):
    """Result payload of a finished page-clone operation — the cloned ``page``.

    Examples:
        >>> PageCloneResult.model_validate({"page": {"id": 42, "slug": "data/y"}}).page.slug
        'data/y'
    """

    page: PageIdentity | None = Field(default=None, description="The page that was cloned.")


class GridCloneResult(APIModel):
    """Result payload of a finished grid-clone operation — the new ``grid_id`` (and page).

    ``page`` is the page the grid landed on; ``grid`` is a transitional legacy-table schema.

    Examples:
        >>> GridCloneResult.model_validate({"grid_id": "g2"}).grid_id
        'g2'
    """

    grid_id: str | int | None = Field(
        default=None, description="Id of the cloned grid (uuid4 or int)."
    )
    page: PageIdentity | None = Field(
        default=None, description="Page the dynamic table was copied onto."
    )
    grid: PageIdentity | None = Field(
        default=None, description="Transitional legacy-table schema (deprecated)."
    )


class CloneOperationStatus(OperationState):
    """Status of a page-clone operation (``GET /operations/clone/{task_id}``).

    Poll this until :attr:`is_terminal`; on ``success`` the ``result.page`` names the clone.

    Examples:
        >>> CloneOperationStatus.model_validate({"status": "success"}).is_terminal
        True
    """

    result: PageCloneResult | None = Field(
        default=None, description="Result payload (present once ``status`` is ``success``)."
    )


class GridCloneOperationStatus(OperationState):
    """Status of an inline-grid-clone operation (``GET /operations/clone_inline_grid/{task_id}``).

    Poll this until :attr:`is_terminal`; on ``success`` the ``result.grid_id`` names the copy.

    Examples:
        >>> GridCloneOperationStatus.model_validate(
        ...     {"status": "success", "result": {"grid_id": "g2"}}
        ... ).result.grid_id
        'g2'
    """

    result: GridCloneResult | None = Field(
        default=None, description="Result payload (present once ``status`` is ``success``)."
    )


class PageMoveResult(APIModel):
    """Result payload of a finished page-move operation — how many pages changed address.

    Examples:
        >>> PageMoveResult.model_validate({"page_count": 3}).page_count
        3
    """

    page_count: int | None = Field(
        default=None, description="Number of pages moved (the page and its descendants)."
    )


class MoveOperationStatus(OperationState):
    """Status of a page-move operation (``GET /operations/move/{task_id}``).

    Undocumented by Yandex (it is in the live OpenAPI only) and may change. Poll this until
    :attr:`is_terminal`; on ``success`` the ``result.page_count`` says how many pages moved.

    Examples:
        >>> MoveOperationStatus.model_validate(
        ...     {"status": "success", "result": {"page_count": 2}}
        ... ).result.page_count
        2
    """

    result: PageMoveResult | None = Field(
        default=None, description="Result payload (present once ``status`` is ``success``)."
    )
