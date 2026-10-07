"""`datalens htmlpages update`: one of two requests, and the model says which it is not."""

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.cli.errors import format_cli_error

HP = "hp000000000001"


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


@pytest.mark.parametrize(
    ("flags", "named"),
    [
        # The API takes both and saves the content (measured); the document describes no such
        # request, so it is refused before anything is sent.
        (["--mode", "save", "--content", "<p>", "--rev-id", "rev1"], ["content", "revId"]),
        # Neither: DataLens answers 400 for it; here the fields that are missing are named.
        (["--mode", "save"], ["content", "revId"]),
    ],
)
def test_content_and_a_revision_together_or_neither_is_refused(api, flags, named):
    result = CliRunner().invoke(cli.app, ["datalens", "htmlpages", "update", HP, *flags])
    assert isinstance(result.exception, ValidationError) and api.calls == []
    said = format_cli_error(result.exception)
    assert all(name in said for name in named), said


def test_a_field_of_the_request_comes_from_the_file_and_a_flag_lies_over_it(api, tmp_path):
    api.add("POST", "https://api.datalens.tech/rpc/updateHtmlPage", json={})
    body = tmp_path / "page.yaml"
    body.write_text("content: <p>From a file</p>\nmode: save\n", encoding="utf-8")
    argv = ["datalens", "htmlpages", "update", HP, "--body-file", str(body), "--mode", "publish"]
    result = CliRunner().invoke(cli.app, argv)
    assert result.exit_code == 0, result.output
    assert api.body() == {"entryId": HP, "content": "<p>From a file</p>", "mode": "publish"}
