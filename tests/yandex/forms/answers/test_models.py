"""TDD for Forms answers models — export body + result flags parse cleanly."""

from ycli.yandex.forms.answers.models import AnswerExport, ExportResult


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
