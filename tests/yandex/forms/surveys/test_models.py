"""TDD for Forms surveys write models (SurveyCreate/Update/Texts/ActionResult)."""

from ycli.yandex.forms.surveys.models import (
    SurveyActionResult,
    SurveyCreate,
    SurveyTexts,
    SurveyUpdate,
)


def test_survey_create_drops_unset_fields_on_dump():
    body = SurveyCreate(name="Onboarding", need_auth=True).model_dump(exclude_none=True)
    assert body == {"name": "Onboarding", "need_auth": True}  # is_public/max_count/... omitted


def test_survey_create_coerces_texts_from_dict():
    payload = SurveyCreate(
        name="F",
        texts={"submit": "Send", "title": "Thanks"},  # ty: ignore[invalid-argument-type]
    )
    assert isinstance(payload.texts, SurveyTexts)
    assert payload.texts.submit == "Send"
    assert payload.model_dump(exclude_none=True) == {
        "name": "F",
        "texts": {"submit": "Send", "title": "Thanks"},
    }


def test_survey_update_is_a_partial_body():
    body = SurveyUpdate(is_published=False).model_dump(exclude_none=True)
    assert body == {"is_published": False}  # PATCH sends only what was set
    assert issubclass(SurveyUpdate, SurveyCreate)


def test_survey_action_result_defaults_ok_true():
    result = SurveyActionResult(survey_id="686d", action="publish")
    assert result.survey_id == "686d" and result.action == "publish" and result.ok is True
