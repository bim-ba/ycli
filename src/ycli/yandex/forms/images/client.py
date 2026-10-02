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

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.images.upload("686d", filename="logo.png", data=b"…").id  # doctest: +SKIP
            7
        """
        return self._session.send(endpoints.upload_image(survey_id, filename=filename, data=data))

    def clone(self, survey_id: str, body: dict[str, Any]) -> Image:
        """``POST /surveys/{id}/images/clone`` — copy an existing image into the form.

        Build ``body`` from an ``ImageClone``: the source image's ``id`` (or its ``links``) and
        an optional new ``name``.

        Example:
            >>> client.images.clone("686d", {"id": 7, "name": "copy.png"}).id  # doctest: +SKIP
            8
        """
        return self._session.send(endpoints.clone_image(survey_id, body))
