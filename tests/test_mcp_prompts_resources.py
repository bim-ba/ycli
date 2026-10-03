"""Prompts and resources of the MCP server: what is offered, and that each follows its tools."""

import json
import re
from importlib.resources import files
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.exceptions import McpError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.full_server import mcp as full_server
from tests.hosts import FORMS_BASE, TRACKER_BASE, WIKI_BASE
from ycli.mcp.selection import CORE, Selection
from ycli.mcp.server import build_server
from ycli.yandex.mcp import NEEDS_TOOLS, REPEATS_TOOL, WRITE_TAG
from ycli.yandex.registry import SERVICES

PROMPTS = {
    "forms_answers_table": {"survey_id": "686d0a1b"},
    "tracker_issue_brief": {"key": "DE-7"},
    "tracker_queue_digest": {"queue": "DE"},
    "tracker_sprint_review": {"board_id": "5"},
    "wiki_page_from_issue": {"key": "DE-7", "parent_slug": "team/decisions"},
}
TEMPLATES = {
    "ycli://forms/survey/{survey_id}",
    "ycli://tracker/issue/{key}",
    "ycli://wiki/page/{slug*}",
}
_TOOL_NAME = re.compile(r"\b(?:tracker|wiki|forms)_[a-z_]+\b")

runner = CliRunner()


async def _offered(selection: Selection) -> tuple[set[str], set[str]]:
    """The prompts and the resource templates a client of ``selection`` is offered."""
    async with Client(build_server(selection)) as client:
        # Prompts first: nothing has listed tools yet when the server answers.
        prompts = {prompt.name for prompt in await client.list_prompts()}
        templates = {template.uri_template for template in await client.list_resource_templates()}
    return prompts, templates


async def test_the_full_server_offers_every_prompt_and_template():
    assert await _offered(Selection()) == (set(PROMPTS), TEMPLATES)


@pytest.mark.parametrize(
    ("selection", "prompts", "templates"),
    [
        # A toolset other than `all` used to hide every prompt and resource (enable(only=True)).
        (
            Selection(toolsets=("tracker",)),
            {"tracker_issue_brief", "tracker_queue_digest", "tracker_sprint_review"},
            {"ycli://tracker/issue/{key}"},
        ),
        # Its text reads Tracker, which this server does not serve.
        (Selection(toolsets=("wiki",)), set(), {"ycli://wiki/page/{slug*}"}),
        (Selection(toolsets=("wiki", "tracker")), set(PROMPTS) - {"forms_answers_table"}, None),
        # It ends in wiki_pages_create.
        (Selection(read_only=True), set(PROMPTS) - {"wiki_page_from_issue"}, TEMPLATES),
        # `core` has no sprint tools.
        (Selection(toolsets=(CORE,)), set(PROMPTS) - {"tracker_sprint_review"}, TEMPLATES),
        (
            Selection(exclude_tools=("tracker_issues_get",)),
            {"forms_answers_table", "tracker_queue_digest", "tracker_sprint_review"},
            TEMPLATES - {"ycli://tracker/issue/{key}"},
        ),
        (
            Selection(toolsets=("forms",), tools=("tracker_issues_get",)),
            {"forms_answers_table"},
            {"ycli://forms/survey/{survey_id}", "ycli://tracker/issue/{key}"},
        ),
        # The search interface replaces the tool listing, not what is served.
        (Selection(tool_search=True), set(PROMPTS), TEMPLATES),
    ],
)
async def test_a_prompt_or_a_resource_is_offered_only_with_its_tools(selection, prompts, templates):
    offered_prompts, offered_templates = await _offered(selection)
    assert offered_prompts == prompts
    if templates is not None:
        assert offered_templates == templates


async def test_what_is_not_offered_cannot_be_fetched_either():
    async with Client(build_server(Selection(toolsets=("wiki",)))) as client:
        with pytest.raises(McpError, match="Unknown prompt"):
            await client.get_prompt("wiki_page_from_issue", PROMPTS["wiki_page_from_issue"])
        with pytest.raises(McpError, match="Resource not found"):
            await client.read_resource("ycli://tracker/issue/DE-7")


async def test_a_prompt_names_only_tools_that_exist_and_lists_them():
    """ARCH-3: the text and ``NEEDS_TOOLS`` agree, and a write among them means the write tag."""
    tools = {tool.name: set(tool.tags) for tool in await full_server.list_tools()}
    async with Client(full_server) as client:
        for prompt in await full_server.list_prompts():
            rendered = await client.get_prompt(prompt.name, PROMPTS[prompt.name])
            (message,) = rendered.messages
            named = set(_TOOL_NAME.findall(message.content.text))
            assert named <= set(tools), f"{prompt.name} names a tool that does not exist"
            assert named == set((prompt.meta or {})[NEEDS_TOOLS]), prompt.name
            writes = any(WRITE_TAG in tools[name] for name in named)
            assert (WRITE_TAG in prompt.tags) is writes, prompt.name


