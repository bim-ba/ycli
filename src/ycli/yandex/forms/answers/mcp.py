"""Forms answers FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.forms.answers.models import AnswerDetail, AnswersResponse
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, app_config, forms_client

mcp = FastMCP("forms-answers")


@mcp.tool(name="answers_list", annotations={**RO, "title": "List Forms answers"}, tags=TAGS)
def list_(
    survey_id: str,
    client: FormsClient = Depends(forms_client),
    cfg: AppConfig = Depends(app_config),
) -> AnswersResponse:
    """A form's responses, capped at cfg.max_items (drains pages via the next cursor).

    Returns the ``{columns, answers, next}`` envelope; ``next`` is always ``None``
    in the merged result. Use the CLI ``--all`` flag for an uncapped drain.
    """
    return client.answers.list_all(survey_id, limit=cfg.max_items)


@mcp.tool(name="answers_get", annotations={**RO, "title": "Get Forms answer"}, tags=TAGS)
def get(
    survey_id: Annotated[str, Field(description="Form id (hex ObjectId) the response belongs to.")],
    answer_id: Annotated[str, Field(description="Response id (integer) to fetch.")],
    client: FormsClient = Depends(forms_client),
) -> AnswerDetail:
    """One form response in full detail — the answer to every question plus quiz scoring.

    Where ``answers_list`` returns a flat positional table across all responses, this
    returns a single response keyed by ``answer_id`` with a per-question ``data`` array
    (label, type, value, scores). Take the ``answer_id`` from an item's ``id`` in
    ``answers_list``.

    >>> await client.call_tool(
    ...     "answers_get", {"survey_id": "686d0a1b", "answer_id": "99"}
    ... )  # doctest: +SKIP
    """
    result = client.answers.get(survey_id, answer_id)
    # A 404 / empty body deserializes into an all-None AnswerDetail (lenient model) rather
    # than raising; turn that into a clean not-found error instead of a phantom empty object.
    if result.id is None:
        raise ValueError(
            f"answer {answer_id!r} not found in survey {survey_id!r} "
            "(empty response — check ids or permissions)"
        )
    return result
