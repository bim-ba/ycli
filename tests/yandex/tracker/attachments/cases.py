"""Contract cases for Tracker issue ``/attachments`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "tracker.attachments.list",
        args=("JUNE-2",),
        cli=["tracker", "attachments", "list", "JUNE-2"],
        mcp=("tracker_attachments_list", {"issue_key": "JUNE-2"}),
        exchanges=[
            (
                Sent("GET", "issues/JUNE-2/attachments"),
                Reply(json=[{"id": "123", "name": "picture.jpg", "size": 19090}]),
            )
        ],
    ),
    Case(
        "tracker.attachments.download",
        args=("JUNE-3", "4159", "report.pdf"),
        cli=["tracker", "attachments", "download", "JUNE-3", "4159", "report.pdf"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "issues/JUNE-3/attachments/4159/report.pdf"),
                Reply(content=b"%PDF-attachment"),
            )
        ],
    ),
    Case(
        "tracker.attachments.download_thumbnail",
        args=("JUNE-4", "4160"),
        cli=["tracker", "attachments", "thumbnail", "JUNE-4", "4160"],
        mcp=None,
        exchanges=[
            (Sent("GET", "issues/JUNE-4/thumbnails/4160"), Reply(content=b"\x89PNGthumb")),
        ],
    ),
]
