"""Forms integration groups (hooks) FastMCP tools (reads + writes, honest hints)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    SurveyId,
    forms_client,
)
from ycli.yandex.forms.hooks.models import Hook, HookCreate, HookList, HookUpdate
from ycli.yandex.models import Ack, require_found

mcp = FastMCP("forms-hooks")

HookId = Annotated[int, Field(description="Integration group id (integer) from hooks_list.")]


@mcp.tool(
    name="hooks_list", annotations={**RO, "title": "List Forms integration groups"}, tags=TAGS
)
def list_(survey_id: SurveyId, client: FormsClient = Depends(forms_client)) -> HookList:
    """A form's integration groups, each with its conditions and integrations.

    An integration group (hook) runs its active integrations on every new answer that matches
    its conditions; ``conditions_hook_*`` edit the conditions, ``subscriptions_*`` the
    integrations.
    """
    return client.hooks.list(survey_id)


@mcp.tool(name="hooks_get", annotations={**RO, "title": "Get Forms integration group"}, tags=TAGS)
def get(survey_id: SurveyId, hook_id: HookId, client: FormsClient = Depends(forms_client)) -> Hook:
    """One integration group by id, with its conditions and integrations."""
    result = client.hooks.get(survey_id, hook_id)
    return require_found(
        result,
        sentinel=lambda r: r.id is None,
        message=f"hook {hook_id!r} not found in survey {survey_id!r} "
        "(empty response — check ids or permissions)",
    )


@mcp.tool(
    name="hooks_create",
    annotations={**WRITE, "title": "Create Forms integration group"},
    tags=WRITE_TAGS,
)
def create(
    survey_id: SurveyId,
    body: Annotated[HookCreate, Field(description="Group name and active flag (both optional).")],
    client: FormsClient = Depends(forms_client),
) -> Hook:
    """Create an empty integration group on a form; returns it with its integer ``id``.

    Add integrations with ``subscriptions_create`` and conditions with
    ``conditions_hook_create``.
    """
    return client.hooks.create(survey_id, body.model_dump(exclude_none=True))


@mcp.tool(
    name="hooks_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms integration group"},
    tags=WRITE_TAGS,
)
def modify(
    survey_id: SurveyId,
    hook_id: HookId,
    body: Annotated[HookUpdate, Field(description="Fields to change; unset ones stay.")],
    client: FormsClient = Depends(forms_client),
) -> Hook:
    """Rename an integration group or switch it on or off; only the fields set change."""
    return client.hooks.modify(survey_id, hook_id, body.model_dump(exclude_none=True))


@mcp.tool(
    name="hooks_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms integration group"},
    tags=WRITE_TAGS,
)
def delete(
    survey_id: SurveyId, hook_id: HookId, client: FormsClient = Depends(forms_client)
) -> Ack:
    """Delete an integration group together with its integrations and conditions."""
    client.hooks.delete(survey_id, hook_id)
    return Ack.deleted("hook", hook_id, from_=f"survey {survey_id}")
