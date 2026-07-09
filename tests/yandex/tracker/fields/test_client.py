"""TDD for the Tracker global-fields client (list + get)."""

import requests
import responses

from ycli.yandex.tracker.fields.client import FieldsClient
from ycli.yandex.tracker.fields.models import CustomField, FieldList

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
