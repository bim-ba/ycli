"""`schema_get` and the budget of a tool's input schema (#365)."""

import json
from typing import Annotated

import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from tests.full_server import mcp as full
from ycli.mcp.schemas import definitions, schema_server
from ycli.mcp.selection import Selection
from ycli.mcp.server import build_server
from ycli.yandex.mcp import RO, SCHEMA_ADDRESS, SCHEMA_BUDGET_BYTES, OverBudget
from ycli.yandex.models import RequestBody

SUBSCRIPTION = "ycli.yandex.forms.subscriptions.models:Subscription"


class Big(RequestBody):
    """A body whose schema alone is over the budget: one long description does it."""

    title: str | None = Field(default=None, description="x" * (SCHEMA_BUDGET_BYTES + 1))


def _over_budget(tools) -> list[str]:
    """Each tool over the budget, with its heaviest parameter: what to mark ``OverBudget``."""
    found = []
    for tool in tools:
        size = len(json.dumps(tool.parameters))
        if size > SCHEMA_BUDGET_BYTES:
            properties = tool.parameters.get("properties", {})
            heaviest = max(properties, key=lambda name: len(json.dumps(properties[name])))
            found.append(f"{tool.name}: {size} bytes, mark `{heaviest}`")
    return found


async def test_every_tool_lists_a_schema_within_the_budget():
    """A body that does not fit is marked ``OverBudget`` and read with ``schema_get``."""
    assert _over_budget(await full.list_tools()) == []


async def test_the_budget_check_bites():
    """Both sides: the same body is over the budget as it is and within it when marked."""
    plain, marked = FastMCP("plain"), FastMCP("marked")

    @plain.tool(name="big_create", annotations=RO)
    def unmarked(survey_id: str, body: Big) -> None:
        """Probe."""

    @marked.tool(name="big_create", annotations=RO)
    def marked_tool(
        survey_id: str, body: Annotated[Big, OverBudget(f"{__name__}:Big", "The body.")]
    ) -> None:
        """Probe."""

    (found,) = _over_budget(await plain.list_tools())
    assert found.startswith("big_create: ")
    assert found.endswith("mark `body`")
    assert _over_budget(await marked.list_tools()) == []


async def test_a_marked_body_is_listed_free_form_and_still_validated():
    async with Client(full) as client:
        tools = {tool.name: tool for tool in await client.list_tools()}
        body = tools["forms_subscriptions_create"].input_schema["properties"]["body"]
        assert body["type"] == "object"
        assert body[SCHEMA_ADDRESS] == SUBSCRIPTION
        assert 'schema_get(service="forms", name="Subscription")' in body["description"]
        wrong = {"survey_id": "s", "hook_id": 1, "body": {"type": "nope"}}
        with pytest.raises(ToolError, match="does not match any of the expected tags"):
            await client.call_tool("forms_subscriptions_create", wrong)


async def _definition(client: Client, name: str) -> dict:
    asked = {"service": "forms", "name": name}
    answer = (await client.call_tool("schema_get", asked)).structured_content
    assert answer is not None
    return answer["definition"]


async def test_schema_get_serves_one_definition_at_a_time():
    async with Client(full) as client:
        union = await _definition(client, "Subscription")
        assert "#/$defs/EmailSubscription" in [member["$ref"] for member in union["oneOf"]]
        assert "$defs" not in union  # the neighbours are read one by one
        assert "subject" in (await _definition(client, "EmailSubscription"))["properties"]


async def test_schema_get_names_what_it_has_when_asked_for_something_else():
    async with Client(full) as client:
        with pytest.raises(ToolError, match="did you mean: EmailSubscription"):
            await _definition(client, "EmailSubscribtion")
        with pytest.raises(ToolError, match="services with schemas: forms"):
            await client.call_tool("schema_get", {"service": "wiki", "name": "Page"})


async def test_schema_get_says_so_when_no_tool_needs_it():
    server = build_server(Selection(toolsets=("wiki",)))
    async with Client(server) as client:
        assert "schema_get" in {tool.name for tool in await client.list_tools()}
        with pytest.raises(ToolError, match="serves no schema on request"):
            await client.call_tool("schema_get", {"service": "wiki", "name": "Page"})


async def test_the_index_is_read_from_the_listing_and_every_address_resolves():
    """An address is written by hand: one that names nothing fails here, not at a user's call."""
    index = definitions(await full.list_tools())
    assert set(index) == {"forms"}
    assert {"Subscription", "EmailSubscription", "SubscriptionHeader"} <= set(index["forms"])


async def test_schema_get_is_annotated_as_a_read():
    """Like ``status_get`` it belongs to no resource, so the contract test does not see it."""
    (tool,) = await schema_server(full.list_tools).list_tools()
    hints = tool.annotations.model_dump(by_alias=True) if tool.annotations else {}
    assert {key: hints.get(key) for key in RO} == RO
