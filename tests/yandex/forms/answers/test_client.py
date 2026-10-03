"""AnswersClient behaviour the contract table cannot reach: paging quirks, export status, guards."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.full_server import mcp
from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.errors import YandexInvalidRequestError
from ycli.yandex.forms.client import FormsClient

SID = "686d0a1b2c3d4e5f00000030"
ANSWERS = f"{BASE}/surveys/{SID}/answers"


def test_get_needs_exactly_one_selector():
    with (
        FormsClient(oauth_token="t", organization_id="o") as client,
        pytest.raises(YandexInvalidRequestError),
    ):
        client.answers.get(answer_id=1, answer_key="k")


def test_integrations_list_needs_exactly_one_selector():
    with FormsClient(oauth_token="t", organization_id="o") as client:
        with pytest.raises(YandexInvalidRequestError):
            client.answers.integrations_list()
        with pytest.raises(YandexInvalidRequestError):
            client.answers.integrations_list(answer_id=1, answer_key="k")


def test_list_all_carries_the_dead_v3_cursor_onto_v1(api):
    """The next link points at a retired /v3/ route; only its ``id`` cursor is followed."""
    api.add(
        "GET",
        ANSWERS,
        json={
            "columns": [{"slug": "q1"}],
            "answers": [{"id": 1}],
            "next": {"next_url": f"/v3/surveys/{SID}/answers/?id=100"},
        },
    )
    api.add("GET", ANSWERS, json={"columns": [{"slug": "ignored"}], "answers": [{"id": 2}]})
    with FormsClient(oauth_token="t", organization_id="o") as client:
        result = client.answers.list(SID)
    assert [answer.id for answer in result.answers] == [1, 2]
    assert [column.slug for column in result.columns] == ["q1"]
    assert str(api.calls[1].url) == f"{ANSWERS}?id=100"


def test_export_results_reports_a_redirect_to_the_file_as_ready_without_following_it(api):
    file_url = "https://forms.s3.test/uploads/answers.csv"
    api.add("GET", f"{ANSWERS}/export-results", status=302, headers={"Location": file_url})
    with FormsClient(oauth_token="t", organization_id="o") as client:
        assert client.answers.export_results(SID, "op-1").is_ready
    assert len(api.calls) == 1


async def test_a_tool_reports_the_wrong_form_as_a_tool_error(api):
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="exactly one of answer_id or answer_key"):
            await client.call_tool("forms_answers_get", {})
    assert api.calls == []
