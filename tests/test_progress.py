"""progress.spinner / progress.wait_for — animated on a terminal stderr, silent when piped."""

import contextlib
import time
from io import StringIO

from rich.console import Console
from rich.status import Status

from ycli.cli.progress import spinner, wait_for


def _console(*, terminal: bool) -> tuple[Console, StringIO]:
    buf = StringIO()
    return Console(file=buf, stderr=True, force_terminal=terminal, width=80), buf


def test_spinner_animates_on_a_terminal():
    console, _buf = _console(terminal=True)
    ctx = spinner("Working…", console=console)
    assert isinstance(ctx, Status)  # the real, animated spinner
    with ctx:  # exercise the render path (enter/exit clears the line)
        pass


def test_spinner_is_a_silent_noop_when_piped():
    console, buf = _console(terminal=False)
    ctx = spinner("Working…", console=console)
    assert isinstance(ctx, contextlib.nullcontext)  # never a Status off a TTY
    with ctx:
        pass
    assert buf.getvalue() == ""  # pristine — nothing written to a piped stream


def test_wait_for_polls_to_done_and_keeps_a_piped_stream_pristine(monkeypatch):
    delays: list[float] = []
    monkeypatch.setattr(time, "sleep", delays.append)
    console, buf = _console(terminal=False)
    statuses = iter(["running", "done"])
    result = wait_for(
        lambda: next(statuses),
        lambda status: status == "done",
        message="Waiting…",
        console=console,
    )
    assert result == "done"
    # the poll's backoff ran through time.sleep resolved at *call* time — the monkeypatch above
    # is what keeps every CLI --wait test instant, so this pins that lookup order
    assert delays == [0.5]
    assert buf.getvalue() == ""  # no spinner bytes on a piped stream


def test_wait_for_animates_on_a_terminal(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    console, _buf = _console(terminal=True)
    statuses = iter(["running", "done"])
    result = wait_for(
        lambda: next(statuses),
        lambda status: status == "done",
        message="Waiting…",
        console=console,
    )
    assert result == "done"  # the Status spinner path is exercised end-to-end (enter/exit)
