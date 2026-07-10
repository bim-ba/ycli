"""Pydantic model for a Forms async operation (``/operations/{id}``)."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel

#: Statuses at which a Forms operation has stopped running (a poll terminates here).
TERMINAL_STATUSES = frozenset({"ok", "fail"})


class OperationResult(APIModel):
    """A Forms async operation's status — ``{id, status, message}`` (``GET /v1/operations/{id}``).

    Long-running Forms actions — notably an answers export (``ycli forms answers export``) —
    return an operation ``id``; re-read this endpoint until :attr:`is_terminal`. ``status`` is
    one of ``ok`` (finished, result ready), ``fail``, ``wait`` (still running) or
    ``not_running``. This is the generic sibling of
    :class:`~ycli.yandex.forms.answers.models.ExportResult`.

    Example:
        >>> OperationResult.model_validate({"id": "op-1", "status": "ok"}).is_ready
        True
    """

    id: str | None = Field(
        default=None, description="Operation id (echoes the id an async trigger returned)."
    )
    status: str | None = Field(
        default=None,
        description="Operation status: one of ``ok``, ``fail``, ``wait``, ``not_running``.",
    )
    message: str | None = Field(default=None, description="Human-readable operation message.")

    @property
    def is_terminal(self) -> bool:
        """``True`` once ``status`` reached a terminal value (see :data:`TERMINAL_STATUSES`)."""
        return self.status in TERMINAL_STATUSES

    @property
    def is_ready(self) -> bool:
        """``True`` when the operation finished successfully (``status == "ok"``)."""
        return self.status == "ok"
