"""Forms questions FastMCP tools (reads + writes, honest hints)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    SurveyId,
    forms_client,
)
from ycli.yandex.forms.questions.models import (
    FORCE_IGNORED,
    Question,
    QuestionCreate,
    QuestionMove,
    QuestionMoveResult,
    QuestionsResponse,
)
from ycli.yandex.models import IGNORED_BY_API, Ack, require_found

mcp = FastMCP("forms-questions")


@mcp.tool(name="questions_list", annotations={**RO, "title": "List Forms questions"})
def list_(survey_id: SurveyId, client: FormsClient = Depends(forms_client)) -> QuestionsResponse:
    """A form's questions, grouped into pages (the {pages} envelope)."""
    return client.questions.list(survey_id)


@mcp.tool(name="questions_get", annotations={**RO, "title": "Get Forms question"})
def get(
    survey_id: Annotated[str, Field(description="Form id (hex ObjectId) the question belongs to.")],
    question_id: Annotated[str, Field(description="Question id (integer) to fetch.")],
    with_slugs: Annotated[
        bool, Field(description="Refer to other questions by slug instead of id.")
    ] = False,
    client: FormsClient = Depends(forms_client),
) -> Question:
    """One question's settings by id — label, slug, type and common presentation flags.

    Where ``questions_list`` returns every question grouped into pages, this fetches a single
    question keyed by ``question_id`` (take it from an item's ``id`` in ``questions_list``).
    Type-specific detail (validators, options, conditions) comes in the fields of its type.
    """
    result = client.questions.get(survey_id, question_id, with_slugs=with_slugs)
    # A 404 / empty body deserializes into an all-None Question (lenient model) rather than
    # raising; turn that into a clean not-found error instead of a phantom empty object.
    return require_found(
        result,
        sentinel=lambda r: r.id is None,
        message=f"question {question_id!r} not found in survey {survey_id!r} "
        "(empty response — check ids or permissions)",
    )


@mcp.tool(
    name="questions_create",
    annotations={**WRITE, "title": "Create Forms question"},
)
def create(
    survey_id: Annotated[str, Field(description="Form id (hex ObjectId) to add the question to.")],
    body: Annotated[
        QuestionCreate,
        Field(description="Typed question body; the ``type`` tag selects the question schema."),
    ],
    client: FormsClient = Depends(forms_client),
) -> Question:
    """Append a question to a form; returns the created ``Question`` (note its ``id``).

    ``body`` is one of the 12 typed question schemas discriminated by ``type`` (``string``,
    ``enum``, ``matrix``, …). The new question lands at the end of the form — reposition it
    afterwards with ``questions_move``.
    """
    return client.questions.create(survey_id, body)


@mcp.tool(
    name="questions_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms question"},
)
def update(
    survey_id: Annotated[str, Field(description="Form id (hex ObjectId) the question belongs to.")],
    question_id: Annotated[str, Field(description="Question id (integer) to modify.")],
    body: Annotated[
        QuestionCreate,
        Field(description="Typed question body; ``type`` must match the existing question."),
    ],
    client: FormsClient = Depends(forms_client),
) -> Question:
    """Replace a question's settings (same typed body as create); returns the updated ``Question``.

    The body's ``type`` must match the existing question's type; look it up with
    ``questions_get`` first.
    """
    return client.questions.update(survey_id, question_id, body)


@mcp.tool(
    name="questions_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms question"},
)
def delete(
    survey_id: Annotated[str, Field(description="Form id (hex ObjectId) the question belongs to.")],
    question_id: Annotated[str, Field(description="Question id (integer) to delete.")],
    force: Annotated[
        bool,
        Field(description=IGNORED_BY_API + FORCE_IGNORED),
    ] = False,
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete a question from a form; one that a display condition refers to is refused.

    Delete the condition first (``conditions_question_delete``).

    The API answers ``204 No Content``; the returned record confirms the accepted action.
    """
    return client.questions.delete(survey_id, question_id, force=force)


@mcp.tool(name="questions_move", annotations={**WRITE, "title": "Move Forms question"})
def move(
    survey_id: Annotated[str, Field(description="Form id (hex ObjectId) the question belongs to.")],
    question_id: Annotated[str, Field(description="Question id (integer) to reposition.")],
    body: Annotated[
        QuestionMove,
        Field(description="Target placement: page / page_id / create_page and position."),
    ],
    client: FormsClient = Depends(forms_client),
) -> QuestionMoveResult:
    """Reposition a question on the form (target page + position); returns the moved question's id.

    ``body.position`` needs a page target to take effect — the underlying API silently ignores
    a bare position (200, nothing moves) — so ``QuestionMove`` raises a validation error if
    ``position`` is set with no ``page`` / ``page_id`` / ``question`` / ``create_page`` target;
    pass one explicitly (e.g. ``page=1``). Display-condition consistency is validated
    server-side — moving a question above one its conditions depend on is rejected.
    """
    return client.questions.move(survey_id, question_id, body)
