"""Forms variables FastMCP tool (a read)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, forms_client, new_server
from ycli.yandex.forms.variables.models import VariableInfo
from ycli.yandex.models import ItemList

mcp = new_server("forms-variables")


@mcp.tool(
    name="variables_list",
    annotations={**RO, "title": "List Forms integration variables"},
)
def list_(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    client: FormsClient = Depends(forms_client),
) -> ItemList[VariableInfo]:
    """The variable types a form's integrations can reference in their texts.

    Each item names a ``type`` (e.g. ``form.answer_url``, ``form.question_answer``), the
    arguments it takes and the renderers it supports; put one into a subscription's
    ``variables`` to use it.
    """
    return client.variables.list(survey_id)
