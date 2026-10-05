"""``-F`` and ``--body-file``: any field of a request body, on any command that sends one (#354)."""

import json

import pytest
import typer
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import FORMS_BASE, TRACKER_BASE
from ycli.cli.body_fields import laid_under
from ycli.cli.context import AppContext
from ycli.cli.inject import inject_dependencies
from ycli.cli.typedefs import FieldOption

runner = CliRunner()


def _update(api, *extra: str) -> dict:
    api.add("PATCH", f"{FORMS_BASE}/surveys/s1", json={"id": "s1"})
    result = runner.invoke(cli.app, ["forms", "surveys", "update", "s1", *extra])
    assert result.exit_code == 0, result.output
    return api.body()


def test_a_field_with_no_flag_of_its_own_reaches_the_body(api):
    assert _update(api, "--name", "Poll", "-F", 'texts={"submit": "Go"}') == {
        "name": "Poll",
        "texts": {"submit": "Go"},
    }


def test_the_file_is_weaker_than_a_field_and_a_field_weaker_than_a_flag(api, tmp_path):
    body_file = tmp_path / "body.json"
    body_file.write_text(json.dumps({"name": "file", "language": "file", "max_count": 1}))
    sent = _update(api, "--name", "flag", "-F", "name=field", "-F", "language=field")
    assert sent == {"name": "flag", "language": "field"}
    sent = _update(api, "--name", "flag", "-F", "language=field", "--body-file", str(body_file))
    assert sent == {"name": "flag", "language": "field", "max_count": 1}


def test_the_options_work_before_the_subcommand_too(api):
    api.add("PATCH", f"{FORMS_BASE}/surveys/s1", json={"id": "s1"})
    result = runner.invoke(cli.app, ["-F", "language=en", "forms", "surveys", "update", "s1"])
    assert result.exit_code == 0, result.output
    assert api.body() == {"language": "en"}


def test_objects_are_merged_field_by_field():
    body = {"name": "A", "fields": {"x": 1, "deep": {"kept": True}}}
    under = {"name": "B", "fields": {"y": 2, "deep": {"added": 1}}, "extra": None}
    assert laid_under(body, under) == {
        "name": "A",
        "fields": {"y": 2, "deep": {"added": 1, "kept": True}, "x": 1},
        "extra": None,
    }


