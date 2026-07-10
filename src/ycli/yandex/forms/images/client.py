"""Declarative Forms images client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.

A single ``multipart/form-data`` upload (field ``image``). It is a write, so it ships SDK + CLI
only — never MCP.
"""

import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.images.models import Image


class ImagesClient(FormsResource):
    """Declarative HTTP for ``POST /surveys/{survey_id}/images`` (multipart image upload)."""

    @uplink.returns.json()
    @uplink.multipart
    @uplink.post("surveys/{survey_id}/images")
    def _upload(
        self,
        survey_id: uplink.Path,
        image_data: uplink.Part("image"),  # ty: ignore[invalid-type-form]
    ) -> Image:  # ty: ignore[empty-body]
        """``POST …/images`` (multipart; internal — callers use :meth:`upload`)."""

    def upload(self, survey_id: str, *, filename: str, data: bytes) -> Image:
        """Upload an image to add to a form (multipart field ``image``) → :class:`Image`.

        ``data`` are the raw image bytes; ``filename`` is recorded as the multipart part filename.
        Reference the returned ``id`` from a question's / option's / form-style ``image`` field.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.images.upload(
            ...     "686d0a1b2c3d4e5f00000001", filename="logo.png", data=b"\\x89PNG…"
            ... ).id  # doctest: +SKIP
            7
        """
        return self._upload(survey_id, image_data=(filename, data))
