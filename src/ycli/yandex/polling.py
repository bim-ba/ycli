"""Poll an async operation to a terminal state — pure, with an injected ``sleep`` for tests.

Yandex exposes several long-running operations (Tracker bulk-change, Wiki page/grid clone,
Forms answer export) as a *trigger* call plus a *status* endpoint you re-read until it reports
done. This module owns that loop once: it re-invokes ``fetch`` until ``is_done`` is satisfied,
sleeping ``backoff(attempt)`` seconds between tries, for ``max_wait_seconds`` at most.
Everything time-related is injected —
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
    hour- or day-long single sleeps instead of failing within the waiting budget.
    """
    return min(60.0, 0.5 * (2**attempt))


def poll[P](
    fetch: Callable[[], P],
    is_done: Callable[[P], bool],
    *,
    max_wait_seconds: float,
    backoff: Callable[[int], float] = default_backoff,
    sleep: Callable[[float], None] = time.sleep,
) -> P:
    """Re-invoke ``fetch`` until ``is_done`` accepts its result, then return that result.

    Between two consecutive fetches it sleeps ``backoff(n)`` seconds (``n`` is the 0-indexed
    attempt just completed), and the sleeps add up to ``max_wait_seconds`` at most: the last one
    is cut to what is left, then one more fetch runs. If ``is_done`` is still false it raises
    :class:`~ycli.yandex.errors.YandexTimeoutError`. The budget counts the sleeps, not the
    fetches. ``sleep`` and ``backoff`` are injected so tests can run the loop instantly and
    assert the delay sequence.

    Args:
        fetch: Re-reads the operation status (closes over the client + operation id).
        is_done: Returns ``True`` once ``fetch``'s latest result is terminal.
        max_wait_seconds: The longest the sleeps may add up to before giving up
            (:attr:`ycli.settings.HTTPConfig.max_wait_seconds` on the CLI).
        backoff: Maps a 0-indexed attempt to the seconds to sleep before the next fetch.
        sleep: The blocking sleep (default :func:`time.sleep`; pass a recorder in tests).

    Returns:
        The first ``fetch`` result for which ``is_done`` returned ``True``.

    Raises:
        YandexTimeoutError: ``max_wait_seconds`` passed without ``is_done`` becoming true.

    Examples:
        >>> statuses = iter([{"done": False}, {"done": True}])
        >>> a_minute = 60.0
        >>> poll(
        ...     lambda: next(statuses),
        ...     lambda status: status["done"],
        ...     max_wait_seconds=a_minute,
        ...     sleep=lambda seconds: None,
        ... )
        {'done': True}
    """
    waited = 0.0
    attempt = 0
    while True:
        status = fetch()
        if is_done(status):
            return status
        left = max_wait_seconds - waited
        if left <= 0:
            raise YandexTimeoutError(f"operation did not finish within {max_wait_seconds:g} s")
        delay = min(backoff(attempt), left)
        sleep(delay)
        waited += delay
        attempt += 1
