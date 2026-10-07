"""`datalens htmlpages update`: one of two requests, and the model says which it is not."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from pydantic import RootModel, ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.full_server import mcp
from ycli.cli.errors import format_cli_error
from ycli.yandex.datalens.htmlpages.models import HTMLPageUpdate
from ycli.yandex.datalens.schemas.html_pages import UpdateHtmlPageArgsVariant1 as Variant1
from ycli.yandex.datalens.schemas.html_pages import UpdateHtmlPageArgsVariant2 as Variant2

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


ONE_OF = "The request cannot be built:\n  body: give exactly one of: content, revId"


@pytest.mark.parametrize(
    "flags",
    [["--mode", "save", "--content", "<p>", "--rev-id", "rev1"], ["--mode", "save"]],
    ids=["both", "neither"],
)
def test_the_refusal_is_one_line_that_names_the_two_fields(api, flags):
    """#459: once, by the fields that tell the two requests apart, not once for each class."""
    result = CliRunner().invoke(cli.app, ["datalens", "htmlpages", "update", HP, *flags])
    assert isinstance(result.exception, ValidationError) and api.calls == []
    assert format_cli_error(result.exception) == ONE_OF


@pytest.mark.parametrize(
    ("flags", "said"),
    [
        (["--content", "<p>", "-F", "nmae=x"], "  content.nmae: Extra inputs are not permitted"),
        # A revision is made current in a mode: the one request it fits says what it lacks.
        (["--rev-id", "rev1"], "  revId.mode: is required"),
    ],
    ids=["a mistyped key", "a revision with no mode"],
)
def test_what_is_wrong_inside_a_request_is_said_once_under_its_field(api, flags, said):
    result = CliRunner().invoke(cli.app, ["datalens", "htmlpages", "update", HP, *flags])
    assert isinstance(result.exception, ValidationError) and api.calls == []
    assert format_cli_error(result.exception) == f"The request cannot be built:\n{said}"


@pytest.mark.parametrize(
    ("body", "lines"),
    [
        ({"entryId": HP, "mode": "save"}, 2),
        ({"entryId": HP, "mode": "save", "content": "<p>", "revId": "rev1"}, 2),
        ({"entryId": HP, "content": "<p>", "nmae": "x"}, 5),
    ],
    ids=["neither", "both", "a mistyped key"],
)
def test_without_the_mark_each_of_the_two_classes_answers(body, lines):
    """The defect, on the same generated members: 2 to 5 lines, each under a class name."""
    with pytest.raises(ValidationError) as refused:
        RootModel[Variant1 | Variant2].model_validate(body)
    said = format_cli_error(refused.value).splitlines()[1:]
    assert len(said) == lines
    assert all(line.strip().startswith("UpdateHtmlPageArgsVariant") for line in said)
    with pytest.raises(ValidationError) as marked:
        HTMLPageUpdate.model_validate(body)
    assert len(marked.value.errors()) == 1


async def test_the_tool_refuses_content_and_a_revision_together_once():
    arguments = {"body": {"entryId": HP, "mode": "save", "content": "<p>", "revId": "rev1"}}
    async with Client(mcp) as client:
        with pytest.raises(ToolError) as refused:
            await client.call_tool("datalens_htmlpages_update", arguments)
    assert str(refused.value) == (
        "The arguments do not fit the tool:\n  body: give exactly one of: content, revId"
    )
