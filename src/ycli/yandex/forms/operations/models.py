"""Pydantic model for a Forms async operation (``/operations/{id}``)."""

from __future__ import annotations

from ycli.yandex.forms import models as _shared

TERMINAL_STATUSES = _shared.TERMINAL_STATUSES  # deprecated, removed in 0.39
OperationResult = _shared.OperationResult  # deprecated, removed in 0.39
