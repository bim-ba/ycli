"""Contract cases for Forms image upload (see tests/contract.py)."""

from pathlib import Path

from tests.contract import Case, Reply, Sent

SID = "686d0a1b2c3d4e5f00000050"
LOGO = Path(__file__).with_name("logo.png")

CASES = [
    Case(
        "forms.images.upload",
        args=(SID,),
        kwargs={"filename": "logo.png", "data": b"PNGDATA"},
        cli=["forms", "images", "upload", SID, str(LOGO)],
        mcp=None,
        exchanges=[
            (
                Sent("POST", f"surveys/{SID}/images", files={"image": ("logo.png", b"PNGDATA")}),
                Reply(json={"id": 7, "name": "logo.png"}, status=201),
            )
        ],
    ),
]
