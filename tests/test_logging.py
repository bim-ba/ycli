"""Logging: the library only emits; ``configure`` sends ``ycli`` records to stderr."""

import json
import logging

import pytest
import responses
from typer.testing import CliRunner
from urllib3.response import HTTPResponse

from ycli.log import LOGGER_NAME, configure
from ycli.yandex.transport import Transport, retry_policy

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
    configure("INFO")
    logger.debug("hidden-line")
    logger.info("shown-line")
    err = capsys.readouterr().err
    assert "INFO ycli.test: shown-line" in err
    assert "hidden-line" not in err


def test_configure_is_idempotent(capsys):
    configure("INFO")
    configure("INFO")  # a second call swaps the handler instead of stacking one
    logger.info("once")
    assert capsys.readouterr().err.count("once") == 1


def test_configure_json_format(capsys):
    configure("INFO", "json")
    logger.info("structured %s", "line")
    entry = json.loads(capsys.readouterr().err)
    assert entry["level"] == "INFO"
    assert entry["logger"] == "ycli.test"
    assert entry["message"] == "structured line"


def test_json_format_carries_the_exception(capsys):
    configure("INFO", "json")
    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("failed")
    entry = json.loads(capsys.readouterr().err)
    assert "ValueError: boom" in entry["exception"]


@responses.activate
def test_http_response_is_logged_without_the_token(capsys):
    responses.get("https://api.example.test/v2/myself", json={}, status=200)
    configure("INFO")
    session = Transport.session(
        oauth_token="y0_secret-token", organization_id="o", timeout_seconds=30.0, retries=0
    )
    session.get("https://api.example.test/v2/myself")
    err = capsys.readouterr().err
    assert "INFO ycli.http: GET https://api.example.test/v2/myself -> 200" in err
    assert "secret-token" not in err


def test_retry_is_logged(capsys):
    configure("INFO")
    retry = retry_policy(2).increment("GET", "/v2/issues", response=HTTPResponse(status=503))
    assert retry.total == 1
    assert "retrying GET /v2/issues after 503 (1 left)" in capsys.readouterr().err


@pytest.mark.integration
@pytest.mark.parametrize(
    ("flags", "level"), [([], "WARNING"), (["-v"], "INFO"), (["--verbose", "-v"], "DEBUG")]
)
def test_verbose_flag_raises_the_level(monkeypatch, flags, level):
    from ycli.cli.app import app

    monkeypatch.delenv("YCLI__LOGGING__LEVEL", raising=False)
    calls = []
    monkeypatch.setattr("ycli.cli.app.configure", lambda **kwargs: calls.append(kwargs))
    # Root --help does not run the callback; a sub-app's --help does.
    CliRunner().invoke(app, [*flags, "tracker", "--help"])
    assert calls == [{"level": level, "log_format": "text"}]
