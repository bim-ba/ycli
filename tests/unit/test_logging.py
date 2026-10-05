"""Logging: the library only emits; ``configure`` sends ``ycli`` records to stderr."""

import json
import logging

import pytest
from typer.testing import CliRunner

from ycli.log import LOGGER_NAME, LogFormat, LogLevel, configure

logger = logging.getLogger("ycli.test")


@pytest.fixture(autouse=True)
def _restore_ycli_logger():
    """Each test configures the shared ``ycli`` logger; put it back afterwards."""
    package_logger = logging.getLogger(LOGGER_NAME)
    saved = (list(package_logger.handlers), package_logger.level, package_logger.propagate)
    yield
    package_logger.handlers[:] = saved[0]
    package_logger.setLevel(saved[1])
    package_logger.propagate = saved[2]


def test_library_is_silent_until_configured():
    """``import ycli`` installs only a NullHandler — a host app sees nothing by default."""
    import ycli  # noqa: F401

    handlers = logging.getLogger(LOGGER_NAME).handlers
    assert any(isinstance(handler, logging.NullHandler) for handler in handlers)


def test_configure_emits_to_stderr_at_level(capsys):
    configure(LogLevel.INFO)
    logger.debug("hidden-line")
    logger.info("shown-line")
    err = capsys.readouterr().err
    assert "INFO ycli.test: shown-line" in err
    assert "hidden-line" not in err


def test_configure_is_idempotent(capsys):
    configure(LogLevel.INFO)
    configure(LogLevel.INFO)  # a second call swaps the handler instead of stacking one
    logger.info("once")
    assert capsys.readouterr().err.count("once") == 1


def test_configure_json_format(capsys):
    configure(LogLevel.INFO, LogFormat.JSON)
    logger.info("structured %s", "line")
    entry = json.loads(capsys.readouterr().err)
    assert entry["level"] == "INFO"
    assert entry["logger"] == "ycli.test"
    assert entry["message"] == "structured line"


def test_json_format_carries_the_exception(capsys):
    configure(LogLevel.INFO, LogFormat.JSON)
    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("failed")
    entry = json.loads(capsys.readouterr().err)
    assert "ValueError: boom" in entry["exception"]


@pytest.mark.parametrize(
    ("flags", "level"), [([], "WARNING"), (["-v"], "INFO"), (["--verbose", "-v"], "DEBUG")]
)
def test_verbose_flag_raises_the_level(monkeypatch, flags, level):
    from ycli.cli.app import app

    monkeypatch.delenv("YCLI__LOGGING__LEVEL", raising=False)
    calls = []
    monkeypatch.setattr("ycli.log.configure", lambda **kwargs: calls.append(kwargs))
    # Root --help does not run the callback; a sub-app's --help does.
    CliRunner().invoke(app, [*flags, "tracker", "--help"])
    assert calls == [{"level": level, "log_format": "text"}]


@pytest.mark.parametrize(
    ("configured", "flags", "level"),
    [
        ("DEBUG", [], "DEBUG"),
        ("DEBUG", ["-v"], "DEBUG"),  # -v never lowers a configured level
        ("ERROR", [], "ERROR"),
        ("ERROR", ["-v"], "INFO"),
        ("INFO", ["-v", "-v"], "DEBUG"),
    ],
)
def test_verbose_flag_never_lowers_the_configured_level(monkeypatch, configured, flags, level):
    from ycli.cli.app import app

    monkeypatch.setenv("YCLI__LOGGING__LEVEL", configured)
    calls = []
    monkeypatch.setattr("ycli.log.configure", lambda **kwargs: calls.append(kwargs))
    CliRunner().invoke(app, [*flags, "tracker", "--help"])
    assert calls == [{"level": level, "log_format": "text"}]
