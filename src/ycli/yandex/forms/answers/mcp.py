"""Forms answers FastMCP tools (reads + writes, honest hints).

``export`` starts the async export job; polling the result and downloading the exported file
(a binary payload) stay CLI/SDK-side (``forms answers export --wait``), though the returned
operation id is also pollable via the generic ``operations_get`` tool.
"""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.forms.answers.models import (
    AnswerDetails,
    AnswerExport,
    AnswerFormat,
    AnswerIntegration,
    AnswersResponse,
)
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    SurveyID,
    app_config,
    forms_client,
    new_server,
)
from ycli.yandex.forms.models import OperationResult
from ycli.yandex.models import Ack, ItemList, SortDirection

mcp = new_server("forms-answers")


@mcp.tool(name="answers_get", annotations={**RO, "title": "Get Forms answer"})
def get(
    answer_id: Annotated[
        int | None,
        Field(description="Numeric answer id (from ``answers_list``; needs form-edit access)."),
    ] = None,
    answer_key: Annotated[
        str | None,
        Field(description="Answer key hash — works without form-edit access."),
    ] = None,
    client: FormsClient = Depends(forms_client),
) -> AnswerDetails:
    """One full form response by ``answer_id`` or ``answer_key`` (the API takes one of them).

    A flat query-param route (``GET /v1/answers``) — no survey id needed. Each ``data``
    item is a self-describing question record (``{id, label, type, value, …}``).
    """
    return client.answers.get(answer_id=answer_id, answer_key=answer_key)


@mcp.tool(name="answers_list", annotations={**RO, "title": "List Forms answers"})
def list_(
    survey_id: SurveyID,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max answers to return; {LIMIT_CAP}")
    ] = None,
    questions: Annotated[
        str | None, Field(description="Comma-separated question ids to return answers for.")
    ] = None,
    use_slugs: Annotated[
        bool | None, Field(description="Name questions and options by slug instead of id.")
    ] = None,
    date_from: Annotated[
        str | None, Field(description="ISO-8601: answers given at or after.")
    ] = None,
    date_to: Annotated[
        str | None, Field(description="ISO-8601: answers given at or before.")
    ] = None,
    ordering: Annotated[
        SortDirection | None,
        Field(description="``asc`` is oldest first; the default is ``desc``."),
    ] = None,
    page_size: Annotated[
        int | None, Field(description="Answers per request (the API's default is 25).")
    ] = None,
    answer_format: Annotated[
        AnswerFormat | None,
        Field(
            description="``default`` (cells aligned to ``columns``) or ``raw`` (each answer's "
            "data as stored, with no ``columns``)."
        ),
    ] = None,
    client: FormsClient = Depends(forms_client),
    config: AppConfig = Depends(app_config),
) -> AnswersResponse:
    """A form's responses, at most ``limit`` (drains pages via the next cursor).

    Returns the ``{columns, answers, next}`` envelope; ``next`` is always ``None``
    in the merged result.
    """
    return client.answers.list(
        survey_id,
        limit=config.http.cap(limit),
        questions=questions,
        use_slugs=use_slugs,
        date_from=date_from,
        date_to=date_to,
        ordering=ordering,
        page_size=page_size,
        answer_format=answer_format,
    )


@mcp.tool(name="answers_export", annotations={**WRITE, "title": "Export Forms answers"})
def export(
    survey_id: SurveyID,
    body: AnswerExport,
    client: FormsClient = Depends(forms_client),
) -> OperationResult:
    """Start an async export of a form's answers (csv/xlsx); returns the operation to poll.

    An empty ``body`` exports every answer as ``xlsx``. Poll the returned ``id`` with
    ``operations_get`` until the status is terminal; download the finished file with the
    ``forms answers export --wait`` CLI command (binary payload — not exposed over MCP).
    """
    return client.answers.export(survey_id, body)


@mcp.tool(
    name="answers_integrations_list",
    annotations={**RO, "title": "List Forms answer integrations"},
)
def integrations_list(
    answer_id: Annotated[
        int | None,
        Field(description="Numeric answer id (from ``answers_list``; needs form-edit access)."),
    ] = None,
    answer_key: Annotated[
        str | None,
        Field(description="Answer key hash — works without form-edit access."),
    ] = None,
    client: FormsClient = Depends(forms_client),
) -> ItemList[AnswerIntegration]:
    """The integration runs one answer triggered, by ``answer_id`` or ``answer_key`` (one of them).

    Each entry has the run's ``status`` and the field of its ``type`` (``issue_key``, ``link``,
    ``to_address``, ``url``, ...); ``notifications_get`` has the full run.
    """
    return client.answers.integrations_list(answer_id=answer_id, answer_key=answer_key)


@mcp.tool(
    name="answers_delete",
    annotations={**DESTRUCTIVE, "title": "Delete a Forms answer"},
)
def delete(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    answer_id: Annotated[int, Field(description="Answer id (integer) from answers_list.")],
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete one answer of a form; ``answers_restore`` brings it back."""
    client.answers.delete(survey_id, answer_id)
    return Ack.deleted("answer", answer_id, from_=f"survey {survey_id}")


@mcp.tool(
    name="answers_restore",
    annotations={**WRITE, "title": "Restore a deleted Forms answer"},
)
def restore(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    answer_id: Annotated[int, Field(description="Id of the deleted answer (integer).")],
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Bring a deleted answer of a form back."""
    client.answers.restore(survey_id, answer_id)
    return Ack.restored("answer", answer_id, in_=f"survey {survey_id}")
