"""Architecture invariants as tests — see ARCHITECTURE.md (ARCH-1/2/3/4/5/6/7/8/9/10/11).

A failure means a change drifted from the architecture. Fix the code, or — if the
change is intentional — update ARCHITECTURE.md and this check together in one PR.
"""

from __future__ import annotations

import ast
import asyncio
import functools
import re
from pathlib import Path

import httpx2
from fastmcp import Client

from ycli.mcp import mcp as root_mcp
from ycli.yandex.core.endpoint import EFFECT_EXTENSION
from ycli.yandex.mcp import DESTRUCTIVE, RO, WRITE, WRITE_IDEMPOTENT
from ycli.yandex.registry import SERVICES

SRC = Path(__file__).resolve().parent.parent / "src" / "ycli"
YANDEX = SRC / "yandex"
DOMAINS = tuple(service.name for service in SERVICES)
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


def _load_gen_coverage():
    """Load ``scripts/gen_coverage.py`` as a module and reuse its SDK-operation discovery.

    D2 leverages the same public-method enumeration gen_coverage uses for the README coverage
    tables, so "what counts as a client operation" has a single definition across the repo.
    """
    import importlib.util
    import sys

    path = SRC.parent.parent / "scripts" / "gen_coverage.py"
    spec = importlib.util.spec_from_file_location("gen_coverage", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registration is needed only *during* exec so gen_coverage's dataclasses can resolve their
    # fields; scope the side effect by restoring any prior sys.modules entry afterwards.
    saved = sys.modules.get(spec.name)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if saved is not None:
            sys.modules[spec.name] = saved
        else:
            sys.modules.pop(spec.name, None)
    return module


@functools.cache
def _clients() -> dict[str, object]:
    return {
        service.name: service.client_class()(oauth_token="x", organization_id="x")
        for service in SERVICES
    }


def _resource_operations():
    """Yield ``(domain_slug, resource_attr, sdk_ops)`` for every domain resource client."""
    gen = _load_gen_coverage()
    for slug, client in _clients().items():
        for attr, resource in sorted(vars(client).items()):
            if isinstance(resource, gen.BaseYandex | gen.Resource):
                yield slug, attr, set(gen._sdk_operations(resource))


def _wrapped_ops_in_source(source: str, resource_attr: str) -> set[str]:
    """Op names invoked as ``….<resource_attr>.<op>(…)`` anywhere in ``source`` (AST).

    Structural, not name-based: the CLI and MCP wrappers reference the client operation
    directly (``app_ctx.tracker.issues.get(…)`` / ``client.issues.get(…)``), so this sees the
    real coverage even where the surface command/tool is *named* differently from the op
    (``checklists.create`` → CLI ``add``; ``pages.get_by_id`` → MCP ``by_id_get``). A same-named
    method on some other object (``other.get(…)``) or a bare-name call does not count.
    """
    wrapped: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == resource_attr
        ):
            wrapped.add(node.func.attr)
    return wrapped


def _wrapped_ops(surface_py: Path, resource_attr: str) -> set[str]:
    """Structural surface coverage for ``resource_attr`` in one cli.py / mcp.py file."""
    if not surface_py.exists():
        return set()
    return _wrapped_ops_in_source(surface_py.read_text(encoding="utf-8"), resource_attr)


def _surface_gaps(sdk_ops: set[str], cli_ops: set[str], mcp_ops: set[str]) -> set[str]:
    """Client ops not wrapped on BOTH the CLI and MCP surfaces (pure set logic)."""
    return {op for op in sdk_ops if not (op in cli_ops and op in mcp_ops)}


