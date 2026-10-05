"""Endpoint: the effect follows the method unless stated; requests carry client defaults."""

import dataclasses
from datetime import UTC, datetime
from http import HTTPMethod
from typing import Any

import httpx2
import pytest
from pydantic import BaseModel, Field, RootModel

from ycli.yandex.core.endpoint import (
    ENDPOINT_EXTENSION,
    Effect,
    Endpoint,
    check_path,
    segment,
)
from ycli.yandex.errors import YandexClientError, YandexUnexpectedReplyError
from ycli.yandex.models import APIModel, RequestBody


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
    assert Endpoint(HTTPMethod.POST, "issues/_search", effect=Effect.READ).effect == "read"


def test_an_unknown_method_fails_at_construction():
    typo: Any = "GTE"  # typed Any: the type checker would reject the literal, the runtime must too
    with pytest.raises(ValueError, match="GTE"):
        Endpoint(typo, "x", effect=Effect.READ)


def test_replace_builds_a_changed_copy():
    endpoint = Endpoint(HTTPMethod.POST, "issues/_search", effect=Effect.READ, params={"page": 1})
    moved = dataclasses.replace(endpoint, path="entities/_search", params={"page": 2})
    assert (moved.path, moved.params, moved.effect) == ("entities/_search", {"page": 2}, "read")


def test_request_uses_the_client_base_url_headers_and_drops_none_params():
    client = httpx2.Client(base_url="https://api.test/v1/", headers={"X-Org-Id": "o"})
    endpoint = Endpoint(
        HTTPMethod.POST,
        "items",
        params={"a": 1, "b": None},
        json={"k": "v"},
        headers={"X-Extra": "1"},
    )
    request = endpoint.request(client)
    assert str(request.url) == "https://api.test/v1/items?a=1"
    assert request.headers["X-Org-Id"] == "o"
    assert request.headers["X-Extra"] == "1"
    assert request.content == b'{"k":"v"}'
    assert request.extensions[ENDPOINT_EXTENSION] is endpoint


def test_request_sends_raw_content():
    client = httpx2.Client(base_url="https://api.test/")
    request = Endpoint(HTTPMethod.POST, "upload", content=b"\x00bytes").request(client)
    assert request.content == b"\x00bytes"


def test_parse_validates_the_response_type():
    response = httpx2.Response(200, json=[{"id": 1}, {"id": 2}])
    assert Endpoint(HTTPMethod.GET, "items", list[_Item]).parse(response) == [
        _Item(id=1),
        _Item(id=2),
    ]
    assert Endpoint(HTTPMethod.GET, "count", int).parse(httpx2.Response(200, json=7)) == 7


def test_parse_ignores_the_body_without_a_response_type():
    assert Endpoint(HTTPMethod.DELETE, "items/1").parse(httpx2.Response(204)) is None


def test_a_path_segment_is_percent_escaped():
    client = httpx2.Client(base_url="https://api.test/v3/")
    request = Endpoint(HTTPMethod.GET, f"issues/{segment('TEST 1?x')}").request(client)
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
    request = Endpoint(HTTPMethod.POST, "files", files={"file": ("cv.txt", b"resume")}).request(
        httpx2.Client(base_url="https://api.test/v1/")
    )
    assert request.headers["Content-Type"].startswith("multipart/form-data")
    assert b'name="file"; filename="cv.txt"' in request.read()


def test_bytes_and_a_parser_read_a_non_json_body():
    response = httpx2.Response(200, content=b"\x89PNG")
    assert Endpoint(HTTPMethod.GET, "x", bytes).parse(response) == b"\x89PNG"
    assert Endpoint(HTTPMethod.GET, "x", parser=lambda r: len(r.content)).parse(response) == 4


class _Step(RequestBody):
    target: str | None  # no default: the caller had to give it, so a null is a value
    note: str | None = None
    at: datetime | None = None
    sort_by: str | None = Field(default=None, serialization_alias="sortBy")
    path: str | None = Field(default=None, alias="fullPath")


class _Open(APIModel):
    summary: str | None = None
    steps: list[_Step] | None = None


def _body(value: Any) -> Any:
    return Endpoint(HTTPMethod.POST, "moves", json=value).body


def test_an_optional_field_left_unset_is_not_sent():
    assert _body(_Step(target="c")) == {"target": "c"}
    step = _Step.model_validate(
        {"target": "c", "at": datetime(2026, 10, 4, tzinfo=UTC), "sort_by": "name", "path": "a/b"}
    )
    assert _body(step) == {
        "target": "c",
        "at": "2026-10-04T00:00:00Z",
        "sortBy": "name",
        "fullPath": "a/b",
    }


def test_a_required_field_given_as_null_is_sent():
    assert _body(_Step(target=None)) == {"target": None}


def test_a_key_the_model_does_not_declare_is_sent_as_given():
    cleared = _Open.model_validate({"summary": None, "assignee": None, "sprint": 7})
    assert _body(cleared) == {"assignee": None, "sprint": 7}


def test_the_rules_hold_for_models_nested_in_a_body():
    nested = _Open(summary="x", steps=[_Step(target=None), _Step(target="a", note="n")])
    assert _body(nested) == {
        "summary": "x",
        "steps": [{"target": None}, {"target": "a", "note": "n"}],
    }
    assert _body(RootModel[list[_Step]]([_Step(target="a")])) == [{"target": "a"}]
    assert _body({"steps": (_Step(target="b", note="x"),), "dry": True, "left": None}) == {
        "steps": [{"target": "b", "note": "x"}],
        "dry": True,
        "left": None,
    }


def test_an_ordinary_dump_keeps_every_field():
    """Only a request body drops what was left unset: output shows the nulls of a reply."""
    assert _Step(target="c").model_dump() == {
        "target": "c",
        "note": None,
        "at": None,
        "sortBy": None,
        "fullPath": None,
    }


def test_a_reply_that_does_not_fit_the_model_is_a_typed_error():
    response = httpx2.Response(
        200, json={"items": "x"}, request=httpx2.Request("GET", "https://api.example/v1/things")
    )
    with pytest.raises(YandexUnexpectedReplyError) as caught:
        Endpoint(HTTPMethod.GET, "things", list[int]).parse(response)
    assert "the reply to GET things does not fit what ycli expects" in str(caught.value)
    assert caught.value.url == "https://api.example/v1/things"
    assert caught.value.status is None
