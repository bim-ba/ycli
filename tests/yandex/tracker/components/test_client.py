"""TDD for the Tracker components client (list + create + edit write bodies)."""

import json

import requests
import responses

from ycli.yandex.tracker.components.client import ComponentsClient
from ycli.yandex.tracker.components.models import (
    Component,
    ComponentCreate,
    ComponentList,
    ComponentUpdate,
)

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_components_list():
    responses.add(
        responses.GET,
        f"{BASE}/components",
        json=[
            {
                "id": 1,
                "name": "Test",
                "queue": {"key": "ORG", "display": "My queue"},
                "assignAuto": False,
            }
        ],
        status=200,
    )
    out = ComponentsClient(session=_session()).list()
    assert isinstance(out, ComponentList) and out.root[0].name == "Test"
    assert out.root[0].queue.key == "ORG" and out.root[0].assign_auto is False


@responses.activate
def test_components_create_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/components",
        json={"id": 111175, "name": "UI", "queue": {"key": "TEST"}},
        status=201,
    )
    out = ComponentsClient(session=_session()).create(
        ComponentCreate(name="UI", queue="TEST", assign_auto=True)
    )
    assert isinstance(out, Component) and out.id == 111175
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": "UI", "queue": "TEST", "assignAuto": True}


@responses.activate
def test_components_edit_sends_version_query():
    responses.add(
        responses.PATCH,
        f"{BASE}/components/111175",
        json={"id": 111175, "name": "UI", "assignAuto": True},
        status=200,
    )
    out = ComponentsClient(session=_session()).edit(
        111175, ComponentUpdate(assign_auto=True), version=1
    )
    assert out.id == 111175
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"assignAuto": True}