# ARCH-1 operation-level parity (D2). Every public client operation is wrapped on BOTH the CLI
# and the MCP surface, EXCEPT the intentional asymmetries frozen here (id -> reason). The gap
# set is computed structurally (which client op each surface actually calls), so it survives the
# surfaces naming a command/tool differently from the op. Regenerate and edit this map in the
# same PR when a genuine asymmetry is added or resolved.
ARCH1_SURFACE_ASYMMETRIES: dict[str, str] = {
    # Binary download — the CLI returns the raw bytes as a BinaryResult (file or stdout); bytes
    # are not a model and can't round-trip an MCP tool result, so these stay CLI-only.
    "tracker.attachments.download": "binary download — CLI-only (bytes)",
    "tracker.attachments.download_thumbnail": "binary download — CLI-only (bytes)",
    "tracker.entities.attachment_download": "binary download — CLI-only (bytes)",
    "wiki.attachments.download": "binary download — CLI-only (bytes)",
    "wiki.attachments.download_by_url": "binary download — CLI-only (bytes)",
    "forms.answers.download_export": "binary download — CLI-only (bytes)",
    "forms.files.download": "binary download — CLI-only (bytes)",
    "forms.keysets.download": "binary download — CLI-only (bytes)",
    # Binary upload — the CLI streams a local file; no MCP tool by design.
    "forms.files.upload": "binary upload — CLI-only (bytes)",
    "forms.images.upload": "binary upload — CLI-only (bytes)",
    # CLI-only helper: the `answers export` command drives the export poll loop; the MCP surface
    # exposes the one-shot `export` submit instead of the polling wrapper.
    "forms.answers.export_results": "CLI-only export poll helper",
    # SDK-internal single-page primitive, superseded by the pagination-aware `list_all` that BOTH
    # surfaces wrap; `list` itself is intentionally unwrapped on both.
    "forms.answers.list": "SDK-internal single-page primitive (surfaces wrap list_all)",
}


def test_arch1_operation_level_parity():
    """Every client operation is wrapped on both the CLI and MCP surfaces (ARCH-1).

    Strengthens the four-file existence check: a client method with no CLI command *and* no MCP
    tool — or one wrapped on only one surface — is caught. Coverage is read structurally from
    each surface's calls into the client, so a command/tool named differently from the op still
    counts. Intentional asymmetries are frozen in ``ARCH1_SURFACE_ASYMMETRIES``.
    """
    gaps: dict[str, tuple[bool, bool]] = {}
    for slug, attr, sdk_ops in _resource_operations():
        rdir = YANDEX / slug / attr
        cli_ops = _wrapped_ops(rdir / "cli.py", attr)
        mcp_ops = _wrapped_ops(rdir / "mcp.py", attr)
        for op in _surface_gaps(sdk_ops, cli_ops, mcp_ops):
            gaps[f"{slug}.{attr}.{op}"] = (op in cli_ops, op in mcp_ops)
    unexpected = sorted(set(gaps) - set(ARCH1_SURFACE_ASYMMETRIES))
    resolved = sorted(set(ARCH1_SURFACE_ASYMMETRIES) - set(gaps))
    assert not unexpected and not resolved, (
        "operation-level surface parity drifted. Every client op must be wrapped on BOTH the "
        "CLI and MCP surfaces, or listed in ARCH1_SURFACE_ASYMMETRIES with a reason.\n"
        f"  newly unwrapped (wrap on both surfaces, or allowlist with a reason): {unexpected}\n"
        f"  now wrapped (remove from the allowlist): {resolved}"
    )


def test_arch1_parity_check_bites():
    """Prove-it: the gap detector flags an op missing from either surface, and the structural
    reader counts a real client call but not a same-named call on another object."""
    # An op wrapped on neither / only one surface is a gap; one on both is not.
    assert _surface_gaps({"orphan", "wired"}, {"wired"}, {"wired"}) == {"orphan"}
    assert _surface_gaps({"cli_only"}, {"cli_only"}, set()) == {"cli_only"}
    assert _surface_gaps({"mcp_only"}, set(), {"mcp_only"}) == {"mcp_only"}
    assert _surface_gaps({"wired"}, {"wired"}, {"wired"}) == set()
    # The structural reader records `….issues.<op>(…)` only — not `.get` on another chain nor a
    # bare-name call — so it neither misses aliased wrappers nor over-counts.
    source = (
        "def cmd(app_ctx):\n"
        "    app_ctx.tracker.issues.get(key)\n"
        "    app_ctx.tracker.issues.update(key, body)\n"
        "    other.get(x)\n"
        "    plain_get(x)\n"
    )
    assert _wrapped_ops_in_source(source, "issues") == {"get", "update"}
    assert _wrapped_ops_in_source(source, "boards") == set()


def _mcp_tools():
    async def go():
        async with Client(root_mcp) as c:
            return await c.list_tools()

    return asyncio.run(go())


def _uplink_tools() -> list:
    """MCP tools of resources still on uplink — the ones the verb maps must classify."""
    core = _core_tool_prefixes()
    return [tool for tool in _mcp_tools() if not tool.name.startswith(core)]


