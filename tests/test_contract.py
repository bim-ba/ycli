"""Every contract case, driven through the SDK, the CLI and the MCP server (see tests/contract.py).

Each surface must send exactly the case's requests, carrying the credentials; the MCP tool's
hints must agree with the strongest effect among them, and the CLI must print what the SDK
returned and the MCP tool return the same data. Coverage is fail-closed: every operation, CLI
command and MCP tool of a resource on the httpx2 core needs a case, and every case must name
something that exists.
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

import pytest
from fastmcp import Client
from pydantic import BaseModel
from typer.testing import CliRunner

from tests.contract import (
    UNSTATED,
    Case,
    Reply,
    Sent,
    Sibling,
    effect_sent,
    hints_disagree,
    load_cases,
    mismatches,
    output_problems,
)
from tests.full_server import mcp as root_mcp
from tests.full_server import tool_with_output_schema
from tests.mock_api import MockAPI
from tests.snapshots._surface import cli_tree
from tests.test_architecture import ARCH1_SURFACE_ASYMMETRIES
from ycli.cli.app import app
from ycli.yandex.core.resource import Resource
from ycli.yandex.registry import SERVICES

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping, Sequence

SERVICE_BY_NAME = {service.name: service for service in SERVICES}


CASES = load_cases()


def _serve(monkeypatch: pytest.MonkeyPatch, case: Case) -> MockAPI:
    """A fresh MockAPI answering ``case``'s requests, in order, for every core session."""
    api = MockAPI()
    base_url = SERVICE_BY_NAME[case.domain].profile.base_url.rstrip("/")
    for sent, reply in case.exchanges:
        api.add(
            sent.method,
            f"{base_url}/{sent.path}",
            json=reply.json,
            status=reply.status,
            headers=dict(reply.headers),
            content=reply.content,
        )
    monkeypatch.setattr("ycli.yandex.core.session.default_transport", api.transport)
    return api


def _check_sent(case: Case, api: MockAPI, surface: str) -> None:
    base_url = SERVICE_BY_NAME[case.domain].profile.base_url
    problems = mismatches([sent for sent, _ in case.exchanges], api.calls, base_url)
    for request in api.calls:
        if request.headers.get("Authorization") != "OAuth t":
            problems.append(f"{request.url}: no OAuth credentials")
        if request.headers.get("X-Org-Id") != "o":
            problems.append(f"{request.url}: no organization header")
    if api.calls and effect_sent(api.calls) != case.expected_effect:
        problems.append(f"effect {effect_sent(api.calls)!r} != {case.expected_effect!r}")
    assert not problems, f"{surface}: {problems}"


def _run_sdk(case: Case) -> object:
    """What the SDK returned, as the CLI would print it (``None`` when it returned nothing)."""
    domain, resource, method = case.operation.split(".")
    client_class = SERVICE_BY_NAME[domain].client_class()
    with client_class(oauth_token="t", organization_id="o") as client:
        args = [getattr(client, a.resource) if isinstance(a, Sibling) else a for a in case.args]
        result = getattr(getattr(client, resource), method)(*args, **case.kwargs)
    return (
        result.model_dump(by_alias=True, mode="json") if isinstance(result, BaseModel) else result
    )


def _run_cli(case: Case, argv: Sequence[str] | None = None) -> object:
    assert case.cli is not None
    # A test has no terminal to answer the prompt a destructive operation raises.
    confirmed = ["--yes"] if case.expected_effect == "destructive" else []
    result = CliRunner().invoke(app, ["--format", "json", *confirmed, *(argv or case.cli)])
    assert result.exit_code == 0, result.output
    try:
        return json.loads(result.stdout_bytes)
    except ValueError:
        return result.stdout_bytes  # raw bytes: a download written to stdout


class _MCPSession:
    """One MCP client session for the whole module.

    FastMCP lists every tool on a session's first call (0.15 s), and later calls on the same
    session skip it.
    """

    def __init__(self) -> None:
        self._runner = asyncio.Runner()
        self._client = Client(root_mcp)
        self._runner.run(self._client.__aenter__())
        self.tools = {tool.name: tool for tool in self._runner.run(self._client.list_tools())}

    def call(self, name: str, arguments: Mapping[str, Any]) -> object:
        result = self._runner.run(self._client.call_tool(name, dict(arguments)))
        data = result.structured_content
        # FastMCP wraps a non-object result (a list, a scalar) as {"result": …}. The listing
        # carries no output schema (it is dropped to keep tools/list small), so the flag is read
        # from the tool itself, which still has it.
        schema = self._runner.run(tool_with_output_schema(name)).output_schema
        return (
            (data or {}).get("result") if schema and schema.get("x-fastmcp-wrap-result") else data
        )

    def close(self) -> None:
        self._runner.run(self._client.__aexit__(None, None, None))
        self._runner.close()


