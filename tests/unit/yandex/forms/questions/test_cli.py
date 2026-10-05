"""`forms questions create`: the flags build the question through the typed union."""

from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli

SID = "686d0a1b2c3d4e5f00000070"


def test_a_flag_the_question_type_does_not_take_is_refused_before_sending(api):
    argv = ["forms", "questions", "create", SID, "--type", "boolean", "--label", "Ok?"]
    res = CliRunner().invoke(cli.app, [*argv, "--multiline"])
    assert isinstance(res.exception, ValidationError), repr(res.exception)
    assert "boolean.multiline" in str(res.exception)
    assert api.calls == []
