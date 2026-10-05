# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class AccessExtSubjectClaims(APIModel):
    sub: str | None = Field(default=None, description="Subject identifier.")
    sub_type: (
        Literal[
            "SUBJECT_TYPE_UNSPECIFIED",
            "USER_ACCOUNT",
            "GROUP",
            "INVITEE",
            "SERVICE_ACCOUNT",
            "_system",
        ]
        | str
        | None
    ) = Field(default=None, alias="subType", description="Subject type.")
    email: str | None = Field(default=None, description="Subject email address.")
    name: str | None = Field(default=None, description="Subject display name.")
    given_name: str | None = Field(
        default=None, alias="givenName", description="Subject given name."
    )
    family_name: str | None = Field(
        default=None, alias="familyName", description="Subject family name."
    )
    preferred_username: str | None = Field(
        default=None,
        alias="preferredUsername",
        description="Preferred username of the subject.",
    )
    federation: Any | None = Field(
        default=None, description="Federation associated with the subject."
    )
    picture_data: str | None = Field(
        default=None, alias="pictureData", description="Encoded profile picture data."
    )
    picture: str | None = Field(default=None, description="URL of the subject profile picture.")
    idp_type: str | None = Field(
        default=None,
        alias="idpType",
        description="Type of the subject identity provider.",
    )


class AccessExtBatchListMembersResult(APIModel):
    members: list[AccessExtSubjectClaims] | None = Field(
        default=None, description="Members matching the request."
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of members.",
    )


class AccessExtBatchListMembersArgs(RequestBody):
    language: Literal["en", "ru"] | str | None = Field(
        default=None, description="Language used for member data."
    )
    search: str | None = Field(default=None, description="Text used to search for members.")
    tab_id: (
        Literal[
            "SUBJECT_TYPE_UNSPECIFIED",
            "USER_ACCOUNT",
            "GROUP",
            "INVITEE",
            "SERVICE_ACCOUNT",
            "_system",
        ]
        | str
        | None
    ) = Field(default=None, alias="tabId", description="Subject type used to filter members.")
    page_size: int | float | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of members to return.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of members.",
    )
    filter: str | None = Field(default=None, description="Filter applied to the member list.")
