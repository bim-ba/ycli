"""Forms /surveys FastMCP tools (reads-only)."""
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.forms._deps import RO, TAGS, forms_client
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.surveys.models import Survey, SurveyList

mcp = FastMCP("forms-surveys")


@mcp.tool(name="surveys_list", annotations={**RO, "title": "List Forms surveys"}, tags=TAGS)
def list_(client: FormsClient = Depends(forms_client)) -> SurveyList:
    """Every form (survey) the caller can see (the {links, result} envelope)."""
    return client.surveys.list()


@mcp.tool(name="surveys_get", annotations={**RO, "title": "Get Forms survey"}, tags=TAGS)
def get(survey_id: str, client: FormsClient = Depends(forms_client)) -> Survey:
    """One form's settings by id."""
    result = client.surveys.get(survey_id)
    # A 404 deserializes into an all-None Survey (lenient model) rather than raising;
    # turn that into a clean not-found error instead of a phantom empty object.
    if result.id is None:
        raise ValueError(f"survey {survey_id!r} not found (got empty response — check id or permissions)")
    return result
