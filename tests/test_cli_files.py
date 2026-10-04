"""A command that reads a local file: a missing file or bad JSON is one line, not a traceback."""

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli

MISSING = "/nonexistent/file.json"

# Every command that reads a local file, with the file's place marked ``{file}``.
READS_A_FILE = [
    ["forms", "filling", "submit", "s1", "--body-file", "{file}"],
    ["forms", "questions", "create", "s1", "--body-file", "{file}"],
    ["forms", "questions", "update", "s1", "7", "--body-file", "{file}"],
    ["forms", "conditions", "question", "create", "s1", "7", "--body-file", "{file}"],
    ["forms", "conditions", "question", "update", "s1", "7", "3", "--body-file", "{file}"],
    ["forms", "subscriptions", "create", "s1", "5", "--body-file", "{file}"],
    ["forms", "subscriptions", "update", "s1", "5", "9", "--body-file", "{file}"],
    ["forms", "subscriptions", "attach", "s1", "5", "9", "{file}"],
    ["forms", "images", "upload", "s1", "{file}"],
    ["forms", "files", "upload", "s1", "{file}"],
    ["tracker", "attachments", "upload", "DE-1", "{file}"],
    ["tracker", "attachments", "upload-temp", "{file}"],
    [
        "tracker",
        "import",
        "file",
        "DE-1",
        "{file}",
        "--created-at",
        "2026-01-01",
        "--created-by",
        "1",
    ],
    [
        "tracker",
        "import",
        "comment-file",
        "DE-1",
        "2",
        "{file}",
        "--created-at",
        "2026-01-01",
        "--created-by",
        "1",
    ],
    ["wiki", "attachments", "upload", "11", "{file}"],
    ["wiki", "uploadsessions", "upload-part", "session-1", "{file}"],
]


def _argv(template: list[str], file: str) -> list[str]:
    return [file if part == "{file}" else part for part in template]


def _text(output: str) -> str:
    """The message of a usage error with its box and line wrapping removed."""
    return " ".join(output.replace("│", " ").split())


@pytest.mark.parametrize("template", READS_A_FILE, ids=lambda template: " ".join(template[:4]))
def test_a_missing_file_is_a_usage_error(api, template):
    res = CliRunner().invoke(cli.app, _argv(template, MISSING))
    assert res.exit_code == 2, res.output
    assert "does not exist" in _text(res.output)
    assert api.calls == []


@pytest.mark.parametrize("template", READS_A_FILE, ids=lambda template: " ".join(template[:4]))
def test_a_directory_is_not_a_file(api, tmp_path, template):
    res = CliRunner().invoke(cli.app, _argv(template, str(tmp_path)))
    assert res.exit_code == 2, res.output
    assert "is a directory" in _text(res.output)
    assert api.calls == []


@pytest.mark.parametrize(
    "template",
    [template for template in READS_A_FILE if "--body-file" in template],
    ids=lambda template: " ".join(template[:4]),
)
def test_a_body_file_with_bad_json_is_a_validation_error(api, tmp_path, template):
    """``main()`` formats a ``ValidationError``; a ``JSONDecodeError`` it would not catch."""
    broken = tmp_path / "body.json"
    broken.write_text("{not json", encoding="utf-8")
    res = CliRunner().invoke(cli.app, _argv(template, str(broken)))
    assert isinstance(res.exception, ValidationError), repr(res.exception)
    assert "Invalid JSON" in str(res.exception)
    assert api.calls == []
