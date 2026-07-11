"""progress.spinner — animated on a terminal stderr, a silent no-op when piped."""

import contextlib
from io import StringIO

from rich.console import Console
from rich.status import Status

from ycli.cli.progress import spinner


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
