"""TDD for ycli.yandex.polling.poll — no real waiting; sleep is injected and recorded."""

import pytest

from ycli.settings import HTTPConfig
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
        max_wait_seconds=60,
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
        max_wait_seconds=60,
        backoff=lambda attempt: attempt + 1,  # 1, 2, 3, …
        sleep=slept.append,
    )
    assert result == {"done": True}
    assert slept == [1, 2]  # done after 3 fetches → 2 sleeps, in backoff order


def test_never_done_raises_once_the_sleeps_add_up_to_the_budget():
    slept: list[float] = []
    fetched: list[int] = []
    with pytest.raises(YandexTimeoutError, match=r"did not finish within 10 s"):
        poll(
            lambda: fetched.append(1) or {"done": False},
            lambda status: status["done"],
            max_wait_seconds=10,
            backoff=lambda attempt: 4,
            sleep=slept.append,
        )
    assert slept == [4, 4, 2]  # the last sleep is cut to what is left of the budget
    assert len(fetched) == 4  # and one more fetch runs after it


def test_the_default_budget_is_the_twenty_three_minutes_it_was():
    slept: list[float] = []
    with pytest.raises(YandexTimeoutError, match=r"within 1380 s"):
        poll(
            lambda: {"done": False},
            lambda status: status["done"],
            max_wait_seconds=HTTPConfig().max_wait_seconds,
            sleep=slept.append,
        )
    assert sum(slept) == 1380.0
    assert max(slept) == 60.0


def test_default_backoff_schedule_is_exponential():
    assert [default_backoff(n) for n in range(4)] == [0.5, 1.0, 2.0, 4.0]


def test_uses_default_backoff_when_not_overridden():
    slept: list[float] = []
    poll(
        _scripted({"done": False}, {"done": True}),
        lambda status: status["done"],
        max_wait_seconds=60,
        sleep=slept.append,
    )
    assert slept == [0.5]  # one sleep, taken from the default exponential schedule
