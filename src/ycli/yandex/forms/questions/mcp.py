"""Forms questions FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.forms._deps import RO, TAGS, forms_client
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.questions.models import QuestionsResponse

mcp = FastMCP("forms-questions")


@mcp.tool(name="questions_list", annotations={**RO, "title": "List Forms questions"}, tags=TAGS)
def list_(survey_id: str, client: FormsClient = Depends(forms_client)) -> QuestionsResponse:  # noqa: B008 — FastMCP resolves Depends at call time, not definition time
    """A form's questions, grouped into pages (the {pages} envelope)."""
    return client.questions.list(survey_id)
