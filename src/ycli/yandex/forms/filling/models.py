"""Pydantic models for Forms form-filling (get-settings / submit / suggest).

Three families:

* :class:`FillableForm` — the ``GET …/form`` fillable-form settings (pages, conditions, values,
  texts, styles). The per-page question schemas are the same 12-way polymorphic union already
  fully typed in :mod:`ycli.yandex.forms.questions.models`; here the deeply nested ``pages`` /
  ``conditions`` / ``styles`` are kept as flexible mappings and the common scalars are typed.
* :class:`SubmitBody` (write, ``extra="allow"``) and :class:`SubmitResult` — the ``POST …/form``
  answer map keyed by question slug, and the success-page payload it returns.
* :class:`Suggestion` / :class:`SuggestionList` — the ``GET …/suggest`` prompts (26 polymorphic
  ``layer`` shapes, so extra keys are preserved).
"""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field, RootModel

from ycli.yandex.models import APIModel


class FrontendTexts(APIModel):
    """Button captions shown while filling the form (``texts``).

    Example:
        >>> FrontendTexts(submit="Send", back="Back", next="Next").submit
        'Send'
    """

    submit: str | None = Field(default=None, description="Caption of the Submit button.")
    back: str | None = Field(default=None, description="Caption of the Back button.")
    next: str | None = Field(default=None, description="Caption of the Next button.")


class FrontendMetric(APIModel):
    """Yandex Metrica counter ids attached to the form (``metric``).

    Example:
        >>> FrontendMetric(form=1, group=2).group
        2
    """

    form: int | None = Field(default=None, description="Form Metrica counter id.")
    group: int | None = Field(default=None, description="Form-group Metrica counter id.")


class FrontendOrganization(APIModel):
    """The organization that owns the form (``org``).

    Example:
        >>> FrontendOrganization(dir_id="1", collab_id="2").dir_id
        '1'
    """

    dir_id: str | None = Field(default=None, description="Organization id in the directory.")
    collab_id: str | None = Field(default=None, description="Organization id in collab.")


class FillableForm(APIModel):
    """Form settings that govern filling (``GET /v1/surveys/{survey}/form``).

    The response describes how to render and validate the form. ``pages`` carry the questions to
    fill (each item is one of the 12 polymorphic question schemas), ``conditions`` gate the Submit
    button, and ``values`` holds any pre-filled answer data keyed by question slug — the same slug
    keys you post back in :class:`SubmitBody`. The deeply polymorphic ``pages`` / ``conditions`` /
    ``styles`` are passed through verbatim.

    Example:
        >>> FillableForm.model_validate(
        ...     {"id": "686d", "name": "Feedback", "pages": [{"items": []}]}
        ... ).name
        'Feedback'
    """

    id: str | None = Field(default=None, description="Form id (hex ObjectId string).")
    name: str | None = Field(default=None, description="Form name.")
    teaser: bool | None = Field(default=None, description="Whether to show the teaser.")
    footer: bool | None = Field(default=None, description="Whether to show the footer.")
    iframe: bool | None = Field(
        default=None, description="Whether the form shows only in an iframe."
    )
    texts: FrontendTexts | None = Field(default=None, description="Button captions on the form.")
    metric: FrontendMetric | None = Field(default=None, description="Yandex Metrica counter ids.")
    org: FrontendOrganization | None = Field(
        default=None, description="Organization that owns the form."
    )
    styles: dict[str, Any] | None = Field(
        default=None, description="Form design styles (custom settings and style images)."
    )
    conditions: list[dict[str, Any]] = Field(
        default_factory=list, description="Submit-button display-condition groups."
    )
    pages: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Form pages; each page's ``items`` are the questions to fill "
        "(one of the 12 polymorphic question schemas).",
    )
    values: dict[str, Any] = Field(
        default_factory=dict,
        description="Pre-fill data keyed by question slug — the same slug keys posted in a submit.",
    )


