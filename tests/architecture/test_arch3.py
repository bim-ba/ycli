"""ARCH-3 — Honest effects (see ARCHITECTURE.md)."""

from __future__ import annotations

import ast

from tests.architecture.scanners import SRC, YANDEX, _mcp_tools, _probe_tools

# An endpoint may state an effect other than its method implies only here, with the reason:
# a wrong label would also make the retry policy re-send a non-idempotent request.
ARCH3_EFFECT_OVERRIDES: dict[str, str] = {
    "tracker/issues/endpoints.py:search": "POST _search only reads",
    "tracker/issues/endpoints.py:search_scroll": "POST _search only reads",
    "tracker/issues/endpoints.py:count": "POST _count only reads",
    "tracker/issues/endpoints.py:scroll_clear": "releasing a scroll twice is harmless",
    "tracker/worklog/endpoints.py:search": "POST _search only reads",
    "forms/files/endpoints.py:verify": "POST verify only reads upload statuses",
    "tracker/entities/endpoints.py:search": "POST _search only reads",
    "tracker/links/endpoints.py:list_filtered": "POST _list only reads",
    "tracker/gaps/endpoints.py:search": "POST _search only reads",
    "tracker/queues/endpoints.py:tags_delete": "POST _remove strips the tag from every issue",
    "wiki/pages/endpoints.py:update": "POST /pages/{id} replaces fields; a resend is a no-op",
    "wiki/grids/endpoints.py:update": "POST /grids/{id} replaces fields; a resend is a no-op",
    "wiki/grids/endpoints.py:cells_update": "POST cells sets values; a resend is a no-op",
    "wiki/grids/endpoints.py:columns_suggest": "POST columns/suggest only reads (checks a slug)",
    "wiki/grids/endpoints.py:columns_update": "POST column/{slug} sets fields; a resend is a no-op",
    "wiki/grids/endpoints.py:rows_update": "POST rows/{id} sets pin and colour; resent, a no-op",
    "wiki/pages/endpoints.py:search": "POST /search only reads",
    "wiki/access/endpoints.py:update": "POST access sets role; a resend is a no-op",
    "wiki/uploadsessions/endpoints.py:abort": "POST abort discards uploaded parts",
    "wiki/uploadsessions/endpoints.py:abort_all": "POST abort discards every upload",
    "forms/access/endpoints.py:update": "POST sets an access level: sending twice converges",
    "forms/access/endpoints.py:grant": "POST grants access: granting twice converges",
    "forms/access/endpoints.py:revoke": "POST revokes access: it removes a permission",
}


def _effect_overrides(source: str, module: str) -> set[str]:
    """``module:function`` for every endpoint in ``source`` built with an ``effect=`` keyword."""
    found = set()
    for function in ast.walk(ast.parse(source)):
        if isinstance(function, ast.FunctionDef):
            for call in ast.walk(function):
                if isinstance(call, ast.Call) and any(k.arg == "effect" for k in call.keywords):
                    found.add(f"{module}:{function.name}")
    return found


def test_arch3_effect_overrides_are_listed():
    found = {
        override
        for path in YANDEX.rglob("endpoints.py")
        for override in _effect_overrides(
            path.read_text(encoding="utf-8"), str(path.relative_to(YANDEX))
        )
    }
    assert found == set(ARCH3_EFFECT_OVERRIDES), (
        f"unlisted: {sorted(found - set(ARCH3_EFFECT_OVERRIDES))}, "
        f"stale: {sorted(set(ARCH3_EFFECT_OVERRIDES) - found)}"
    )


def test_arch3_effect_override_guard_bites():
    source = 'def move_issue(key):\n    return Endpoint("POST", "x", effect="read")\n'
    assert _effect_overrides(source, "tracker/issues/endpoints.py") == {
        "tracker/issues/endpoints.py:move_issue"
    }


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
