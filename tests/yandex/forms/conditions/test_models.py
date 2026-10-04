"""TDD for Forms display-conditions models (semantic envelope + strict write bodies)."""

import pytest
from pydantic import ValidationError

from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionItemWrite, ConditionUpdate
from ycli.yandex.forms.models import ConditionItem, ConditionsResponse

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


def test_condition_item_write_keeps_a_value_of_any_length():
    item = ConditionItemWrite(type="question", condition="eq", value="x" * 101)
    assert item.value == "x" * 101


def test_condition_create_requires_operator_and_items():
    with pytest.raises(ValidationError) as no_operator:
        ConditionCreate.model_validate({"items": [{"type": "language", "condition": "eq"}]})
    assert [(e["type"], e["loc"]) for e in no_operator.value.errors()] == [
        ("missing", ("operator",))
    ]
    with pytest.raises(ValidationError) as no_items:
        ConditionCreate.model_validate({"operator": "and"})
    assert [(e["type"], e["loc"]) for e in no_items.value.errors()] == [("missing", ("items",))]


def test_condition_create_keeps_an_empty_list_of_items():
    body = ConditionCreate(operator="and", items=[]).model_dump(by_alias=True, exclude_none=True)
    assert body == {"operator": "and", "items": []}


def test_condition_create_dump_drops_unset_clause_fields():
    body = ConditionCreate(
        operator="and", items=[ConditionItemWrite(type="language", condition="eq")]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {"operator": "and", "items": [{"type": "language", "condition": "eq"}]}


def test_condition_update_subclasses_create():
    assert issubclass(ConditionUpdate, ConditionCreate)
