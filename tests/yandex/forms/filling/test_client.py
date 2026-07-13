"""TDD for FillingClient — get-settings read, submit write (body+query), suggest read."""

import json

import requests
import responses

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.filling.client import FillingClient
from ycli.yandex.forms.filling.models import (
    FillableForm,
    SubmitBody,
    SubmitResult,
    SuggestionList,
)

SID = "6818ceffe010db4f59d11329"


def _client() -> FillingClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return FillingClient(session=session)


@responses.activate
def test_get_returns_fillable_form():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/form",
        json={
            "id": SID,
            "name": "Feedback",
            "texts": {"submit": "Send"},
            "pages": [{"items": [{"id": "q1", "type": "string"}]}],
            "values": {"q1": "hi"},
        },
        status=200,
    )
    out = _client().get(SID)
    assert isinstance(out, FillableForm)
    assert out.name == "Feedback"
    assert out.texts is not None and out.texts.submit == "Send"
    assert out.pages[0]["items"][0]["id"] == "q1"
    assert out.values == {"q1": "hi"}


@responses.activate
def test_get_passes_fill_key_query():
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/form", json={"id": SID}, status=200)
    _client().get(SID, key="k1")
    assert "key=k1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_submit_posts_answer_map_and_dry_run_query():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/form",
        json={"id": SID, "answer_id": 99, "answer_key": "ak"},
        status=200,
    )
    body = SubmitBody.model_validate({"answer_short_text_1": "Ann", "q2": [1, 2]})
    out = _client().submit(SID, body, dry_run=True, key="k1")
    assert isinstance(out, SubmitResult)
    assert out.answer_id == 99 and out.answer_key == "ak"
    request = responses.calls[0].request
    assert json.loads(request.body) == {  # ty: ignore[invalid-argument-type]
        "answer_short_text_1": "Ann",
        "q2": [1, 2],
    }
    assert request.url is not None
    assert "dry_run=true" in request.url
    assert "key=k1" in request.url


@responses.activate
def test_submit_omits_dry_run_when_false():
    responses.add(responses.POST, f"{BASE}/surveys/{SID}/form", json={"id": SID}, status=200)
    _client().submit(SID, SubmitBody.model_validate({"q1": "a"}))
    assert "dry_run=" not in responses.calls[0].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_suggest_returns_list_with_query_params():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/suggest",
        json=[{"layer": "city", "id": "1", "text": "Berlin", "country_id": "de"}],
        status=200,
    )
    out = _client().suggest(SID, question="city_1", text="Ber", suggest_id="1", parent_id="p")
    assert isinstance(out, SuggestionList)
    assert out.root[0].text == "Berlin"
    assert out.root[0].model_dump()["country_id"] == "de"  # layer-specific extra preserved
    url = responses.calls[0].request.url
    assert url is not None
    assert "question=city_1" in url and "text=Ber" in url
    assert "id=1" in url and "parent_id=p" in url  # suggest_id maps to the ?id= query key


@responses.activate
def test_suggest_omits_unset_query():
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/suggest", json=[], status=200)
    _client().suggest(SID)
    url = responses.calls[0].request.url
    assert url is not None
    assert "question=" not in url and "text=" not in url and "parent_id=" not in url
