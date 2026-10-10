"""Forms /surveys FastMCP tools (reads + writes, honest hints)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    All,
    Next,
    SurveyID,
    app_config,
    forms_client,
    new_server,
)
from ycli.yandex.forms.surveys.models import Survey, SurveyCreate, SurveyUpdate
from ycli.yandex.models import Ack, Listed

mcp = new_server("forms-surveys")


@mcp.tool(name="surveys_list", annotations={**RO, "title": "List Forms surveys"})
def list_(
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max forms to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    name: Annotated[str | None, Field(description="Keep the forms whose name matches.")] = None,
    published: Annotated[
        bool | None, Field(description="Only published (true) or only unpublished (false).")
    ] = None,
    ownership: Annotated[
        str | None,
        Field(description="``mine`` (created by the caller) or ``shared`` (open to them)."),
    ] = None,
    group: Annotated[str | None, Field(description="Keep the forms of this group.")] = None,
    favourite: Annotated[
        bool | None, Field(description="Only favourites (true) or only the others (false).")
    ] = None,
    show_all: Annotated[
        bool | None, Field(description="For an administrator, every form of the organization.")
    ] = None,
    orderby: Annotated[
        str | None, Field(description="Sort, a comma list such as ``name,-modified,-count``.")
    ] = None,
    client: FormsClient = Depends(forms_client),
    config: AppConfig = Depends(app_config),
) -> Listed[Survey]:
    """Every form (survey) the caller can see, auto-paginated over the API's offset pages.

    Capped at the configured item cap unless ``limit`` is given. Each item's ``id`` is the
    form id you pass to ``surveys_get`` / ``questions_list`` / ``answers_list``.
    """
    cap = config.http.tool_cap(limit, all_=all)
    return client.surveys.list(
        limit=cap,
        next=next,
        name=name,
        published=published,
        ownership=ownership,
        group=group,
        favourite=favourite,
        show_all=show_all,
        orderby=orderby,
    ).collect()


@mcp.tool(name="surveys_get", annotations={**RO, "title": "Get Forms survey"})
def get(survey_id: SurveyID, client: FormsClient = Depends(forms_client)) -> Survey:
    """One form's settings by id."""
    return client.surveys.get(survey_id)


@mcp.tool(name="surveys_create", annotations={**WRITE, "title": "Create Forms survey"})
def create(body: SurveyCreate, client: FormsClient = Depends(forms_client)) -> Survey:
    """Create a new form from the given settings; returns the created ``Survey`` (note its ``id``).

    Only the fields you set are sent. Follow up with ``questions_create`` to add questions and
    ``surveys_publish`` to make the form fillable.
    """
    return client.surveys.create(body)


@mcp.tool(
    name="surveys_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms survey"},
)
def update(
    survey_id: SurveyID, body: SurveyUpdate, client: FormsClient = Depends(forms_client)
) -> Survey:
    """Patch a form's settings — only the fields set in ``body`` change; returns the ``Survey``.

    Untouched settings keep their current values, so a partial patch is safe to repeat.
    """
    return client.surveys.update(survey_id, body)


@mcp.tool(
    name="surveys_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms survey"},
)
def delete(survey_id: SurveyID, client: FormsClient = Depends(forms_client)) -> Ack:
    """Delete a form permanently — IRREVERSIBLE: its questions and collected answers are lost.

    The API answers ``204 No Content``; the returned record confirms the accepted action.
    """
    return client.surveys.delete(survey_id)


@mcp.tool(name="surveys_publish", annotations={**WRITE, "title": "Publish Forms survey"})
def publish(survey_id: SurveyID, client: FormsClient = Depends(forms_client)) -> Ack:
    """Publish a form so respondents can fill it; fails if the form is blocked or at its cap.

    The API answers a bare ``200 OK``; the returned record confirms the accepted action.
    Reverse with ``surveys_unpublish``.
    """
    return client.surveys.publish(survey_id)


@mcp.tool(
    name="surveys_unpublish",
    annotations={**WRITE, "title": "Unpublish Forms survey"},
)
def unpublish(survey_id: SurveyID, client: FormsClient = Depends(forms_client)) -> Ack:
    """Take a published form offline (respondents can no longer fill it); reversible via publish.

    The API answers a bare ``200 OK``; the returned record confirms the accepted action.
    """
    return client.surveys.unpublish(survey_id)
