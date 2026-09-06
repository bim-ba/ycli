"""TDD for Forms questions models — read Question + the 12-type write discriminated union."""

import pytest
from pydantic import ValidationError

from ycli.yandex.forms.questions.models import (
    BooleanQuestion,
    CommentQuestion,
    DateQuestion,
    DateRangeQuestion,
    EnumQuestion,
    FileQuestion,
    IntegerQuestion,
    MatrixQuestion,
    Page,
    PaymentQuestion,
    Question,
    QuestionCreateAdapter,
    QuestionMove,
    QuestionsResponse,
    QuestionValidator,
    SeriesQuestion,
    StringQuestion,
    SuggestQuestion,
)

# The 12 discriminated-union members keyed by their ``type`` tag.
TWELVE_TYPES = {
    "string": StringQuestion,
    "boolean": BooleanQuestion,
    "integer": IntegerQuestion,
    "file": FileQuestion,
    "comment": CommentQuestion,
    "date": DateQuestion,
    "daterange": DateRangeQuestion,
    "payment": PaymentQuestion,
    "enum": EnumQuestion,
    "suggest": SuggestQuestion,
    "matrix": MatrixQuestion,
    "series": SeriesQuestion,
}


def test_question_parses_extended_get_fields():
    q = Question.model_validate(
        {
            "id": 5,
            "label": "L",
            "slug": "s",
            "type": "integer",
            "comment": "hint",
            "hidden": False,
            "placeholder": "p",
            "initial": 0,
            "multiline": False,
            "has_quiz": True,
            "validators": [{"type": "required"}],  # type-specific detail is lenient-ignored
        }
    )
    assert q.id == 5 and q.slug == "s" and q.comment == "hint"
    assert q.placeholder == "p" and q.initial == 0 and q.has_quiz is True


def test_question_initial_is_polymorphic():
    q = Question.model_validate({"id": 1, "type": "enum", "initial": [{"id": 1, "label": "A"}]})
    assert q.initial == [{"id": 1, "label": "A"}]


def test_questions_response_still_parses_pages():
    resp = QuestionsResponse.model_validate({"pages": [{"id": 1, "items": [{"id": 9}]}]})
    assert isinstance(resp.pages[0], Page)
    assert resp.pages[0].items[0].id == 9


@pytest.mark.parametrize(("tag", "cls"), TWELVE_TYPES.items())
def test_discriminator_routes_each_of_the_12_types(tag, cls):
    """Every ``type`` tag validates and the union routes it to the matching class."""
    obj = QuestionCreateAdapter.validate_python({"type": tag, "label": "L"})
    assert isinstance(obj, cls)
    assert obj.type == tag and obj.label == "L"


def test_unknown_type_is_rejected():
    with pytest.raises(ValidationError):
        QuestionCreateAdapter.validate_python({"type": "bogus", "label": "x"})


def test_missing_type_is_rejected():
    with pytest.raises(ValidationError):
        QuestionCreateAdapter.validate_python({"label": "x"})


def test_string_question_carries_typed_validators_and_quiz():
    q = QuestionCreateAdapter.validate_python(
        {
            "type": "string",
            "label": "Email",
            "multiline": False,
            "validators": [{"type": "required"}, {"type": "email"}, {"type": "min", "value": 3}],
            "has_quiz": True,
            "quiz_items": [{"label": "ok", "correct": True, "scores": 1.0}],
        }
    )
    assert isinstance(q, StringQuestion)
    assert [v.type for v in q.validators] == ["required", "email", "min"]
    assert q.validators[2].value == 3
    assert q.quiz_items[0].correct is True


def test_enum_question_models_items_widget_and_choices():
    q = QuestionCreateAdapter.validate_python(
        {
            "type": "enum",
            "label": "Pick",
            "widget": "checkbox",
            "modify_choices": "shuffle",
            "items": [
                {"slug": "a", "label": "A", "correct": True, "scores": 0.5},
                {"slug": "b", "label": "B"},
            ],
        }
    )
    assert isinstance(q, EnumQuestion)
    assert q.widget == "checkbox" and q.modify_choices == "shuffle"
    assert [i.slug for i in q.items] == ["a", "b"] and q.items[0].correct is True


def test_enum_rejects_invalid_widget():
    with pytest.raises(ValidationError):
        QuestionCreateAdapter.validate_python({"type": "enum", "widget": "slider"})


