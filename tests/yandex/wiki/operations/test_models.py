"""Model behaviour for operations — terminal predicate + result parsing across both statuses."""

import pytest

from ycli.yandex.wiki.operations.models import (
    CloneOperationStatus,
    GridCloneOperationStatus,
    OperationProgress,
    PageCloneResult,
    PageSchema,
)


@pytest.mark.parametrize(
    ("status", "terminal"),
    [("scheduled", False), ("in_progress", False), ("success", True), ("failed", True)],
)
def test_clone_status_is_terminal(status, terminal):
    assert CloneOperationStatus(status=status).is_terminal is terminal


@pytest.mark.parametrize(
    ("status", "terminal"),
    [("scheduled", False), ("success", True), ("failed", True)],
)
def test_gridclone_status_is_terminal(status, terminal):
    assert GridCloneOperationStatus(status=status).is_terminal is terminal


def test_clone_status_none_is_not_terminal():
    assert CloneOperationStatus().is_terminal is False


def test_page_clone_result_parses_page():
    result = PageCloneResult(page=PageSchema(id=1, slug="data/y"))
    assert result.page is not None and result.page.slug == "data/y"


def test_gridclone_result_parses_grid_id():
    out = GridCloneOperationStatus.model_validate(
        {"status": "success", "result": {"grid_id": "g2", "page": {"id": 1, "slug": "data/y"}}}
    )
    assert out.result is not None and out.result.grid_id == "g2"
    assert out.result.page is not None and out.result.page.id == 1


def test_operation_progress_fields():
    progress = OperationProgress(percentage=0.25, details="copying")
    assert progress.percentage == 0.25 and progress.details == "copying"
