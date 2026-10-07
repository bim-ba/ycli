"""Forms MCP resources: what a user attaches, each repeating one read tool."""

from fastmcp.dependencies import Depends
from fastmcp.resources import ResourceContent

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import TAGS, forms_client
from ycli.yandex.forms.surveys.mcp import get as surveys_get
from ycli.yandex.mcp import REPEATS_TOOL, guide, new_server

mcp = new_server("forms-resources")


@mcp.resource(
    "ycli://survey/{survey_id}",
    name="survey",
    title="Forms survey",
    mime_type="application/json",
    tags=TAGS,
    meta={REPEATS_TOOL: "forms_surveys_get"},
)
def survey(survey_id: str, client: FormsClient = Depends(forms_client)) -> list[ResourceContent]:
    """One form's settings by id, as ``forms_surveys_get`` returns them."""
    return [ResourceContent(surveys_get(survey_id, client=client))]


@mcp.resource(
    "ycli://guide",
    name="guide",
    title="How to work with Yandex Forms through ycli",
    mime_type="text/markdown",
    tags=TAGS,
)
def forms_guide() -> str:
    """How to work with Yandex Forms through these tools: what to call for what, and the traps."""
    return guide("ycli.yandex.forms.mcp")
