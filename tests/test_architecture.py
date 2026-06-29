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
# Allow-list (fail-closed): an MCP tool's verb MUST be a known read. A new read
# operation adds its verb here deliberately; any other verb (modify/patch/post/…)
# fails, so a write tool can't slip in by naming. Keep in sync with ARCHITECTURE.md.
READ_VERBS = {"get", "list", "count", "full", "search", "descendants", "meta"}
# Behavioral backstop: even a read-named tool must not call a client write method.
_WRITE_CALL_RE = re.compile(r"\.(create|update|add|execute|delete|remove|set)\(")


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
        assert verb in READ_VERBS, (
            f"MCP tool {t.name!r} verb {verb!r} is not a known read verb {sorted(READ_VERBS)} "
            "— writes ship SDK+CLI only; if this is a new read, add the verb to READ_VERBS"
        )
        ann = getattr(t, "annotations", None)
        assert ann is not None and ann.readOnlyHint is True, f"{t.name!r} lacks readOnlyHint"


def test_arch3_mcp_modules_call_no_write_methods():
    """Even a read-named tool must not invoke a client write method from an mcp.py."""
    offenders = []
    for mcp_py in YANDEX.rglob("mcp.py"):
        for m in _WRITE_CALL_RE.finditer(mcp_py.read_text(encoding="utf-8")):
            offenders.append(f"{mcp_py.relative_to(SRC)}: calls .{m.group(1)}(")
    assert not offenders, f"MCP modules must not call client write methods: {offenders}"


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

# Patterns that match CALL/USAGE syntax of purged idioms — not prose rule-descriptions.
# Rationale: `.from_env(` and `session_from_env(` match invocation; prose like "no from_env"
# does not match because it lacks the trailing `(`.
_PURGED_CALL_PATTERNS = [
    ".from_env(",
    "session_from_env(",
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
    Patterns checked: .from_env(  session_from_env(
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
