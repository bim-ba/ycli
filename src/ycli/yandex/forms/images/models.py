"""Pydantic models for Forms images (an uploaded or cloned image, and the clone request)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel


class Image(APIModel):
    """An image uploaded to a form (``POST …/images`` result).

    The upload is scanned asynchronously — ``check_status`` starts at ``check`` and moves to
    ``ready`` (or an error state); ``links`` maps each rendered size to its URL. Reference the
    returned ``id`` from a question's / option's / style's ``image`` field.

    Examples:
        >>> Image.model_validate(
        ...     {"id": 7, "links": {}, "name": "logo.png", "check_status": "check"}
        ... ).id
        7
    """

    id: int | None = Field(
        default=None, description="Image ID (reference it from a form image field)."
    )
    links: dict[str, Any] = Field(
        default_factory=dict, description="Map of image size → URL for each rendered variant."
    )
    name: str | None = Field(default=None, description="Original image file name.")
    check_status: str | None = Field(
        default=None,
        description="Virus/upload scan status — one of: check, ready, infected, error, deleted.",
    )
    check_mode: str | None = Field(
        default=None, description="Scan mode: strict or loose (reported on clone)."
    )


class ImageClone(APIModel):
    """Typed body for ``POST /surveys/{id}/images/clone``: the image to copy and its new name.

    Unset fields are dropped before the request is sent.

    Examples:
        >>> ImageClone(id=7, name="copy.png").model_dump(exclude_none=True)
        {'id': 7, 'name': 'copy.png'}
    """

    id: int | None = Field(default=None, description="Id of the image to clone.")
    links: dict[str, str] | None = Field(
        default=None, description="Map of image size → URL of the image to clone."
    )
    name: str | None = Field(default=None, description="File name for the clone.")
