"""Forms access (survey permissions) FastMCP tools (reads + writes, honest hints)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.access.models import AccessGrant, AccessRevoke, AccessUpdate, PermissionList
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    forms_client,
)

mcp = FastMCP("forms-access")

SurveyId = Annotated[str, Field(description="Form id (24-char hex).")]


@mcp.tool(name="access_get", annotations={**RO, "title": "Get Forms survey access"}, tags=TAGS)
def get(survey_id: SurveyId, client: FormsClient = Depends(forms_client)) -> PermissionList:
    """Who may edit (``change``) and who may fill (``submit``) a form, one entry per action.

    ``access`` is owner, restricted (the listed ``users``/``groups``), common (the whole
    organization) or public (anyone with the link).
    """
    return client.access.get(survey_id)


@mcp.tool(
    name="access_set",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Forms survey access level"},
    tags=WRITE_TAGS,
)
def set_(
    survey_id: SurveyId,
    body: Annotated[AccessUpdate, Field(description="The action and its new access level.")],
    client: FormsClient = Depends(forms_client),
) -> PermissionList:
    """Set the access level of one action (change or submit); returns every permission."""
    return client.access.set(survey_id, body.model_dump())


@mcp.tool(
    name="access_grant",
    annotations={**WRITE_IDEMPOTENT, "title": "Grant Forms survey access"},
    tags=WRITE_TAGS,
)
def grant(
    survey_id: SurveyId,
    body: Annotated[AccessGrant, Field(description="The action and the user or group to add.")],
    client: FormsClient = Depends(forms_client),
) -> PermissionList:
    """Let a user or a group perform an action on a form; returns every permission.

    Granting someone who already has the action changes nothing.
    """
    return client.access.grant(survey_id, body.model_dump(exclude_none=True))


@mcp.tool(
    name="access_revoke",
    annotations={**DESTRUCTIVE, "title": "Revoke Forms survey access"},
    tags=WRITE_TAGS,
)
def revoke(
    survey_id: SurveyId,
    body: Annotated[AccessRevoke, Field(description="The action and the user or group to remove.")],
    client: FormsClient = Depends(forms_client),
) -> PermissionList:
    """Stop a user or a group performing an action on a form; returns every permission."""
    return client.access.revoke(survey_id, body.model_dump(exclude_none=True))
