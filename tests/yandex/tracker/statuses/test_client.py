"""TDD for StatusesClient — GET /statuses + create/edit write bodies."""

import json

import requests
import responses

from ycli.yandex.tracker.statuses.client import StatusesClient
from ycli.yandex.tracker.statuses.models import (
    LocalizedName,
    Status,
    StatusCreate,
    StatusList,
    StatusUpdate,
)

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_statuses_list():
    responses.add(
        responses.GET,
        f"{BASE}/statuses",
        json=[{"id": 1, "key": "open", "name": "Открыт", "type": "new"}],
        status=200,
    )
    out = StatusesClient(session=_session()).list()
    assert isinstance(out, StatusList)
    assert out.root[0].key == "open" and out.root[0].type == "new"


@responses.activate
def test_statuses_create_posts_localized_body():
    responses.add(
        responses.POST,
        f"{BASE}/statuses/",
        json={"id": 29, "key": "pause", "name": "On pause", "type": "paused"},
        status=201,
    )
    out = StatusesClient(session=_session()).create(
        StatusCreate(key="pause", name=LocalizedName(ru="Пауза", en="On pause"), type="paused")
    )
    assert isinstance(out, Status) and out.key == "pause"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"key": "pause", "name": {"ru": "Пауза", "en": "On pause"}, "type": "paused"}


@responses.activate
def test_statuses_edit_sends_version_query():
    responses.add(
        responses.PATCH,
        f"{BASE}/statuses/29",
        json={"id": 29, "key": "pause", "name": "Приостановлен", "type": "paused"},
        status=200,
    )
    out = StatusesClient(session=_session()).edit(
        "29", StatusUpdate(description="Issue is paused"), version=1
    )
    assert out.id == 29
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"description": "Issue is paused"}
