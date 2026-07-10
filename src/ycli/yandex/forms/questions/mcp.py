"""Forms questions FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, forms_client
from ycli.yandex.forms.questions.models import Question, QuestionsResponse

mcp = FastMCP("forms-questions")


@mcp.tool(name="questions_list", annotations={**RO, "title": "List Forms questions"}, tags=TAGS)
def list_(survey_id: str, client: FormsClient = Depends(forms_client)) -> QuestionsResponse:
    """A form's questions, grouped into pages (the {pages} envelope)."""
    return client.questions.list(survey_id)


@mcp.tool(name="questions_get", annotations={**RO, "title": "Get Forms question"}, tags=TAGS)
def get(
    survey_id: Annotated[str, Field(description="Form id (hex ObjectId) the question belongs to.")],
    question_id: Annotated[str, Field(description="Question id (integer) to fetch.")],
    client: FormsClient = Depends(forms_client),
) -> Question:
    """One question's settings by id — label, slug, type and common presentation flags.

    Where ``questions_list`` returns every question grouped into pages, this fetches a single
    question keyed by ``question_id`` (take it from an item's ``id`` in ``questions_list``).
    Type-specific detail (validators, options, conditions) is lenient-ignored.

    >>> await client.call_tool(
    ...     "questions_get", {"survey_id": "686d0a1b", "question_id": "17"}
    ... )  # doctest: +SKIP
    """
    result = client.questions.get(survey_id, question_id)
    # A 404 / empty body deserializes into an all-None Question (lenient model) rather than
    # raising; turn that into a clean not-found error instead of a phantom empty object.
    if result.id is None:
        raise ValueError(
            f"question {question_id!r} not found in survey {survey_id!r} "
            "(empty response — check ids or permissions)"
        )
    return result
