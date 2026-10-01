"""Endpoint: the effect follows the method unless stated; requests carry client defaults."""

import httpx2
import pytest
from pydantic import BaseModel

from ycli.yandex.core.endpoint import EFFECT_EXTENSION, Endpoint, segment


class _Item(BaseModel):
    id: int


@pytest.mark.parametrize(
    ("method", "effect", "idempotent"),
    [
        ("get", "read", True),
        ("HEAD", "read", True),
        ("PUT", "idempotent_write", True),
        ("PATCH", "idempotent_write", True),
        ("DELETE", "destructive", False),
        ("POST", "write", False),
    ],
)
def test_effect_follows_the_method(method, effect, idempotent):
    endpoint = Endpoint(method, "x")
    assert endpoint.method == method.upper()
    assert endpoint.effect == effect
    assert endpoint.idempotent is idempotent


def test_a_stated_effect_wins():
    assert Endpoint("POST", "issues/_search", effect="read").effect == "read"


def test_request_uses_the_client_base_url_headers_and_drops_none_params():
    client = httpx2.Client(base_url="https://api.test/v1/", headers={"X-Org-Id": "o"})
    endpoint = Endpoint(
        "POST", "items", params={"a": 1, "b": None}, json={"k": "v"}, headers={"X-Extra": "1"}
    )
    request = endpoint.request(client)
    assert str(request.url) == "https://api.test/v1/items?a=1"
    assert request.headers["X-Org-Id"] == "o"
    assert request.headers["X-Extra"] == "1"
    assert request.content == b'{"k":"v"}'
    assert request.extensions[EFFECT_EXTENSION] == "write"


def test_request_sends_raw_content():
    client = httpx2.Client(base_url="https://api.test/")
    request = Endpoint("POST", "upload", content=b"\x00bytes").request(client)
    assert request.content == b"\x00bytes"


def test_parse_validates_the_response_type():
    response = httpx2.Response(200, json=[{"id": 1}, {"id": 2}])
    assert Endpoint("GET", "items", list[_Item]).parse(response) == [_Item(id=1), _Item(id=2)]
    assert Endpoint("GET", "count", int).parse(httpx2.Response(200, json=7)) == 7


def test_parse_ignores_the_body_without_a_response_type():
    assert Endpoint("DELETE", "items/1").parse(httpx2.Response(204)) is None


def test_a_path_segment_cannot_escape_its_place():
    client = httpx2.Client(base_url="https://api.test/v3/")
    request = Endpoint("PATCH", f"issues/{segment('../queues/DE?x=1')}").request(client)
    assert request.url.raw_path == b"/v3/issues/..%2Fqueues%2FDE%3Fx%3D1"