async def test_the_sprint_prompt_takes_a_named_sprint():
    async with Client(full_server) as client:
        rendered = await client.get_prompt(
            "tracker_sprint_review", {"board_id": "5", "sprint": "Sprint 12"}
        )
    assert "'Sprint 12'" in rendered.messages[0].content.text


async def test_a_resource_repeats_a_read_tool():
    """ARCH-3: the tool a resource template names exists and is a read."""
    tools = {tool.name: tool for tool in await full_server.list_tools()}
    templates = await full_server.list_resource_templates()
    assert {template.uri_template for template in templates} == TEMPLATES
    for template in templates:
        tool = tools[(template.meta or {})[REPEATS_TOOL]]
        assert tool.annotations is not None
        assert tool.annotations.read_only_hint is True, template.uri_template
        assert WRITE_TAG not in template.tags


@pytest.mark.parametrize(
    ("uri", "tool", "arguments", "url", "answer"),
    [
        (
            "ycli://tracker/issue/DE-7",
            "tracker_issues_get",
            {"key": "DE-7"},
            f"{TRACKER_BASE}/issues/DE-7",
            {"key": "DE-7", "summary": "Fix the login page"},
        ),
        (
            "ycli://forms/survey/686d0a1b",
            "forms_surveys_get",
            {"survey_id": "686d0a1b"},
            f"{FORMS_BASE}/surveys/686d0a1b",
            {"id": "686d0a1b", "name": "Feedback"},
        ),
    ],
)
async def test_a_json_resource_reads_what_its_tool_returns(api, uri, tool, arguments, url, answer):
    api.add("GET", url, json=answer)
    api.add("GET", url, json=answer)
    async with Client(full_server) as client:
        (content,) = await client.read_resource(uri)
        result = await client.call_tool(tool, arguments)
    assert content.mime_type == "application/json"
    assert json.loads(content.text) == result.structured_content


async def test_a_wiki_page_resource_is_its_markdown_and_takes_a_nested_slug(api):
    api.add(
        "GET",
        f"{WIKI_BASE}/pages",
        json={
            "id": 1,
            "slug": "team/onboarding/first-day",
            "title": "First day",
            "content": "# Onboarding\n\nHello.",
        },
    )
    async with Client(full_server) as client:
        (content,) = await client.read_resource("ycli://wiki/page/team/onboarding/first-day")
    assert (content.mime_type, content.text) == ("text/markdown", "# Onboarding\n\nHello.")
    assert api.calls[0].url.params["slug"] == "team/onboarding/first-day"


def test_mcp_methods_lists_prompts_and_resources_under_the_same_flags():
    prompts = runner.invoke(cli.app, ["mcp", "methods", "--kind", "prompts", "--read-only"])
    assert prompts.stdout.split() == sorted(set(PROMPTS) - {"wiki_page_from_issue"})
    resources = runner.invoke(
        cli.app, ["mcp", "methods", "--kind", "resources", "--toolsets", "wiki,forms"]
    )
    assert resources.stdout.split() == [
        "ycli://forms/guide",
        "ycli://forms/survey/{survey_id}",
        "ycli://guide",
        "ycli://wiki/guide",
        "ycli://wiki/page/{slug*}",
    ]
    tools = runner.invoke(cli.app, ["mcp", "methods", "--toolsets", "wiki"])
    assert "wiki_pages_get" in tools.stdout.split()
    assert "wiki_page_from_issue" not in tools.stdout.split()


SKILLS = Path(__file__).resolve().parent.parent / "plugins" / "yandex-360" / "skills"
GUIDES = {
    "ycli://guide": ("ycli.mcp", "yandex-360"),
    **{
        f"ycli://{service.name}/guide": (
            f"ycli.yandex.{service.name}.mcp",
            f"yandex-360-{service.name}",
        )
        for service in SERVICES
    },
}


@pytest.mark.parametrize(
    ("uri", "package", "skill"), [(uri, *where) for uri, where in GUIDES.items()]
)
async def test_a_guide_is_the_plugins_skill_byte_for_byte(uri, package, skill):
    """One source of text: the packaged ``guide.md`` is a link to the plugin's ``SKILL.md``."""
    source = SKILLS / skill / "SKILL.md"
    packaged = files(package).joinpath("guide.md")
    assert packaged.read_bytes() == source.read_bytes()
    assert Path(str(packaged)).is_symlink(), "guide.md is a copy; link it to the skill instead"
    async with Client(full_server) as client:
        (content,) = await client.read_resource(uri)
    assert (content.mime_type, content.text) == (
        "text/markdown",
        source.read_text(encoding="utf-8"),
    )


@pytest.mark.parametrize(
    ("selection", "guides"),
    [
        (Selection(), set(GUIDES)),
        (Selection(toolsets=("wiki",)), {"ycli://guide", "ycli://wiki/guide"}),
        (Selection(toolsets=(CORE,), read_only=True), set(GUIDES)),
    ],
)
async def test_a_guide_is_offered_for_every_mounted_service(selection, guides):
    server = build_server(selection)
    async with Client(server) as client:
        assert {str(resource.uri) for resource in await client.list_resources()} == guides
    for uri in guides - {"ycli://guide"}:
        assert uri in (server.instructions or "")
