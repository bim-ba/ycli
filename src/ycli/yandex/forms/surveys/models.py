"""Pydantic models for Forms /surveys (Survey + SurveysResponse envelope + ItemList[Survey])."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ycli.yandex.forms.images.models import Image
from ycli.yandex.forms.models import QuizShowFormat, UserRef
from ycli.yandex.models import IGNORED_BY_API, APIModel, RequestBody, WarnsOnIgnored

#: The captcha a form asks before it is submitted.
CaptchaType = Literal["std", "ocr", "nbg"] | str


class SurveyTexts(APIModel):
    """Button labels and the post-submission message of a form (the ``texts`` write sub-object).

    Every field is optional — only the labels you set are sent; the rest keep the form's
    current values. Passed inside :class:`SurveyCreate` / :class:`SurveyUpdate`.

    Examples:
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


class SurveyStyleImages(APIModel):
    """The background images of a form's design (``styles.images``).

    Examples:
        >>> SurveyStyleImages.model_validate({"page": {"id": 5}}).page.id
        5
    """

    page: Image | None = Field(default=None, description="Background behind the text.")
    form: Image | None = Field(default=None, description="Background of the form itself.")


class SurveyStyles(APIModel):
    """The design of a form (``styles``): a built-in template or custom settings.

    Examples:
        >>> SurveyStyles.model_validate({"id": 3, "type": "default", "custom": {}}).type
        'default'
    """

    id: int | None = Field(
        default=None, description="Id of the design; in a request, the built-in template to apply."
    )
    name: str | None = Field(default=None, description="Name of the design.")
    type: Literal["default", "custom"] | str | None = Field(
        default=None, description="``default`` (a built-in template) or ``custom``."
    )
    custom: dict[str, Any] | None = Field(
        default=None, description="Custom design settings, as the form editor stores them."
    )
    images: SurveyStyleImages | None = Field(default=None, description="Background images.")


class SurveyAutoPublication(APIModel):
    """When a form publishes and unpublishes itself (``auto_publication``).

    Examples:
        >>> SurveyAutoPublication(enabled=True, date_close="2026-12-31T00:00:00Z").enabled
        True
    """

    enabled: bool | None = Field(
        default=None, description="Whether the publication state is managed automatically."
    )
    date_open: str | None = Field(default=None, description="ISO-8601 time the form opens.")
    date_close: str | None = Field(default=None, description="ISO-8601 time the form closes.")


class SurveyQuizItem(APIModel):
    """One result range of a quiz: what the respondent sees for a score in it.

    Examples:
        >>> SurveyQuizItem(title="Passed", upper_limit=10).title
        'Passed'
    """

    title: str | None = Field(default=None, description="Heading of the result page.")
    description: str | None = Field(default=None, description="Text of the result page.")
    image: Image | None = Field(default=None, description="Image of the result page.")
    upper_limit: float | None = Field(
        default=None, description="Upper bound of the range (for ``calc_method`` ``range``)."
    )


class SurveyQuiz(APIModel):
    """The quiz settings of a form (``quiz``).

    ``question_count`` and ``total_scores`` are computed by the API and only come back in a
    reply.

    Examples:
        >>> SurveyQuiz(calc_method="scores", items=[]).calc_method
        'scores'
    """

    show_results: bool | None = Field(default=None, description="Whether to show the result.")
    show_format: QuizShowFormat | None = Field(
        default=None,
        description="How the result is shown: score_with_total, score, percent, text or off.",
    )
    show_correct: bool | None = Field(
        default=None, description="Whether to show the correct answers."
    )
    calc_method: Literal["range", "scores"] | str | None = Field(
        default=None, description="How points are counted: ``range`` or ``scores``."
    )
    pass_scores: float | None = Field(default=None, description="Points needed to pass.")
    question_count: int | None = Field(
        default=None, description="Number of quiz questions (reply only)."
    )
    total_scores: float | None = Field(
        default=None, description="Most points the quiz gives (reply only)."
    )
    items: list[SurveyQuizItem] | None = Field(
        default=None, description="Result ranges of the quiz."
    )


