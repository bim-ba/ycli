"""TDD for ycli.yandex.polling.poll — no real waiting; sleep is injected and recorded."""

import pytest

from ycli.yandex.errors import YandexTimeoutError
from ycli.yandex.polling import default_backoff, poll


def _scripted(*statuses):
    """A fetch callable that returns the given statuses in order (then raises if overdrawn)."""
    it = iter(statuses)
    return lambda: next(it)


def test_done_immediately_never_sleeps():
    slept: list[float] = []
    result = poll(
        _scripted({"done": True}),
        lambda status: status["done"],
        sleep=slept.append,
    )
    assert result == {"done": True}
    assert slept == []  # terminal on the first fetch → no sleep


def test_done_after_n_sleeps_n_minus_one_times_with_backoff_sequence():
    slept: list[float] = []
    statuses = [{"done": False}, {"done": False}, {"done": True}]
    result = poll(
        _scripted(*statuses),
        lambda status: status["done"],
        backoff=lambda attempt: attempt + 1,  # 1, 2, 3, …
        sleep=slept.append,
    )
    assert result == {"done": True}
    assert slept == [1, 2]  # done after 3 fetches → 2 sleeps, in backoff order


def test_never_done_raises_and_sleeps_attempts_minus_one_times():
    slept: list[float] = []
    with pytest.raises(YandexTimeoutError, match="did not finish within 3 attempts"):
        poll(
            lambda: {"done": False},
            lambda status: status["done"],
            attempts=3,
            backoff=lambda attempt: attempt,
            sleep=slept.append,
        )
    assert slept == [0, 1]  # 3 attempts → sleeps after the first two, none after the last


def test_default_backoff_schedule_is_exponential():
    assert [default_backoff(n) for n in range(4)] == [0.5, 1.0, 2.0, 4.0]


def test_uses_default_backoff_when_not_overridden():
    slept: list[float] = []
    poll(
        _scripted({"done": False}, {"done": True}),
        lambda status: status["done"],
        sleep=slept.append,
    )
    assert slept == [0.5]  # one sleep, taken from the default exponential schedule


def test_on_attempt_hook_fires_once_per_fetch_with_the_attempt_index():
    seen: list[int] = []
    result = poll(
        _scripted({"done": False}, {"done": False}, {"done": True}),
        lambda status: status["done"],
        sleep=lambda seconds: None,
        on_attempt=seen.append,
    )
    assert result == {"done": True}
    assert seen == [0, 1, 2]  # called before each of the three fetches, 0-indexed
