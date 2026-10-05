"""Pydantic model for Tracker /myself (Me)."""

from pydantic import Field

from ycli.yandex.models import APIModel


class Me(APIModel):
    """The authenticated Tracker user (``GET /v3/myself``) — a safe auth probe."""

    uid: int | None = Field(default=None, description="Tracker account identifier of the user.")
    login: str | None = Field(default=None, description="User login.")
    display: str | None = Field(default=None, description="Display name of the user.")
    email: str | None = Field(default=None, description="User email address.")
    self_url: str | None = Field(
        default=None, alias="self", description="API resource URL of the user."
    )
    tracker_uid: int | None = Field(
        default=None, alias="trackerUid", description="Identifier of the account in Tracker."
    )
    passport_uid: int | None = Field(
        default=None,
        alias="passportUid",
        description="Identifier of the account in Yandex 360 for Business and Yandex ID.",
    )
    cloud_uid: str | None = Field(
        default=None,
        alias="cloudUid",
        description="Identifier of the user in Yandex Cloud Organization.",
    )
    first_name: str | None = Field(default=None, alias="firstName", description="First name.")
    last_name: str | None = Field(default=None, alias="lastName", description="Last name.")
    has_license: bool | None = Field(
        default=None,
        alias="hasLicense",
        description="Whether the user has full access to Tracker (false: read only).",
    )
    dismissed: bool | None = Field(
        default=None, description="Whether the user was removed from the organization."
    )
    external: bool | None = Field(default=None, description="Service parameter.")
    use_new_filters: bool | None = Field(
        default=None, alias="useNewFilters", description="Service parameter."
    )
    disable_notifications: bool | None = Field(
        default=None,
        alias="disableNotifications",
        description="Whether notifications are forcibly turned off for the user.",
    )
    first_login_date: str | None = Field(
        default=None,
        alias="firstLoginDate",
        description="When the user first signed in to Tracker (ISO 8601).",
    )
    last_login_date: str | None = Field(
        default=None,
        alias="lastLoginDate",
        description="When the user last signed in to Tracker (ISO 8601).",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Where the profile comes from: ``directory`` (the organization's catalogue) "
        "or ``tracker`` (added in Tracker itself).",
    )
