"""Architecture invariants as tests — see ARCHITECTURE.md (ARCH-1/3/4/5).

A failure means a change drifted from the architecture. Fix the code, or — if the
change is intentional — update ARCHITECTURE.md and this check together in one PR.
"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path

from fastmcp import Client

from ycli.mcp import mcp as root_mcp

SRC = Path(__file__).resolve().parent.parent / "src" / "ycli"
YANDEX = SRC / "yandex"
DOMAINS = ("tracker", "wiki", "forms")
CANONICAL = {"__init__.py", "client.py", "cli.py", "mcp.py", "models.py"}
WRITE_VERBS = {"create", "update", "add", "execute", "delete", "set", "remove"}


def _resource_dirs():
    for domain in DOMAINS:
        for child in sorted((YANDEX / domain).iterdir()):
            if child.is_dir() and not child.name.startswith(("_", "__")):
                yield child


def test_arch1_four_surface_symmetry():
    checked = 0
    for d in _resource_dirs():
        files = {p.name for p in d.iterdir() if p.is_file()}
        missing = CANONICAL - files
        assert not missing, f"{d.relative_to(SRC)} missing canonical files: {sorted(missing)}"
        checked += 1
    assert checked >= 16, f"expected >=16 resource dirs, found {checked}"


def _mcp_tools():
    async def go():
        async with Client(root_mcp) as c:
            return await c.list_tools()
    return asyncio.run(go())


def test_arch3_mcp_tools_are_read_only():
    tools = _mcp_tools()
    assert tools, "no MCP tools discovered"
    for t in tools:
        verb = t.name.rsplit("_", 1)[-1]
        assert verb not in WRITE_VERBS, f"MCP tool {t.name!r} has a write verb"
        ann = getattr(t, "annotations", None)
        assert ann is not None and ann.readOnlyHint is True, f"{t.name!r} lacks readOnlyHint"


def test_arch4_model_dump_json_only_in_output():
    offenders = [
        str(p.relative_to(SRC))
        for p in SRC.rglob("*.py")
        if p.name != "output.py" and "model_dump_json" in p.read_text(encoding="utf-8")
    ]
    assert not offenders, f"model_dump_json must live only in output.py; found in {offenders}"


_TOKEN_RE = re.compile(r"YANDEX_ID_\w+\s*=\s*['\"]")
_VERSION_RE = re.compile(r"__version__\s*=\s*['\"]\d")
_ORG_HEADER_RE = re.compile(r"X-Org-I[dD]")


def test_arch5_single_sources_of_truth():
    offenders = []
    for p in SRC.rglob("*.py"):
        rel = p.relative_to(SRC)
        text = p.read_text(encoding="utf-8")
        if _TOKEN_RE.search(text):
            offenders.append(f"{rel}: hardcoded YANDEX_ID token literal")
        if p.name != "__init__.py" and _VERSION_RE.search(text):
            offenders.append(f"{rel}: hardcoded __version__ literal")
        if p.name != "transport.py" and _ORG_HEADER_RE.search(text):
            offenders.append(f"{rel}: org header string outside transport.py")
    assert not offenders, offenders
