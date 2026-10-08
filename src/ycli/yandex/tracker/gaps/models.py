"""Pydantic models for Tracker ``/gaps`` (employee absences: vacations, illness, trips, …).

Replies carry the absence with the whole user record on create and grouped by user on search;
requests take up to 100 absences at once. The API names the window ``from``/``to``; Python
code says ``date_from``/``date_to`` (the docs' JSON is accepted as is).
"""

from typing import Literal

from pydantic import AliasChoices, Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.tracker.models import User

#: The kinds of absence the API documents.
GapWorkflow = (
    Literal[
        "vacation",
        "paid_day_off",
        "illness",
        "absence",
        "trip",
        "conference_trip",
        "conference",
        "learning",
        "maternity",
        "duty",
    ]
    | str
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
    user: User | None = Field(default=None, description="The absent user (create replies).")
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

    user: User | None = Field(default=None, description="The requested user.")
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


class GapInput(RequestBody):
    """One absence to create.

    Examples:
        >>> GapInput(
        ...     user="ann", workflow="trip", date_from="2026-07-10", date_to="2026-07-20"
        ... ).model_dump(exclude_none=True, mode="json")
        {'user': 'ann', 'workflow': 'trip', 'from': '2026-07-10', 'to': '2026-07-20'}
    """

    id: str | None = Field(
        default=None,
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


class GapsSearch(RequestBody):
    """Typed request body for ``gaps.search`` (``POST /gaps/_search``).

    Examples:
        >>> GapsSearch(users=["ann"], date_from="2026-07-01T00:00:00.000Z").model_dump(
        ...     exclude_none=True, mode="json"
        ... )
        {'users': ['ann'], 'from': '2026-07-01T00:00:00.000Z'}
    """

    users: list[str] = Field(description="Logins or ids of the users to look up (up to 100).")
    date_from: str | None = Field(
        default=None,
        validation_alias=AliasChoices("from", "date_from"),
        serialization_alias="from",
        description="Start of the window (ISO 8601); now when omitted.",
    )
    date_to: str | None = Field(
        default=None,
        validation_alias=AliasChoices("to", "date_to"),
        serialization_alias="to",
        description="End of the window (ISO 8601); must be after the start.",
    )


class GapsCreate(RequestBody):
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

    gaps: list[GapInput] = Field(description="The absences to create (up to 100).")
