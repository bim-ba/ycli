"""TDD for ResolutionsClient — GET /resolutions + create/edit write bodies."""

import json

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.resolutions.client import ResolutionsClient
from ycli.yandex.tracker.resolutions.models import (
    LocalizedName,
    Resolution,
    ResolutionCreate,
    ResolutionList,
    ResolutionUpdate,
)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_resolutions_list():
    responses.add(
        responses.GET,
        f"{BASE}/resolutions",
        json=[{"id": 1, "key": "fixed", "name": "Решен"}],
        status=200,
    )
    out = ResolutionsClient(session=_session()).list()
    assert isinstance(out, ResolutionList)
    assert out.root[0].key == "fixed" and out.root[0].name == "Решен"


@responses.activate
def test_resolutions_create_posts_localized_body():
    responses.add(
        responses.POST,
        f"{BASE}/resolutions/",
        json={"id": 9, "key": "wontFix", "name": "Отклонено"},
        status=201,
    )
    out = ResolutionsClient(session=_session()).create(
        ResolutionCreate(key="wontFix", name=LocalizedName(ru="Отклонено", en="Won't fix"))
    )
    assert isinstance(out, Resolution) and out.key == "wontFix"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"key": "wontFix", "name": {"ru": "Отклонено", "en": "Won't fix"}}


@responses.activate
def test_resolutions_edit_sends_version_query():
    responses.add(
        responses.PATCH,
        f"{BASE}/resolutions/9",
        json={"id": 9, "key": "wontFix", "description": "Won't be fixed"},
        status=200,
    )
    out = ResolutionsClient(session=_session()).edit(
        "9", ResolutionUpdate(description="Won't be fixed"), version=1
    )
    assert out.id == 9
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"description": "Won't be fixed"}
