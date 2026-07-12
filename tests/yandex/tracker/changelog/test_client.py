"""TDD for ChangelogClient — relative-paginated list draining ``id=<last change id>``."""

import json
from urllib.parse import parse_qs, urlparse

import requests
import responses

from ycli.yandex.tracker.changelog.client import ChangelogClient
from ycli.yandex.tracker.changelog.models import ChangelogList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> ChangelogClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return ChangelogClient(session=s)


def _changelog_page_callback(request):
    """Three-request drain: page 1 (no id) → id=ch2 page → id=ch3 empty page terminates."""
    cursor = parse_qs(urlparse(request.url).query).get("id", [None])[0]
    if cursor is None:
        body = [
            {
                "id": "ch1",
                "updatedBy": {"display": "Сава"},
                "type": "IssueUpdated",
                "fields": [
                    {
                        "field": {"id": "status"},
                        "from": None,
                        "to": {"key": "done", "display": "Готово"},
                    }
                ],
            },
            {"id": "ch2", "type": "IssueCommentAdded", "fields": []},
        ]
    elif cursor == "ch2":
        body = [{"id": "ch3", "type": "IssueUpdated", "fields": []}]
    else:  # id=ch3 → nothing left → RelativeCursorStrategy stops
        body = []
    return (200, {}, json.dumps(body))


@responses.activate
def test_list_drains_pages_and_parses_polymorphic_fields():
    responses.add_callback(
        responses.GET,
        f"{BASE}/issues/DE-1/changelog",
        callback=_changelog_page_callback,
        content_type="application/json",
    )
    out = _client().list("DE-1")
    assert isinstance(out, ChangelogList)
    assert [e.id for e in out.root] == ["ch1", "ch2", "ch3"]  # pages joined in order
    first = out.root[0]
    assert first.updated_by == "Сава"
    assert first.fields[0].to == {"key": "done", "display": "Готово"}  # polymorphic passthrough
    assert len(responses.calls) == 3  # page1 + id=ch2 page + id=ch3 empty page
    assert "perPage=100" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    assert "id=ch2" in responses.calls[1].request.url  # ty: ignore[unsupported-operator]
    assert "id=ch3" in responses.calls[2].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_list_respects_limit_within_first_page():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/changelog",
        json=[{"id": "ch1", "fields": []}, {"id": "ch2", "fields": []}],
        status=200,
    )
    out = _client().list("DE-1", limit=1)
    assert [e.id for e in out.root] == ["ch1"]  # truncated to the limit
    assert len(responses.calls) == 1  # limit satisfied by page 1 — no second fetch
