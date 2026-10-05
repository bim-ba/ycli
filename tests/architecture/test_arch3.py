"""ARCH-3 — Honest effects (see ARCHITECTURE.md)."""

from __future__ import annotations

import ast

from tests.architecture.scanners import SRC, YANDEX, _mcp_tools, _probe_tools, unexplained


def _effect_overrides(source: str, module: str) -> list[tuple[int, str]]:
    """(line, ``module:function``) for every endpoint in ``source`` built with ``effect=``."""
    found = set()
    for function in ast.walk(ast.parse(source)):
        if isinstance(function, ast.FunctionDef):
            for call in ast.walk(function):
                if isinstance(call, ast.Call) and any(k.arg == "effect" for k in call.keywords):
                    found.add((call.lineno, f"{module}:{function.name}"))
    return sorted(found)


def _unmarked_overrides(source: str, module: str) -> list[str]:
    """Overrides of ``source`` with no ``# violation(arch-3)`` above, and markers above none."""
    return unexplained(_effect_overrides(source, module), source, "arch-3", module)


def test_arch3_effect_overrides_are_marked():
    """An endpoint states an effect other than its method implies only with the reason above it.

    A wrong label would also make the retry policy re-send a non-idempotent request.
    """
    found = [
        finding
        for path in sorted(YANDEX.rglob("endpoints.py"))
        for finding in _unmarked_overrides(
            path.read_text(encoding="utf-8"), str(path.relative_to(YANDEX))
        )
    ]
    assert found == []


def test_arch3_effect_override_guard_bites():
    """Prove-it, both sides: an override with no marker, and a marker above no override."""
    module = "tracker/issues/endpoints.py"
    marked = (
        "def search(body):\n"
        "    # violation(arch-3): POST _search only reads\n"
        '    return Endpoint(HTTPMethod.POST, "x", json=body, effect=Effect.READ)\n'
    )
    assert _unmarked_overrides(marked, module) == []
    unmarked = marked.replace("violation(arch-3)", "violation(arch-9)")
    assert _unmarked_overrides(unmarked, module) == [f"{module}:search"]
    stale = marked.replace(", effect=Effect.READ", "")
    assert _unmarked_overrides(stale, module) == [
        f"{module}:2: violation(arch-3) marks nothing the check finds"
    ]


def test_arch3_write_tools_carry_write_tag():
    """`--read-only` hides writes by tag, so every write tool MUST carry the write tag.

    `ycli mcp start --read-only` calls ``mcp.disable(tags={WRITE_TAG})``. The tag is derived at
    the root server (``DerivedTags``) from ``readOnlyHint``; this reads the served tools, so a
    server built without that transform, or a tool with no annotations, fails here.
    """
    from ycli.yandex.mcp import WRITE_TAG

    tools = _mcp_tools()
    assert tools, "no MCP tools discovered"
    assert _write_tag_mismatches(tools, WRITE_TAG) == []


def _tools_with_their_own_tags(source: str) -> list[str]:
    """Functions of ``source`` whose ``@mcp.tool`` passes ``tags=``."""
    return [
        function.name
        for function in ast.walk(ast.parse(source))
        if isinstance(function, ast.FunctionDef)
        for decorator in function.decorator_list
        if isinstance(decorator, ast.Call)
        and ast.unparse(decorator.func) == "mcp.tool"
        and any(keyword.arg == "tags" for keyword in decorator.keywords)
    ]


def test_arch3_no_tool_states_its_tags_itself():
    """A tool's tags are derived at the root from its name and ``readOnlyHint`` (#232).

    A tool that passed ``tags=`` would state its service and its effect a second time, and the
    two statements could disagree.
    """
    offenders = {
        str(path.relative_to(SRC)): found
        for path in SRC.rglob("mcp.py")
        if (found := _tools_with_their_own_tags(path.read_text(encoding="utf-8")))
    }
    assert offenders == {}


def test_arch3_own_tags_check_bites():
    source = (
        "@mcp.tool(name='a_get', annotations=RO, tags=TAGS)\ndef get(): ...\n"
        "@mcp.tool(name='a_list', annotations=RO)\ndef list_(): ...\n"
        "@mcp.prompt(name='digest', tags=TAGS)\ndef digest(): ...\n"
    )
    assert _tools_with_their_own_tags(source) == ["get"]


def _write_tag_mismatches(tools, write_tag: str) -> list[str]:
    """Tools whose write tag disagrees with ``readOnlyHint``, or that carry no annotations."""
    mismatches = []
    for tool in tools:
        tags = set(((tool.meta or {}).get("fastmcp") or {}).get("tags") or [])
        is_write = tool.annotations is not None and tool.annotations.read_only_hint is False
        if tool.annotations is None or (write_tag in tags) != is_write:
            mismatches.append(tool.name)
    return mismatches


def test_arch3_write_tag_check_bites():
    from ycli.yandex.mcp import RO, WRITE, WRITE_TAG

    def register(server):
        @server.tool(annotations={**WRITE, "title": "t"}, tags={"probe"})
        def untagged_write() -> str:
            """Probe."""
            return ""

        @server.tool(annotations={**RO, "title": "t"}, tags={"probe", WRITE_TAG})
        def tagged_read() -> str:
            """Probe."""
            return ""

        @server.tool(tags={"probe"})
        def unannotated() -> str:
            """Probe."""
            return ""

        @server.tool(annotations={**WRITE, "title": "t"}, tags={"probe", WRITE_TAG})
        def honest_write() -> str:
            """Probe."""
            return ""

    assert sorted(_write_tag_mismatches(_probe_tools(register), WRITE_TAG)) == [
        "tagged_read",
        "unannotated",
        "untagged_write",
    ]
