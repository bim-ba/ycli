"""Every contract case, driven through the SDK, the CLI and the MCP server (see tests/contract.py).

Each surface must send exactly the case's requests, carrying the credentials; the MCP tool's
hints must agree with the strongest effect among them, and the CLI must print what the SDK
returned and the MCP tool return the same data. Coverage is fail-closed: every operation, CLI
command and MCP tool of a resource on the httpx2 core needs a case, and every case must name
something that exists.
"""

from __future__ import annotations

import asyncio
import importlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from fastmcp import Client
from pydantic import BaseModel
from typer.testing import CliRunner

from tests.contract import (
    NO_BODY,
    Case,
    Reply,
    Sent,
    effect_sent,
    hints_disagree,
    lost_values,
    mismatches,
)
from tests.mock_api import MockAPI
from tests.snapshots._surface import cli_tree
from tests.test_architecture import ARCH1_SURFACE_ASYMMETRIES
from ycli.cli.app import app
from ycli.mcp.server import mcp as root_mcp
from ycli.yandex.core.resource import Resource
from ycli.yandex.registry import SERVICES

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

TESTS = Path(__file__).parent
SERVICE_BY_NAME = {service.name: service for service in SERVICES}


def _load_cases() -> list[Case]:
    cases = []
    for path in sorted(TESTS.glob("yandex/*/*/cases.py")):
        module = ".".join(path.relative_to(TESTS.parent).with_suffix("").parts)
        cases += importlib.import_module(module).CASES
    return cases


CASES = _load_cases()


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


def _check_output(case: Case, output: object) -> None:
    """The SDK kept what the API answered, and returned the stated ``output`` if there is one.

    Only a one-request case is compared with its reply: a walk over pages, or a flow of several
    requests, returns something no single reply holds, so such a case states its ``output``.
    """
    reply = case.exchanges[-1][1]
    if isinstance(output, bytes):
        assert output == reply.content, "the SDK returned other bytes than the API sent"
    elif reply.json is not None and case.output is NO_BODY and len(case.exchanges) == 1:
        lost = lost_values(output, reply.json)
        assert not lost, f"the SDK lost values the API returned: {lost}"
    if case.output is not NO_BODY:
        assert output == case.output, f"the SDK returned {output!r}, expected {case.output!r}"


def _run_sdk(case: Case) -> object:
    """What the SDK returned, as the CLI would print it (``None`` when it returned nothing)."""
    domain, resource, method = case.operation.split(".")
    client_class = SERVICE_BY_NAME[domain].client_class()
    with client_class(oauth_token="t", organization_id="o") as client:
        result = getattr(getattr(client, resource), method)(*case.args, **case.kwargs)
    return (
        result.model_dump(by_alias=True, mode="json") if isinstance(result, BaseModel) else result
    )


def _run_cli(case: Case) -> object:
    assert case.cli is not None
    result = CliRunner().invoke(app, ["--format", "json", *case.cli])
    assert result.exit_code == 0, result.output
    try:
        return json.loads(result.stdout_bytes)
    except ValueError:
        return result.stdout_bytes  # raw bytes: a download written to stdout


class _MCPSession:
    """One MCP client session for the whole module: FastMCP lists every tool on a session's
    first call (0.15 s), and later calls on the same session skip it."""

    def __init__(self) -> None:
        self._runner = asyncio.Runner()
        self._client = Client(root_mcp)
        self._runner.run(self._client.__aenter__())
        self.tools = {tool.name: tool for tool in self._runner.run(self._client.list_tools())}

    def call(self, name: str, arguments: Mapping[str, Any]) -> object:
        result = self._runner.run(self._client.call_tool(name, dict(arguments)))
        data = result.structured_content
        # FastMCP wraps a non-object result (a list, a scalar) as {"result": …}.
        schema = self.tools[name].output_schema
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
    _check_output(case, sdk_output)
    cli_output = None
    if case.cli is not None:
        api = _serve(monkeypatch, case)
        cli_output = _run_cli(case)
        _check_sent(case, api, "cli")
        if case.cli_output is not NO_BODY:
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
        "commands without a case": sorted(
            commands - {" ".join(case.cli[:3]) for case in cases if case.cli}
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
    gaps = coverage_gaps(
        [case],
        {"forms.me.get", "forms.me.list"},
        {"forms me get", "forms me list"},
        {"forms_me_get"},
    )
    assert gaps == {
        "operations without a case": ["forms.me.list"],
        "operations no CLI case reaches": ["forms.me.list"],
        "operations no MCP case reaches": ["forms.me.get", "forms.me.list"],
        "commands without a case": ["forms me list"],
        "tools without a case": ["forms_me_get"],
        "cases of unknown operations": [],
    }
