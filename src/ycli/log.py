"""Logging for ycli — the library only emits records; the entry points decide where they go.

Every module logs under the ``ycli`` logger (``ycli.http`` for HTTP traffic). The package
installs a ``NullHandler`` on import, as the stdlib recommends for libraries, so the SDK stays
silent inside a host application until that application configures logging. The CLI and the
MCP server call :func:`configure`, which installs exactly one stderr handler: stdout stays
clean for command output and for the MCP stdio protocol.

Example:
    >>> configure("INFO", "json")  # doctest: +SKIP
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Literal

type LogFormat = Literal["text", "json"]

LOGGER_NAME = "ycli"
_HANDLER_NAME = "ycli.stderr"


class JSONFormatter(logging.Formatter):
    """One JSON object per line: ``{"time", "level", "logger", "message"}``.

    Example:
        >>> record = logging.LogRecord("ycli.http", logging.INFO, "", 0, "GET /x", None, None)
        >>> json.loads(JSONFormatter().format(record))["message"]
        'GET /x'
    """

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


def configure(level: str = "WARNING", log_format: LogFormat = "text") -> None:
    """Send ``ycli`` records at ``level`` and above to stderr, replacing an earlier setup.

    Idempotent: a repeated call swaps the handler instead of stacking a second one, and binds
    the current ``sys.stderr`` (pytest's ``capsys`` replaces it per test).
    """
    logger = logging.getLogger(LOGGER_NAME)
    for handler in [h for h in logger.handlers if h.name == _HANDLER_NAME]:
        logger.removeHandler(handler)
    handler = logging.StreamHandler(sys.stderr)
    handler.name = _HANDLER_NAME
    handler.setFormatter(
        JSONFormatter()
        if log_format == "json"
        else logging.Formatter("%(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(level)
    # The process owns this handler; a root handler set up by a dependency must not print twice.
    logger.propagate = False
    # ycli logs its own retries under ycli.http; stamina's duplicate WARNING would otherwise
    # reach stderr through logging's last-resort handler.
    logging.getLogger("stamina").setLevel(logging.ERROR)
