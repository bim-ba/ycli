"""Forms images client on the httpx2 core (upload takes raw bytes: SDK and CLI only)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.images import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.images.models import Image


class ImagesClient(Resource):
    """Images to reference from a form's questions, options or style."""

    def upload(self, survey_id: str, *, filename: str, data: bytes) -> Image:
        """Upload an image (multipart field ``image``) → :class:`Image`.

        Reference the returned ``id`` from a question's, option's or form style's ``image``.

        Args:
            survey_id: The form's id.
            filename: The image's file name.
            data: The image's raw bytes.

        Returns:
            The uploaded image, with its ``id``.

        Examples:
            >>> forms.images.upload(
            ...     "686d0a1b2c3d4e5f00000050", filename="logo.png", data=b"PNGDATA"
            ... ).id
            7
        """
        return self._session.send(endpoints.upload_image(survey_id, filename=filename, data=data))

    def clone(self, survey_id: str, body: dict[str, Any]) -> Image:
        """``POST /surveys/{id}/images/clone`` — copy an existing image into the form.

        Build ``body`` from an ``ImageClone``: the source image's ``id`` (or its ``links``) and
        an optional new ``name``.

        Args:
            survey_id: The form's id.
            body: The dumped ``ImageClone``.

        Returns:
            The copied image, with its new ``id``.

        Examples:
            >>> forms.images.clone("686d0a1b2c3d4e5f00000051", {"id": 7, "name": "copy.png"}).id
            8
        """
        return self._session.send(endpoints.clone_image(survey_id, body))
