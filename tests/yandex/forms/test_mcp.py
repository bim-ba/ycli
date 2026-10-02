"""Forms MCP tools refusing what the API would answer badly or not at all."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import FORMS_BASE as BASE
from ycli.mcp.server import mcp

SID = "686d0a1b2c3d4e5f00000080"


@pytest.mark.parametrize(
    ("tool", "arguments", "url"),
    [
        ("forms_me_get", {}, "users/me"),
        ("forms_surveys_get", {"survey_id": SID}, f"surveys/{SID}"),
        (
            "forms_questions_get",
            {"survey_id": SID, "question_id": "1"},
            f"surveys/{SID}/questions/1",
        ),
        ("forms_operations_get", {"operation_id": "op-1"}, "operations/op-1"),
        ("forms_filling_get", {"survey": SID}, f"surveys/{SID}/form"),
        ("forms_hooks_get", {"survey_id": SID, "hook_id": 11}, f"surveys/{SID}/hooks/11"),
        (
            "forms_conditions_question_get",
            {"survey_id": SID, "question_id": "17", "condition_id": 5},
            f"surveys/{SID}/questions/17/conditions/5",
        ),
        (
            "forms_conditions_page_get",
            {"survey_id": SID, "page_id": 3, "condition_id": 6},
            f"surveys/{SID}/pages/3/conditions/6",
        ),
        (
            "forms_conditions_submit_get",
            {"survey_id": SID, "condition_id": 7},
            f"surveys/{SID}/conditions/7",
        ),
        (
            "forms_conditions_hook_get",
            {"survey_id": SID, "hook_id": 11, "condition_id": 8},
            f"surveys/{SID}/hooks/11/conditions/8",
        ),
    ],
)
async def test_an_empty_answer_is_an_error(api, tool, arguments, url):
    api.add("GET", f"{BASE}/{url}", json={})
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="empty"):
            await client.call_tool(tool, arguments)


@pytest.mark.parametrize(
    ("tool", "arguments"),
    [
        ("forms_answers_get", {}),
        ("forms_answers_get", {"answer_id": 1, "answer_key": "k"}),
        ("forms_questions_move", {"survey_id": SID, "question_id": "1", "body": {"position": 2}}),
    ],
)
async def test_invalid_arguments_send_nothing(api, tool, arguments):
    async with Client(mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool(tool, arguments)
    assert api.calls == []
