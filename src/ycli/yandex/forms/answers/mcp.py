"""Forms answers FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.forms._deps import RO, TAGS, forms_client
from ycli.yandex.forms.answers.models import AnswersResponse
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.settings import AppConfig

mcp = FastMCP("forms-answers")


@mcp.tool(name="answers_list", annotations={**RO, "title": "List Forms answers"}, tags=TAGS)
def list_(survey_id: str, client: FormsClient = Depends(forms_client)) -> AnswersResponse:  # noqa: B008 — FastMCP resolves Depends at call time, not definition time
    """A form's responses, capped at AppConfig().max_items (drains pages via the next cursor).

    Returns the ``{columns, answers, next}`` envelope; ``next`` is always ``None``
    in the merged result. Use the CLI ``--all`` flag for an uncapped drain.
    """
    return client.answers.list_all(survey_id, limit=AppConfig().max_items)