def test_arch3_verb_maps_are_still_needed():
    """Kill-criterion: once no resource is left on uplink, delete the verb maps and their tests."""
    assert _uplink_tools(), (
        "every resource runs on the httpx2 core: delete the READ/WRITE/… verb maps, "
        "test_arch3_mcp_annotation_honesty and the read-tool AST backstop (ARCH-3)"
    )


def test_arch3_mcp_annotation_honesty():
    """Every uplink tool's hints match its verb class exactly (fail-closed on unknown verbs).

    Tools of resources on the httpx2 core are checked against their endpoint's effect instead
    (``test_arch3_core_tools_are_annotated_by_their_endpoint_effect``).

    The MCP-spec default for an unannotated tool is destructiveHint=true, so every
    write tool must declare its hints explicitly (WRITE / WRITE_IDEMPOTENT / DESTRUCTIVE
    in ycli.yandex.mcp); reads keep RO.
    """
    tools = _uplink_tools()
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


# The hints each endpoint effect implies (ARCH-3): the effect is declared once, on the
# endpoint; the MCP tool must agree with it.
_EFFECT_HINTS = {
    "read": RO,
    "write": WRITE,
    "idempotent_write": WRITE_IDEMPOTENT,
    "destructive": DESTRUCTIVE,
}
_HINT_KEYS = ("readOnlyHint", "destructiveHint", "idempotentHint")
# Arguments that make each core-resource tool send its request. Fail-closed both ways: a core
# tool without a case, or a case without a tool, fails the build.
ARCH3_EFFECT_CASES: dict[str, dict] = {
    "tracker_issues_get": {"key": "T-1"},
    "tracker_issues_list": {"queue": "T"},
    "tracker_issues_search": {"query": "Queue: T"},
    "tracker_issues_count": {},
    "tracker_issues_suggest": {"text": "bug"},
    "tracker_issues_create": {"body": {"queue": "T", "summary": "s"}},
    "tracker_issues_update": {"key": "T-1", "body": {"summary": "s"}},
    "tracker_issues_move": {"key": "T-1", "queue": "Q"},
    "tracker_issues_scroll_clear": {"body": {"scroll": "token"}},
}


class _SentError(Exception):
    """Stops a tool right after it sends its first request."""


def _core_tool_prefixes() -> tuple[str, ...]:
    gen = _load_gen_coverage()
    return tuple(
        f"{slug}_{attr.rstrip('_')}_"
        for slug, attr, _ in _resource_operations()
        if isinstance(getattr(_clients()[slug], attr), gen.Resource)
    )


def _hints_disagree(annotations: dict, effect: str) -> list[str]:
    expected = _EFFECT_HINTS[effect]
    return [key for key in _HINT_KEYS if annotations.get(key) != expected.get(key)]


def test_arch3_core_tools_are_annotated_by_their_endpoint_effect(monkeypatch):
    effects: list[str] = []

    def record(request: httpx2.Request) -> httpx2.Response:
        effects.append(request.extensions[EFFECT_EXTENSION])
        raise _SentError

    monkeypatch.setattr(
        "ycli.yandex.core.session.default_transport", lambda: httpx2.MockTransport(record)
    )
    prefixes = _core_tool_prefixes()
    tools = {tool.name: tool for tool in _mcp_tools() if tool.name.startswith(prefixes)}
    assert set(tools) == set(ARCH3_EFFECT_CASES), "ARCH3_EFFECT_CASES must list every core tool"

    async def sent_effect(name: str) -> str:
        effects.clear()
        async with Client(root_mcp) as client:
            await client.call_tool(name, ARCH3_EFFECT_CASES[name], raise_on_error=False)
        assert effects, f"{name} sent no request"
        return effects[0]

    offenders = {}
    for name, tool in tools.items():
        effect = asyncio.run(sent_effect(name))
        annotations = tool.annotations.model_dump() if tool.annotations else {}
        if wrong := _hints_disagree(annotations, effect):
            offenders[name] = f"effect {effect!r} but {wrong} disagree"
    assert not offenders, offenders


def test_arch3_effect_guard_bites():
    assert _hints_disagree(RO, "read") == []
    assert _hints_disagree(RO, "destructive") == [
        "readOnlyHint",
        "destructiveHint",
        "idempotentHint",
    ]
    assert _hints_disagree(WRITE, "idempotent_write") == ["idempotentHint"]


