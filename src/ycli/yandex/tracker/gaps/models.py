"""Pydantic models for Tracker ``/gaps`` (employee absences: vacations, illness, trips, …).

Replies carry the absence with the whole user record on create and grouped by user on search;
requests take up to 100 absences at once. The API names the window ``from``/``to``; Python
code says ``date_from``/``date_to`` (the docs' JSON is accepted as is).
"""

from __future__ import annotations

import enum

from pydantic import AliasChoices, Field

from ycli.yandex.models import APIModel


class GapWorkflow(enum.StrEnum):
    """The kinds of absence the API documents (``GET /v3/gaps/workflows`` is undocumented)."""

    VACATION = "vacation"
    PAID_DAY_OFF = "paid_day_off"
    ILLNESS = "illness"
    ABSENCE = "absence"
    TRIP = "trip"
    CONFERENCE_TRIP = "conference_trip"
    CONFERENCE = "conference"
    LEARNING = "learning"
    MATERNITY = "maternity"
    DUTY = "duty"


class GapUser(APIModel):
    """The user an absence belongs to, as a full directory record.

    Examples:
        >>> GapUser.model_validate({"login": "ann", "uid": 1, "sources": ["directory"]}).login
        'ann'
    """

    self_url: str | None = Field(default=None, alias="self", description="API URL of the user.")
    uid: int | None = Field(default=None, description="Numeric id of the user.")
    login: str | None = Field(default=None, description="Login of the user.")
    tracker_uid: int | None = Field(
        default=None, alias="trackerUid", description="Id of the user in Tracker."
    )
    passport_uid: int | None = Field(
        default=None, alias="passportUid", description="Id of the user's Yandex account."
    )
    cloud_uid: str | None = Field(
        default=None, alias="cloudUid", description="Id of the user in Yandex Cloud."
    )
    first_name: str | None = Field(default=None, alias="firstName", description="First name.")
    last_name: str | None = Field(default=None, alias="lastName", description="Last name.")
    display: str | None = Field(default=None, description="Display name.")
    email: str | None = Field(default=None, description="Email address.")
    external: bool | None = Field(default=None, description="Whether the user is external.")
    dismissed: bool | None = Field(default=None, description="Whether the user is dismissed.")
    first_login_date: str | None = Field(
        default=None, alias="firstLoginDate", description="First login time (ISO 8601)."
    )
    last_login_date: str | None = Field(
        default=None, alias="lastLoginDate", description="Last login time (ISO 8601)."
    )
    sources: list[str] = Field(
        default_factory=list, description="Where the user record comes from, e.g. directory."
    )


class Gap(APIModel):
    """One absence. ``user`` is filled on create replies and absent inside search results.

    Examples:
        >>> Gap.model_validate(
        ...     {"id": "g1", "workflow": "trip", "from": "2026-07-10T00:00:00.000+0000"}
        ... ).date_from
        '2026-07-10T00:00:00.000+0000'
    """

    id: str | None = Field(default=None, description="Identifier of the absence.")
    user: GapUser | None = Field(default=None, description="The absent user (create replies).")
    workflow: str | None = Field(default=None, description="Kind of absence, e.g. vacation.")
    date_from: str | None = Field(
        default=None, alias="from", description="Start of the absence (ISO 8601)."
    )
    date_to: str | None = Field(
        default=None, alias="to", description="End of the absence (ISO 8601)."
    )
    full_day: bool | None = Field(
        default=None, alias="fullDay", description="Whether the absence covers whole days."
    )
    work_in_absence: bool | None = Field(
        default=None, alias="workInAbsence", description="Whether the user works while absent."
    )


class GapCreated(APIModel):
    """The reply to ``gaps.create``: the absences actually saved (outdated ones are left out).

    Examples:
        >>> GapCreated.model_validate({"gaps": [{"id": "g1"}]}).gaps[0].id
        'g1'
    """

    gaps: list[Gap] = Field(default_factory=list, description="The saved absences.")


class UserGaps(APIModel):
    """One requested user with their absences in the window (empty when they have none).

    Examples:
        >>> UserGaps.model_validate({"user": {"login": "ann"}, "gaps": []}).user.login
        'ann'
    """

    user: GapUser | None = Field(default=None, description="The requested user.")
    gaps: list[Gap] = Field(default_factory=list, description="Their absences in the window.")


class GapSearchPage(APIModel):
    """One page of ``POST /gaps/_search``: users with absences and the more-pages flag.

    Examples:
        >>> GapSearchPage.model_validate({"userGaps": [], "hasMore": False}).has_more
        False
    """

    user_gaps: list[UserGaps] = Field(
        default_factory=list,
        alias="userGaps",
        description="One entry per requested user on this page.",
    )
    has_more: bool = Field(
        default=False, alias="hasMore", description="Whether a next page of users follows."
    )


class GapInput(APIModel):
    """One absence to create.

    Examples:
        >>> GapInput(
        ...     user="ann", workflow="trip", date_from="2026-07-10", date_to="2026-07-20"
        ... ).model_dump(exclude_none=True, mode="json")
        {'user': 'ann', 'workflow': 'trip', 'from': '2026-07-10', 'to': '2026-07-20'}
    """

    id: str | None = Field(
        default=None,
        max_length=128,
        description="Identifier of the absence (up to 128 characters); generated if omitted.",
    )
    user: str = Field(description="Login or id of the absent user.")
    workflow: GapWorkflow = Field(description="Kind of absence.")
    date_from: str = Field(
        validation_alias=AliasChoices("from", "date_from"),
        serialization_alias="from",
        description="Start of the absence (ISO 8601); must be before the end.",
    )
    date_to: str = Field(
        validation_alias=AliasChoices("to", "date_to"),
        serialization_alias="to",
        description="End of the absence (ISO 8601); must be after the start.",
    )
    full_day: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("fullDay", "full_day"),
        serialization_alias="fullDay",
        description="Whether the absence covers whole days (API default false).",
    )
    work_in_absence: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("workInAbsence", "work_in_absence"),
        serialization_alias="workInAbsence",
        description="Whether the user works while absent (API default false).",
    )


class GapsCreate(APIModel):
    """Typed request body for ``gaps.create`` (``POST /gaps``): up to 100 absences.

    Examples:
        >>> body = GapsCreate(
        ...     gaps=[
        ...         GapInput(
        ...             user="ann", workflow="trip", date_from="2026-07-10", date_to="2026-07-20"
        ...         )
        ...     ]
        ... )
        >>> body.model_dump(exclude_none=True, mode="json")["gaps"][0]["workflow"]
        'trip'
    """

    gaps: list[GapInput] = Field(max_length=100, description="The absences to create (up to 100).")
