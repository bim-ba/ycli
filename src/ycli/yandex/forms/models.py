"""Forms models that several resources share: one class per shape."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel

#: Statuses at which a background operation has stopped running.
TERMINAL_STATUSES = frozenset({"ok", "fail"})


class OperationResult(APIModel):
    """The status of a Forms background operation: ``{id, status, message}``.

    A long-running action (an answers export) answers with an operation ``id``; re-read its
    status until :attr:`is_terminal`. ``status`` is one of ``ok`` (finished, result ready),
    ``fail``, ``wait`` (still running) or ``not_running``.

    Examples:
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