def test_a_dry_run_shows_the_body_with_the_fields(api):
    result = runner.invoke(
        cli.app, ["-o", "json", "--dry-run", "forms", "surveys", "update", "s1", "-F", "name=X"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["body"] == {"name": "X"}
    assert api.calls == []


@pytest.mark.parametrize(
    "argv",
    [
        ["tracker", "issues", "get", "TEST-1", "-F", "a=1"],
        ["tracker", "comments", "delete", "TEST-1", "7", "--yes", "-F", "a=1"],
    ],
    ids=["a read", "a write without a body"],
)
def test_a_command_that_sends_no_object_refuses_the_fields_before_sending(api, argv):
    result = runner.invoke(cli.app, argv)
    assert result.exit_code == 2
    assert "sends no JSON object" in " ".join(result.output.split())
    assert api.calls == []


def test_a_file_that_is_not_an_object_cannot_build_the_request(api, tmp_path):
    body_file = tmp_path / "body.json"
    body_file.write_text("[1, 2]")
    result = runner.invoke(
        cli.app, ["forms", "surveys", "update", "s1", "--name", "X", "--body-file", str(body_file)]
    )
    assert isinstance(result.exception, ValidationError)
    assert api.calls == []


def test_only_the_first_request_of_a_command_gets_the_fields(api, tmp_path, monkeypatch):
    """A command that waits reads the operation afterwards: those reads are left alone."""
    monkeypatch.setattr("time.sleep", lambda *_: None)
    body_file = tmp_path / "body.json"
    body_file.write_text(json.dumps({"comment": "moved"}))
    api.add("POST", f"{TRACKER_BASE}/bulkchange/_move", json={"id": "1ab", "status": "CREATED"})
    api.add("GET", f"{TRACKER_BASE}/bulkchange/1ab", json={"id": "1ab", "status": "COMPLETE"})
    argv = ["tracker", "issues", "move-bulk", "CHECK", "--issue", "TEST-1"]
    result = runner.invoke(cli.app, [*argv, "--body-file", str(body_file)])
    assert result.exit_code == 0, result.output
    assert json.loads(api.calls[0].content) == {
        "queue": "CHECK",
        "issues": ["TEST-1"],
        "comment": "moved",
    }
    assert [call.method for call in api.calls] == ["POST", "GET"]


def test_a_key_may_name_a_nested_field_and_a_value_is_taken_as_written(api):
    fields = ["texts[submit]=Go", "name=@ann", "tags[]=a", "ratio=1.5"]
    sent = _update(api, *(part for field in fields for part in ("-F", field)))
    assert sent == {"texts": {"submit": "Go"}, "name": "@ann", "tags": ["a"], "ratio": 1.5}


QUESTIONS = f"{FORMS_BASE}/surveys/s1/questions"


def test_a_command_whose_body_is_a_union_merges_before_it_validates(api, tmp_path):
    """The file names the type, ``-F`` adds to it and a flag wins over both (#354, question 6)."""
    body_file = tmp_path / "question.json"
    body_file.write_text(json.dumps({"type": "string", "label": "file", "comment": "file"}))
    api.add("POST", QUESTIONS, json={"id": 1, "type": "string"})
    argv = ["forms", "questions", "create", "s1", "--label", "flag", "-F", "comment=field"]
    result = runner.invoke(cli.app, [*argv, "-F", "label=field", "--body-file", str(body_file)])
    assert result.exit_code == 0, result.output
    assert api.body() == {"type": "string", "label": "flag", "comment": "field"}


def test_such_a_command_still_refuses_a_field_its_model_does_not_know(api):
    result = runner.invoke(
        cli.app,
        ["forms", "questions", "create", "s1", "--type", "string", "--label", "L", "-F", "nope=1"],
    )
    assert isinstance(result.exception, ValidationError)
    assert api.calls == []


def test_a_body_given_only_by_fields_is_enough_where_there_are_no_flags(api):
    api.add("POST", f"{FORMS_BASE}/surveys/s1/form", json={"answer_id": 9})
    result = runner.invoke(cli.app, ["forms", "filling", "submit", "s1", "-F", "name=Ann"])
    assert result.exit_code == 0, result.output
    assert api.body() == {"name": "Ann"}


@pytest.mark.parametrize(
    "argv",
    [["auth", "profiles", "-F", "a=1"], ["mcp", "start", "-F", "a=1"]],
    ids=["a command that sends no request", "a command that serves"],
)
def test_a_command_that_sends_nothing_refuses_the_fields(api, argv):
    result = runner.invoke(cli.app, argv)
    assert result.exit_code == 2
    assert "sends no JSON object" in " ".join(result.output.split())
    assert api.calls == []


def test_a_field_before_the_subcommand_and_one_after_it_add_up(api):
    api.add("PATCH", f"{FORMS_BASE}/surveys/s1", json={"id": "s1"})
    argv = ["-F", "a=1", "-F", "b=1", "forms", "surveys", "update", "s1", "-F", "b=2"]
    result = runner.invoke(cli.app, argv)
    assert result.exit_code == 0, result.output
    assert api.body() == {"a": 1, "b": 2}


@pytest.mark.parametrize(
    "argv",
    [["auth", "status", "-F", "a=1"], ["doctor", "-F", "a=1"], ["mcp", "methods", "-F", "a=1"]],
    ids=["auth status", "doctor", "a command with nothing injected"],
)
def test_a_command_that_only_reports_refuses_the_fields_before_it_asks_anything(api, argv):
    result = runner.invoke(cli.app, argv)
    assert result.exit_code == 2
    assert "sends no JSON object" in " ".join(result.output.split())
    assert api.calls == []


def test_submitting_a_form_with_no_answers_given_is_refused(api):
    result = runner.invoke(cli.app, ["forms", "filling", "submit", "s1"])
    assert result.exit_code == 2
    assert "--body-file or -F" in " ".join(result.output.split())
    assert api.calls == []


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", "1e999"])
def test_a_number_json_cannot_carry_is_sent_as_the_text_written(api, value):
    assert _update(api, "-F", f"name={value}") == {"name": value}


@pytest.mark.parametrize("value", ["NaN", "Infinity", "1e999"])
def test_a_file_with_a_number_json_cannot_carry_is_a_usage_error(api, tmp_path, value):
    body_file = tmp_path / "body.json"
    body_file.write_text(f'{{"texts": [{{"max_count": {value}}}]}}')
    result = runner.invoke(
        cli.app, ["forms", "surveys", "update", "s1", "--body-file", str(body_file)]
    )
    assert result.exit_code == 2, result.output
    assert "JSON cannot carry" in " ".join(result.output.split())
    assert api.calls == []


@pytest.mark.parametrize(
    "argv",
    [
        ["tracker", "issues", "update-bulk", "--issue", "TEST-1", "-F", "b=2"],
        ["api", "issues", "--service", "tracker", "-F", "b=2"],
    ],
    ids=["a bulk change", "api"],
)
def test_a_command_with_its_own_field_option_refuses_the_common_one(api, argv):
    result = runner.invoke(cli.app, ["-F", "a=1", *argv])
    assert result.exit_code == 2
    assert "--field of its own" in " ".join(result.output.split())
    assert api.calls == []


def test_a_list_from_a_field_replaces_the_one_in_the_file(api, tmp_path):
    body_file = tmp_path / "body.json"
    body_file.write_text(json.dumps({"tags": ["a", "b"]}))
    assert _update(api, "-F", "tags[]=x", "--body-file", str(body_file)) == {"tags": ["x"]}


def test_a_command_that_took_the_context_and_sent_nothing_still_says_so():
    """The last net: such a command answers for the fields itself, and this one forgot to."""
    app = typer.Typer()

    @app.callback()
    def root(context: typer.Context, field: FieldOption = None) -> None:
        context.obj.options = context.params

    @app.command()
    def silent(*, context: typer.Context) -> None:
        """Send nothing."""

    inject_dependencies(app)
    result = runner.invoke(app, ["silent", "-F", "a=1"], obj=AppContext())
    assert result.exit_code == 2
    assert "sends no JSON object" in " ".join(result.output.split())


def _update_from(api, tmp_path, name: str, text: str, *extra: str) -> dict:
    body_file = tmp_path / name
    body_file.write_text(text)
    return _update(api, "--body-file", str(body_file), *extra)


def test_a_yaml_file_is_read_by_its_name_and_takes_the_same_path(api, tmp_path):
    text = "base: &base {submit: Go}\ntexts:\n  <<: *base\n  back: Back\nname: file\n"
    for name in ("body.yaml", "body.YML"):
        assert _update_from(api, tmp_path, name, text, "-F", "name=field") == {
            "base": {"submit": "Go"},
            "texts": {"submit": "Go", "back": "Back"},
            "name": "field",
        }


def test_yaml_guesses_types_unless_a_value_is_quoted(api, tmp_path):
    text = 'a: no\nb: yes\nc: 1.10\nd: "no"\ne: "1.10"\n'
    assert _update_from(api, tmp_path, "body.yaml", text) == {
        "a": False,
        "b": True,
        "c": 1.1,
        "d": "no",
        "e": "1.10",
    }


def test_a_file_with_any_other_name_is_json(api, tmp_path):
    assert _update_from(api, tmp_path, "body", '{"name": "X"}') == {"name": "X"}
    (tmp_path / "body").write_text("name: X\n")
    result = runner.invoke(
        cli.app, ["forms", "surveys", "update", "s1", "--body-file", str(tmp_path / "body")]
    )
    assert isinstance(result.exception, ValidationError)


@pytest.mark.parametrize(
    ("text", "says"),
    [
        ("a:\n\tb: 1\n", "not YAML"),
        ("a: 1\n---\nb: 2\n", "the file holds 2"),
        ("", "the file holds 0"),
        ("a: .nan\n", "JSON cannot carry"),
    ],
    ids=["a tab", "two documents", "empty", "a number JSON cannot carry"],
)
def test_a_yaml_file_that_cannot_be_read_is_a_usage_error(api, tmp_path, text, says):
    body_file = tmp_path / "body.yaml"
    body_file.write_text(text)
    result = runner.invoke(
        cli.app, ["forms", "surveys", "update", "s1", "--body-file", str(body_file)]
    )
    assert result.exit_code == 2, result.output
    assert says in " ".join(result.output.split())
    assert api.calls == []


@pytest.mark.parametrize(
    "text",
    ["- a\n- b\n", "just text\n", "day: 2026-10-06\n", "1: one\n"],
    ids=["a list", "a scalar", "a date", "a key that is not text"],
)
def test_a_yaml_file_that_holds_no_json_object_cannot_build_the_request(api, tmp_path, text):
    body_file = tmp_path / "body.yaml"
    body_file.write_text(text)
    result = runner.invoke(
        cli.app, ["forms", "surveys", "update", "s1", "--body-file", str(body_file)]
    )
    assert isinstance(result.exception, ValidationError)
    assert api.calls == []


def test_a_yaml_file_names_the_type_of_a_union_body(api, tmp_path):
    body_file = tmp_path / "question.yaml"
    body_file.write_text("type: string\nlabel: file\n")
    api.add("POST", QUESTIONS, json={"id": 1, "type": "string"})
    argv = ["forms", "questions", "create", "s1", "--label", "flag"]
    result = runner.invoke(cli.app, [*argv, "--body-file", str(body_file)])
    assert result.exit_code == 0, result.output
    assert api.body() == {"type": "string", "label": "flag"}
