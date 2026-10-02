"""Contract cases for Wiki ``/pages/{id}/attachments`` (see tests/contract.py)."""

import base64
from pathlib import Path

from tests.contract import Case, Reply, Sent, Sibling

FILE = Path(__file__).with_name("diagram.txt")
DATA = FILE.read_bytes()
ATTACHMENT = {"id": 5611, "name": "spec.pdf", "size": "2048", "mimetype": "application/pdf"}
SESSION = "3f2b1a0c-5d4e-4f6a-8b9c-0d1e2f3a4b5c"

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
            "--session",
            "s-5605-a",
            "--session",
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
]
