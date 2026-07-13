"""TDD for the Tracker filters client (get + create + edit write bodies)."""

import json

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.filters.client import FiltersClient
from ycli.yandex.tracker.filters.models import Filter, FilterCreate, FilterUpdate


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_filters_get():
    responses.add(
        responses.GET,
        f"{BASE}/filters/12345",
        json={
            "id": 12345,
            "name": "My open issues",
            "filter": {"assignee": "me()", "status": "open"},
            "favorite": False,
        },
        status=200,
    )
    out = FiltersClient(session=_session()).get(filter_id="12345")
    assert isinstance(out, Filter) and out.id == 12345
    assert out.filter == {"assignee": "me()", "status": "open"}


@responses.activate
def test_filters_create_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/filters/",
        json={"id": 12345, "name": "My open", "filter": {"status": "open"}},
        status=201,
    )
    out = FiltersClient(session=_session()).create(
        FilterCreate(name="My open", filter={"status": "open"})
    )
    assert isinstance(out, Filter) and out.id == 12345
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": "My open", "filter": {"status": "open"}}


@responses.activate
def test_filters_edit_patches_without_version():
    responses.add(
        responses.PATCH,
        f"{BASE}/filters/12345",
        json={"id": 12345, "name": "Renamed"},
        status=200,
    )
    out = FiltersClient(session=_session()).edit("12345", FilterUpdate(name="Renamed"))
    assert out.name == "Renamed"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=" not in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": "Renamed"}
