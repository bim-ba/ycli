"""AnswersClient behaviour the contract table cannot reach: paging quirks, export status, guards."""

from fastmcp import Client

from tests.full_server import mcp
from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.client import FormsClient

SID = "686d0a1b2c3d4e5f00000030"
ANSWERS = f"{BASE}/surveys/{SID}/answers"


def test_get_sends_both_selectors_as_given(api):
    api.add("GET", f"{BASE}/answers", json={"id": 1})
    with FormsClient(oauth_token="t", organization_id="o") as client:
        client.answers.get(answer_id=1, answer_key="k")
    assert dict(api.calls[0].url.params) == {"answer_id": "1", "answer_key": "k"}


def test_integrations_list_sends_the_selectors_it_is_given_and_none_when_given_none(api):
    api.add("GET", f"{BASE}/answers/integrations", json=[])
    with FormsClient(oauth_token="t", organization_id="o") as client:
        client.answers.integrations_list()
        client.answers.integrations_list(answer_id=1, answer_key="k")
    assert dict(api.calls[0].url.params) == {}
    assert dict(api.calls[1].url.params) == {"answer_id": "1", "answer_key": "k"}


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


async def test_a_tool_sends_no_selector_as_given(api):
    api.add("GET", f"{BASE}/answers", json={"id": 1})
    async with Client(mcp) as client:
        await client.call_tool("forms_answers_get", {})
    assert dict(api.calls[0].url.params) == {}
