"""Pydantic models for Tracker users (User and the relative-page envelope)."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel
from ycli.yandex.tracker.models import Reference


class User(APIModel):
    """An organisation user account (``/users/{login_or_id}`` and ``/users/_relative`` item).

    Examples:
        >>> User.model_validate({"uid": 12, "login": "username", "display": "Ivan Ivanov"}).login
        'username'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the user account.",
    )
    uid: int | None = Field(
        default=None,
        description="Unique identifier of the user account in Tracker (the default id type).",
    )
    login: str | None = Field(default=None, description="Login (username) of the user.")
    tracker_uid: int | None = Field(
        default=None,
        alias="trackerUid",
        description="Unique identifier of the user's account in Tracker.",
    )
    passport_uid: int | None = Field(
        default=None,
        alias="passportUid",
        description="Unique identifier of the account in Yandex 360 for Business and Yandex ID.",
    )
    cloud_uid: str | None = Field(
        default=None,
        alias="cloudUid",
        description="Unique identifier of the user in Yandex Cloud Organization.",
    )
    first_name: str | None = Field(
        default=None, alias="firstName", description="Given name of the user."
    )
    last_name: str | None = Field(
        default=None, alias="lastName", description="Family name of the user."
    )
    display: str | None = Field(default=None, description="Display name of the user.")
    email: str | None = Field(default=None, description="Email address of the user.")
    groups: list[Reference] = Field(
        default_factory=list,
        description="Groups the user belongs to; populated only when expand=groups is requested.",
    )
    external: bool | None = Field(default=None, description="Internal service flag.")
    has_license: bool | None = Field(
        default=None,
        alias="hasLicense",
        description="Whether the user has full Tracker access (true) or read-only access (false).",
    )
    dismissed: bool | None = Field(
        default=None,
        description="Membership status: true if removed from the organisation, false if active.",
    )
    use_new_filters: bool | None = Field(
        default=None, alias="useNewFilters", description="Internal service flag."
    )
    disable_notifications: bool | None = Field(
        default=None,
        alias="disableNotifications",
        description="Whether notifications are force-disabled for the user (true) or enabled.",
    )
    first_login_date: str | None = Field(
        default=None,
        alias="firstLoginDate",
        description="First Tracker sign-in timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    last_login_date: str | None = Field(
        default=None,
        alias="lastLoginDate",
        description="Most recent Tracker sign-in timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    welcome_mail_sent: bool | None = Field(
        default=None,
        alias="welcomeMailSent",
        description="How the user was added: true via an email invitation, false another way.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Origin of the account data, e.g. the corporate directory.",
    )
    position: str | None = Field(default=None, description="Job title of the user.")


class UsersRelativeResponse(APIModel):
    """Internal envelope of one ``/users/_relative`` page (``{users, hasNext}``).

    Examples:
        >>> UsersRelativeResponse.model_validate({"users": [{"uid": 1}], "hasNext": True}).has_next
        True
    """

    users: list[User] = Field(
        default_factory=list, description="Users on this page, sorted by ascending uid."
    )
    has_next: bool | None = Field(
        default=None,
        alias="hasNext",
        description="Whether further pages remain (true) or this is the last page (false).",
    )
