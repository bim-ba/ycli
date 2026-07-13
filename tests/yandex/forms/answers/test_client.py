"""TDD for AnswersClient — single-answer get + the {columns, answers, next} envelope verbatim."""

import json
from urllib.parse import parse_qs, urlparse

import pytest
import requests
import responses

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.answers.client import AnswersClient
from ycli.yandex.forms.answers.models import AnswerDetails, AnswersResponse, ExportResult

SID = "6818ceffe010db4f59d11329"

ANSWER_BODY = {
    "id": 2469549806,
    "created": "2026-07-12T10:00:00Z",
    "survey": {"id": SID, "name": "Feedback"},
    "quiz": None,
    "data": [{"id": "1", "label": "Q1", "type": "string", "value": "x"}],
}


def _client() -> AnswersClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return AnswersClient(session=s)


@responses.activate
def test_get_by_answer_id_hits_flat_route():
    """The single-answer read is the flat ``GET /v1/answers?answer_id=`` (live-verified 200);
    the ``/surveys/{id}/answers/{answer_id}`` path variants 404."""
    responses.add(responses.GET, f"{BASE}/answers", json=ANSWER_BODY, status=200)
    out = _client().get(answer_id=2469549806)
    assert isinstance(out, AnswerDetails)
    assert out.id == 2469549806
    assert out.survey is not None and out.survey.name == "Feedback"
    assert out.data[0]["value"] == "x"
    url = responses.calls[0].request.url
    assert url is not None
    assert urlparse(url).path == "/v1/answers"
    assert parse_qs(urlparse(url).query) == {"answer_id": ["2469549806"]}


@responses.activate
def test_get_by_answer_key_sends_only_key():
    responses.add(responses.GET, f"{BASE}/answers", json=ANSWER_BODY, status=200)
    out = _client().get(answer_key="a1b2c3hash")
    assert isinstance(out, AnswerDetails) and out.id == 2469549806
    url = responses.calls[0].request.url
    assert url is not None
    assert parse_qs(urlparse(url).query) == {"answer_key": ["a1b2c3hash"]}


def test_get_requires_exactly_one_selector():
    with pytest.raises(ValueError, match="exactly one"):
        _client().get()
    with pytest.raises(ValueError, match="exactly one"):
        _client().get(answer_id=1, answer_key="k")


@responses.activate
def test_list_returns_envelope_verbatim():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
            "answers": [{"id": 99, "created": "2026-01-01", "data": [{"value": "x"}]}],
            "next": None,
        },
        status=200,
    )
    ar = _client().list(SID)
    assert isinstance(ar, AnswersResponse)
    assert ar.columns[0].text == "T"
    assert ar.answers[0].id == 99 and ar.answers[0].data == [{"value": "x"}]
    assert ar.next is None
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/answers"


def _paginated_callback(request):
    """Two-page stub: page 1 hands a next_url carrying ``id=100``; page 2 drains it."""
    params = parse_qs(urlparse(request.url).query)
    if "id" not in params:
        body = {
            "columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
            "answers": [{"id": 1, "created": "2026-01-01", "data": [{"value": "a"}]}],
            "next": {"next_url": f"{BASE}/surveys/{SID}/answers?id=100&page_size=1"},
        }
    else:
        body = {
            "columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
            "answers": [{"id": 2, "created": "2026-01-02", "data": [{"value": "b"}]}],
            "next": None,
        }
    return (200, {}, json.dumps(body))


@responses.activate
def test_list_all_follows_next_url_and_concatenates():
    responses.add_callback(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        callback=_paginated_callback,
        content_type="application/json",
    )
    ar = _client().list_all(SID)
    assert isinstance(ar, AnswersResponse)
    # every page drained, answers concatenated in order
    assert [a.id for a in ar.answers] == [1, 2]
    assert ar.columns[0].text == "T"  # columns kept from the first page
    assert ar.next is None  # merged envelope is fully drained
    assert len(responses.calls) == 2  # page 1 + the followed next_url
    assert "id=100" in responses.calls[1].request.url  # ty: ignore[unsupported-operator]  # followed the server's cursor verbatim


@responses.activate
def test_list_all_breaks_on_self_pointing_cursor():
    """A server whose next_url points at itself must terminate, not loop forever."""
    same = f"{BASE}/surveys/{SID}/answers?id=100"

    def cb(request):
        body = {
            "columns": [],
            "answers": [{"id": 1, "created": "x", "data": []}],
            "next": {"next_url": same},
        }  # every page hands back the SAME cursor
        return (200, {}, json.dumps(body))

    responses.add_callback(
        responses.GET, f"{BASE}/surveys/{SID}/answers", callback=cb, content_type="application/json"
    )
    ar = _client().list_all(SID)
    # page 1 (no id) + one follow of id=100; the second sighting of id=100 trips the guard
    assert len(responses.calls) == 2
    assert [a.id for a in ar.answers] == [1, 1]


@responses.activate
def test_list_all_single_page_makes_one_call():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={"columns": [], "answers": [{"id": 7, "created": "x", "data": []}], "next": None},
        status=200,
    )
    ar = _client().list_all(SID)
    assert [a.id for a in ar.answers] == [7]
    assert len(responses.calls) == 1  # no next_url → no extra request


