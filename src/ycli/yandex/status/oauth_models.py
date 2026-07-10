"""Models for `ycli auth login` — the OAuth device/implicit flow + api360 org payloads.

Inherit ``APIModel`` (lenient parse, ignore extras) like every other Yandex model;
these are plain data with no serialization logic (that lives in ``output.py``).
"""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel


class DeviceCodeResponse(APIModel):
    """``POST /device/code`` — what the user approves and how to poll for the token.

    ``device_code`` is required: it is the poll key and is always present on a 200; an
    error payload lacking it raises rather than silently polling with a missing code.
    """

    device_code: str
    user_code: str | None = None
    verification_url: str | None = None
    expires_in: int | None = None
    interval: int = 5


class TokenResponse(APIModel):
    """``POST /token`` success payload — the issued OAuth access token.

    ``access_token`` is required: this model is built only from a 200 response, where the
    token is always present.
    """

    access_token: str
    token_type: str | None = None
    expires_in: int | None = None
    scope: str | None = None


class Organization(APIModel):
    """One organization from the api360 directory listing."""

    id: int | None = None
    name: str | None = None


class OrganizationList(APIModel):
    """``GET /directory/v1/org`` — the organizations the token can see."""

    organizations: list[Organization] = Field(default_factory=list)
