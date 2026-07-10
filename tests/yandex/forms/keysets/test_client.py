"""TDD for KeysetsClient — reads (list/get), writes (create/modify/delete), binary download."""

import json

import requests
import responses

from ycli.yandex.forms.keysets.client import KeysetsClient
from ycli.yandex.forms.keysets.models import Keyset, KeysetList

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"
KID = 7


def _client() -> KeysetsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return KeysetsClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/keysets",
        json=[{"id": 7, "name": "Q1", "total": 100, "used": 3, "is_enabled": True}],
        status=200,
    )
    out = _client().list(SID)
    assert isinstance(out, KeysetList)
    assert out.root[0].id == 7 and out.root[0].used == 3
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/keysets"


@responses.activate
def test_get_returns_single_keyset():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/keysets/{KID}",
        json={"id": KID, "name": "Q1", "total": 100, "used": 3, "is_enabled": True},
        status=200,
    )
    out = _client().get(SID, KID)
    assert isinstance(out, Keyset)
    assert out.id == KID and out.name == "Q1"


@responses.activate
def test_create_posts_body_and_returns_keyset():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/keysets",
        json={"id": KID, "name": "Q1", "total": 250, "used": 0, "is_enabled": True},
        status=200,
    )
    out = _client().create(SID, body={"name": "Q1", "total": 250, "is_enabled": True})
    assert isinstance(out, Keyset) and out.id == KID
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Q1",
        "total": 250,
        "is_enabled": True,
    }


@responses.activate
def test_modify_patches_body_and_returns_keyset():
    responses.add(
        responses.PATCH,
        f"{BASE}/surveys/{SID}/keysets/{KID}",
        json={"id": KID, "name": "Q1", "is_enabled": False},
        status=200,
    )
    out = _client().modify(SID, KID, body={"is_enabled": False})
    assert isinstance(out, Keyset) and out.is_enabled is False
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "is_enabled": False,
    }


@responses.activate
def test_delete_returns_raw_response():
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}/keysets/{KID}", status=200)
    out = _client().delete(SID, KID)
    assert out.status_code == 200
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_download_returns_raw_bytes():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/keysets/{KID}/download",
        body=b"key1,link1\nkey2,link2\n",
        status=200,
    )
    out = _client().download(SID, KID)
    assert out == b"key1,link1\nkey2,link2\n"  # verbatim, no JSON parse
    assert responses.calls[0].request.url.endswith(f"/keysets/{KID}/download")  # ty: ignore[unresolved-attribute]
