"""The one place e2e reads its own configuration from the environment."""

from __future__ import annotations

import os

QUEUE_VARIABLE = "YCLI_E2E_QUEUE"
DEFAULT_QUEUE = "YCLIPAGE"  # the owner's sandbox queue: Tracker issues cannot be deleted


def sandbox_queue() -> str:
    """The Tracker queue scenarios write to: ``$YCLI_E2E_QUEUE``, else ``YCLIPAGE``."""
    return os.environ.get(QUEUE_VARIABLE, DEFAULT_QUEUE)
