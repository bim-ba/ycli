"""Forms image upload and clone, declared once (sans-IO).

Example:
    >>> upload_image("686d", filename="a.png", data=b"x").files
    {'image': ('a.png', b'x')}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.images.models import Image


def upload_image(survey_id: str, *, filename: str, data: bytes) -> Endpoint[Image]:
    path = f"surveys/{segment(survey_id)}/images"
    return Endpoint("POST", path, Image, files={"image": (filename, data)})


def clone_image(survey_id: str, body: dict[str, Any]) -> Endpoint[Image]:
    return Endpoint("POST", f"surveys/{segment(survey_id)}/images/clone", Image, json=body)
