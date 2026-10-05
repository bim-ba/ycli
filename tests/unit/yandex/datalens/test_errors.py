"""A DataLens validation error reaches the user with the field it is about (#365, #376).

ycli requires nothing of a body below its top level and sets no limit on a value: DataLens
answers for both, so what it answers must be shown whole.
"""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.full_server import mcp
from ycli.cli.errors import format_cli_error
from ycli.yandex.errors import YandexClientError, describe_error_body

PROBE = "https://api.datalens.tech/rpc/getTenantDetails"
# Measured on the live API: a collection id one character too long.
REFUSED = {
    "status": 400,
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "requestId": "r1",
    "details": {
        "title": "too_big",
        "details": [
            {
                "origin": "string",
                "code": "too_big",
                "maximum": 13,
                "path": ["collectionId"],
                "message": "Too big: expected string to have <=13 characters",
            },
            {"code": "invalid_type", "path": ["items", 0, "title"], "message": "Invalid input"},
        ],
    },
}
LINE = (
    "VALIDATION_ERROR: Validation error (collectionId: Too big: expected string to have <=13 "
    "characters; items.0.title: Invalid input)"
)


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


def test_the_cli_names_the_field_datalens_refused(api):
    api.add("POST", PROBE, json=REFUSED, status=400)
    result = CliRunner().invoke(cli.app, ["datalens", "tenant", "details-get"])
    assert isinstance(result.exception, YandexClientError)
    assert LINE in format_cli_error(result.exception)


async def test_an_agent_is_told_the_field_datalens_refused(api):
    api.add("POST", PROBE, json=REFUSED, status=400)
    async with Client(mcp) as client:
        with pytest.raises(ToolError) as refused:
            await client.call_tool("datalens_tenant_details_get", {})
    assert LINE in str(refused.value)


@pytest.mark.parametrize(
    ("body", "line"),
    [
        # Another error of DataLens: its code, and no list of fields.
        (
            '{"status": 403, "code": "LICENSE_IS_REQUIRED", "message": "No license"}',
            "LICENSE_IS_REQUIRED: No license",
        ),
        # Measured: the list of fields is `details` itself, not `details.details`.
        (
            '{"status": 400, "code": "VALIDATION_ERROR", "message": "Invalid params", '
            '"details": [{"code": "custom", "path": ["sort"], "message": '
            '"sort must contain at least one field when offset is greater than 0"}]}',
            "VALIDATION_ERROR: Invalid params (sort: sort must contain at least one field when "
            "offset is greater than 0)",
        ),
        # Measured: details that describe the error and list no field; the message says it.
        (
            '{"status": 400, "code": "ERR.DS_API.FIELD.NOT_FOUND", "message": "Unknown field '
            'Region", "details": {"title": "ERR.DS_API.FIELD.NOT_FOUND", "description": '
            '"Unknown field Region"}}',
            "ERR.DS_API.FIELD.NOT_FOUND: Unknown field Region",
        ),
        # Measured (423): an entry locked by another; the details say by whom and until when.
        (
            '{"status": 423, "code": "ERR.US.ENTRY_IS_LOCKED", "message": "The entry is locked", '
            '"details": {"title": "ERR.US.ENTRY_IS_LOCKED", "description": "The entry is '
            'locked", "loginOrId": "user-1", "expiryDate": "2026-10-05T23:07:26.920Z"}}',
            "ERR.US.ENTRY_IS_LOCKED: The entry is locked (loginOrId: user-1; expiryDate: "
            "2026-10-05T23:07:26.920Z)",
        ),
        # Details of another shape, or items that name nothing, add nothing.
        ('{"code": "X", "message": "Bad", "details": {"details": "text"}}', "X: Bad"),
        ('{"code": "X", "message": "Bad", "details": {"details": [{"path": []}, 5]}}', "X: Bad"),
        # An item without a path reads as its message.
        (
            '{"code": "X", "message": "Bad", "details": {"details": [{"message": "whole body"}]}}',
            "X: Bad (whole body)",
        ),
    ],
)
def test_the_other_shapes_of_a_datalens_error(body, line):
    assert describe_error_body(body) == line
