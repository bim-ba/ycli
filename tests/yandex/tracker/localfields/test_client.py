"""TDD for LocalFieldsClient — list/get + create/edit write bodies (no version on edit)."""

import json

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.localfields.client import LocalFieldsClient
from ycli.yandex.tracker.localfields.models import (
    LocalField,
    LocalFieldCreate,
    LocalFieldList,
    LocalFieldUpdate,
    LocalizedName,
    OptionsProviderInput,
)


def _client() -> LocalFieldsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return LocalFieldsClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields",
        json=[
            {"key": "loc_field_key", "name": "Loc field", "schema": {"type": "string"}},
            {"key": "second_key", "name": "Second"},
        ],
        status=200,
    )
    out = _client().list("ORG")
    assert isinstance(out, LocalFieldList)
    assert [f.key for f in out.root] == ["loc_field_key", "second_key"]
    assert out.root[0].field_schema.type == "string"
    assert responses.calls[0].request.url == f"{BASE}/queues/ORG/localFields"


@responses.activate
def test_get_returns_single_field():
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields/loc_field_key",
        json={
            "type": "local",
            "id": "6054--loc_field_key",
            "name": "loc_field_name",
            "key": "loc_field_key",
            "version": 1,
            "schema": {"type": "array", "items": "string", "required": False},
            "readonly": True,
            "options": True,
            "suggest": False,
            "optionsProvider": {
                "type": "FixedListOptionsProvider",
                "needValidation": True,
                "values": ["First item", "Second item"],
            },
            "queryProvider": {"type": "StringOptionalQueryProvider"},
            "order": 3,
            "category": {"id": "1", "display": "Системные"},
            "queue": {"id": "1", "key": "ORG", "display": "My queue"},
        },
        status=200,
    )
    f = _client().get("ORG", "loc_field_key")
    assert isinstance(f, LocalField)
    assert f.key == "loc_field_key" and f.version == 1 and f.readonly is True
    assert f.field_schema.type == "array" and f.field_schema.items == "string"
    assert f.options_provider.values == ["First item", "Second item"]
    assert f.options_provider.need_validation is True
    assert f.query_provider.type == "StringOptionalQueryProvider"
    assert f.category.display == "Системные"
    assert f.queue.key == "ORG"
    assert responses.calls[0].request.url == f"{BASE}/queues/ORG/localFields/loc_field_key"


@responses.activate
def test_create_posts_body_to_queue_path():
    responses.add(
        responses.POST,
        f"{BASE}/queues/ORG/localFields",
        json={"key": "loc", "name": "Loc field"},
        status=200,
    )
    out = _client().create(
        "ORG",
        LocalFieldCreate(
            name=LocalizedName(ru="Поле"),
            id="loc",
            category="1",
            type="ru.yandex.startrek.core.fields.StringFieldType",
            options_provider=OptionsProviderInput(type="FixedListOptionsProvider", values=["a"]),
        ),
    )
    assert isinstance(out, LocalField) and out.key == "loc"
    assert responses.calls[0].request.url == f"{BASE}/queues/ORG/localFields"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {
        "name": {"ru": "Поле"},
        "id": "loc",
        "category": "1",
        "type": "ru.yandex.startrek.core.fields.StringFieldType",
        "optionsProvider": {"type": "FixedListOptionsProvider", "values": ["a"]},
    }


@responses.activate
def test_edit_patches_without_version():
    responses.add(
        responses.PATCH,
        f"{BASE}/queues/ORG/localFields/loc",
        json={"key": "loc", "order": 102},
        status=200,
    )
    out = _client().edit("ORG", "loc", LocalFieldUpdate(order=102))
    assert isinstance(out, LocalField) and out.order == 102
    assert responses.calls[0].request.method == "PATCH"
    assert responses.calls[0].request.url == f"{BASE}/queues/ORG/localFields/loc"
    assert "version=" not in responses.calls[0].request.url
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"order": 102}
