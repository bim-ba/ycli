"""Forms FastMCP domain server — 5 reads-only tools, named <resource>_<action>."""
import requests
import responses
from fastmcp import Client

from ycli.yandex.forms import mcp as forms_mcp
from ycli.yandex.forms.client import FormsClient

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


def _stub() -> FormsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return FormsClient(session=s)


async def test_all_five_read_tools_registered():
    async with Client(forms_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {"me_get", "surveys_list", "surveys_get", "questions_list", "answers_list"}


@responses.activate
async def test_answers_list_tool(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/answers",
                  json={"columns": [], "answers": [{"id": 99, "created": "2026-01-01", "data": []}], "next": None},
                  status=200)
    async with Client(forms_mcp.mcp) as client:
        result = await client.call_tool("answers_list", {"survey_id": SID})
    assert result.data.answers[0].id == 99


@responses.activate
async def test_questions_list_tool(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/questions",
                  json={"pages": [{"id": 7, "items": [{"id": 1, "slug": "s"}]}]}, status=200)
    async with Client(forms_mcp.mcp) as client:
        result = await client.call_tool("questions_list", {"survey_id": SID})
    assert result.data.pages[0].items[0].slug == "s"