def test_arch3_write_tools_carry_write_tag():
    """`--read-only` hides writes by tag, so every write tool MUST carry the write tag.

    `ycli mcp start --read-only` calls ``mcp.disable(tags={WRITE_TAG})``; if a write tool were
    registered with the read ``TAGS`` (a copy-paste slip), it would leak through the reads-only
    view. The hint↔tag correlation is checked here so the safety flag can't fail open — a mis-
    tagged tool trips this even though its annotations are internally honest.
    """
    from ycli.yandex.mcp import WRITE_TAG

    tools = _mcp_tools()
    assert tools, "no MCP tools discovered"
    for t in tools:
        ann = getattr(t, "annotations", None)
        assert ann is not None, f"{t.name!r} lacks annotations"
        meta = getattr(t, "meta", None) or {}
        tags = set(meta.get("fastmcp", {}).get("tags", []) or [])
        is_write = ann.readOnlyHint is False
        assert (WRITE_TAG in tags) == is_write, (
            f"{t.name!r}: readOnlyHint={ann.readOnlyHint} but write-tag "
            f"{'present' if WRITE_TAG in tags else 'absent'} — a write tool must carry the "
            f"{WRITE_TAG!r} tag (so --read-only hides it) and a read must not"
        )


_WRITE_CLASSES = frozenset({"write", "write_idempotent", "destructive"})
# Every resource attribute name (== resource directory name). A write verb only counts when its
# receiver chain resolves to one of these — i.e. the call is `….<resource>.<op>(…)`, the same
# structural-receiver signal ARCH-1 parity uses. This stops a client write-verb (`update`,
# `add`, `clear`, `remove`, `set`, `move`, `append`) from being confused with the identically
# named Python container method on a bare local (`result.append(row)`, `acc.update(d)`).
_RESOURCE_NAMES = frozenset(d.name for d in _resource_dirs())


def _write_method_calls(
    node: ast.AST, module_defs: dict[str, ast.FunctionDef], seen: set[str]
) -> list[str]:
    """Client write-method names reachable from ``node``.

    Collects ``….<resource>.<verb>(…)`` calls whose verb classifies as a write — the receiver
    must be an attribute access naming a known resource (a bare local/builtin container receiver
    like ``result.append(…)`` is ignored, so a same-named container method is not mistaken for a
    client write) — and **follows** bare-name calls (``_helper(…)``) that resolve to a
    module-level ``def`` in ``module_defs`` so a write laundered one hop through a same-module
    helper is still seen. ``seen`` guards recursion.
    """
    found: list[str] = []
    for call in ast.walk(node):
        if not isinstance(call, ast.Call):
            continue
        func = call.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Attribute)
            and func.value.attr in _RESOURCE_NAMES
            and _classify(func.attr) in _WRITE_CLASSES
        ):
            found.append(func.attr)
        elif isinstance(func, ast.Name) and func.id in module_defs and func.id not in seen:
            seen.add(func.id)
            found.extend(_write_method_calls(module_defs[func.id], module_defs, seen))
    return found


def _read_tool_write_offenders(source: str) -> list[str]:
    """Read-classified MCP tools in ``source`` that reach a client write method.

    A tool is any ``@mcp.tool(name=…)``-decorated function; one without ``name=`` is itself an
    offender. For each read-classified tool, writes reached directly or through a module-level
    helper (see :func:`_write_method_calls`) are reported. Pure over source text so the guard
    can be exercised on a synthetic module (the prove-it test).
    """
    tree = ast.parse(source)
    module_defs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    offenders: list[str] = []
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
                    if kw.arg == "name"
                    and isinstance(kw.value, ast.Constant)
                    and isinstance(kw.value.value, str)
                ]
                if not names:
                    offenders.append(f"{node.name} registers a tool without name=")
                    continue
                tool_name = names[0]
        if tool_name is None or _classify(tool_name) != "read":
            continue
        for attr in _write_method_calls(node, module_defs, {node.name}):
            offenders.append(f"read tool {tool_name!r} calls .{attr}(…)")
    return offenders


def test_arch3_read_tools_call_no_write_methods():
    """A read-classified tool must not invoke a client write method — directly or laundered
    through a module-level helper in the same module (AST-checked)."""
    offenders = []
    for mcp_py in YANDEX.rglob("mcp.py"):
        rel = mcp_py.relative_to(SRC)
        offenders += [
            f"{rel}: {offender}"
            for offender in _read_tool_write_offenders(mcp_py.read_text(encoding="utf-8"))
        ]
    assert not offenders, f"read tools must not reach client write methods: {offenders}"


