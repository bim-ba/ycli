"""Poll an async operation to a terminal state — pure, with an injected ``sleep`` for tests.

Yandex exposes several long-running operations (Tracker bulk-change, Wiki page/grid clone,
Forms answer export) as a *trigger* call plus a *status* endpoint you re-read until it reports
done. This module owns that loop once: it re-invokes ``fetch`` until ``is_done`` is satisfied,
sleeping ``backoff(attempt)`` seconds between tries. Everything time-related is injected —
``sleep`` and ``backoff`` are callables — so a test drives the whole schedule with a no-op
recorder and observes the exact delay sequence without ever waiting. Pure: no HTTP here (the
caller's ``fetch`` closes over a client), so the same style as ``pagination.py``.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from ycli.yandex.errors import YandexTimeoutError

if TYPE_CHECKING:
    from collections.abc import Callable


def default_backoff(attempt: int) -> float:
    """Default delay ``0.5, 1, 2, 4, …`` s (doubling per 0-indexed attempt), capped at 60 s.

    The cap keeps a stuck long-poll (``--wait`` is the default for bulk ops) from ballooning to
    hour- or day-long single sleeps instead of failing within the ``attempts`` budget.
    """
    return min(60.0, 0.5 * (2**attempt))


def poll[P](
    fetch: Callable[[], P],
    is_done: Callable[[P], bool],
    *,
    attempts: int = 30,
    backoff: Callable[[int], float] = default_backoff,
    sleep: Callable[[float], None] = time.sleep,
) -> P:
    """Re-invoke ``fetch`` until ``is_done`` accepts its result, then return that result.

    Runs at most ``attempts`` fetches. Between two consecutive fetches it sleeps
    ``backoff(n)`` seconds (``n`` is the 0-indexed attempt just completed); it never sleeps
    after the final attempt. If ``is_done`` never becomes true within the budget it raises
    :class:`~ycli.yandex.errors.YandexTimeoutError`. ``sleep`` and ``backoff`` are injected so
    tests can run the loop instantly and assert the delay sequence.

    Args:
        fetch: Re-reads the operation status (closes over the client + operation id).
        is_done: Returns ``True`` once ``fetch``'s latest result is terminal.
        attempts: Maximum number of ``fetch`` calls before giving up.
        backoff: Maps a 0-indexed attempt to the seconds to sleep before the next fetch.
        sleep: The blocking sleep (default :func:`time.sleep`; pass a recorder in tests).

    Returns:
        The first ``fetch`` result for which ``is_done`` returned ``True``.

    Raises:
        YandexTimeoutError: ``attempts`` fetches elapsed without ``is_done`` becoming true.

    Example:
        >>> statuses = iter([{"done": False}, {"done": True}])
        >>> poll(
        ...     lambda: next(statuses),
        ...     lambda status: status["done"],
        ...     sleep=lambda seconds: None,
        ... )
        {'done': True}
    """
    for attempt in range(attempts):
        status = fetch()
        if is_done(status):
            return status
        if attempt < attempts - 1:
            sleep(backoff(attempt))
    raise YandexTimeoutError(f"operation did not finish within {attempts} attempts")
