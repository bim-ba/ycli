"""TDD for Forms answers models — AnswerDetail + nested out-models parse cleanly."""

from ycli.yandex.forms.answers.models import (
    AnswerDetail,
    AnswerExport,
    AnswerQuestionOut,
    AnswerQuizOut,
    AnswerSurveyOut,
    ExportResult,
    ImageOut,
)


def test_answer_detail_parses_full_payload():
    ad = AnswerDetail.model_validate(
        {
            "id": 7,
            "created": "2026-01-01",
            "survey": {"id": "abc", "name": "F"},
            "quiz": {
                "scores": 1.5,
                "total": 3.0,
                "questions": 2,
                "title": "Result",
                "subtitle": "sub",
                "image": {
                    "id": 1,
                    "links": {"orig": "https://e"},
                    "name": "i.png",
                    "check_status": "ready",
                },
                "show_results": True,
            },
            "data": [
                {"id": "q1", "label": "Name", "type": "string", "value": "Ann", "scores": 0.5},
                {
                    "id": "q2",
                    "label": "Pick",
                    "type": "radio",
                    "widget": "radio",
                    "multichoice": True,
                    "items": [{"id": "o1", "label": "A", "scores": 1}],
                    "value": [{"id": "o1", "label": "A"}],
                },
            ],
        }
    )
    assert ad.id == 7 and ad.created == "2026-01-01"
    assert isinstance(ad.survey, AnswerSurveyOut) and ad.survey.id == "abc"
    assert isinstance(ad.quiz, AnswerQuizOut)
    assert isinstance(ad.quiz.image, ImageOut) and ad.quiz.image.check_status == "ready"
    assert ad.quiz.image.links == {"orig": "https://e"}
    assert ad.data[0].value == "Ann" and ad.data[0].scores == 0.5
    assert ad.data[1].multichoice is True and ad.data[1].value == [{"id": "o1", "label": "A"}]


def test_answer_detail_minimal_omits_optionals():
    ad = AnswerDetail.model_validate({"id": 1})
    assert ad.survey is None and ad.quiz is None and ad.data == []


def test_image_out_defaults_are_lenient():
    img = ImageOut.model_validate({})
    assert img.id is None and img.links == {} and img.check_status is None


def test_answer_question_out_value_is_polymorphic():
    q = AnswerQuestionOut.model_validate(
        {"id": "q", "type": "file", "value": [{"name": "a", "path": "p"}]}
    )
    assert q.value == [{"name": "a", "path": "p"}]
    assert q.items is None  # unset polymorphic field stays None


def test_answer_export_body_drops_unset_fields():
    body = AnswerExport(format="csv", limit=10, columns=["q1"]).model_dump(exclude_none=True)
    assert body == {"format": "csv", "limit": 10, "columns": ["q1"]}


def test_answer_export_empty_body_is_empty():
    assert AnswerExport().model_dump(exclude_none=True) == {}


def test_export_result_status_flags():
    assert ExportResult.model_validate({"id": "o", "status": "ok"}).is_ready is True
    assert ExportResult.model_validate({"id": "o", "status": "ok"}).is_terminal is True
    assert ExportResult.model_validate({"id": "o", "status": "fail"}).is_terminal is True
    assert ExportResult.model_validate({"id": "o", "status": "fail"}).is_ready is False
    assert ExportResult.model_validate({"id": "o", "status": "wait"}).is_terminal is False
    assert ExportResult.model_validate({}).is_ready is False
