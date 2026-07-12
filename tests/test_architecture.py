"""Architecture invariants as tests — see ARCHITECTURE.md (ARCH-1/2/3/4/5/6/7/8/9/10/11).

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
# Fail-closed verb classification (ARCH-3 annotation honesty): every MCP tool name's
# verb — its longest `_`-suffix found below — MUST classify as read, write,
# idempotent-write, or destructive. An unknown verb fails the build; a new operation
# adds its verb here deliberately. Keep in sync with ARCHITECTURE.md.
READ_VERBS = {"get", "list", "count", "search", "descendants", "meta", "suggest", "verify"}
WRITE_VERBS = {
    "create", "add", "execute", "submit", "publish", "unpublish", "move", "start",
    "archive", "restore", "react", "attach", "upload", "upload_part", "clone", "append",
    "append_content", "finish", "export", "transition", "create_report",
    "add_rows", "move_rows", "add_columns", "move_columns", "add_cycle_time_widget",
    "import_task", "import_comment", "import_link", "import_worklog", "import_file",
}  # fmt: skip
WRITE_IDEMPOTENT_VERBS = {
    "update", "edit", "modify", "set", "set_permissions", "permissions_set",
    "update_cells", "edit_item", "scroll_clear",
}  # fmt: skip
DESTRUCTIVE_VERBS = {
    "delete", "remove", "clear", "abort", "abort_all",
    "remove_rows", "remove_columns", "delete_item",
}  # fmt: skip

_VERB_CLASS: dict[str, str] = (
    dict.fromkeys(READ_VERBS, "read")
    | dict.fromkeys(WRITE_VERBS, "write")
    | dict.fromkeys(WRITE_IDEMPOTENT_VERBS, "write_idempotent")
    | dict.fromkeys(DESTRUCTIVE_VERBS, "destructive")
)


def _classify(name: str) -> str | None:
    """Classify a tool/method name by its longest known `_`-suffix (fail-closed: None)."""
    tokens = name.split("_")
    for start in range(len(tokens)):  # longest suffix first
        suffix = "_".join(tokens[start:])
        if suffix in _VERB_CLASS:
            return _VERB_CLASS[suffix]
    return None


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


def test_arch3_mcp_annotation_honesty():
    """Every tool's hints match its verb class exactly (fail-closed on unknown verbs).

    The MCP-spec default for an unannotated tool is destructiveHint=true, so every
    write tool must declare its hints explicitly (WRITE / WRITE_IDEMPOTENT / DESTRUCTIVE
    in ycli.yandex.mcp); reads keep RO.
    """
    tools = _mcp_tools()
    assert tools, "no MCP tools discovered"
    for t in tools:
        cls = _classify(t.name)
        assert cls is not None, (
            f"MCP tool {t.name!r} has no known verb suffix — add its verb to the "
            "READ/WRITE/WRITE_IDEMPOTENT/DESTRUCTIVE maps deliberately (fail-closed)"
        )
        ann = getattr(t, "annotations", None)
        assert ann is not None, f"{t.name!r} lacks annotations"
        if cls == "read":
            assert ann.readOnlyHint is True, f"{t.name!r} is a read but readOnlyHint is not True"
        else:
            assert ann.readOnlyHint is False, f"{t.name!r} is a write but readOnlyHint is not False"
            assert ann.destructiveHint is (cls == "destructive"), (
                f"{t.name!r} verb class {cls!r} demands destructiveHint="
                f"{cls == 'destructive'}, got {ann.destructiveHint}"
            )
            assert ann.idempotentHint is (cls == "write_idempotent"), (
                f"{t.name!r} verb class {cls!r} demands idempotentHint="
                f"{cls == 'write_idempotent'}, got {ann.idempotentHint}"
            )


def test_arch3_read_tools_call_no_write_methods():
    """A read-classified tool must not invoke a client write method (AST-checked)."""
    import ast

    offenders = []
    for mcp_py in YANDEX.rglob("mcp.py"):
        tree = ast.parse(mcp_py.read_text(encoding="utf-8"))
        rel = mcp_py.relative_to(SRC)
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            tool_name = None
            for deco in node.decorator_list:
                if (
                    isinstance(deco, ast.Call)
                    and isinstance(deco.func, ast.Attribute)
                    and deco.func.attr == "tool"
                ):
                    names = [
                        kw.value.value
                        for kw in deco.keywords
                        if kw.arg == "name" and isinstance(kw.value, ast.Constant)
                    ]
                    if not names:
                        offenders.append(f"{rel}: {node.name} registers a tool without name=")
                        continue
                    tool_name = names[0]
            if tool_name is None or _classify(tool_name) != "read":
                continue
            for call in ast.walk(node):
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and _classify(call.func.attr) in {"write", "write_idempotent", "destructive"}
                ):
                    offenders.append(f"{rel}: read tool {tool_name!r} calls .{call.func.attr}(…)")
    assert not offenders, f"read tools must not call client write methods: {offenders}"


def test_arch4_serialization_confined_to_output():
    """Rendering via Serializer; model_dump_json/yaml.safe_dump/json.dumps only in output.py."""
    offenders = []
    for p in SRC.rglob("*.py"):
        if p.name == "output.py":
            continue
        text = p.read_text(encoding="utf-8")
        if "model_dump_json" in text or "yaml.safe_dump" in text or "json.dumps" in text:
            offenders.append(str(p.relative_to(SRC)))
    assert not offenders, f"serialization must live only in output.py; found in {offenders}"


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
        if rel != Path("__init__.py") and _VERSION_RE.search(text):
            offenders.append(f"{rel}: hardcoded __version__ literal")
        if p.name != "transport.py" and _ORG_HEADER_RE.search(text):
            offenders.append(f"{rel}: org header string outside transport.py")
    assert not offenders, offenders


def test_arch7_clients_never_resolve_credentials():
    """No client reads the env or constructs settings — credentials arrive as constructor args."""
    offenders = []
    for client in YANDEX.rglob("client.py"):
        text = client.read_text(encoding="utf-8")
        for needle in ("os.environ", "from_env", "Credentials(", "AppConfig("):
            if needle in text:
                offenders.append(f"{client.relative_to(SRC)}: {needle}")
    base = (YANDEX / "base.py").read_text(encoding="utf-8")
    for needle in ("os.environ", "from_env", "Credentials(", "AppConfig("):
        if needle in base:
            offenders.append(f"yandex/base.py: {needle}")
    assert not offenders, offenders


def test_arch8_single_config_source():
    """os.environ access and BaseSettings subclass definitions live only in settings.py."""
    offenders = []
    settings = SRC / "settings.py"
    for p in SRC.rglob("*.py"):
        if p == settings:
            continue
        text = p.read_text(encoding="utf-8")
        if "os.environ" in text:
            offenders.append(f"{p.relative_to(SRC)}: os.environ")
        if re.search(r"class \w+\(BaseSettings\)", text):
            offenders.append(f"{p.relative_to(SRC)}: BaseSettings subclass")
    assert not offenders, offenders


def test_arch9_no_status_branching_outside_transport():
    """Non-2xx responses raise typed YandexError subclasses from transport.py only."""
    offenders = [
        str(p.relative_to(SRC))
        for p in SRC.rglob("*.py")
        if p.name != "transport.py" and "raise_for_status" in p.read_text(encoding="utf-8")
    ]
    assert not offenders, offenders


def test_arch10_no_uplink_timeout_shadow():
    """A configurable value is never overridden by a hardcoded literal at a call site."""
    offenders = [
        str(p.relative_to(SRC))
        for p in SRC.rglob("*.py")
        if "@uplink.timeout" in p.read_text(encoding="utf-8")
    ]
    assert not offenders, f"@uplink.timeout shadows YCLI_TIMEOUT_SECONDS: {offenders}"


def test_arch10_sdk_defaults_match_appconfig():
    """The SDK constructor defaults (carve-out) stay equal to AppConfig's defaults."""
    import inspect

    from ycli.settings import AppConfig
    from ycli.yandex.tracker.client import TrackerClient

    params = inspect.signature(TrackerClient).parameters
    assert params["timeout_seconds"].default == int(
        AppConfig.model_fields["timeout_seconds"].default
    )
    assert params["retries"].default == AppConfig.model_fields["retries"].default


