"""TDD for IssueTypesClient — GET /issuetypes + create/edit write bodies."""

import json

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.issuetypes.client import IssueTypesClient
from ycli.yandex.tracker.issuetypes.models import (
    IssueType,
    IssueTypeCreate,
    IssueTypeList,
    IssueTypeUpdate,
    LocalizedName,
)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_issuetypes_list():
    # The live v3 API carries the display name in `name` (`display` stays null).
    responses.add(
        responses.GET, f"{BASE}/issuetypes", json=[{"key": "task", "name": "Task"}], status=200
    )
    out = IssueTypesClient(session=_session()).list()
    assert isinstance(out, IssueTypeList) and out.root[0].key == "task"
    assert out.root[0].name == "Task"


@responses.activate
def test_issuetypes_create_posts_localized_body():
    responses.add(
        responses.POST,
        f"{BASE}/issuetypes/",
        json={"id": 23, "key": "client", "name": "Клиент"},
        status=201,
    )
    out = IssueTypesClient(session=_session()).create(
        IssueTypeCreate(key="client", name=LocalizedName(ru="Клиент", en="Customer"))
    )
    assert isinstance(out, IssueType) and out.key == "client" and out.name == "Клиент"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"key": "client", "name": {"ru": "Клиент", "en": "Customer"}}


@responses.activate
def test_issuetypes_edit_sends_version_query():
    responses.add(
        responses.PATCH,
        f"{BASE}/issuetypes/23",
        json={"id": 23, "key": "client", "name": "Покупатель"},
        status=200,
    )
    out = IssueTypesClient(session=_session()).edit(
        "23", IssueTypeUpdate(name=LocalizedName(ru="Покупатель")), version=1
    )
    assert out.key == "client"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": {"ru": "Покупатель"}}