class SurveyApiKey(RequestBody):
    """An API key a form's integrations use (``api_keys`` item of a request).

    Examples:
        >>> SurveyApiKey(name="crm", value="secret").name
        'crm'
    """

    name: str = Field(description="Name of the key.")
    id: str | None = Field(default=None, description="Id of an existing key.")
    value: str | None = Field(default=None, description="Value of the key.")
    secure: bool | None = Field(
        default=None, description="Whether the value is stored encrypted (the API's default)."
    )


class SurveyFollower(APIModel):
    """Who is told about a form's integration errors: a user or a mailing list (``followers``).

    Examples:
        >>> SurveyFollower.model_validate({"id": "team@x.test", "type": "mail_list"}).type
        'mail_list'
    """

    id: int | str | None = Field(
        default=None, description="Id of the user, or the address of the mailing list."
    )
    type: Literal["user", "mail_list"] | str | None = Field(
        default=None, description="``user`` or ``mail_list``."
    )
    email: str | None = Field(default=None, description="Address of the user or the list.")
    uid: str | None = Field(default=None, description="Passport uid of the user.")
    cloud_uid: str | None = Field(default=None, description="Cloud uid of the user.")
    login: str | None = Field(default=None, description="Login of the user.")
    display: str | None = Field(default=None, description="Name to show for the user.")
    avatar: str | None = Field(default=None, description="Avatar of the user.")
    is_superuser: bool | None = Field(default=None, description="Whether a superuser.")
    is_staff: bool | None = Field(default=None, description="Whether support staff.")


