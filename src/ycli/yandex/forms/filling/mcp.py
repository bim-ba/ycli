"""Forms form-filling FastMCP tools (reads + writes, honest hints).

All three endpoints are exposed: the ``get-settings`` and ``suggest`` reads, and the
``submit`` write (posts a real response unless ``dry_run``).
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, WRITE, WRITE_TAGS, forms_client
from ycli.yandex.forms.filling.models import (
    FillableForm,
    SubmitBody,
    SubmitResult,
    SuggestionList,
)
from ycli.yandex.models import require_found

mcp = FastMCP("forms-filling")


@mcp.tool(name="filling_get", annotations={**RO, "title": "Get Forms fillable form"}, tags=TAGS)
def get(
    survey: Annotated[
        str,
        Field(description="Form id, its slug, or an id+verification-key combination."),
    ],
    key: Annotated[
        str | None,
        Field(description="Personal-link fill key, when the form uses one."),
    ] = None,
    client: FormsClient = Depends(forms_client),
) -> FillableForm:
    """The form's fill-time settings — the pages/questions to fill, submit conditions, and values.

    Use this to discover a form's fillable structure: ``pages[].items[]`` are the questions (each a
    polymorphic question schema) and their ``id`` values are the slug keys a response is posted
    under. Complements ``surveys_get`` (admin settings) and ``questions_list`` (authoring view).
    Post a response with ``filling_submit``.

    >>> await client.call_tool(
    ...     "filling_get", {"survey": "686d0a1b2c3d4e5f00000001"}
    ... )  # doctest: +SKIP
    """
    result = client.filling.get(survey, key=key)
    # A 404 / empty body deserializes into an all-None FillableForm (lenient model) rather than
    # raising; turn that into a clean not-found error instead of a phantom empty object.
    return require_found(
        result,
        sentinel=lambda r: r.id is None,
        message=f"fillable form {survey!r} not found (empty response — check the id/slug, "
        "the fill key, or whether the form is published)",
    )


@mcp.tool(
    name="filling_suggest",
    annotations={**RO, "title": "Get Forms fill suggestions"},
    tags=TAGS,
)
def suggest(
    survey: Annotated[str, Field(description="Form id or slug.")],
    question: Annotated[str | None, Field(description="Question slug to suggest for.")] = None,
    text: Annotated[str | None, Field(description="Search text typed so far.")] = None,
    suggest_id: Annotated[
        str | None,
        Field(description="Comma-separated suggestion-object ids to resolve (the API's ``id``)."),
    ] = None,
    parent_id: Annotated[
        str | None, Field(description="Parent object id scoping a Master/Detail lookup.")
    ] = None,
    client: FormsClient = Depends(forms_client),
) -> SuggestionList:
    """Autocomplete prompts for a ``suggest``-type question while filling a form.

    Pass the question ``slug`` (from ``filling_get``) plus the search ``text``; each returned
    item's ``id``/``text`` is a candidate value for the answer.
    """
    return client.filling.suggest(
        survey, question=question, text=text, suggest_id=suggest_id, parent_id=parent_id
    )


@mcp.tool(
    name="filling_submit",
    annotations={**WRITE, "title": "Submit Forms response"},
    tags=WRITE_TAGS,
)
def submit(
    survey: Annotated[str, Field(description="Form id or slug of a published form.")],
    body: Annotated[
        SubmitBody,
        Field(description="Answer map keyed by question slug (see ``filling_get`` for the slugs)."),
    ],
    dry_run: Annotated[
        bool,
        Field(description="Validate only — saves nothing and fires no integrations."),
    ] = False,
    key: Annotated[
        str | None, Field(description="Personal-link fill key, when the form uses one.")
    ] = None,
    client: FormsClient = Depends(forms_client),
) -> SubmitResult:
    """Submit a response to a published form — this saves a REAL answer unless ``dry_run`` is set.

    ``body`` maps each question ``slug`` (discover them via ``filling_get``) to its answer — a
    scalar, a string list, a ``{begin, end}`` date range, or matrix ``{row, column}`` items.
    Returns the success-page payload (``answer_id`` confirms the save).
    """
    return client.filling.submit(survey, body, dry_run=dry_run, key=key)
