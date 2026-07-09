"""Pydantic models for Forms /surveys (Survey + SurveysResponse envelope + SurveyList)."""

from __future__ import annotations

from typing import Any

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class Survey(APIModel):
    """A form/survey (``GET /v1/surveys`` item and ``GET /v1/surveys/{id}``).

    ``id`` is a hex ObjectId **string** (not numeric); ``answers`` is an int
    response count. Settings-only fields (``texts``, ``followers``, …) are
    lenient-ignored.

    Example:
        >>> Survey.model_validate({"id": "686d", "name": "F", "answers": 444}).answers
        444
    """

    id: str | None = None
    name: str | None = None
    dir_id: str | None = None
    collab_id: str | None = None
    created: str | None = None
    modified: str | None = None
    language: str | None = None
    is_published: bool | None = None
    is_public: bool | None = None
    is_banned: bool | None = None
    answers: int | None = None
    is_favourite: bool | None = None


class SurveysResponse(APIModel):
    """Envelope for ``GET /v1/surveys`` — ``{links, result:[Survey]}``.

    Internal per-page parse type used by ``SurveysClient._list_page``.

    Example:
        >>> SurveysResponse.model_validate({"result": [{"id": "a"}]}).result[0].id
        'a'
    """

    links: dict[str, Any] = Field(default_factory=dict)
    result: list[Survey] = Field(default_factory=list)


class SurveyList(RootModel[list[Survey]]):
    """Flat collection of :class:`Survey` items — the public return type of ``SurveysClient.list``.

    Example:
        >>> SurveyList([Survey.model_validate({"id": "a"})]).root[0].id
        'a'
    """

    root: list[Survey] = []


class SurveyTexts(APIModel):
    """Button labels and the post-submission message of a form (the ``texts`` write sub-object).

    Every field is optional — only the labels you set are sent; the rest keep the form's
    current values. Passed inside :class:`SurveyCreate` / :class:`SurveyUpdate`.

    Example:
        >>> SurveyTexts(title="Thanks!", submit="Send").submit
        'Send'
    """

    title: str | None = Field(
        default=None, description="Heading shown on the page after a response is submitted."
    )
    subtitle: str | None = Field(
        default=None, description="Body text shown on the page after a response is submitted."
    )
    submit: str | None = Field(default=None, description="Label of the Submit button.")
    back: str | None = Field(default=None, description="Label of the Back button.")
    next: str | None = Field(default=None, description="Label of the Next button.")
    redirect: str | None = Field(default=None, description="Label of the website-redirect button.")


class SurveyCreate(APIModel):
    """Typed request body for creating a form (``POST /surveys``).

    Only the most common form settings are modelled as first-class fields; advanced keys
    (``styles``, ``quiz``, ``auto_publication``, ``followers``, …) go through the CLI's
    repeatable ``--field key=value`` JSON escape and are merged onto this body. Unset
    (``None``) fields are dropped before the request is sent.

    Example:
        >>> SurveyCreate(name="Onboarding survey", need_auth=True).name
        'Onboarding survey'
    """

    name: str | None = Field(default=None, description="Form name (title).")
    language: str | None = Field(
        default=None, description="Interface language at form creation, e.g. ``ru`` or ``en``."
    )
    texts: SurveyTexts | None = Field(
        default=None, description="Button labels and the post-submission message."
    )
    is_published: bool | None = Field(
        default=None, description="Whether the form is published (visible to respondents)."
    )
    is_public: bool | None = Field(
        default=None, description="Whether the form is public (fillable without an invite)."
    )
    need_auth: bool | None = Field(
        default=None, description="Require the respondent to sign in before filling the form."
    )
    allow_multiple_answers: bool | None = Field(
        default=None, description="Allow one respondent to submit the form more than once."
    )
    max_count: int | None = Field(
        default=None, description="Maximum number of responses the form will accept."
    )


class SurveyUpdate(SurveyCreate):
    """Typed request body for modifying a form (``PATCH /surveys/{survey_id}``).

    Same optional fields as :class:`SurveyCreate`; only the fields you set are sent, so a
    partial patch never disturbs untouched settings.

    Example:
        >>> SurveyUpdate(is_published=False).is_published
        False
    """


class SurveyActionResult(APIModel):
    """Synthesized result of a bodyless survey action (delete / publish / unpublish).

    The API answers these with ``204 No Content`` (delete) or a bare ``200 OK`` (publish /
    unpublish) and no JSON body, so the client fabricates this small typed record for the CLI
    to render instead of returning an empty response.

    Example:
        >>> SurveyActionResult(survey_id="686d", action="publish").ok
        True
    """

    survey_id: str = Field(description="Id of the form the action was applied to.")
    action: str = Field(description="Action performed: ``delete``, ``publish`` or ``unpublish``.")
    ok: bool = Field(default=True, description="True when the API accepted the action (2xx).")
