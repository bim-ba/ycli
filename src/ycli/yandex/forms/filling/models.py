"""Pydantic models for Forms form-filling (get-settings / submit / suggest).

Three families:

* :class:`FillableForm` — the ``GET …/form`` fillable-form settings (pages, conditions, values,
  texts, styles). The per-page question schemas are the same 12-way polymorphic union already
  fully typed in :mod:`ycli.yandex.forms.questions.models`; here the deeply nested ``pages`` /
  ``conditions`` / ``styles`` are kept as flexible mappings and the common scalars are typed.
* :class:`SubmitBody` (write, ``extra="allow"``) and :class:`SubmitResult` — the ``POST …/form``
  answer map keyed by question slug, and the success-page payload it returns.
* :class:`Suggestion` / ``ItemList[Suggestion]`` — the ``GET …/suggest`` prompts (26 polymorphic
  ``layer`` shapes, so extra keys are preserved).
"""

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from ycli.yandex.forms.models import QuizShowFormat
from ycli.yandex.models import APIModel
from ycli.yandex.sync.marks import Identity


class FrontendTexts(APIModel):
    """Button captions shown while filling the form (``texts``).

    Examples:
        >>> FrontendTexts(submit="Send", back="Back", next="Next").submit
        'Send'
    """

    submit: str | None = Field(default=None, description="Caption of the Submit button.")
    back: str | None = Field(default=None, description="Caption of the Back button.")
    next: str | None = Field(default=None, description="Caption of the Next button.")


class FrontendMetric(APIModel):
    """Yandex Metrica counter ids attached to the form (``metric``).

    Examples:
        >>> FrontendMetric(form=1, group=2).group
        2
    """

    form: int | None = Field(default=None, description="Form Metrica counter id.")
    group: int | None = Field(default=None, description="Form-group Metrica counter id.")


class FrontendOrganization(APIModel):
    """The organization that owns the form (``org``).

    Examples:
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

    Examples:
        >>> FillableForm.model_validate(
        ...     {"id": "686d", "name": "Feedback", "pages": [{"items": []}]}
        ... ).name
        'Feedback'
    """

    id: Annotated[str | None, Identity()] = Field(
        default=None, description="Form id (hex ObjectId string)."
    )
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

    Examples:
        >>> SubmitBody.model_validate({"answer_short_text_1": "Ann"}).model_dump()
        {'answer_short_text_1': 'Ann'}
    """

    model_config = ConfigDict(extra="allow")


class SubmitQuizResult(APIModel):
    """What a respondent scored on a quiz (``quiz_result`` of a submission).

    Examples:
        >>> SubmitQuizResult(show_format="score_with_total", scores=7, total_scores=10).scores
        7.0
    """

    show_format: QuizShowFormat | None = Field(
        default=None, description="How the result is shown: score, percent or score_with_total."
    )
    scores: float | None = Field(default=None, description="Points scored, or the percentage.")
    total_scores: float | None = Field(
        default=None, description="Most points the quiz gives (``score_with_total`` only)."
    )


class SubmitResult(APIModel):
    """The success-page payload returned by ``POST …/form`` (``200 OK``).

    Confirms the response was accepted (``answer_id`` / ``answer_key``) and carries the
    result-page content (title/subtitle, redirect, quiz scores, triggered integrations). Nested
    polymorphic blocks (``redirect``, ``image``, ``payment``, ``styles``, ``integrations``) are
    passed through verbatim.

    Examples:
        >>> SubmitResult.model_validate({"id": "686d", "answer_id": 99}).answer_id
        99
    """

    id: Annotated[str | None, Identity()] = Field(
        default=None, description="Form id (hex ObjectId string)."
    )
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
    correct: bool | None = Field(
        default=None, description="Whether correct quiz answers are shown."
    )
    quiz_result: SubmitQuizResult | None = Field(
        default=None, description="Result of the quiz, in the format the form shows it."
    )
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
    share ``layer`` / ``id`` / ``text`` and add layer-specific keys (``country_id``,
    ``population``, ``login``, ``email``, ``queue``, …). One class reads them all: the keys a
    layer does not have stay ``None``, and ``extra="allow"`` keeps a key of a layer Yandex adds.

    Examples:
        >>> Suggestion.model_validate({"layer": "city", "id": "1", "text": "Berlin"}).text
        'Berlin'
    """

    model_config = ConfigDict(extra="allow")

    layer: str | None = Field(default=None, description="Suggestion type / data layer.")
    id: Annotated[str | None, Identity()] = Field(default=None, description="Suggestion object id.")
    text: str | None = Field(default=None, description="Display text of the suggestion.")
    orig_id: str | None = Field(default=None, description="Source-database id, where applicable.")
    country_id: str | None = Field(default=None, description="Id of the country (city).")
    population: int | None = Field(default=None, description="Population of the city.")
    city: str | None = Field(default=None, description="City of the university.")
    region: str | None = Field(default=None, description="Region of the university.")
    tracks_count: int | None = Field(
        default=None, description="Number of tracks in the music genre."
    )
    address: str | None = Field(default=None, description="Address of the office.")
    url: str | None = Field(default=None, description="Slug of the staff group.")
    type: str | None = Field(default=None, description="Kind of the staff group.")
    role_scope: str | None = Field(default=None, description="Scope of the staff group.")
    full_name: str | None = Field(default=None, description="Full name of the employee.")
    login: str | None = Field(default=None, description="Login of the user.")
    email: str | None = Field(default=None, description="Email of the user or employee.")
    uid: str | None = Field(default=None, description="Passport uid of the user or employee.")
    yandex_uid: str | None = Field(
        default=None, description="Passport uid of the user or employee."
    )
    cloud_uid: str | None = Field(default=None, description="Cloud uid of the user.")
    avatar: str | None = Field(default=None, description="Avatar of the user or employee.")
    group_id: str | None = Field(default=None, description="Id of the employee's staff group.")
    department: str | None = Field(default=None, description="Department of the employee.")
    office_id: str | None = Field(default=None, description="Id of the meeting room's office.")
    floor_number: str | None = Field(default=None, description="Floor of the meeting room.")
    floor_id: str | None = Field(default=None, description="Id of the meeting room's floor.")
    row_id: str | None = Field(default=None, description="Universal id of the table row.")
    parent_id: str | None = Field(
        default=None, description="Id of the parent row, for linked suggestions."
    )
    display_text: str | None = Field(default=None, description="Text to show for the table row.")
    board: str | None = Field(default=None, description="Name of the sprint's agile board.")
    queue: str | None = Field(
        default=None, description="Queue of the Tracker issue, component or field."
    )
    status: str | None = Field(default=None, description="Status of the Tracker issue.")
    slug: str | None = Field(default=None, description="Slug of the Tracker field.")