def test_every_mcp_tool_has_description_and_output_schema():
    """Every tool has a docstring-derived description and a return-annotation-derived output schema.

    The docstring IS the client-facing description (the LLM's selector).
    The return type annotation IS the output schema (auto-derived by fastmcp).
    Both are required — omitting either makes the tool invisible or unusable to agents.
    See docs/conventions/resources.md §MCP tool-metadata standard.
    """
    tools = _mcp_tools()
    assert tools, "no MCP tools discovered"
    for tool in tools:
        assert tool.description, f"{tool.name!r} is missing a docstring (→ description)"
        assert tool.outputSchema is not None, (
            f"{tool.name!r} is missing a return type annotation (→ outputSchema)"
        )


ROOT = Path(__file__).resolve().parent.parent

# User-facing doc files and globs to scan for purged idioms (ARCH-11).
# Historical / rule-defining files are intentionally excluded:
#   docs/superpowers/**  — point-in-time specs and plans
#   PROMPT.md            — historical transcript
#   CHANGELOG.md         — historical release notes
#   ARCHITECTURE.md      — DEFINES the forbidden idioms as rules
#   .venv/** / .git/**   — not user-facing docs
_LIVE_DOC_GLOBS = [
    "README.md",
    "CLAUDE.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/api-coverage.md",
    "docs/conventions/**/*.md",
    "plugins/**/*.md",
]

