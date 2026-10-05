"""Forms CLI arguments refused before any request is sent."""

import re

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import FORMS_BASE as BASE

SID = "686d0a1b2c3d4e5f00000070"


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["files", "verify", SID, "--path", "a", "--url", "u", "--url", "v"], "count must match"),
        (
            ["questions", "create", SID, "--type", "matrix", "--label", "x"],
            "'matrix' is not one of",
        ),
        (["surveys", "create", "--name", "x", "--field", "no-equals"], "key=value"),
        (["keysets", "create", SID, "--name", "x", "--total", "1"], "--enabled"),
    ],
)
def test_bad_arguments_fail_before_sending(argv, message):
    res = CliRunner().invoke(cli.app, ["forms", *argv])
    assert res.exit_code != 0
    # CI forces colour: drop the escape codes and the panel border before matching the words.
    plain = re.sub(r"[│╭╮╰╯─]", " ", re.sub(r"\x1b\[[0-9;]*m", "", res.output))
    assert message in " ".join(plain.split())


def test_files_verify_with_no_path_is_sent_as_given(api):
    api.add("POST", f"{BASE}/surveys/{SID}/files/verify", json=[])
    res = CliRunner().invoke(cli.app, ["forms", "files", "verify", SID])
    assert res.exit_code == 0
    assert api.body() == []


def test_files_delete_with_no_path_or_url_is_sent_as_given(api):
    api.add("DELETE", f"{BASE}/files", status=204)
    res = CliRunner().invoke(cli.app, ["forms", "files", "delete", "--yes"])
    assert res.exit_code == 0
    assert api.body() == {}


def test_a_question_without_a_type_is_refused_by_the_model_before_sending(api):
    res = CliRunner().invoke(cli.app, ["forms", "questions", "create", SID])
    assert isinstance(res.exception, ValidationError)
    assert [e["type"] for e in res.exception.errors()] == ["union_tag_not_found"]
    assert api.calls == []


def test_a_condition_without_operator_and_items_is_refused_by_the_model_before_sending(api):
    res = CliRunner().invoke(cli.app, ["forms", "conditions", "submit", "create", SID])
    assert isinstance(res.exception, ValidationError)
    assert [(e["type"], e["loc"]) for e in res.exception.errors()] == [
        ("missing", ("operator",)),
        ("missing", ("items",)),
    ]
    assert api.calls == []
