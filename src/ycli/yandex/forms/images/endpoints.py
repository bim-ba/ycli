"""Forms image upload and clone, declared once (sans-IO).

Examples:
    >>> upload("686d", filename="a.png", data=b"x").files
    {'image': ('a.png', b'x')}
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.images.models import Image, ImageClone


def upload(survey_id: str, *, filename: str, data: bytes) -> Endpoint[Image]:
    path = f"surveys/{segment(survey_id)}/images"
    return Endpoint(HTTPMethod.POST, path, Image, files={"image": (filename, data)})


def clone(survey_id: str, body: ImageClone) -> Endpoint[Image]:
    return Endpoint(HTTPMethod.POST, f"surveys/{segment(survey_id)}/images/clone", Image, json=body)
