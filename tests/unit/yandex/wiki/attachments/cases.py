"""Contract cases for Wiki ``/pages/{id}/attachments`` (see tests/contract/)."""

import base64
from pathlib import Path

from tests.contract import Case, Reply, Sent, Sibling

FILE = Path(__file__).with_name("diagram.txt")
DATA = FILE.read_bytes()
ATTACHMENT = {"id": 5611, "name": "spec.pdf", "size": "2048", "mimetype": "application/pdf"}
SESSION = "3f2b1a0c-5d4e-4f6a-8b9c-0d1e2f3a4b5c"

DETAILS = {
    "id": 5621,
    "name": "photo.png",
    "is_downloadable": True,
    "download_url": "/eng/specs/.files/photo.png",
    "size": "1.50",
    "description": "team photo",
    "user": {"id": 8104, "username": "vera", "display_name": "Vera"},
    "created_at": "2026-10-02T18:34:14.606Z",
    "mimetype": "image/png",
    "has_preview": True,
    "check_status": "ready",
}

CASES = [
    Case(
        "wiki.attachments.list",
        args=(5601,),
        kwargs={"limit": 20},
        cli=["wiki", "attachments", "list", "5601", "--limit", "20"],
        mcp=("wiki_attachments_list", {"page_id": 5601, "limit": 20}),
        exchanges=[
            (
                Sent("GET", "pages/5601/attachments", {"page_size": "100"}),
                Reply(json={"results": [ATTACHMENT], "next_cursor": "ac-2"}),
            ),
            (
                Sent("GET", "pages/5601/attachments", {"page_size": "100", "cursor": "ac-2"}),
                Reply(json={"results": [{"id": 5612, "name": "logo.png"}], "next_cursor": None}),
            ),
        ],
    ),
    Case(
        "wiki.attachments.list",
        args=(5602,),
        cli=["wiki", "attachments", "list", "5602", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/5602/attachments", {"page_size": "100"}),
                Reply(json={"results": [ATTACHMENT]}),
            )
        ],
    ),
    # GET …/attachments/{file_id} and …/preview (undocumented).
    Case(
        "wiki.attachments.get",
        args=(5607, 5621),
        cli=["wiki", "attachments", "get", "5607", "5621"],
        mcp=("wiki_attachments_get", {"page_id": 5607, "file_id": 5621}),
        exchanges=[(Sent("GET", "pages/5607/attachments/5621"), Reply(json=DETAILS))],
    ),
    Case(
        "wiki.attachments.previews_download",
        args=(5608, 5622),
        cli=["wiki", "attachments", "previews-download", "5608", "5622"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/5608/attachments/5622/preview"),
                Reply(content=b"\x89PNG preview bytes"),
            )
        ],
    ),
    Case(
        "wiki.attachments.download",
        args=(5603, 5613),
        cli=["wiki", "attachments", "download", "5603", "5613"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/5603/attachments/5613/download"),
                Reply(content=b"%PDF-1.7 spec"),
            )
        ],
    ),
    Case(
        "wiki.attachments.download_by_url",
        args=("eng/specs/.files/spec.pdf",),
        cli=["wiki", "attachments", "download-by-url", "eng/specs/.files/spec.pdf"],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "GET",
                    "pages/attachments/download_by_url",
                    {"url": "eng/specs/.files/spec.pdf", "download": "true"},
                ),
                Reply(content=b"%PDF-1.7 by url"),
            )
        ],
    ),
    Case(
        "wiki.attachments.delete",
        args=(5604, 5614),
        cli=["wiki", "attachments", "delete", "5604", "5614"],
        mcp=("wiki_attachments_delete", {"page_id": 5604, "file_id": 5614}),
        exchanges=[(Sent("DELETE", "pages/5604/attachments/5614"), Reply(status=204))],
    ),
    Case(
        "wiki.attachments.attach",
        args=(5605, ["s-5605-a", "s-5605-b"]),
        cli=[
            "wiki",
            "attachments",
            "attach",
            "5605",
            "--session-ids",
            "s-5605-a",
            "--session-ids",
            "s-5605-b",
        ],
        mcp=(
            "wiki_attachments_attach",
            {"page_id": 5605, "session_ids": ["s-5605-a", "s-5605-b"]},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/5605/attachments",
                    json={"upload_sessions": ["s-5605-a", "s-5605-b"]},
                ),
                Reply(json={"results": [ATTACHMENT, {"id": 5615, "name": "b.png"}]}),
            )
        ],
    ),
    Case(
        "wiki.attachments.upload",
        output=[
            {
                "id": 5616,
                "name": "diagram.txt",
                "is_downloadable": None,
                "download_url": None,
                "size": None,
                "description": None,
                "user": None,
                "mimetype": None,
                "has_preview": None,
                "check_status": None,
                "created_at": None,
            }
        ],
        args=(Sibling("uploadsessions"), 5606),
        kwargs={"file_name": "diagram.txt", "data": DATA},
        cli=["wiki", "attachments", "upload", "5606", str(FILE)],
        mcp=(
            "wiki_attachments_upload",
            {"page_id": 5606, "file_name": "diagram.txt", "data": base64.b64encode(DATA).decode()},
        ),
        # The four requests of one upload: open a session sized to the file, PUT the bytes as
        # part 1, finish the session, attach it to the page.
        exchanges=[
            (
                Sent(
                    "POST",
                    "upload_sessions",
                    json={"file_name": "diagram.txt", "file_size": len(DATA)},
                ),
                Reply(json={"session_id": SESSION, "status": "not_started"}),
            ),
            (
                Sent(
                    "PUT",
                    f"upload_sessions/{SESSION}/upload_part",
                    {"part_number": "1"},
                    content=DATA,
                    headers={"Content-Type": "application/octet-stream"},
                ),
                Reply(json={"session_id": SESSION, "status": "in_progress"}),
            ),
            (
                Sent("POST", f"upload_sessions/{SESSION}/finish"),
                Reply(json={"session_id": SESSION, "status": "finished"}),
            ),
            (
                Sent("POST", "pages/5606/attachments", json={"upload_sessions": [SESSION]}),
                Reply(json={"results": [{"id": 5616, "name": "diagram.txt"}]}),
            ),
        ],
    ),
    Case(
        "wiki.attachments.list",
        args=(5608,),
        kwargs={"limit": 17, "order_by": "size", "order_direction": "desc"},
        cli=[
            "wiki",
            "attachments",
            "list",
            "5608",
            "--limit",
            "17",
            "--order-by",
            "size",
            "--order-direction",
            "desc",
        ],
        mcp=(
            "wiki_attachments_list",
            {"page_id": 5608, "limit": 17, "order_by": "size", "order_direction": "desc"},
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    "pages/5608/attachments",
                    {"page_size": "100", "order_by": "size", "order_direction": "desc"},
                ),
                Reply(json={"results": [ATTACHMENT], "next_cursor": None}),
            )
        ],
    ),
]
