"""Forms MCP behaviour a contract case cannot express."""

from fastmcp import Client

from tests.full_server import mcp
from tests.hosts import FORMS_BASE as BASE

SID = "686d0a1b2c3d4e5f00000080"


async def test_a_question_move_with_a_bare_position_is_sent_as_given(api):
    api.add("POST", f"{BASE}/surveys/{SID}/questions/1/move", json={"id": "1"})
    async with Client(mcp) as client:
        await client.call_tool(
            "forms_questions_move",
            {"survey_id": SID, "question_id": "1", "body": {"position": 2}},
        )
    assert api.body() == {"position": 2}
