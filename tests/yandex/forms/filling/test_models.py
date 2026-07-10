"""TDD for Forms filling models (FillableForm / SubmitBody / SubmitResult / Suggestion)."""

from ycli.yandex.forms.filling.models import (
    FillableForm,
    SubmitBody,
    SubmitResult,
    Suggestion,
    SuggestionList,
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
        {"id": "686d", "answer_id": 99, "scores": 1.5, "integrations": [{"id": 1, "type": "email"}]}
    )
    assert out.answer_id == 99 and out.scores == 1.5
    assert out.integrations[0]["type"] == "email"


def test_suggestion_preserves_layer_extras():
    s = Suggestion.model_validate(
        {"layer": "dir_user", "id": "1", "text": "Ann", "login": "ann", "email": "a@x"}
    )
    dumped = s.model_dump()
    assert dumped["login"] == "ann" and dumped["email"] == "a@x"


def test_suggestion_list_is_flat_root():
    sl = SuggestionList.model_validate([{"layer": "gender", "id": "m", "text": "Male"}])
    assert sl.root[0].text == "Male"
