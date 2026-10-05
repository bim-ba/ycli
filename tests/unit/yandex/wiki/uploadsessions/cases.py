"""Contract cases for Wiki ``/upload_sessions`` (see tests/contract/)."""

import base64
from pathlib import Path

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.wiki.uploadsessions.models import UploadSessionCreate

PART = Path(__file__).with_name("part3.bin")
DATA = PART.read_bytes()
SID = "9c8b7a6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d"


def _session(status: str) -> dict[str, object]:
    return {"session_id": SID, "file_name": "report.xlsx", "file_size": 7340032, "status": status}


CASES = [
    Case(
        "wiki.uploadsessions.create",
        args=(UploadSessionCreate(file_name="report.xlsx", file_size=7340032),),
        cli=[
            "wiki",
            "uploadsessions",
            "create",
            "--file-name",
            "report.xlsx",
            "--file-size",
            "7340032",
        ],
        mcp=(
            "wiki_uploadsessions_create",
            {"body": {"file_name": "report.xlsx", "file_size": 7340032}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "upload_sessions",
                    json={"file_name": "report.xlsx", "file_size": 7340032},
                ),
                Reply(json=_session("not_started")),
            )
        ],
    ),
    Case(
        "wiki.uploadsessions.get",
        args=(SID,),
        cli=["wiki", "uploadsessions", "get", SID],
        mcp=("wiki_uploadsessions_get", {"session_id": SID}),
        exchanges=[(Sent("GET", f"upload_sessions/{SID}"), Reply(json=_session("in_progress")))],
    ),
    Case(
        "wiki.uploadsessions.parts_upload",
        args=(SID,),
        kwargs={"part_number": 3, "data": DATA},
        cli=["wiki", "uploadsessions", "parts-upload", SID, str(PART), "--part-number", "3"],
        mcp=(
            "wiki_uploadsessions_parts_upload",
            {"session_id": SID, "part_number": 3, "data": base64.b64encode(DATA).decode()},
        ),
        exchanges=[
            (
                Sent(
                    "PUT",
                    f"upload_sessions/{SID}/upload_part",
                    {"part_number": "3"},
                    content=DATA,
                    headers={"Content-Type": "application/octet-stream"},
                ),
                Reply(json=_session("in_progress")),
            )
        ],
    ),
    Case(
        "wiki.uploadsessions.parts_upload",
        args=(SID,),
        kwargs={"part_number": 1, "data": DATA},
        cli=["wiki", "uploadsessions", "parts-upload", SID, str(PART), "--part-number", "1"],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "PUT",
                    f"upload_sessions/{SID}/upload_part",
                    {"part_number": "1"},
                    content=DATA,
                    headers={"Content-Type": "application/octet-stream"},
                ),
                Reply(json=_session("in_progress")),
            )
        ],
    ),
    Case(
        "wiki.uploadsessions.finish",
        args=(SID,),
        cli=["wiki", "uploadsessions", "finish", SID],
        mcp=("wiki_uploadsessions_finish", {"session_id": SID}),
        exchanges=[
            (Sent("POST", f"upload_sessions/{SID}/finish"), Reply(json=_session("finished")))
        ],
    ),
    Case(
        "wiki.uploadsessions.abort",
        args=(SID,),
        cli=["wiki", "uploadsessions", "abort", SID],
        mcp=("wiki_uploadsessions_abort", {"session_id": SID}),
        exchanges=[(Sent("POST", f"upload_sessions/{SID}/abort"), Reply(json=_session("aborted")))],
        effect=Effect.DESTRUCTIVE,
    ),
    Case(
        "wiki.uploadsessions.abort_all",
        cli=["wiki", "uploadsessions", "abort-all"],
        mcp=("wiki_uploadsessions_abort_all", {}),
        exchanges=[
            (Sent("POST", "upload_sessions/abort_active_uploads"), Reply(json={"status": "ok"}))
        ],
        effect=Effect.DESTRUCTIVE,
    ),
]