@pytest.fixture(scope="module")
def mcp_session() -> Iterator[_MCPSession]:
    session = _MCPSession()
    yield session
    session.close()


@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
def test_every_surface_sends_the_declared_requests(case: Case, monkeypatch, mcp_session):
    api = _serve(monkeypatch, case)
    sdk_output = _run_sdk(case)
    _check_sent(case, api, "sdk")
    problems = output_problems(case, sdk_output)
    assert not problems, f"sdk result: {problems}"
    cli_output = None
    for name, value in case.env.items():
        monkeypatch.setenv(name, value)
    if case.cli is not None:
        api = _serve(monkeypatch, case)
        cli_output = _run_cli(case)
        _check_sent(case, api, "cli")
        if case.cli_output is not UNSTATED:
            assert cli_output == case.cli_output, f"the CLI printed {cli_output!r}"
        # A bodyless write returns None from the SDK; the surfaces print an Ack instead.
        elif sdk_output is not None:
            assert cli_output == sdk_output, "the CLI printed something other than the SDK result"
    if case.mcp is not None:
        api = _serve(monkeypatch, case)
        name, arguments = case.mcp
        mcp_output = mcp_session.call(name, arguments)
        _check_sent(case, api, "mcp")
        tool = mcp_session.tools[name]
        hints = tool.annotations.model_dump(by_alias=True) if tool.annotations else {}
        wrong = hints_disagree(hints, case.expected_effect)
        assert not wrong, f"{case.mcp[0]}: effect {case.expected_effect!r} but {wrong} disagree"
        if case.cli is not None:
            assert cli_output == mcp_output, "the CLI and MCP return different data"


def _core_resources() -> dict[str, object]:
    """``<domain>.<resource>`` → the resource client, for every resource on the httpx2 core."""
    resources = {}
    for service in SERVICES:
        with service.client_class()(oauth_token="t", organization_id="o") as client:
            for name, value in vars(client).items():
                if isinstance(value, Resource):
                    resources[f"{service.name}.{name}"] = value
    return resources


def _public_methods(resource: object) -> set[str]:
    return {
        name
        for name, value in vars(type(resource)).items()
        if callable(value) and not name.startswith("_")
    }


def _starts_with(argv: Sequence[str], command: str) -> bool:
    words = command.split()
    return list(argv[: len(words)]) == words


def coverage_gaps(
    cases: list[Case], operations: set[str], commands: set[str], tools: set[str]
) -> dict[str, list[str]]:
    """What the ``cases`` leave uncovered, or name without it existing (empty lists: nothing)."""
    named = {case.operation for case in cases}
    exempt = set(ARCH1_SURFACE_ASYMMETRIES)
    return {
        "operations without a case": sorted(operations - named),
        "operations no CLI case reaches": sorted(
            operations - exempt - {case.operation for case in cases if case.cli}
        ),
        "operations no MCP case reaches": sorted(
            operations - exempt - {case.operation for case in cases if case.mcp}
        ),
        # A command is reached by a case whose argv starts with it (a nested group's command
        # runs four words deep: `tracker entities comments list`).
        "commands without a case": sorted(
            command
            for command in commands
            if not any(case.cli and _starts_with(case.cli, command) for case in cases)
        ),
        "tools without a case": sorted(tools - {case.mcp[0] for case in cases if case.mcp}),
        "cases of unknown operations": sorted(named - operations),
    }


def test_every_core_operation_command_and_tool_has_a_case(mcp_session):
    resources = _core_resources()
    operations = {
        f"{slug}.{method}"
        for slug, resource in resources.items()
        for method in _public_methods(resource)
    }
    commands = {
        path
        for path in cli_tree()
        if ".".join(path.split()[:2]) in resources and len(path.split()) > 2
    }
    prefixes = tuple(f"{slug.replace('.', '_').rstrip('_')}_" for slug in resources)
    tools = {name for name in mcp_session.tools if name.startswith(prefixes)}
    gaps = coverage_gaps(CASES, operations, commands, tools)
    assert not any(gaps.values()), {label: names for label, names in gaps.items() if names}


