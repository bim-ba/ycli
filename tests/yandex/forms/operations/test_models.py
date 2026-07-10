"""TDD for Forms operations models — OperationResult status flags."""

from ycli.yandex.forms.operations.models import OperationResult


def test_operation_result_ok_is_terminal_and_ready():
    op = OperationResult.model_validate({"id": "op-1", "status": "ok", "message": "done"})
    assert op.id == "op-1" and op.message == "done"
    assert op.is_terminal is True and op.is_ready is True


def test_operation_result_fail_is_terminal_not_ready():
    op = OperationResult.model_validate({"id": "op-1", "status": "fail"})
    assert op.is_terminal is True and op.is_ready is False


def test_operation_result_wait_is_not_terminal():
    op = OperationResult.model_validate({"id": "op-1", "status": "wait"})
    assert op.is_terminal is False and op.is_ready is False


def test_operation_result_empty_is_all_none():
    op = OperationResult.model_validate({})
    assert op.id is None and op.status is None
    assert op.is_terminal is False and op.is_ready is False
