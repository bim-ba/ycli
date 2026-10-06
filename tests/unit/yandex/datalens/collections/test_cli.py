"""`datalens collections`: where a command line cannot say what the request needs."""

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


def test_a_delta_that_is_not_json_is_refused_before_anything_is_sent(api):
    argv = ["datalens", "collections", "access-bindings-update", "col1", "--delta", "{oops"]
    result = CliRunner().invoke(cli.app, argv)
    assert isinstance(result.exception, ValidationError)
    assert api.calls == []


@pytest.mark.parametrize(
    ("argv", "rpc", "sent"),
    [
        (
            ["collections", "content-list", "--no-only-my", "--no-include-permissions-info"],
            "getCollectionContent",
            {"collectionId": None, "onlyMy": False, "includePermissionsInfo": False},
        ),
        (
            ["collections", "access-bindings-list", "col1", "--no-get-inherited-bindings"],
            "listCollectionAccessBindings",
            {"collectionId": "col1", "getInheritedBindings": False},
        ),
        (
            ["workbooks", "list", "--only-my", "--no-include-permissions-info"],
            "getWorkbooksList",
            {"onlyMy": True, "includePermissionsInfo": False},
        ),
        (
            ["workbooks", "entries-list", "wb1", "--no-only-my"],
            "getWorkbookEntries",
            {"workbookId": "wb1", "onlyMy": False},
        ),
        (
            ["workbooks", "access-bindings-list", "wb1", "--no-get-inherited-bindings"],
            "listWorkbookAccessBindings",
            {"workbookId": "wb1", "getInheritedBindings": False},
        ),
        # Not given: the field is not sent at all.
        (["workbooks", "get", "wb1"], "getWorkbook", {"workbookId": "wb1"}),
    ],
)
def test_a_boolean_option_says_yes_no_or_nothing(api, argv, rpc, sent):
    """Three states on the command line, as in the SDK and in a tool."""
    api.add("POST", f"https://api.datalens.tech/rpc/{rpc}", json={})
    result = CliRunner().invoke(cli.app, ["-o", "json", "datalens", *argv])
    assert result.exit_code == 0, result.output
    assert api.body() == sent
