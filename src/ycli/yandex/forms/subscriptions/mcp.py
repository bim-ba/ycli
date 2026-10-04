"""Forms integrations (subscriptions) FastMCP tools (reads + writes, honest hints).

Uploading a fixed attachment is a binary payload and stays CLI/SDK-only.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    HookID,
    SurveyID,
    forms_client,
)
from ycli.yandex.forms.subscriptions.models import Subscription
from ycli.yandex.models import Ack, ItemList

mcp = FastMCP("forms-subscriptions")

SubscriptionID = Annotated[
    int, Field(description="Integration id (integer) from subscriptions_list.")
]


@mcp.tool(name="subscriptions_list", annotations={**RO, "title": "List Forms integrations"})
def list_(
    survey_id: SurveyID, hook_id: HookID, client: FormsClient = Depends(forms_client)
) -> ItemList[Subscription]:
    """Every integration of an integration group (hook), each tagged by ``type``.

    Types: email, tracker, tracker_comment, wiki, jsonrpc, http, function. ``hooks_list``
    returns the same integrations nested in each hook.
    """
    return client.subscriptions.list(survey_id, hook_id)


@mcp.tool(name="subscriptions_get", annotations={**RO, "title": "Get Forms integration"})
def get(
    survey_id: SurveyID,
    hook_id: HookID,
    subscription_id: SubscriptionID,
    client: FormsClient = Depends(forms_client),
) -> Subscription:
    """One integration of a hook by id, with its type-specific settings."""
    return client.subscriptions.get(survey_id, hook_id, subscription_id)


@mcp.tool(
    name="subscriptions_create",
    annotations={**WRITE, "title": "Create Forms integration"},
)
def create(
    survey_id: SurveyID,
    hook_id: HookID,
    body: Annotated[
        Subscription, Field(description="The integration; ``type`` selects its schema.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Subscription:
    """Add an integration to a hook; it runs on every new answer while ``active`` is true.

    Create it with ``active: false`` to configure it without sending anything yet. Returns the
    integration with its integer ``id``.
    """
    return client.subscriptions.create(survey_id, hook_id, body)


@mcp.tool(
    name="subscriptions_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms integration"},
)
def update(
    survey_id: SurveyID,
    hook_id: HookID,
    subscription_id: SubscriptionID,
    body: Annotated[
        Subscription,
        Field(description="Fields to change; ``type`` must match the integration's type."),
    ],
    client: FormsClient = Depends(forms_client),
) -> Subscription:
    """Change an integration: only the fields set in ``body`` change."""
    return client.subscriptions.update(survey_id, hook_id, subscription_id, body)


@mcp.tool(
    name="subscriptions_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms integration"},
)
def delete(
    survey_id: SurveyID,
    hook_id: HookID,
    subscription_id: SubscriptionID,
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete one integration from a hook; the hook's other integrations stay."""
    client.subscriptions.delete(survey_id, hook_id, subscription_id)
    return Ack.deleted("subscription", subscription_id, from_=f"hook {hook_id}")