def test_matrix_question_models_rows_and_columns():
    q = QuestionCreateAdapter.validate_python(
        {
            "type": "matrix",
            "label": "Grid",
            "rows": [{"slug": "r1", "label": "Row 1"}],
            "columns": [{"slug": "c1", "label": "Col 1"}],
        }
    )
    assert isinstance(q, MatrixQuestion)
    assert q.rows[0].label == "Row 1" and q.columns[0].slug == "c1"


def test_suggest_question_models_data_source():
    q = QuestionCreateAdapter.validate_python(
        {
            "type": "suggest",
            "label": "Dept",
            "multichoice": True,
            "data_source": {"name": "departments", "params": [{"type": "org", "value": "1"}]},
        }
    )
    assert isinstance(q, SuggestQuestion)
    assert q.multichoice is True and q.data_source.name == "departments"
    assert q.data_source.params[0].value == "1"


def test_payment_question_models_wallet_and_amount():
    q = QuestionCreateAdapter.validate_python(
        {"type": "payment", "label": "Pay", "account_id": "410011", "fixed": False, "initial": 100}
    )
    assert isinstance(q, PaymentQuestion)
    assert q.account_id == "410011" and q.fixed is False and q.initial == 100


def test_series_question_nests_typed_questions():
    q = QuestionCreateAdapter.validate_python(
        {
            "type": "series",
            "label": "People",
            "items": [
                {"type": "string", "label": "Name"},
                {"type": "integer", "label": "Age"},
            ],
        }
    )
    assert isinstance(q, SeriesQuestion)
    assert isinstance(q.items[0], StringQuestion)
    assert isinstance(q.items[1], IntegerQuestion)


def test_image_and_hidden_are_shared_and_conditions_key_is_dropped():
    q = QuestionCreateAdapter.validate_python(
        {
            "type": "string",
            "label": "Q",
            "hidden": True,
            "image": {"id": 7, "name": "cover.png"},
            "conditions": [
                {
                    "operator": "and",
                    "items": [
                        {"type": "question", "condition": "eq", "question": "q1", "value": "yes"}
                    ],
                }
            ],
        }
    )
    assert q.hidden is True and q.image.id == 7
    assert "conditions" not in type(q).model_fields


def test_dump_by_alias_exclude_none_is_a_clean_request_body():
    q = StringQuestion(
        label="Name", multiline=True, validators=[QuestionValidator(type="required")]
    )
    assert q.model_dump(by_alias=True, exclude_none=True) == {
        "label": "Name",
        "type": "string",
        "multiline": True,
        "validators": [{"type": "required"}],
    }


def test_daterange_and_comment_and_file_smoke():
    dr = QuestionCreateAdapter.validate_python({"type": "daterange", "label": "Period"})
    cm = QuestionCreateAdapter.validate_python({"type": "comment", "label": "H", "header": True})
    fl = QuestionCreateAdapter.validate_python(
        {"type": "file", "label": "F", "validators": [{"type": "size", "value": 20}]}
    )
    assert isinstance(dr, DateRangeQuestion)
    assert isinstance(cm, CommentQuestion) and cm.header is True
    assert isinstance(fl, FileQuestion) and fl.validators[0].value == 20


def test_question_move_body_is_typed():
    mv = QuestionMove(page=2, position=1, create_page=True, question="17")
    assert mv.model_dump(by_alias=True, exclude_none=True) == {
        "page": 2,
        "position": 1,
        "create_page": True,
        "question": "17",
    }


def test_question_move_bare_position_raises():
    """A position with no page target is a silent no-op live (200, nothing moves) — the model
    now raises instead of silently defaulting ``page`` to 1 (owner decision; see the CLI ``move``
    command, which sets the visible default before constructing this model)."""
    with pytest.raises(ValidationError, match="question move needs a target"):
        QuestionMove(position=1)


def test_question_move_keeps_explicit_targets():
    """Any explicit target (page / page_id / create_page / question) satisfies the requirement."""
    assert QuestionMove(position=1, page=3).page == 3
    assert QuestionMove(position=1, page_id=9).page is None
    assert QuestionMove(position=1, create_page=True).page is None
    assert QuestionMove(position=1, question="17").page is None
    assert QuestionMove(page=2).model_dump(exclude_none=True) == {"page": 2}  # no position → as-is
