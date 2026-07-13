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
    AnswersResponse,
    ExportResult,
)
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, WRITE, WRITE_TAGS, app_config, forms_client

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
    survey_id: str,
    client: FormsClient = Depends(forms_client),
    config: AppConfig = Depends(app_config),
) -> AnswersResponse:
    """A form's responses, capped at config.max_items (drains pages via the next cursor).

    Returns the ``{columns, answers, next}`` envelope; ``next`` is always ``None``
    in the merged result. Use the CLI ``--all`` flag for an uncapped drain.
    """
    return client.answers.list_all(survey_id, limit=config.max_items)


@mcp.tool(
    name="answers_export", annotations={**WRITE, "title": "Export Forms answers"}, tags=WRITE_TAGS
)
def export(
    survey_id: str,
    body: AnswerExport,
    client: FormsClient = Depends(forms_client),
) -> ExportResult:
    """Start an async export of a form's answers (csv/xlsx); returns the operation to poll.

    An empty ``body`` exports every answer as ``xlsx``. Poll the returned ``id`` with
    ``operations_get`` until the status is terminal; download the finished file with the
    ``forms answers export --wait`` CLI command (binary payload — not exposed over MCP).
    """
    return client.answers.export(survey_id, body.model_dump(exclude_none=True))
