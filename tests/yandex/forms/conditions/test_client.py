"""TDD for ConditionsClient — all three families and their six operations, over mocked HTTP."""

import json

import pytest
import requests
import responses

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.conditions.client import ConditionsClient
from ycli.yandex.forms.conditions.models import (
    Condition,
    ConditionCreate,
    ConditionItemWrite,
    ConditionsResponse,
    ConditionUpdate,
)
from ycli.yandex.models import Ack

SID = "6818ceffe010db4f59d11329"
QID = "17"
PID = 3
CID = 5
GROUP = {
    "id": CID,
    "operator": "and",
    "items": [{"type": "question", "condition": "eq", "question": "q1", "value": "yes"}],
}
ENVELOPE = {"operator": "and", "items": [GROUP]}
WIRE_BODY = {
    "operator": "and",
    "items": [{"type": "question", "condition": "eq", "question": "q1", "value": "yes"}],
}

FAMILIES = [
    ("question", f"surveys/{SID}/questions/{QID}/conditions", (SID, QID)),
    ("page", f"surveys/{SID}/pages/{PID}/conditions", (SID, PID)),
    ("submit", f"surveys/{SID}/conditions", (SID,)),
]
DELETE_DETAIL = {
    "question": f"deleted condition {CID} from question {QID}",
    "page": f"deleted condition {CID} from page {PID}",
    "submit": f"deleted condition {CID} from survey {SID}",
}


def _client() -> ConditionsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return ConditionsClient(session=s)


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
def test_list_returns_envelope(family, path, ancestors):
    responses.add(responses.GET, f"{BASE}/{path}", json=ENVELOPE, status=200)
    out = getattr(_client(), f"{family}_list")(*ancestors)
    assert isinstance(out, ConditionsResponse)
    assert out.operator == "and" and out.items[0].id == CID
    assert responses.calls[0].request.url == f"{BASE}/{path}"


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
def test_get_returns_single_group(family, path, ancestors):
    responses.add(responses.GET, f"{BASE}/{path}/{CID}", json=GROUP, status=200)
    out = getattr(_client(), f"{family}_get")(*ancestors, CID)
    assert isinstance(out, Condition)
    assert out.id == CID and out.items[0].question == "q1"
    assert responses.calls[0].request.url == f"{BASE}/{path}/{CID}"


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
def test_create_posts_typed_body(family, path, ancestors):
    responses.add(responses.POST, f"{BASE}/{path}", json=GROUP, status=200)
    body = ConditionCreate(
        operator="and",
        items=[ConditionItemWrite(type="question", condition="eq", question="q1", value="yes")],
    )
    out = getattr(_client(), f"{family}_create")(*ancestors, body)
    assert isinstance(out, Condition) and out.id == CID
    assert json.loads(responses.calls[0].request.body) == WIRE_BODY  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
def test_modify_patches_full_group(family, path, ancestors):
    responses.add(responses.PATCH, f"{BASE}/{path}/{CID}", json=GROUP, status=200)
    body = ConditionUpdate(
        operator="and",
        items=[ConditionItemWrite(type="question", condition="eq", question="q1", value="yes")],
    )
    out = getattr(_client(), f"{family}_modify")(*ancestors, CID, body)
    assert isinstance(out, Condition)
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == WIRE_BODY  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
def test_delete_returns_ack_on_bodyless_200(family, path, ancestors):
    responses.add(responses.DELETE, f"{BASE}/{path}/{CID}", status=200)
    out = getattr(_client(), f"{family}_delete")(*ancestors, CID)
    assert isinstance(out, Ack) and out.ok is True
    assert out.detail == DELETE_DETAIL[family]
    assert responses.calls[0].request.method == "DELETE"


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
def test_set_operator_patches_collection_and_returns_envelope(family, path, ancestors):
    responses.add(responses.PATCH, f"{BASE}/{path}", json=ENVELOPE, status=200)
    out = getattr(_client(), f"{family}_set_operator")(*ancestors, "or")
    assert isinstance(out, ConditionsResponse) and out.items[0].id == CID
    assert responses.calls[0].request.url == f"{BASE}/{path}"
    assert json.loads(responses.calls[0].request.body) == {"operator": "or"}  # ty: ignore[invalid-argument-type]
