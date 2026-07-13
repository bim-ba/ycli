"""TDD for Tracker import bodies — createdAt/createdBy preserved via serialization aliases."""

from ycli.yandex.tracker.import_.models import (
    ImportComment,
    ImportLink,
    ImportTask,
    ImportWorklog,
)


def test_import_task_preserves_created_fields():
    body = ImportTask(  # ty: ignore[missing-argument]
        queue="TEST",
        summary="Test",
        created_at="2017-08-29T12:34:41.740+0000",  # ty: ignore[unknown-argument]
        created_by="11",  # ty: ignore[unknown-argument]
        key="TEST-1",
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "queue": "TEST",
        "summary": "Test",
        "createdAt": "2017-08-29T12:34:41.740+0000",
        "createdBy": "11",
        "key": "TEST-1",
    }


def test_import_task_omits_absent_optionals():
    body = ImportTask(  # ty: ignore[missing-argument]
        queue="Q",
        summary="S",
        created_at="t",  # ty: ignore[unknown-argument]
        created_by="u",  # ty: ignore[unknown-argument]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {"queue": "Q", "summary": "S", "createdAt": "t", "createdBy": "u"}


def test_import_comment_body():
    body = ImportComment(  # ty: ignore[missing-argument]
        text="Test",
        created_at="2017-08-29T12:34:41.740+0000",  # ty: ignore[unknown-argument]
        created_by="11",  # ty: ignore[unknown-argument]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "text": "Test",
        "createdAt": "2017-08-29T12:34:41.740+0000",
        "createdBy": "11",
    }


def test_import_link_body():
    body = ImportLink(  # ty: ignore[missing-argument]
        relationship="relates",
        issue="TEST-2",
        created_at="2017-08-29T12:34:41.740+0000",  # ty: ignore[unknown-argument]
        created_by="11",  # ty: ignore[unknown-argument]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "relationship": "relates",
        "issue": "TEST-2",
        "createdAt": "2017-08-29T12:34:41.740+0000",
        "createdBy": "11",
    }


def test_import_worklog_body_uses_plural_fields():
    body = ImportWorklog(  # ty: ignore[missing-argument]
        duration="PT1H",
        created_at="2025-02-18T16:35:41.740+0000",  # ty: ignore[unknown-argument]
        created_by="username",  # ty: ignore[unknown-argument]
        start="2025-02-18T16:35:41.740+0000",
        comment="my comment",
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "duration": "PT1H",
        "createdAt": "2025-02-18T16:35:41.740+0000",
        "createdBy": "username",
        "start": "2025-02-18T16:35:41.740+0000",
        "comment": "my comment",
    }
