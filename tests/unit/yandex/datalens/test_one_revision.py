"""A read of an entry names exactly one of a branch and a revision (#486).

DataLens answers a named revision whatever the branch says, and the published version when
neither is given (measured), so a read that names both, or neither, does not say which version
it means. One check refuses it, for the six reads that take a branch, on every surface.
"""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from pydantic import SecretStr, ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.full_server import mcp
from ycli.cli.errors import format_cli_error
from ycli.yandex.core.auth import IAMTokenAuth
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import one_revision

ONE_OF = "give exactly one of: branch, rev_id"
READS = {
    "charts wizard get": ("charts", "wizard_get"),
    "charts ql get": ("charts", "ql_get"),
    "charts editor get": ("charts", "editor_get"),
    "dashboards get": ("dashboards", "get"),
    "htmlpages get": ("htmlpages", "get"),
    "htmlpages preview-url-get": ("htmlpages", "preview_url_get"),
}
BOTH = {"branch": "saved", "rev_id": "rev1"}


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


@pytest.mark.parametrize("given", [{}, BOTH], ids=["neither", "both"])
def test_the_check_refuses_neither_and_both_once(given):
    with pytest.raises(ValidationError) as refused:
        one_revision(branch=given.get("branch"), rev_id=given.get("rev_id"))
    assert [error["msg"] for error in refused.value.errors()] == [ONE_OF]


def test_the_check_takes_a_branch_or_a_revision():
    one_revision(branch="published", rev_id=None)
    one_revision(branch=None, rev_id="rev1")


@pytest.mark.parametrize("given", [{}, BOTH], ids=["neither", "both"])
@pytest.mark.parametrize("read", READS)
def test_the_method_refuses_before_anything_is_sent(api, read, given):
    resource, method = READS[read]
    auth = IAMTokenAuth(SecretStr("t"))
    with (
        DataLensClient(auth=auth, cloud_organization_id="c") as datalens,
        pytest.raises(ValidationError, match=ONE_OF),
    ):
        getattr(getattr(datalens, resource), method)("id1", **given)
    assert api.calls == []


@pytest.mark.parametrize(
    "flags", [[], ["--branch", "saved", "--rev-id", "rev1"]], ids=["neither", "both"]
)
@pytest.mark.parametrize("read", READS)
def test_the_command_says_it_as_any_request_that_cannot_be_built(api, read, flags):
    result = CliRunner().invoke(cli.app, ["datalens", *read.split(), "id1", *flags])
    assert isinstance(result.exception, ValidationError) and api.calls == []
    assert format_cli_error(result.exception) == f"The request cannot be built:\n  body: {ONE_OF}"


IDENTITY = {"charts": "chart_id", "dashboards": "dashboard_id", "htmlpages": "entry_id"}


@pytest.mark.parametrize("given", [{}, BOTH], ids=["neither", "both"])
@pytest.mark.parametrize("read", READS)
async def test_the_tool_says_the_same_line(api, read, given):
    resource, method = READS[read]
    arguments = {IDENTITY[resource]: "id1", **given}
    async with Client(mcp) as client:
        with pytest.raises(ToolError) as refused:
            await client.call_tool(f"datalens_{resource}_{method}", arguments)
    assert str(refused.value) == f"The request cannot be built:\n  body: {ONE_OF}"
    assert api.calls == []
