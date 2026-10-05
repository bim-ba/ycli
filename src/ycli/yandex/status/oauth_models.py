"""Models for `ycli auth login` — the OAuth device/implicit flow + the API 360 organization list.

Inherit ``APIModel`` (lenient parse, ignore extras) like every other Yandex model;
these are plain data with no serialization logic (that lives in ``output.py``).
"""

from pydantic import Field

from ycli.yandex.models import APIModel


class DeviceCodeResponse(APIModel):
    """``POST /device/code`` — what the user approves and how to poll for the token.

    ``device_code`` is required: it is the poll key and is always present on a 200; an
    error payload lacking it raises rather than silently polling with a missing code.
    """

    device_code: str = Field(description="Code to poll for the token with.")
    user_code: str | None = Field(
        default=None, description="Code the user enters at the verification URL."
    )
    verification_url: str | None = Field(
        default=None, description="URL where the user enters the code."
    )
    expires_in: int | None = Field(
        default=None, description="Seconds until the device and user codes expire."
    )
    interval: int = Field(default=5, description="Seconds to wait between polls.")


class TokenResponse(APIModel):
    """``POST /token`` success payload — the issued OAuth access token.

    ``access_token`` is required: this model is built only from a 200 response, where the
    token is always present.
    """

    access_token: str = Field(description="The issued OAuth access token.")
    token_type: str | None = Field(default=None, description="Type of the token, e.g. `bearer`.")
    expires_in: int | None = Field(default=None, description="Seconds until the token expires.")
    scope: str | None = Field(default=None, description="Scopes the token was granted.")


class Organization(APIModel):
    """One organization from the API 360 directory listing."""

    id: int | None = Field(default=None, description="Id of the organization.")
    name: str | None = Field(default=None, description="Name of the organization.")


class OrganizationList(APIModel):
    """``GET /directory/v1/org`` — the organizations the token can see."""

    organizations: list[Organization] = Field(
        default_factory=list, description="Organizations the token can see."
    )
