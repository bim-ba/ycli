"""Model tests for the Wiki /upload_sessions resource."""

from ycli.yandex.wiki.uploadsessions.models import (
    AbortActiveUploadsResult,
    UploadSession,
    UploadSessionCreate,
    UploadSessionUser,
)


def test_upload_session_parses_full_payload():
    session = UploadSession.model_validate(
        {
            "session_id": "s-1",
            "file_name": "d.png",
            "file_size": 2048,
            "status": "not_started",
            "user": {
                "id": 1,
                "identity": {"uid": "42", "cloud_uid": "c"},
                "username": "j",
                "display_name": "Jane",
                "is_dismissed": False,
                "affiliation": "org",
            },
            "created_at": "2025-01-01T00:00:00Z",
            "finished_at": "2025-01-01T00:01:00Z",
            "storage_type": "mds",
        }
    )
    assert session.session_id == "s-1"
    assert session.file_size == 2048
    assert isinstance(session.user, UploadSessionUser)
    assert session.user.identity is not None and session.user.identity.uid == "42"
    assert session.storage_type == "mds"


def test_upload_session_ignores_unknown_fields():
    session = UploadSession.model_validate({"session_id": "s-1", "surprise": "value"})
    assert session.session_id == "s-1"
    assert not hasattr(session, "surprise")


def test_upload_session_create_dumps_body():
    body = UploadSessionCreate(file_name="d.png", file_size=2048)
    assert body.model_dump(by_alias=True, exclude_none=True) == {
        "file_name": "d.png",
        "file_size": 2048,
    }


def test_abort_active_uploads_result_defaults_ok():
    assert AbortActiveUploadsResult().status == "ok"
    assert AbortActiveUploadsResult.model_validate({"status": "ok"}).status == "ok"
