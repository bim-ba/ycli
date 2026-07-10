"""TDD for the Tracker global-fields client (list + get + create/edit + categories)."""

import json

import requests
import responses

from ycli.yandex.tracker.fields.client import FieldsClient
from ycli.yandex.tracker.fields.models import (
    CustomField,
    FieldCategoryCreate,
    FieldCategoryRecord,
    FieldCategoryUpdate,
    FieldCreate,
    FieldList,
    FieldUpdate,
    LocalizedName,
    OptionsProviderInput,
)

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_fields_list():
    responses.add(
        responses.GET,
        f"{BASE}/fields",
        json=[{"id": "ruName", "key": "ruName", "schema": {"type": "string"}}],
        status=200,
    )
    out = FieldsClient(session=_session()).list()
    assert isinstance(out, FieldList) and out.root[0].id == "ruName"
    assert out.root[0].field_schema.type == "string"


@responses.activate
def test_fields_get():
    responses.add(
        responses.GET,
        f"{BASE}/fields/ruName",
        json={"id": "ruName", "name": "Field", "category": {"id": "1", "display": "System"}},
        status=200,
    )
    out = FieldsClient(session=_session()).get(field_id="ruName")
    assert isinstance(out, CustomField) and out.id == "ruName"
    assert out.category.display == "System"


@responses.activate
def test_fields_create_posts_body_with_options_provider():
    responses.add(
        responses.POST, f"{BASE}/fields", json={"id": "myField", "key": "myField"}, status=201
    )
    out = FieldsClient(session=_session()).create(
        FieldCreate(
            name=LocalizedName(ru="Поле", en="Field"),
            id="myField",
            category="1",
            type="ru.yandex.startrek.core.fields.StringFieldType",
            options_provider=OptionsProviderInput(type="FixedListOptionsProvider", values=["a"]),
        )
    )
    assert isinstance(out, CustomField) and out.id == "myField"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {
        "name": {"ru": "Поле", "en": "Field"},
        "id": "myField",
        "category": "1",
        "type": "ru.yandex.startrek.core.fields.StringFieldType",
        "optionsProvider": {"type": "FixedListOptionsProvider", "values": ["a"]},
    }


@responses.activate
def test_fields_edit_sends_version_query():
    responses.add(
        responses.PATCH, f"{BASE}/fields/ruName", json={"id": "ruName", "name": "Имя"}, status=200
    )
    out = FieldsClient(session=_session()).edit(
        "ruName", FieldUpdate(name=LocalizedName(ru="Имя")), version=3
    )
    assert out.id == "ruName"
    assert "version=3" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": {"ru": "Имя"}}


@responses.activate
def test_fields_category_create_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/fields/categories",
        json={"id": "604f99", "name": "category_name", "version": 1},
        status=201,
    )
    out = FieldsClient(session=_session()).category_create(
        FieldCategoryCreate(name=LocalizedName(ru="Своя"), order=400)
    )
    assert isinstance(out, FieldCategoryRecord) and out.id == "604f99"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": {"ru": "Своя"}, "order": 400}


@responses.activate
def test_fields_category_edit_sends_version_query():
    responses.add(
        responses.PATCH,
        f"{BASE}/fields/categories/604f99",
        json={"id": "604f99", "name": "category_name", "version": 2},
        status=200,
    )
    out = FieldsClient(session=_session()).category_edit(
        "604f99", FieldCategoryUpdate(order=400), version=1
    )
    assert out.version == 2
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"order": 400}
