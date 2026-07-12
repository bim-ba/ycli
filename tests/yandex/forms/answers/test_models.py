"""TDD for Forms answers models — single-answer details + export body + result flags."""

from ycli.yandex.forms.answers.models import AnswerDetails, AnswerExport, ExportResult


def test_answer_details_parses_full_answer():
    details = AnswerDetails.model_validate(
        {
            "id": 2469549806,
            "created": "2026-07-12T10:00:00Z",
            "survey": {"id": "6818ceff", "name": "Feedback"},
            "quiz": {"scores": 0.5, "total": 1.0},
            "data": [{"id": "1", "label": "Q1", "type": "string", "value": "x"}],
        }
    )
    assert details.id == 2469549806
    assert details.survey is not None
    assert details.survey.id == "6818ceff" and details.survey.name == "Feedback"
    assert details.quiz == {"scores": 0.5, "total": 1.0}  # passed through verbatim
    assert details.data[0]["value"] == "x"  # self-describing record, verbatim


def test_answer_details_defaults_are_lenient():
    details = AnswerDetails.model_validate({})
    assert details.id is None and details.survey is None
    assert details.quiz is None and details.data == []


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
