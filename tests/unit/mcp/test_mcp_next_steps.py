"""A tool's error tells an agent the next step a person is told by the CLI (#492, idea 17).

One place holds the hints (``ycli.yandex.errors.next_step``); the CLI prints them under
``Hint:`` and every server adds the same line to the error of a tool.
"""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.full_server import mcp
from tests.hosts import TRACKER_BASE
from ycli.cli.errors import format_cli_error
from ycli.yandex.errors import (
    YandexAuthError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
    next_step,
)
from ycli.yandex.tracker.issues.mcp import mcp as issues_mcp

URL = f"{TRACKER_BASE}/issues/A-1"


async def _said(server, tool: str, arguments: dict) -> str:
    async with Client(server) as client:
        with pytest.raises(ToolError) as failed:
            await client.call_tool(tool, arguments)
    return str(failed.value)


@pytest.mark.parametrize(
    ("status", "words"),
    [
        (401, "run `ycli auth login`"),
        (403, "the token is valid but lacks access here"),
        (404, "check the id or key"),
    ],
)
async def test_a_tool_error_ends_with_the_hint_the_cli_gives(api, status, words):
    api.add("GET", URL, json={"errorMessages": ["Nope."]}, status=status)
    said = await _said(mcp, "tracker_issues_get", {"issue_key": "A-1"})
    first, _, hint = said.partition("\nHint: ")
    assert first.startswith("Error calling tool 'issues_get': ") and "Nope." in first
    assert words in hint
    # Said once, though the resource's, the service's and the root server each could say it.
    assert said.count("Hint: ") == 1


async def test_a_resource_server_run_alone_gives_the_hint_too(api):
    api.add("GET", URL, json={}, status=404)
    assert "\nHint: check the id or key" in await _said(
        issues_mcp, "issues_get", {"issue_key": "A-1"}
    )


async def test_an_error_with_no_next_step_is_left_as_it_is(api):
    api.add("GET", URL, json={}, status=500)
    assert "Hint" not in await _said(mcp, "tracker_issues_get", {"issue_key": "A-1"})


@pytest.mark.parametrize(
    "error",
    [
        YandexAuthError("no", status=401),
        YandexAuthError("no", status=403),
        YandexNotFoundError("gone", status=404),
        YandexRateLimitError("slow", status=429, retry_after=30),
        YandexRateLimitError("slow", status=429),
    ],
)
def test_the_cli_prints_the_same_words(error):
    hint = next_step(error)
    assert hint is not None
    assert format_cli_error(error) == f"Error: {error}\nHint: {hint}"


def test_an_error_nobody_can_act_on_has_no_next_step():
    assert next_step(YandexServerError("down", status=503)) is None
    assert next_step(RuntimeError("boom")) is None
