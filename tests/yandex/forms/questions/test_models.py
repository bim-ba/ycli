"""TDD for Forms questions models — Question parses list items and the single-get payload."""

from ycli.yandex.forms.questions.models import Page, Question, QuestionsResponse


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