def test_arch3_read_tool_helper_indirection_is_caught():
    """Prove-it: a read tool laundering a write through a module-level helper trips the guard.

    The old body-only walk saw only ``_helper(client)`` (a bare name) and missed the write
    inside the helper; following module-level defs catches it. Direct writes stay caught and a
    read-only helper stays clean.
    """
    laundered = (
        "def _helper(client):\n"
        "    client.pages.delete(page_id)\n"
        "\n"
        '@mcp.tool(name="pages_get")\n'
        "def get(client):\n"
        "    return _helper(client)\n"
    )
    assert _read_tool_write_offenders(laundered) == ["read tool 'pages_get' calls .delete(…)"]

    direct = '@mcp.tool(name="pages_get")\ndef get(client):\n    return client.pages.delete(id)\n'
    assert _read_tool_write_offenders(direct) == ["read tool 'pages_get' calls .delete(…)"]

    clean = (
        "def _helper(client):\n"
        "    return client.pages.get(page_id)\n"
        "\n"
        '@mcp.tool(name="pages_get")\n'
        "def get(client):\n"
        "    return _helper(client)\n"
    )
    assert _read_tool_write_offenders(clean) == []


def test_arch3_container_methods_are_not_writes():
    """Prove-it: a read tool whose helper builds a plain collection is not mis-flagged.

    ``result.append(row)`` / ``acc.update(d)`` / ``seen.add(x)`` share names with client write
    verbs but are container methods on bare locals — a write verb only counts when its receiver
    chain names a known resource. A real ``self.client.<resource>.delete`` laundered through the
    same helper is still caught, so pagination/collection helpers stay legal without opening a
    hole.
    """
    container_only = (
        "def _collect(client):\n"
        "    result = []\n"
        "    result.append(row)\n"
        "    acc.update(d)\n"
        "    seen.add(x)\n"
        "    return result\n"
        "\n"
        '@mcp.tool(name="pages_list")\n'
        "def list_(client):\n"
        "    return _collect(client)\n"
    )
    assert _read_tool_write_offenders(container_only) == []

    laundered_via_self = (
        "def _collect(self):\n"
        "    result = []\n"
        "    result.append(row)\n"
        "    self.client.pages.delete(page_id)\n"
        "    return result\n"
        "\n"
        '@mcp.tool(name="pages_list")\n'
        "def list_(self):\n"
        "    return _collect(self)\n"
    )
    assert _read_tool_write_offenders(laundered_via_self) == [
        "read tool 'pages_list' calls .delete(…)"
    ]


# ARCH-3 typed body (docs/conventions/resources.md §4 "Typed request body — never `dict`"): a
# write MCP tool's `body` parameter must be the resource's typed pydantic request model, never a
# bare `dict`/`dict[...]`. Fail-closed with exactly one documented exception (id -> reason),
# frozen here in the same `ARCH1_SURFACE_ASYMMETRIES` string-map style. `Annotated[Base64Bytes,
# …]` (binary uploads) is an `ast.Subscript` whose `.value` is `ast.Name(id="Annotated")`, never
# `dict`, so it never matches this check — no allowlist entry is needed for it.
ARCH8_BODY_DICT_ALLOWLIST: dict[str, str] = {
    # PATCH …/extendedPermissions nests READ/WRITE/GRANT principal sets under grant/revoke verbs
    # (see references/yandex-360/tracker/ru/api-ref/entities/patch-access.md); the existing
    # ExtendedPermissionsUpdate/AclInput models describe a different, direct READ/WRITE/GRANT
    # shape and would misrepresent this endpoint's real wire body if used here. See the NOTE on
    # `set_permissions` in yandex/tracker/entities/mcp.py.
    "yandex/tracker/entities/mcp.py:set_permissions": (
        "wire shape nests READ/WRITE/GRANT under grant/revoke verbs; the existing "
        "ExtendedPermissionsUpdate/AclInput models describe a different (direct) shape"
    ),
}


def _bare_dict_annotation(annotation: ast.expr | None) -> bool:
    """``True`` if ``annotation`` is bare ``dict`` or subscripted ``dict[...]``.

    ``Annotated[Base64Bytes, …]`` is a subscript whose ``.value`` is ``ast.Name(id="Annotated")``
    — never ``"dict"`` — so it is never flagged.
    """
    if annotation is None:
        return False
    if isinstance(annotation, ast.Name):
        return annotation.id == "dict"
    return (
        isinstance(annotation, ast.Subscript)
        and isinstance(annotation.value, ast.Name)
        and annotation.value.id == "dict"
    )


