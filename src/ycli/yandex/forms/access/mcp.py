"""Forms access (survey permissions) FastMCP tools (reads + writes, honest hints)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.access.models import AccessGrant, AccessRevoke, AccessUpdate, Permission
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    GRANTS_ACCESS,
    RO,
    WRITE_IDEMPOTENT,
    SurveyID,
    forms_client,
    new_server,
)
from ycli.yandex.models import ItemList

mcp = new_server("forms-access")


@mcp.tool(name="access_list", annotations={**RO, "title": "Get Forms survey access"})
def list_(survey_id: SurveyID, client: FormsClient = Depends(forms_client)) -> ItemList[Permission]:
    """Who may edit (``change``) and who may fill (``submit``) a form, one entry per action.

    ``access`` is owner, restricted (the listed ``users``/``groups``), common (the whole
    organization) or public (anyone with the link).
    """
    return client.access.list(survey_id)


@mcp.tool(
    name="access_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Forms survey access level"},
    meta=GRANTS_ACCESS,
)
def update(
    survey_id: SurveyID,
    body: Annotated[AccessUpdate, Field(description="The action and its new access level.")],
    client: FormsClient = Depends(forms_client),
) -> ItemList[Permission]:
    """Set the access level of one action (change or submit); returns every permission."""
    return client.access.update(survey_id, body)


@mcp.tool(
    name="access_grant",
    annotations={**WRITE_IDEMPOTENT, "title": "Grant Forms survey access"},
    meta=GRANTS_ACCESS,
)
def grant(
    survey_id: SurveyID,
    body: Annotated[AccessGrant, Field(description="The action and the user or group to add.")],
    client: FormsClient = Depends(forms_client),
) -> ItemList[Permission]:
    """Let a user or a group perform an action on a form; returns every permission.

    Granting someone who already has the action changes nothing.
    """
    return client.access.grant(survey_id, body)


@mcp.tool(
    name="access_revoke",
    annotations={**DESTRUCTIVE, "title": "Revoke Forms survey access"},
)
def revoke(
    survey_id: SurveyID,
    body: Annotated[AccessRevoke, Field(description="The action and the user or group to remove.")],
    client: FormsClient = Depends(forms_client),
) -> ItemList[Permission]:
    """Stop a user or a group performing an action on a form; returns every permission."""
    return client.access.revoke(survey_id, body)
