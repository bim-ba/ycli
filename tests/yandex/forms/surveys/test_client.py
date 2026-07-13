"""TDD for SurveysClient — reads (list/get) plus writes (create/modify/delete/publish)."""

import json

import requests
import responses

from ycli.yandex.forms.surveys.client import SurveysClient
from ycli.yandex.forms.surveys.models import Survey, SurveyList
from ycli.yandex.models import Ack

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


def _client() -> SurveysClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return SurveysClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/surveys",
        json={"links": {}, "result": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}]},
        status=200,
    )
    out = _client().list()
    assert isinstance(out, SurveyList)
    assert [s.id for s in out.root] == ["a", "b"]
    assert responses.calls[0].request.params["offset"] == "0"  # ty: ignore[unresolved-attribute]
    assert responses.calls[0].request.params["limit"] == "100"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_drains_offset_pages():
    full_page = [
        {"id": str(index)} for index in range(100)
    ]  # exactly page_size → not the last page
    responses.add(
        responses.GET,
        f"{BASE}/surveys",
        json={"links": {"next": "x"}, "result": full_page},
        status=200,
    )
    responses.add(
        responses.GET, f"{BASE}/surveys", json={"links": {}, "result": [{"id": "tail"}]}, status=200
    )
    out = _client().list()
    assert len(out.root) == 101 and out.root[-1].id == "tail"  # both pages drained
    assert len(responses.calls) == 2
    assert responses.calls[1].request.params["offset"] == "100"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_respects_limit_without_extra_fetch():
    responses.add(
        responses.GET,
        f"{BASE}/surveys",
        json={"links": {}, "result": [{"id": "a"}, {"id": "b"}, {"id": "c"}]},
        status=200,
    )
    out = _client().list(limit=2)
    assert [s.id for s in out.root] == ["a", "b"]  # truncated to the cap
    assert len(responses.calls) == 1


@responses.activate
def test_get_returns_single_survey():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}",
        json={"id": SID, "name": "Новая Задача", "is_published": True, "language": "ru"},
        status=200,
    )
    s = _client().get(SID)
    assert isinstance(s, Survey)
    assert s.id == SID and s.is_published is True
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}"


@responses.activate
def test_create_posts_body_and_returns_survey():
    responses.add(
        responses.POST, f"{BASE}/surveys", json={"id": SID, "name": "New form"}, status=200
    )
    out = _client().create(body={"name": "New form", "need_auth": True})
    assert isinstance(out, Survey) and out.id == SID
    assert responses.calls[0].request.url == f"{BASE}/surveys"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "New form",
        "need_auth": True,
    }


@responses.activate
def test_modify_patches_body_and_returns_survey():
    responses.add(
        responses.PATCH, f"{BASE}/surveys/{SID}", json={"id": SID, "name": "Renamed"}, status=200
    )
    out = _client().modify(SID, body={"name": "Renamed"})
    assert isinstance(out, Survey) and out.name == "Renamed"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Renamed",
    }


@responses.activate
def test_delete_returns_synthesized_result():
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}", status=204)
    out = _client().delete(SID)
    assert out == Ack(detail=f"deleted survey {SID}")
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_publish_posts_bodyless_and_returns_result():
    responses.add(responses.POST, f"{BASE}/surveys/{SID}/publish", body="OK", status=200)
    out = _client().publish(SID)
    assert out == Ack(detail=f"published survey {SID}")
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/publish"
    assert not responses.calls[0].request.body  # no request body sent


@responses.activate
def test_unpublish_posts_bodyless_and_returns_result():
    responses.add(responses.POST, f"{BASE}/surveys/{SID}/unpublish", body="OK", status=200)
    out = _client().unpublish(SID)
    assert out == Ack(detail=f"unpublished survey {SID}")
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/unpublish"
