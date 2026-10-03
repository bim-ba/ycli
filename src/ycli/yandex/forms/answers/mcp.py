"""Forms answers FastMCP tools (reads + writes, honest hints).

``export`` starts the async export job; polling the result and downloading the exported file
(a binary payload) stay CLI/SDK-side (``forms answers export --wait``), though the returned
operation id is also pollable via the generic ``operations_get`` tool.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.forms.answers.models import (
    AnswerDetails,
    AnswerExport,
    AnswerIntegration,
    AnswersResponse,
)
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_TAGS,
    SurveyId,
    app_config,
    forms_client,
)
from ycli.yandex.forms.models import OperationResult
from ycli.yandex.models import Ack, ItemList

mcp = FastMCP("forms-answers")


@mcp.tool(name="answers_get", annotations={**RO, "title": "Get Forms answer"}, tags=TAGS)
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
    """One full form response by ``answer_id`` or ``answer_key`` (exactly one required).

    A flat query-param route (``GET /v1/answers``) — no survey id needed. Each ``data``
    item is a self-describing question record (``{id, label, type, value, …}``).
    """
    return client.answers.get(answer_id=answer_id, answer_key=answer_key)


@mcp.tool(name="answers_list", annotations={**RO, "title": "List Forms answers"}, tags=TAGS)
def list_(
    survey_id: SurveyId,
    questions: Annotated[
        str, Field(description="Comma-separated question ids to return answers for.")
    ] = "",
    use_slugs: Annotated[
        bool, Field(description="Name questions and options by slug instead of id.")
    ] = False,
    date_from: Annotated[str, Field(description="ISO-8601: answers given at or after.")] = "",
    date_to: Annotated[str, Field(description="ISO-8601: answers given at or before.")] = "",
    ordering: Annotated[
        str, Field(description="``asc`` (oldest first) or ``desc`` (the default).")
    ] = "",
    page_size: Annotated[
        int | None, Field(description="Answers per request (the API's default is 25).")
    ] = None,
    answer_format: Annotated[
        str,
        Field(
            description="``default`` (cells aligned to ``columns``) or ``raw`` (each answer's "
            "data as stored, with no ``columns``)."
        ),
    ] = "",
    client: FormsClient = Depends(forms_client),
    config: AppConfig = Depends(app_config),
) -> AnswersResponse:
    """A form's responses, capped at config.http.max_items (drains pages via the next cursor).

    Returns the ``{columns, answers, next}`` envelope; ``next`` is always ``None``
    in the merged result. Use the CLI ``--all`` flag for an uncapped drain.
    """
    return client.answers.list_all(
        survey_id,
        limit=config.http.max_items,
        questions=questions or None,
        use_slugs=use_slugs,
        date_from=date_from or None,
        date_to=date_to or None,
        ordering=ordering or None,
        page_size=page_size,
        answer_format=answer_format or None,
    )


@mcp.tool(
    name="answers_export", annotations={**WRITE, "title": "Export Forms answers"}, tags=WRITE_TAGS
)
def export(
    survey_id: SurveyId,
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
    tags=TAGS,
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
    """The integration runs one answer triggered, by ``answer_id`` or ``answer_key`` (exactly one).

    Each entry has the run's ``status`` and the field of its ``type`` (``issue_key``, ``link``,
    ``to_address``, ``url``, ...); ``notifications_get`` has the full run.
    """
    return client.answers.integrations_list(answer_id=answer_id, answer_key=answer_key)


@mcp.tool(
    name="answers_delete",
    annotations={**DESTRUCTIVE, "title": "Delete a Forms answer"},
    tags=WRITE_TAGS,
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
    tags=WRITE_TAGS,
)
def restore(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    answer_id: Annotated[int, Field(description="Id of the deleted answer (integer).")],
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Bring a deleted answer of a form back."""
    client.answers.restore(survey_id, answer_id)
    return Ack.restored("answer", answer_id, in_=f"survey {survey_id}")