# Patterns whose mere presence in a live doc signals a purged idiom — either the CALL/USAGE
# syntax of a decommissioned API, or a decommissioned literal string.
# Rationale: `.from_env(` and `session_from_env(` match invocation; prose like "no from_env"
# does not match because it lacks the trailing `(`. `X-Org-ID` (capital D) is the wrong-cased
# org header from the old "casing differs per service" gotcha — the transport emits one
# canonical `X-Org-Id` for every service (case-insensitive per RFC 9110), so the correct
# `X-Org-Id` must never regress to `X-Org-ID`. The substring differs in the final letter, so
# the correct casing is not matched.
_PURGED_CALL_PATTERNS = [
    ".from_env(",
    "session_from_env(",
    "X-Org-ID",
]


def _live_doc_files() -> list[Path]:
    """Return the list of tracked user-facing doc files to scan (ARCH-11)."""
    files: list[Path] = []
    for glob_pattern in _LIVE_DOC_GLOBS:
        matched = sorted(ROOT.glob(glob_pattern))
        files.extend(p for p in matched if p.is_file())
    return files


def test_arch11_no_purged_idioms_in_live_docs():
    """User-facing docs must not show purged call idioms that ARCH-7/ARCH-10 forbid in code.

    Scanned files: README.md, CLAUDE.md, AGENTS.md, CONTRIBUTING.md, SECURITY.md,
    docs/api-coverage.md, docs/conventions/**/*.md, plugins/**/*.md.
    Excluded (historical/rule-defining): docs/superpowers/**, PROMPT.md, CHANGELOG.md,
    ARCHITECTURE.md (it defines the forbidden idioms as rules), .venv/**, .git/**.
    Patterns checked: .from_env(  session_from_env(  X-Org-ID
    """
    doc_files = _live_doc_files()
    assert doc_files, "expected at least one live doc file to scan; glob list may be broken"
    offenders: list[str] = []
    for doc_file in doc_files:
        text = doc_file.read_text(encoding="utf-8")
        for pattern in _PURGED_CALL_PATTERNS:
            if pattern in text:
                rel = doc_file.relative_to(ROOT)
                offenders.append(f"{rel}: contains purged call pattern {pattern!r}")
    assert not offenders, (
        "Purged idioms found in live docs — remove the call-site example or update the doc. "
        f"Offenders: {offenders}"
    )