def _untyped_body_offenders(source: str, module_label: str) -> list[str]:
    """``@mcp.tool``-decorated functions in ``source`` with a bare-``dict`` ``body`` parameter.

    Detects the ``@mcp.tool`` decorator the same way :func:`_read_tool_write_offenders` does.
    Matches both ``def`` and ``async def`` tool functions, so a future async write tool cannot
    slip a bare-``dict`` ``body`` past the guard. For each such function, every
    positional-or-keyword and keyword-only parameter named ``body`` is checked; a bare
    ``dict``/``dict[...]`` annotation is an offender unless ``{module_label}:{function_name}``
    is listed in :data:`ARCH8_BODY_DICT_ALLOWLIST`. Pure over source text so the guard can be
    exercised on a synthetic module (the prove-it test).
    """
    tree = ast.parse(source)
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(
            isinstance(deco, ast.Call)
            and isinstance(deco.func, ast.Attribute)
            and deco.func.attr == "tool"
            for deco in node.decorator_list
        ):
            continue
        for arg in (*node.args.args, *node.args.kwonlyargs):
            if arg.arg != "body" or arg.annotation is None:
                continue
            if not _bare_dict_annotation(arg.annotation):
                continue
            if f"{module_label}:{node.name}" in ARCH8_BODY_DICT_ALLOWLIST:
                continue
            offenders.append(
                f"{module_label}: {node.name}(body: {ast.unparse(arg.annotation)}) "
                "— must be a typed pydantic model, not dict"
            )
    return offenders


def test_arch8_mcp_write_tool_bodies_are_typed():
    """An MCP write tool's ``body`` parameter is a typed pydantic model, never bare ``dict``.

    docs/conventions/resources.md §4: the model becomes the tool's input schema, so an agent
    sees field names/types/aliases instead of an opaque ``object``, and a malformed payload
    fails schema validation before the HTTP call. Fail-closed: only the one documented
    ``ARCH8_BODY_DICT_ALLOWLIST`` entry is exempt.
    """
    offenders = []
    for mcp_py in YANDEX.rglob("mcp.py"):
        rel = str(mcp_py.relative_to(SRC))
        offenders += _untyped_body_offenders(mcp_py.read_text(encoding="utf-8"), rel)
    assert not offenders, (
        "MCP write-tool `body` parameters must be typed pydantic models, not dict — convert the "
        f"parameter, or add a documented ARCH8_BODY_DICT_ALLOWLIST entry: {offenders}"
    )


def test_arch8_typed_body_guard_bites():
    """Prove-it: the guard flags bare/subscripted ``dict`` bodies but not a typed model or
    ``Annotated[Base64Bytes, …]``, and respects the allowlist."""
    bare = (
        '@mcp.tool(name="widgets_create")\n'
        "def create(body: dict, client=Depends(x)) -> Widget:\n"
        "    return client.widgets.create(body)\n"
    )
    assert _untyped_body_offenders(bare, "synthetic/mcp.py") == [
        "synthetic/mcp.py: create(body: dict) — must be a typed pydantic model, not dict"
    ]

    async_bare = (
        '@mcp.tool(name="widgets_create")\n'
        "async def create(body: dict, client=Depends(x)) -> Widget:\n"
        "    return await client.widgets.create(body)\n"
    )
    assert _untyped_body_offenders(async_bare, "synthetic/mcp.py") == [
        "synthetic/mcp.py: create(body: dict) — must be a typed pydantic model, not dict"
    ]

    subscripted = (
        '@mcp.tool(name="widgets_create")\n'
        "def create(body: dict[str, str], client=Depends(x)) -> Widget:\n"
        "    return client.widgets.create(body)\n"
    )
    assert _untyped_body_offenders(subscripted, "synthetic/mcp.py") == [
        "synthetic/mcp.py: create(body: dict[str, str]) — must be a typed pydantic model, not dict"
    ]

    typed = (
        '@mcp.tool(name="widgets_create")\n'
        "def create(body: WidgetCreate, client=Depends(x)) -> Widget:\n"
        "    return client.widgets.create(body)\n"
    )
    assert _untyped_body_offenders(typed, "synthetic/mcp.py") == []

    binary_upload = (
        '@mcp.tool(name="files_upload")\n'
        "def upload(body: Annotated[Base64Bytes, Field(...)], client=Depends(x)) -> Ack:\n"
        "    return client.files.upload(body)\n"
    )
    assert _untyped_body_offenders(binary_upload, "synthetic/mcp.py") == []

    allowlisted_key = next(iter(ARCH8_BODY_DICT_ALLOWLIST))
    module_label, func_name = allowlisted_key.rsplit(":", 1)
    allowlisted = (
        f'@mcp.tool(name="{func_name}")\n'
        f"def {func_name}(body: dict, client=Depends(x)) -> Permissions:\n"
        "    return client.entities.set_permissions(body)\n"
    )
    assert _untyped_body_offenders(allowlisted, module_label) == []


