"""Progress feedback for long, silent operations — animated on a TTY, silent when piped.

This is *progress UI*, not data: a spinner renders to **stderr** and only when that stream
is an interactive terminal, so piped/redirected **stdout** stays byte-clean (the ``auto`` and
``json`` machine formats are never touched — ARCH-4 keeps data rendering in ``output.py``; this
module renders no model). On a non-terminal stderr the helper is a no-op context manager, so a
caller wraps a blocking call unconditionally::

    with spinner("Waiting for bulk change…", console=app_ctx.stderr_console):
        result = poll(...)
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console
    from rich.status import Status


def spinner(message: str, *, console: Console) -> Status | contextlib.AbstractContextManager[None]:
    """A ``with``-able spinner: animate ``message`` on a terminal ``console``, else do nothing.

    Args:
        message: The status text shown beside the animated spinner.
        console: The (stderr) console; the spinner renders only when it ``is_terminal``.

    Returns:
        A :class:`rich.status.Status` when ``console`` is an interactive terminal (it animates
        and clears itself on exit), otherwise a :func:`contextlib.nullcontext` that produces no
        output at all — keeping a piped stream pristine.
    """
    if console.is_terminal:
        return console.status(message)
    return contextlib.nullcontext()
