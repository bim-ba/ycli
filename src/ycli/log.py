"""Central loguru configuration — one sink to stderr, idempotent.

``configure()`` always removes existing sinks and installs exactly one stderr sink,
so calling it more than once never stacks duplicate output and always rebinds to the
current ``sys.stderr`` (important under pytest's ``capsys``). stdout stays clean for
machine-readable command output.

Example:
    >>> from ycli.log import configure
    >>> configure()  # doctest: +SKIP
"""

from __future__ import annotations

import sys

from loguru import logger


def configure(level: str = "INFO") -> None:
    """Install a single stderr sink at ``level`` (idempotent — safe to call repeatedly).

    Example:
        >>> configure("DEBUG")  # doctest: +SKIP
    """
    logger.remove()
    logger.add(sys.stderr, level=level, backtrace=False, diagnose=False)
