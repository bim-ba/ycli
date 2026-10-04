"""TDD for Forms filling models (FillableForm / SubmitBody / SubmitResult / Suggestion)."""

from ycli.yandex.forms.filling.models import (
    FillableForm,
    SubmitBody,
    SubmitQuizResult,
    SubmitResult,
    Suggestion,
)


def test_fillable_form_defaults_and_nested_texts():
    form = FillableForm.model_validate({"id": "686d", "texts": {"submit": "Go"}})
    assert form.pages == [] and form.values == {} and form.conditions == []
    assert form.texts is not None and form.texts.submit == "Go"


def test_submit_body_is_flexible_slug_map():
    body = SubmitBody.model_validate({"q1": "a", "q2": [1, 2], "q3": False})
    assert body.model_dump() == {"q1": "a", "q2": [1, 2], "q3": False}


def test_submit_result_typed_scalars():
    out = SubmitResult.model_validate(
        {
            "id": "686d",
            "answer_id": 99,
            # As the API sends it: the numbers of a quiz result arrive as strings.
            "quiz_result": {
                "show_format": "score_with_total",
                "scores": "1.5",
                "total_scores": "2",
            },
            "integrations": [{"id": 1, "type": "email"}],
        }
    )
    assert out.answer_id == 99
    assert out.quiz_result == SubmitQuizResult(
        show_format="score_with_total", scores=1.5, total_scores=2
    )
    assert out.integrations[0]["type"] == "email"


def test_suggestion_preserves_layer_extras():
    s = Suggestion.model_validate(
        {"layer": "dir_user", "id": "1", "text": "Ann", "login": "ann", "email": "a@x"}
    )
    dumped = s.model_dump()
    assert dumped["login"] == "ann" and dumped["email"] == "a@x"
