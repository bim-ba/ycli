"""Pydantic models for Forms images (the result of uploading a form image)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel


class Image(APIModel):
    """An image uploaded to a form (``POST …/images`` result).

    The upload is scanned asynchronously — ``check_status`` starts at ``check`` and moves to
    ``ready`` (or an error state); ``links`` maps each rendered size to its URL. Reference the
    returned ``id`` from a question's / option's / style's ``image`` field.

    Example:
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
