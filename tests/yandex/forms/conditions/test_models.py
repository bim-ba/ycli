"""TDD for Forms display-conditions models (semantic envelope + strict write bodies)."""

import pytest
from pydantic import ValidationError

from ycli.yandex.forms.conditions.models import (
    ConditionCreate,
    ConditionItemWrite,
    ConditionsResponse,
    ConditionUpdate,
)
from ycli.yandex.forms.questions.models import ConditionItem

CID = 5
GROUP = {
    "id": CID,
    "operator": "and",
    "items": [{"type": "question", "condition": "eq", "question": "q1", "value": "yes"}],
}
ENVELOPE = {"operator": "and", "items": [GROUP]}


def test_condition_item_read_accepts_quiz():
    item = ConditionItem.model_validate({"type": "quiz", "condition": "eq", "value": "5"})
    assert item.type == "quiz"


def test_conditions_response_parses_envelope():
    out = ConditionsResponse.model_validate(ENVELOPE)
    assert out.operator == "and"
    assert out.items[0].id == CID
    group_items = out.items[0].items
    assert group_items is not None
    assert group_items[0].question == "q1"


def test_conditions_response_defaults():
    out = ConditionsResponse.model_validate({})
    assert out.operator is None and out.items == []


def test_condition_item_write_requires_type_and_condition():
    with pytest.raises(ValidationError):
        ConditionItemWrite.model_validate({})


def test_condition_item_write_caps_value_at_100():
    ok = ConditionItemWrite(type="question", condition="eq", value="x" * 100)
    assert ok.value == "x" * 100
    with pytest.raises(ValidationError):
        ConditionItemWrite(type="question", condition="eq", value="x" * 101)


def test_condition_create_requires_operator_and_nonempty_items():
    with pytest.raises(ValidationError):
        ConditionCreate(operator="and", items=[])
    with pytest.raises(ValidationError):
        ConditionCreate.model_validate({"items": [{"type": "language", "condition": "eq"}]})


def test_condition_create_dump_drops_unset_clause_fields():
    body = ConditionCreate(
        operator="and", items=[ConditionItemWrite(type="language", condition="eq")]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {"operator": "and", "items": [{"type": "language", "condition": "eq"}]}


def test_condition_update_subclasses_create():
    assert issubclass(ConditionUpdate, ConditionCreate)
