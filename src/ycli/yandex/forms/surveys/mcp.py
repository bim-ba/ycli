"""Forms /surveys FastMCP tools (reads + writes, honest hints)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    app_config,
    forms_client,
)
from ycli.yandex.forms.surveys.models import (
    Survey,
    SurveyActionResult,
    SurveyCreate,
    SurveyList,
    SurveyUpdate,
)
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


@mcp.tool(
    name="surveys_create", annotations={**WRITE, "title": "Create Forms survey"}, tags=WRITE_TAGS
)
def create(body: SurveyCreate, client: FormsClient = Depends(forms_client)) -> Survey:
    """Create a new form from the given settings; returns the created ``Survey`` (note its ``id``).

    Only the fields you set are sent. Follow up with ``questions_create`` to add questions and
    ``surveys_publish`` to make the form fillable.
    """
    return client.surveys.create(body.model_dump(exclude_none=True))


@mcp.tool(
    name="surveys_modify",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms survey"},
    tags=WRITE_TAGS,
)
def modify(
    survey_id: str, body: SurveyUpdate, client: FormsClient = Depends(forms_client)
) -> Survey:
    """Patch a form's settings — only the fields set in ``body`` change; returns the ``Survey``.

    Untouched settings keep their current values, so a partial patch is safe to repeat.
    """
    return client.surveys.modify(survey_id, body.model_dump(exclude_none=True))


@mcp.tool(
    name="surveys_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms survey"},
    tags=WRITE_TAGS,
)
def delete(survey_id: str, client: FormsClient = Depends(forms_client)) -> SurveyActionResult:
    """Delete a form permanently — IRREVERSIBLE: its questions and collected answers are lost.

    The API answers ``204 No Content``; the returned record confirms the accepted action.
    """
    return client.surveys.delete(survey_id)


@mcp.tool(
    name="surveys_publish", annotations={**WRITE, "title": "Publish Forms survey"}, tags=WRITE_TAGS
)
def publish(survey_id: str, client: FormsClient = Depends(forms_client)) -> SurveyActionResult:
    """Publish a form so respondents can fill it; fails if the form is blocked or at its cap.

    The API answers a bare ``200 OK``; the returned record confirms the accepted action.
    Reverse with ``surveys_unpublish``.
    """
    return client.surveys.publish(survey_id)


@mcp.tool(
    name="surveys_unpublish",
    annotations={**WRITE, "title": "Unpublish Forms survey"},
    tags=WRITE_TAGS,
)
def unpublish(survey_id: str, client: FormsClient = Depends(forms_client)) -> SurveyActionResult:
    """Take a published form offline (respondents can no longer fill it); reversible via publish.

    The API answers a bare ``200 OK``; the returned record confirms the accepted action.
    """
    return client.surveys.unpublish(survey_id)
