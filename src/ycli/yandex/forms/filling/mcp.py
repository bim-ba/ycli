"""Forms form-filling FastMCP tools (reads-only).

Only ``get-settings`` is exposed here (verb ``get``); ``submit`` is a write and ``suggest``'s verb
is not an MCP read verb, so both stay CLI/SDK-only.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, forms_client
from ycli.yandex.forms.filling.models import FillableForm

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
    Submitting a response is a write — use the ``forms filling submit`` CLI, not MCP.

    >>> await client.call_tool(
    ...     "filling_get", {"survey": "686d0a1b2c3d4e5f00000001"}
    ... )  # doctest: +SKIP
    """
    result = client.filling.get(survey, key=key)
    # A 404 / empty body deserializes into an all-None FillableForm (lenient model) rather than
    # raising; turn that into a clean not-found error instead of a phantom empty object.
    if result.id is None:
        raise ValueError(
            f"fillable form {survey!r} not found (empty response — check the id/slug, "
            "the fill key, or whether the form is published)"
        )
    return result
