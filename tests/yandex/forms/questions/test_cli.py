"""TDD for `forms questions` CLI — reads (get/list) plus writes (create/modify/delete/move)."""

import json
import re

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"
runner = CliRunner()

# Rich colourises option flags in error panels and even splits the leading dashes into
# separately-styled tokens (``-`` + ``-type``), so the literal ``--type`` is absent from the
# raw output whenever colour is on (CI forces it; a local TTY may not). Strip ANSI before
# asserting on flag names so the check tests the message, not the terminal's colour state.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _plain(text: str) -> str:
    return _ANSI_RE.sub("", text)


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


def _sent_body():
    return json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]


@responses.activate
def test_get_dumps_single_question():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/questions/17",
        json={"id": 17, "slug": "s1", "type": "string", "label": "Name"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "questions", "get", SID, "17"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == 17


@responses.activate
def test_list_dumps_pages_envelope():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/questions",
        json={
            "pages": [
                {"id": 1, "items": [{"id": 11, "slug": "s1", "type": "string", "label": "A"}]}
            ]
        },
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "questions", "list", SID])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["pages"][0]["items"][0]["id"] == 11


@responses.activate
def test_create_string_via_flags():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/questions",
        json={"id": 17, "type": "string", "label": "Name"},
        status=201,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "questions",
            "create",
            SID,
            "--type",
            "string",
            "--label",
            "Name",
            "--required",
            "--multiline",
        ],
    )
    assert res.exit_code == 0
    assert _sent_body() == {
        "label": "Name",
        "type": "string",
        "multiline": True,
        "validators": [{"type": "required"}],
    }


@responses.activate
def test_create_enum_via_repeatable_option():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/questions",
        json={"id": 18, "type": "enum", "label": "Pick"},
        status=201,
    )
    res = runner.invoke(
        cli.app,
        [
            "forms",
            "questions",
            "create",
            SID,
            "--type",
            "enum",
            "--label",
            "Pick",
            "--widget",
            "radio",
            "--option",
            "A",
            "--option",
            "B",
        ],
    )
    assert res.exit_code == 0
    sent = _sent_body()
    assert sent["type"] == "enum" and sent["widget"] == "radio"
    assert [item["label"] for item in sent["items"]] == ["A", "B"]


@responses.activate
def test_create_boolean_via_flags():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/questions",
        json={"id": 1, "type": "boolean"},
        status=201,
    )
    res = runner.invoke(
        cli.app, ["forms", "questions", "create", SID, "--type", "boolean", "--label", "Agree"]
    )
    assert res.exit_code == 0
    assert _sent_body() == {"label": "Agree", "type": "boolean"}


@responses.activate
def test_create_integer_via_flags():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/questions",
        json={"id": 1, "type": "integer"},
        status=201,
    )
    res = runner.invoke(
        cli.app,
        ["forms", "questions", "create", SID, "--type", "integer", "--label", "Age", "--hidden"],
    )
    assert res.exit_code == 0
    assert _sent_body() == {"label": "Age", "type": "integer", "hidden": True}


@responses.activate
def test_create_date_via_flags():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/questions",
        json={"id": 1, "type": "date"},
        status=201,
    )
    res = runner.invoke(
        cli.app, ["forms", "questions", "create", SID, "--type", "date", "--label", "Born"]
    )
    assert res.exit_code == 0
    assert _sent_body() == {"label": "Born", "type": "date"}


@responses.activate
def test_create_matrix_via_body_file(tmp_path):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/questions",
        json={"id": 9, "type": "matrix"},
        status=201,
    )
    body = {
        "type": "matrix",
        "label": "Grid",
        "rows": [{"slug": "r1", "label": "Row 1"}],
        "columns": [{"slug": "c1", "label": "Col 1"}],
    }
    path = tmp_path / "matrix.json"
    path.write_text(json.dumps(body), encoding="utf-8")
    res = runner.invoke(cli.app, ["forms", "questions", "create", SID, "--body-file", str(path)])
    assert res.exit_code == 0
    assert _sent_body() == body


def test_create_unknown_type_is_a_bad_parameter():
    res = runner.invoke(
        cli.app, ["forms", "questions", "create", SID, "--type", "matrix", "--label", "x"]
    )
    assert res.exit_code != 0
    assert "no typed flags" in res.output


def test_create_without_type_or_body_file_errors():
    res = runner.invoke(cli.app, ["forms", "questions", "create", SID, "--label", "x"])
    assert res.exit_code != 0
    assert "--type" in _plain(res.output)


@responses.activate
def test_modify_via_flags_patches():
    responses.add(
        responses.PATCH,
        f"{BASE}/surveys/{SID}/questions/17",
        json={"id": 17, "type": "string", "label": "Full name"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "forms",
            "questions",
            "modify",
            SID,
            "17",
            "--type",
            "string",
            "--label",
            "Full name",
        ],
    )
    assert res.exit_code == 0
    assert responses.calls[0].request.method == "PATCH"
    assert _sent_body() == {"label": "Full name", "type": "string"}


@responses.activate
def test_modify_via_body_file_suggest(tmp_path):
    responses.add(
        responses.PATCH,
        f"{BASE}/surveys/{SID}/questions/17",
        json={"id": 17, "type": "suggest"},
        status=200,
    )
    body = {"type": "suggest", "label": "Dept", "data_source": {"name": "departments"}}
    path = tmp_path / "suggest.json"
    path.write_text(json.dumps(body), encoding="utf-8")
    res = runner.invoke(
        cli.app, ["forms", "questions", "modify", SID, "17", "--body-file", str(path)]
    )
    assert res.exit_code == 0
    assert _sent_body() == body


@responses.activate
def test_delete_question():
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}/questions/17", status=204)
    res = runner.invoke(cli.app, ["--format", "json", "forms", "questions", "delete", SID, "17"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["action"] == "delete"
    assert "force" not in (responses.calls[0].request.url or "")


@responses.activate
def test_delete_force_sends_query():
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}/questions/17", status=204)
    res = runner.invoke(cli.app, ["forms", "questions", "delete", SID, "17", "--force"])
    assert res.exit_code == 0
    assert responses.calls[0].request.params["force"] == "true"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_move_question():
    responses.add(
        responses.POST, f"{BASE}/surveys/{SID}/questions/17/move", json={"id": 17}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "questions",
            "move",
            SID,
            "17",
            "--page",
            "2",
            "--position",
            "1",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == 17
    assert _sent_body() == {"page": 2, "position": 1}


@responses.activate
def test_move_question_bare_position_defaults_page_to_1():
    """``--position`` without ``--page`` used to 200-but-move-nothing live; the body now
    defaults page to 1 so the move takes effect."""
    responses.add(
        responses.POST, f"{BASE}/surveys/{SID}/questions/17/move", json={"id": 17}, status=200
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "forms", "questions", "move", SID, "17", "--position", "1"],
    )
    assert res.exit_code == 0
    assert _sent_body() == {"page": 1, "position": 1}
