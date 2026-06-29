"""Forms answers FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.settings import AppConfig
from ycli.yandex.forms._deps import RO, TAGS, app_config, forms_client
from ycli.yandex.forms.answers.models import AnswersResponse
from ycli.yandex.forms.client import FormsClient

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
