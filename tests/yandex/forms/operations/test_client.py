"""TDD for OperationsClient — GET /operations/{id} → OperationResult."""

import requests
import responses

from ycli.yandex.forms.operations.client import OperationsClient
from ycli.yandex.forms.operations.models import OperationResult

BASE = "https://api.forms.yandex.net/v1"
OID = "op-4a1b"


def _client() -> OperationsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return OperationsClient(session=s)


@responses.activate
def test_get_returns_operation_result():
    responses.add(
        responses.GET,
        f"{BASE}/operations/{OID}",
        json={"id": OID, "status": "ok", "message": "done"},
        status=200,
    )
    out = _client().get(OID)
    assert isinstance(out, OperationResult)
    assert out.id == OID and out.status == "ok" and out.is_ready is True
    assert responses.calls[0].request.url == f"{BASE}/operations/{OID}"


@responses.activate
def test_get_running_operation_is_not_terminal():
    responses.add(
        responses.GET,
        f"{BASE}/operations/{OID}",
        json={"id": OID, "status": "wait"},
        status=200,
    )
    out = _client().get(OID)
    assert out.is_terminal is False