def test_coverage_gaps_bite():
    case = Case(
        "forms.me.get",
        cli=["forms", "me", "get"],
        mcp=None,
        exchanges=[(Sent("GET", "users/me"), Reply())],
    )
    nested = Case(
        "forms.conditions.page_list",
        cli=["forms", "conditions", "page", "list", "686d", "3"],
        mcp=None,
        exchanges=[(Sent("GET", "surveys/686d/pages/3/conditions"), Reply())],
    )
    gaps = coverage_gaps(
        [case, nested],
        {"forms.me.get", "forms.me.list", "forms.conditions.page_list"},
        {
            "forms me get",
            "forms me list",
            "forms conditions page",
            "forms conditions page list",
            "forms conditions page get",
        },
        {"forms_me_get"},
    )
    assert gaps == {
        "operations without a case": ["forms.me.list"],
        "operations no CLI case reaches": ["forms.me.list"],
        "operations no MCP case reaches": [
            "forms.conditions.page_list",
            "forms.me.get",
            "forms.me.list",
        ],
        "commands without a case": ["forms conditions page get", "forms me list"],
        "tools without a case": ["forms_me_get"],
        "cases of unknown operations": [],
    }


def _one(reply: Reply, output: object = UNSTATED) -> Case:
    return Case(
        "forms.me.get",
        cli=None,
        mcp=None,
        exchanges=[(Sent("GET", "users/me"), reply)],
        output=output,
    )


def test_output_check_bites():
    survey = {"id": "s1", "name": "Onboarding"}
    assert output_problems(_one(Reply(json=survey)), {**survey, "extra": None}) == []
    # A blanked value, a result sharing nothing with the reply, other bytes, a stated result.
    assert output_problems(_one(Reply(json=survey)), {"id": "s1", "name": None}) == [
        "name: None != 'Onboarding'"
    ]
    assert output_problems(_one(Reply(json=survey)), {"unrelated": 1}) == [
        "kept no field of the reply; state the case's output"
    ]
    assert output_problems(_one(Reply(content=b"abc")), b"") == ["other bytes than the API sent"]
    assert output_problems(_one(Reply(), output={"ok": True}), {"ok": False}) == [
        "returned {'ok': False}, stated {'ok': True}"
    ]
    # A listing keeps the items of every page; a merged envelope must be stated.
    pages = Case(
        "forms.surveys.list",
        cli=None,
        mcp=None,
        exchanges=[
            (Sent("GET", "surveys"), Reply(json={"result": [{"id": "a"}]})),
            (Sent("GET", "surveys"), Reply(json={"result": [{"id": "b"}]})),
        ],
    )
    assert output_problems(pages, [{"id": "a"}, {"id": "b"}]) == []
    assert output_problems(pages, [{"id": "a"}]) == ["items: 1 items != 2"]
    assert output_problems(pages, {"merged": True}) == [
        "no reply lines up with this result; state the case's output"
    ]


def test_request_check_bites():
    import httpx2

    upload = httpx2.Request(
        "POST", "https://x.test/v1/files?debug=1", files={"file": ("cv.txt", b"resume")}
    )
    upload.read()  # MockTransport reads the body before the harness sees it
    wanted = Sent("POST", "files", files={"file": ("cv.txt", b"resume")})
    assert mismatches([wanted], [upload], "https://x.test/v1") == [
        "request 0: params {'debug': '1'} != {}"
    ]
    other_part = Sent("POST", "files", {"debug": "1"}, files={"file": ("cv.txt", b"other")})
    assert mismatches([other_part], [upload], "https://x.test/v1") == [
        "request 0: no part 'file' with file 'cv.txt' and its bytes"
    ]
    assert mismatches([wanted, wanted], [upload], "https://x.test/v1")[0] == (
        "sent 1 requests, expected 2"
    )


def test_nested_command_coverage_bites():
    case = Case(
        "tracker.entities.comments_list",
        cli=["tracker", "entities", "comments", "list", "project", "1"],
        mcp=None,
        exchanges=[(Sent("GET", "entities/project/1/comments"), Reply())],
    )
    commands = {"tracker entities comments", "tracker entities comments list"}
    nested = "tracker entities comments delete"
    gaps = coverage_gaps([case], set(), commands | {nested}, set())
    assert gaps["commands without a case"] == [nested]