@responses.activate
def test_list_all_respects_limit():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [{"id": 1, "slug": "c", "type": "string", "text": "C"}],
            "answers": [
                {"id": 1, "created": "x", "data": []},
                {"id": 2, "created": "x", "data": []},
            ],
            "next": {"next_url": f"surveys/{SID}/answers?id=2"},
        },
        status=200,
    )
    ar = _client().list_all(SID, limit=1)
    assert len(ar.answers) == 1
    assert ar.next is None
    assert len(responses.calls) == 1  # limit satisfied by page 1 — no second fetch


@responses.activate
def test_list_all_limit_spans_pages():
    """limit=3 forces a second-page fetch (page 1 has 2 answers) then truncates within page 2."""
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [{"id": 1, "slug": "c", "type": "string", "text": "C"}],
            "answers": [
                {"id": 1, "created": "x", "data": []},
                {"id": 2, "created": "x", "data": []},
            ],
            "next": {"next_url": f"{BASE}/surveys/{SID}/answers?id=2&page_size=2"},
        },
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [{"id": 1, "slug": "c", "type": "string", "text": "C"}],
            "answers": [
                {"id": 3, "created": "x", "data": []},
                {"id": 4, "created": "x", "data": []},
            ],
            "next": None,
        },
        status=200,
    )
    ar = _client().list_all(SID, limit=3)
    assert len(ar.answers) == 3  # page 1 (2) + page 2 first 1, truncated
    assert [a.id for a in ar.answers] == [1, 2, 3]
    assert ar.next is None
    assert len(responses.calls) == 2  # page boundary was crossed


@responses.activate
def test_export_posts_typed_body():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/answers/export",
        json={"id": "op-1", "status": "wait", "message": "started"},
        status=202,
    )
    er = _client().export(SID, body={"format": "xlsx", "upload": "default", "limit": 10})
    assert isinstance(er, ExportResult)
    assert er.id == "op-1" and er.status == "wait" and er.is_terminal is False
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "format": "xlsx",
        "upload": "default",
        "limit": 10,
    }
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/answers/export"


@responses.activate
def test_list_all_rebuilds_dead_v3_next_url_onto_v1():
    """The live API hands back a *relative* ``/v3/…/answers/?id=…`` next_url that 404s; ``list_all``
    must re-issue the same cursor against the working v1 endpoint, not follow the dead v3 path."""

    def cb(request):
        params = parse_qs(urlparse(request.url).query)
        if "id" not in params:
            body = {
                "columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
                "answers": [{"id": 200, "created": "2026-01-01", "data": [{"value": "a"}]}],
                "next": {"next_url": f"/v3/surveys/{SID}/answers/?id=200&page_size=1"},
            }
        else:
            body = {
                "columns": [],
                "answers": [{"id": 100, "created": "2026-01-02", "data": [{"value": "b"}]}],
                "next": None,
            }
        return (200, {}, json.dumps(body))

    responses.add_callback(
        responses.GET, f"{BASE}/surveys/{SID}/answers", callback=cb, content_type="application/json"
    )
    ar = _client().list_all(SID)
    assert [a.id for a in ar.answers] == [200, 100]  # both pages drained
    assert len(responses.calls) == 2
    follow_url = responses.calls[1].request.url
    assert follow_url is not None
    assert "/v1/surveys/" in follow_url  # pinned to the working v1 endpoint
    assert "/v3/" not in follow_url  # NOT the dead path the server handed back
    assert "id=200" in follow_url  # carried the server's cursor


@responses.activate
def test_export_results_ready_redirect_to_csv_is_terminal():
    """Once ready, the status endpoint 302-redirects to the exported file (CSV/binary), not JSON;
    ``export_results`` must read the followed redirect as terminal ``ok`` instead of choking on the
    non-JSON body (the ``@uplink.returns.json()`` bug)."""
    file_url = "https://forms.s3-private.mds.yandex.net/uploads/answers.csv"
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers/export-results",
        status=302,
        headers={"Location": file_url},
    )
    responses.add(
        responses.GET,
        file_url,
        body=b"Name\nresp0\nresp1\n",
        content_type="application/octet-stream",
    )
    er = _client().export_results(SID, "op-1")
    assert isinstance(er, ExportResult)
    assert er.is_terminal is True and er.is_ready is True


@responses.activate
def test_export_results_returns_status():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers/export-results",
        json={"id": "op-1", "status": "ok", "message": "ready"},
        status=200,
    )
    er = _client().export_results(SID, "op-1")
    assert isinstance(er, ExportResult)
    assert er.is_ready is True and er.is_terminal is True
    url = responses.calls[0].request.url
    assert url is not None
    assert parse_qs(urlparse(url).query)["task_id"] == ["op-1"]


@responses.activate
def test_download_export_returns_file_bytes():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers/export-results",
        body=b"col1,col2\n1,2\n",
        status=200,
    )
    data = _client().download_export(SID, "op-1")
    assert data == b"col1,col2\n1,2\n"
    url = responses.calls[0].request.url
    assert url is not None
    assert parse_qs(urlparse(url).query)["task_id"] == ["op-1"]
