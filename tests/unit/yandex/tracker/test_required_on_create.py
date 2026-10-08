"""What the API requires of a create is required before the call, on every surface.

Measured in the test organization: ``POST /priorities`` without ``order`` and ``POST /queues``
without ``issueTypesConfig`` both answer ``422 ... Требуется параметр`` (the documentation
lists the second among the required parameters). The commands let both be left out.
"""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.full_server import mcp
from ycli.yandex.tracker.models import LocalizedName
from ycli.yandex.tracker.priorities.models import PriorityCreate
from ycli.yandex.tracker.queues.models import QueueCreate

PRIORITY = ["tracker", "priorities", "create", "--key", "k", "--name-en", "N"]
QUEUE = [
    "tracker", "queues", "create", "--key", "K", "--name", "N", "--lead", "l",
    "--default-type", "task", "--default-priority", "normal",
]  # fmt: skip


@pytest.mark.parametrize(
    ("command", "option"), [(PRIORITY, "--order"), (QUEUE, "--issue-type-config")]
)
def test_the_command_asks_for_it(api, command, option):
    result = CliRunner().invoke(cli.app, command)
    assert result.exit_code == 2
    assert f"Missing option '{option}'" in result.output
    assert api.calls == []


@pytest.mark.parametrize(
    ("tool", "body", "field"),
    [
        ("tracker_priorities_create", {"key": "k", "name": {"en": "N"}}, "order"),
        (
            "tracker_queues_create",
            {"key": "K", "name": "N", "lead": "l", "default_type": "task",
             "default_priority": "normal"},
            "issue_types_config",
        ),
    ],
)  # fmt: skip
async def test_the_tool_asks_for_it(api, tool, body, field):
    async with Client(mcp) as client:
        with pytest.raises(ToolError) as refused:
            await client.call_tool(tool, {"body": body})
    assert f"body.{field}: is required" in str(refused.value)
    assert api.calls == []


def test_the_model_asks_for_it():
    with pytest.raises(ValidationError, match="order"):
        PriorityCreate(key="k", name=LocalizedName(en="N"))  # ty: ignore[missing-argument]
    with pytest.raises(ValidationError, match="issue_types_config"):
        QueueCreate(  # ty: ignore[missing-argument]
            key="K", name="N", lead="l", default_type="task", default_priority="normal"
        )
