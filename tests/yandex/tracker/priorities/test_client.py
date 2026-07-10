"""TDD for the three Tracker lookup clients (+ priorities create/edit write bodies)."""

import json

import requests
import responses

from ycli.yandex.tracker.issuetypes.client import IssueTypesClient
from ycli.yandex.tracker.issuetypes.models import IssueTypeList
from ycli.yandex.tracker.linktypes.client import LinkTypesClient
from ycli.yandex.tracker.linktypes.models import LinkTypeList
from ycli.yandex.tracker.priorities.client import PrioritiesClient
from ycli.yandex.tracker.priorities.models import (
    LocalizedName,
    Priority,
    PriorityCreate,
    PriorityList,
    PriorityUpdate,
)

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_priorities_list():
    responses.add(
        responses.GET,
        f"{BASE}/priorities",
        json=[{"key": "critical", "display": "Critical"}],
        status=200,
    )
    out = PrioritiesClient(session=_session()).list()
    assert isinstance(out, PriorityList) and out.root[0].key == "critical"


@responses.activate
def test_issuetypes_list():
    responses.add(
        responses.GET, f"{BASE}/issuetypes", json=[{"key": "task", "display": "Task"}], status=200
    )
    out = IssueTypesClient(session=_session()).list()
    assert isinstance(out, IssueTypeList) and out.root[0].key == "task"


@responses.activate
def test_linktypes_list():
    responses.add(
        responses.GET,
        f"{BASE}/linktypes",
        json=[{"id": "relates", "inward": "related to", "outward": "related to"}],
        status=200,
    )
    out = LinkTypesClient(session=_session()).list()
    assert isinstance(out, LinkTypeList) and out.root[0].id == "relates"


@responses.activate
def test_priorities_create_posts_localized_body():
    responses.add(
        responses.POST,
        f"{BASE}/priorities/",
        json={"id": 6, "key": "one", "name": "Низкий", "order": 60},
        status=201,
    )
    out = PrioritiesClient(session=_session()).create(
        PriorityCreate(key="one", name=LocalizedName(ru="Низкий", en="Low"), order=60)
    )
    assert isinstance(out, Priority) and out.key == "one"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"key": "one", "name": {"ru": "Низкий", "en": "Low"}, "order": 60}


@responses.activate
def test_priorities_edit_sends_version_query():
    responses.add(
        responses.PATCH,
        f"{BASE}/priorities/one",
        json={"id": 6, "key": "one", "name": "Низкий"},
        status=200,
    )
    out = PrioritiesClient(session=_session()).edit(
        "one", PriorityUpdate(name=LocalizedName(ru="Низкий")), version=1
    )
    assert out.key == "one"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": {"ru": "Низкий"}}
