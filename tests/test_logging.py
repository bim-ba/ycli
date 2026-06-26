"""TDD for central loguru configuration — one sink to stderr, idempotent."""

from loguru import logger

from ycli.log import configure


def test_configure_emits_to_stderr(capsys):
    configure()
    logger.info("hello-from-test")
    assert "hello-from-test" in capsys.readouterr().err


def test_configure_idempotent_no_duplicate_output(capsys):
    configure()
    configure()  # second call must not stack a duplicate sink
    logger.info("once")
    assert capsys.readouterr().err.count("once") == 1
