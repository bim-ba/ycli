"""Forms /surveys FastMCP tools (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, app_config, forms_client
from ycli.yandex.forms.surveys.models import Survey, SurveyList
from ycli.yandex.pagination import resolve_cap

mcp = FastMCP("forms-surveys")


@mcp.tool(name="surveys_list", annotations={**RO, "title": "List Forms surveys"}, tags=TAGS)
def list_(
    limit: int = 0,
    client: FormsClient = Depends(forms_client),
    cfg: AppConfig = Depends(app_config),
) -> SurveyList:
    """Every form (survey) the caller can see, auto-paginated over the API's offset pages.

    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given. Each item's ``id`` is the
    form id you pass to ``surveys_get`` / ``questions_list`` / ``answers_list``.
    """
    cap = resolve_cap(limit, cfg.max_items)
    return client.surveys.list(limit=cap)


@mcp.tool(name="surveys_get", annotations={**RO, "title": "Get Forms survey"}, tags=TAGS)
def get(survey_id: str, client: FormsClient = Depends(forms_client)) -> Survey:
    """One form's settings by id."""
    result = client.surveys.get(survey_id)
    # A 404 deserializes into an all-None Survey (lenient model) rather than raising;
    # turn that into a clean not-found error instead of a phantom empty object.
    if result.id is None:
        raise ValueError(
            f"survey {survey_id!r} not found (got empty response — check id or permissions)"
        )
    return result