class SubmitBody(APIModel):
    """The write body for ``POST …/form`` — an answer map keyed by question slug.

    A flexible bag (``extra="allow"``): each key is a question ``slug`` (see :class:`FillableForm`
    ``pages[].items[].id`` / ``values``) and the value is that question's answer — a scalar
    (string / bool / int), a string list (multi-choice), a ``{begin, end}`` date range, a list of
    ``{name, path}`` files, or matrix ``{row, column}`` items. Whatever keys you set are sent
    verbatim.

    Example:
        >>> SubmitBody.model_validate({"answer_short_text_1": "Ann"}).model_dump()
        {'answer_short_text_1': 'Ann'}
    """

    model_config = ConfigDict(extra="allow")


class SubmitResult(APIModel):
    """The success-page payload returned by ``POST …/form`` (``200 OK``).

    Confirms the response was accepted (``answer_id`` / ``answer_key``) and carries the
    result-page content (title/subtitle, redirect, quiz scores, triggered integrations). Nested
    polymorphic blocks (``redirect``, ``image``, ``payment``, ``styles``, ``integrations``) are
    passed through verbatim.

    Example:
        >>> SubmitResult.model_validate({"id": "686d", "answer_id": 99}).answer_id
        99
    """

    id: str | None = Field(default=None, description="Form id (hex ObjectId string).")
    name: str | None = Field(default=None, description="Form name.")
    answer_id: int | None = Field(default=None, description="Id of the saved response.")
    answer_key: str | None = Field(default=None, description="Key of the saved response.")
    title: str | None = Field(default=None, description="Title of the success page.")
    subtitle: str | None = Field(default=None, description="Subtitle of the success page.")
    teaser: bool | None = Field(default=None, description="Whether to show the teaser.")
    footer: bool | None = Field(default=None, description="Whether to show the footer.")
    share: bool | None = Field(default=None, description="Whether sharing the result is enabled.")
    fill_again: bool | None = Field(
        default=None, description="Whether refilling the form is offered."
    )
    results: bool | None = Field(default=None, description="Whether the quiz result is shown.")
    correct: bool | None = Field(
        default=None, description="Whether correct quiz answers are shown."
    )
    scores: float | None = Field(default=None, description="Points scored on the quiz.")
    total_scores: float | None = Field(default=None, description="Maximum points on the quiz.")
    stats: dict[str, Any] | None = Field(default=None, description="Fill-statistics block.")
    integrations: list[dict[str, Any]] = Field(
        default_factory=list, description="Integrations triggered by the submit (id + type)."
    )
    redirect: dict[str, Any] | None = Field(
        default=None, description="Post-submit redirect settings."
    )
    image: dict[str, Any] | None = Field(
        default=None, description="Image shown on the result page."
    )
    payment: dict[str, Any] | None = Field(default=None, description="Payment-form data, if any.")
    styles: dict[str, Any] | None = Field(default=None, description="Form design styles.")


class Suggestion(APIModel):
    """One fill-suggestion (``GET …/suggest`` item).

    Suggestions come in 26 ``layer`` shapes (country, city, staff person, tracker issue, …) that
    share ``layer`` / ``id`` / ``text`` and add layer-specific keys; ``extra="allow"`` preserves
    those extras (``country_id``, ``population``, ``login``, ``email``, ``queue``, …).

    Example:
        >>> Suggestion.model_validate({"layer": "city", "id": "1", "text": "Berlin"}).text
        'Berlin'
    """

    model_config = ConfigDict(extra="allow")

    layer: str | None = Field(default=None, description="Suggestion type / data layer.")
    id: str | None = Field(default=None, description="Suggestion object id.")
    text: str | None = Field(default=None, description="Display text of the suggestion.")
    orig_id: str | None = Field(default=None, description="Source-database id, where applicable.")


class SuggestionList(RootModel[list[Suggestion]]):
    """Flat list of :class:`Suggestion` — the public return of ``FillingClient.suggest``.

    Example:
        >>> SuggestionList.model_validate([{"layer": "gender", "id": "m", "text": "Male"}]).root[
        ...     0
        ... ].text
        'Male'
    """

    root: list[Suggestion] = []
