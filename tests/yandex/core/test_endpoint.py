"""Endpoint: the effect follows the method unless stated; requests carry client defaults."""

import dataclasses
from typing import Any

import httpx2
import pytest
from pydantic import BaseModel

from ycli.yandex.core.endpoint import EFFECT_EXTENSION, Endpoint, check_path, segment
from ycli.yandex.errors import YandexClientError


class _Item(BaseModel):
    id: int


@pytest.mark.parametrize(
    ("method", "effect", "idempotent"),
    [
        ("GET", "read", True),
        ("HEAD", "read", True),
        ("PUT", "idempotent_write", True),
        ("PATCH", "idempotent_write", True),
        ("DELETE", "destructive", False),
        ("POST", "write", False),
    ],
)
def test_effect_follows_the_method(method, effect, idempotent):
    endpoint = Endpoint(method, "x")
    assert endpoint.effect == effect
    assert endpoint.idempotent is idempotent


def test_a_stated_effect_wins():
    assert Endpoint("POST", "issues/_search", effect="read").effect == "read"


def test_an_unknown_method_fails_at_construction():
    typo: Any = "GTE"  # typed Any: the type checker would reject the literal, the runtime must too
    with pytest.raises(ValueError, match="GTE"):
        Endpoint(typo, "x", effect="read")


def test_replace_builds_a_changed_copy():
    endpoint = Endpoint("POST", "issues/_search", effect="read", params={"page": 1})
    moved = dataclasses.replace(endpoint, path="entities/_search", params={"page": 2})
    assert (moved.path, moved.params, moved.effect) == ("entities/_search", {"page": 2}, "read")


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


def test_a_path_segment_is_percent_escaped():
    client = httpx2.Client(base_url="https://api.test/v3/")
    request = Endpoint("GET", f"issues/{segment('TEST 1?x')}").request(client)
    assert request.url.raw_path == b"/v3/issues/TEST%201%3Fx"


@pytest.mark.parametrize(
    "raw_path",
    [
        "/v3/issues/..%2Fqueues%2FDE",  # the live case: Tracker decodes %2F, then resolves ..
        "/v3/issues/..%2fqueues",
        "/v3/issues/a%5Cb",
        "/v3/issues\\..\\queues",  # a raw backslash: no Yandex path has one
        "/v3/issues/../queues/DE",
        "/v3/issues/./x",
        "/v3/issues//comments",
    ],
)
def test_check_path_refuses_a_path_that_leaves_its_endpoint(raw_path):
    with pytest.raises(YandexClientError, match="leaves its endpoint"):
        check_path(raw_path)


@pytest.mark.parametrize("raw_path", ["/v3/issues/", "/v3/issues/TEST-1", "/v1/a%20b/c..d"])
def test_check_path_accepts_ordinary_paths(raw_path):
    check_path(raw_path)


def test_files_send_a_multipart_body():
    request = Endpoint("POST", "files", files={"file": ("cv.txt", b"resume")}).request(
        httpx2.Client(base_url="https://api.test/v1/")
    )
    assert request.headers["Content-Type"].startswith("multipart/form-data")
    assert b'name="file"; filename="cv.txt"' in request.read()


def test_bytes_and_a_parser_read_a_non_json_body():
    response = httpx2.Response(200, content=b"\x89PNG")
    assert Endpoint("GET", "x", bytes).parse(response) == b"\x89PNG"
    assert Endpoint("GET", "x", parser=lambda r: len(r.content)).parse(response) == 4
