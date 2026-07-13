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
import time
from typing import TYPE_CHECKING

from ycli.yandex.polling import poll

if TYPE_CHECKING:
    from collections.abc import Callable

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


def wait_for[P](
    fetch: Callable[[], P],
    is_done: Callable[[P], bool],
    *,
    message: str,
    console: Console,
) -> P:
    """Poll ``fetch`` to a terminal state behind one shared stderr spinner — the CLI ``--wait`` UX.

    Every ``--wait`` flag funnels through here so all commands share the same feedback: an
    animated ``message`` on an interactive stderr (via :func:`spinner`), byte-clean silence
    when piped. Polling semantics (attempt budget, backoff, timeout) live in
    :func:`ycli.yandex.polling.poll` — this wrapper adds presentation only.

    Args:
        fetch: Re-reads the operation status (closes over the client + operation id).
        is_done: Returns ``True`` once ``fetch``'s latest result is terminal.
        message: The status text shown beside the spinner while waiting.
        console: The (stderr) console the spinner renders to when it ``is_terminal``.

    Returns:
        The first ``fetch`` result for which ``is_done`` returned ``True``.

    Raises:
        YandexTimeoutError: the poll's attempt budget elapsed without a terminal state.
    """
    with spinner(message, console=console):
        # ``time.sleep`` is passed at *call* time (poll's default binds it at import), so a
        # test that monkeypatches ``time.sleep`` keeps every ``--wait`` path instant.
        return poll(fetch, is_done, sleep=time.sleep)
