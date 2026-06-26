"""Forms answers FastMCP tool (reads-only)."""
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.forms._deps import RO, TAGS, forms_client
from ycli.yandex.forms.answers.models import AnswersResponse
from ycli.yandex.forms.client import FormsClient

mcp = FastMCP("forms-answers")


@mcp.tool(name="answers_list", annotations=RO, tags=TAGS)
def list_(survey_id: str, client: FormsClient = Depends(forms_client)) -> AnswersResponse:
    """A form's responses (columns + answers + next cursor)."""
    return client.answers.list(survey_id)