def test_arch4_serialization_confined_to_output():
    """Rendering lives in output.py; model_dump_json/yaml.safe_dump/json.dumps nowhere else."""
    offenders = []
    # log.py formats diagnostic log records for stderr (its JSON formatter), not model output.
    allowed = {SRC / "cli" / "output.py", SRC / "log.py"}
    for p in SRC.rglob("*.py"):
        if p in allowed:
            continue
        text = p.read_text(encoding="utf-8")
        if "model_dump_json" in text or "yaml.safe_dump" in text or "json.dumps" in text:
            offenders.append(str(p.relative_to(SRC)))
    assert not offenders, f"serialization must live only in output.py; found in {offenders}"


def _to_stderr(call: ast.Call) -> bool:
    """``err=True`` (typer) or ``stderr=True`` (rich ``Console``) among the call's keywords."""
    return any(
        k.arg in {"err", "stderr"} and isinstance(k.value, ast.Constant) and k.value.value is True
        for k in call.keywords
    )


def _stdout_writes(source: str) -> list[str]:
    """Places in ``source`` that write to stdout: ``print``, ``rich.print``, ``typer.echo`` /
    ``secho`` and ``Console(...)`` without a stderr flag, ``os.write``, and any use of the name
    ``stdout``. Messages to stderr are UI, not output."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            owner = (
                func.value.id
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)
                else None
            )
            if name == "print" and (isinstance(func, ast.Name) or owner == "rich"):
                found.append(f"print (line {node.lineno})")
            elif name in {"echo", "secho", "Console"} and not _to_stderr(node):
                found.append(f"{name} (line {node.lineno})")
            elif name == "write" and owner == "os":
                found.append(f"os.write (line {node.lineno})")
        elif (
            (isinstance(node, ast.Attribute) and node.attr == "stdout")
            or (isinstance(node, ast.Name) and node.id == "stdout")
            or (isinstance(node, ast.ImportFrom) and any(a.name == "stdout" for a in node.names))
        ):
            found.append(f"stdout (line {node.lineno})")
    return found


def test_arch4_commands_return_and_never_print():
    """A CLI command returns its result; only ``output.render`` writes to stdout."""
    offenders = {
        str(cli_py.relative_to(SRC)): writes
        for cli_py in SRC.rglob("cli.py")
        if (writes := _stdout_writes(cli_py.read_text(encoding="utf-8")))
    }
    assert not offenders, f"return the value instead of printing it: {offenders}"


def test_arch4_stdout_guard_bites():
    """Prove-it: the guard flags each way to reach stdout and lets stderr messages through."""
    flagged = {
        "print(model)": "print (line 1)",
        "rich.print(model)": "print (line 1)",
        "typer.echo(name)": "echo (line 1)",
        "Console().print(model)": "Console (line 1)",
        "sys.stdout.buffer.write(data)": "stdout (line 1)",
        "from sys import stdout": "stdout (line 1)",
        "os.write(1, data)": "os.write (line 1)",
    }
    for source, finding in flagged.items():
        assert finding in _stdout_writes(source), source
    assert _stdout_writes("typer.echo('note', err=True)") == []
    assert _stdout_writes("Console(stderr=True).print('Opening')") == []
    assert _stdout_writes("console.print('Opening')\npprint(x)") == []


_TOKEN_RE = re.compile(r"YANDEX_ID_\w+\s*=\s*['\"]")
_VERSION_RE = re.compile(r"__version__\s*=\s*['\"]\d")
_ORG_HEADER_RE = re.compile(r"X-Org-I[dD]")
_YANDEX_HOST_RE = re.compile(
    r"https://[\w.-]*api[\w.-]*\.yandex\.(?:net|ru)"
)  # API hosts, not web pages
# Where a Yandex host may be spelled, and why: each service's profile, the IAM token endpoint,
# and the OAuth login flow's own endpoints.
ARCH5_HOST_HOMES = {
    Path("yandex/tracker/__init__.py"): "Tracker service profile",
    Path("yandex/wiki/__init__.py"): "Wiki service profile",
    Path("yandex/forms/__init__.py"): "Forms service profile",
    Path("yandex/core/auth.py"): "IAM token endpoint for service accounts",
    Path("yandex/status/client.py"): "OAuth device/implicit flow and api360 org lookup",
}


def _single_source_offenders(rel: Path, text: str) -> list[str]:
    offenders = []
    if _TOKEN_RE.search(text):
        offenders.append(f"{rel}: hardcoded YANDEX_ID token literal")
    if rel != Path("__init__.py") and _VERSION_RE.search(text):
        offenders.append(f"{rel}: hardcoded __version__ literal")
    if rel != Path("yandex/core/profile.py") and _ORG_HEADER_RE.search(text):
        offenders.append(f"{rel}: org header string outside yandex/core/profile.py")
    if rel not in ARCH5_HOST_HOMES and _YANDEX_HOST_RE.search(text):
        offenders.append(f"{rel}: Yandex host outside a service profile")
    if rel != Path("settings.py"):
        if "os.environ" in text:
            offenders.append(f"{rel}: os.environ outside settings.py")
        if re.search(r"class \w+\(BaseSettings\)", text):
            offenders.append(f"{rel}: BaseSettings subclass outside settings.py")
    if "@uplink.timeout" in text:
        offenders.append(f"{rel}: @uplink.timeout shadows YCLI__HTTP__TIMEOUT_SECONDS")
    return offenders


def test_arch5_single_sources_of_truth():
    """Version, credentials, org header, hosts, env access and timeouts each have one home."""
    offenders = [
        finding
        for p in SRC.rglob("*.py")
        for finding in _single_source_offenders(p.relative_to(SRC), p.read_text(encoding="utf-8"))
    ]
    assert not offenders, offenders


def test_arch5_guard_bites():
    rel = Path("yandex/wiki/pages/client.py")
    for source in (
        'YANDEX_ID_OAUTH_TOKEN = "x"',
        '__version__ = "1.0"',
        'headers = {"X-Org-Id": org}',
        'URL = "https://api.wiki.yandex.net/v1"',
        "token = os.environ['T']",
        "class Local(BaseSettings): ...",
        "@uplink.timeout(30)",
    ):
        assert _single_source_offenders(rel, source), source


# The composition roots: the only modules that build settings from the environment.
ARCH7_ROOTS = {
    Path("cli/app.py"): "CLI root callback (logging config)",
    Path("cli/context.py"): "CLI dependency container",
    Path("mcp/__main__.py"): "python -m ycli.mcp entry point",
    Path("yandex/mcp.py"): "MCP per-request providers",
    Path("yandex/status/cli.py"): "auth status/login read and write credentials by design",
}
_SETTINGS_MODELS = {"AppConfig", "Credentials", "OAuthAppConfig"}


def _settings_constructions(source: str) -> list[int]:
    return [
        node.lineno
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _SETTINGS_MODELS
    ]


def test_arch7_settings_are_built_only_at_composition_roots():
    """Everything else receives its configuration as arguments (dependency injection)."""
    offenders = {
        str(rel): lines
        for p in SRC.rglob("*.py")
        if (rel := p.relative_to(SRC)) not in ARCH7_ROOTS and rel != Path("settings.py")
        if (lines := _settings_constructions(p.read_text(encoding="utf-8")))
    }
    assert not offenders, f"settings built outside a composition root: {offenders}"


def test_arch7_guard_bites():
    assert _settings_constructions("config = AppConfig()\ncreds = Credentials()") == [1, 2]
    assert _settings_constructions("def f(config: AppConfig): return config.http") == []


def test_arch8_errors_are_mapped_in_one_place():
    """Non-2xx answers become typed YandexErrors through ``errors.error_for_status`` only."""
    homes = {Path("yandex/errors.py"), Path("yandex/transport.py"), Path("yandex/core/session.py")}
    offenders = [
        str(rel)
        for p in SRC.rglob("*.py")
        if (rel := p.relative_to(SRC)) not in homes
        if re.search(r"raise_for_status|error_for_status\(", p.read_text(encoding="utf-8"))
        and rel != Path("yandex/core/auth.py")  # the IAM token exchange maps its own failure
    ]
    assert not offenders, offenders


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
