"""Contract cases for Forms images: upload and clone (see tests/contract.py)."""

from pathlib import Path

from tests.contract import Case, Reply, Sent
from ycli.yandex.forms.images.models import ImageClone

SID = "686d0a1b2c3d4e5f00000050"
LOGO = Path(__file__).with_name("logo.png")
CLONED = {
    "id": 8,
    "links": {"orig": "https://img.test/8.png"},
    "name": "copy.png",
    "check_status": "ready",
    "check_mode": "strict",
}

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
    Case(
        "forms.images.clone",
        args=("686d0a1b2c3d4e5f00000051", ImageClone.model_validate({"id": 7, "name": "copy.png"})),
        cli=[
            "forms",
            "images",
            "clone",
            "686d0a1b2c3d4e5f00000051",
            "--image-id",
            "7",
            "--name",
            "copy.png",
        ],
        mcp=(
            "forms_images_clone",
            {"survey_id": "686d0a1b2c3d4e5f00000051", "body": {"id": 7, "name": "copy.png"}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "surveys/686d0a1b2c3d4e5f00000051/images/clone",
                    json={"id": 7, "name": "copy.png"},
                ),
                Reply(json=CLONED),
            )
        ],
    ),
    Case(
        "forms.images.clone",
        args=(
            "686d0a1b2c3d4e5f00000052",
            ImageClone.model_validate({"links": {"orig": "https://img.test/a.png"}}),
        ),
        cli=[
            "forms",
            "images",
            "clone",
            "686d0a1b2c3d4e5f00000052",
            "--link",
            "orig=https://img.test/a.png",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "surveys/686d0a1b2c3d4e5f00000052/images/clone",
                    json={"links": {"orig": "https://img.test/a.png"}},
                ),
                Reply(json=CLONED),
            )
        ],
    ),
]