class Survey(APIModel):
    """A form/survey (``GET /v1/surveys`` item and ``GET /v1/surveys/{id}``).

    ``id`` is a hex ObjectId **string** (not numeric); ``answers`` is an int
    response count. The listing returns the first block of fields; the settings
    (``texts``, ``styles``, ``quiz``, ``followers``, …) come with a single form.

    Examples:
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
    hashed_id: str | None = Field(default=None, description="Form id with a hash.")
    author: UserRef | None = Field(default=None, description="Who created the form.")
    need_auth: bool | None = Field(
        default=None, description="Whether the respondent must sign in to fill the form."
    )
    allow_multiple_answers: bool | None = Field(
        default=None, description="Whether one respondent may fill the form more than once."
    )
    show_last_answer: bool | None = Field(
        default=None, description="Whether the respondent's previous answer is filled in."
    )
    max_count: int | None = Field(default=None, description="Most responses the form accepts.")
    texts: SurveyTexts | None = Field(
        default=None, description="Button labels and the message after submission."
    )
    styles: SurveyStyles | None = Field(default=None, description="Design of the form.")
    quiz: SurveyQuiz | None = Field(default=None, description="Quiz settings.")
    auto_publication: SurveyAutoPublication | None = Field(
        default=None, description="When the form publishes and unpublishes itself."
    )
    follow: str | None = Field(
        default=None, description="How often integration errors are mailed: 5m, 1h or 1d."
    )
    followers: list[SurveyFollower] | None = Field(
        default=None, description="Who is told about integration errors."
    )
    captcha: CaptchaType | None = Field(
        default=None, description="Captcha asked before submission: std, ocr or nbg."
    )
    metric: int | None = Field(default=None, description="Yandex Metrica counter.")
    file_storage: str | None = Field(
        default=None, description="Link to the organization's own file storage."
    )
    validator_url: str | None = Field(
        default=None, description="URL that validates the answers from outside."
    )
    iframe: bool | None = Field(
        default=None, description="Whether the form may be published only in an iframe."
    )
    footer: bool | None = Field(default=None, description="Whether to show the footer.")
    teaser: bool | None = Field(default=None, description="Whether to show the teaser.")
    stats: bool | None = Field(
        default=None, description="Whether to show statistics on the page after submission."
    )
    share: bool | None = Field(default=None, description="Whether sharing the form is offered.")
    fill_again: bool | None = Field(
        default=None, description="Whether filling the form again is offered."
    )


class SurveysResponse(APIModel):
    """Envelope for ``GET /v1/surveys`` — ``{links, result:[Survey]}``.

    Internal per-page parse type used by ``SurveysClient._list_page``.

    Examples:
        >>> SurveysResponse.model_validate({"result": [{"id": "a"}]}).result[0].id
        'a'
    """

    links: dict[str, Any] = Field(default_factory=dict)
    result: list[Survey] = Field(default_factory=list)


class SurveyCreate(WarnsOnIgnored):
    """Typed request body for creating a form (``POST /surveys``).

    Every setting the API publishes is a field. The CLI has an option for the common ones and
    takes the rest through its repeatable ``--field key=value`` JSON escape, merged onto this
    body. Unset (``None``) fields are dropped before the request is sent. ``language``,
    ``is_published`` and ``is_public`` are accepted and ignored by the API (checked live on
    2026-10-04): they stay for callers that send them, and setting one logs a warning.

    Examples:
        >>> SurveyCreate(name="Onboarding survey", need_auth=True).name
        'Onboarding survey'
    """

    name: str | None = Field(default=None, description="Form name (title).")
    language: str | None = Field(
        default=None,
        description=IGNORED_BY_API + "the reply reports the language, a request cannot set it.",
    )
    texts: SurveyTexts | None = Field(
        default=None, description="Button labels and the post-submission message."
    )
    is_published: bool | None = Field(
        default=None,
        description=IGNORED_BY_API + "publish a form with ``surveys publish`` instead.",
    )
    is_public: bool | None = Field(
        default=None,
        description=IGNORED_BY_API + "the reply reports whether the form is public, a request "
        "cannot set it.",
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
    show_last_answer: bool | None = Field(
        default=None, description="Fill in the respondent's previous answer."
    )
    styles: SurveyStyles | None = Field(default=None, description="Design of the form.")
    quiz: SurveyQuiz | None = Field(default=None, description="Quiz settings.")
    auto_publication: SurveyAutoPublication | None = Field(
        default=None, description="When the form publishes and unpublishes itself."
    )
    api_keys: list[SurveyApiKey] | None = Field(
        default=None, description="API keys the form's integrations use."
    )
    follow: Literal["5m", "1h", "1d"] | str | None = Field(
        default=None, description="How often integration errors are mailed: 5m, 1h or 1d."
    )
    captcha: CaptchaType | None = Field(
        default=None, description="Captcha asked before submission: std, ocr or nbg."
    )
    metric: int | None = Field(default=None, description="Yandex Metrica counter.")
    file_storage: str | None = Field(
        default=None, description="Link to the organization's own file storage."
    )
    validator_url: str | None = Field(
        default=None, description="URL that validates the answers from outside."
    )
    iframe: bool | None = Field(
        default=None, description="Allow publishing the form only in an iframe."
    )
    footer: bool | None = Field(default=None, description="Show the footer.")
    teaser: bool | None = Field(default=None, description="Show the teaser.")
    stats: bool | None = Field(
        default=None, description="Show statistics on the page after submission."
    )
    share: bool | None = Field(default=None, description="Offer sharing the form.")
    fill_again: bool | None = Field(default=None, description="Offer filling the form again.")


class SurveyUpdate(SurveyCreate):
    """Typed request body for modifying a form (``PATCH /surveys/{survey_id}``).

    Same optional fields as :class:`SurveyCreate`; only the fields you set are sent, so a
    partial patch never disturbs untouched settings.

    Examples:
        >>> SurveyUpdate(is_favourite=True).is_favourite
        True
    """

    is_favourite: bool | None = Field(
        default=None, description="Add the form to the caller's favourites, or remove it."
    )
