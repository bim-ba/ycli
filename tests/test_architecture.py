"""Architecture invariants as tests — see ARCHITECTURE.md (ARCH-1/2/3/4/5/6/7/8/9/10/11).

A failure means a change drifted from the architecture. Fix the code, or — if the
change is intentional — update ARCHITECTURE.md and this check together in one PR.
"""

from __future__ import annotations

import ast
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


def _resource_operations():
    """Yield ``(domain_slug, resource_attr, sdk_ops)`` for every domain resource client."""
    gen = _load_gen_coverage()
    clients = {
        "tracker": gen.TrackerClient(oauth_token="x", organization_id="x"),
        "wiki": gen.WikiClient(oauth_token="x", organization_id="x"),
        "forms": gen.FormsClient(oauth_token="x", organization_id="x"),
    }
    for slug, client in clients.items():
        for attr, resource in sorted(vars(client).items()):
            if isinstance(resource, gen.BaseYandex):
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
    # Binary download — raw bytes go to a file/stdout via ycli.cli.binary.write_output; bytes
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
ARCH3_BODY_DICT_ALLOWLIST: dict[str, str] = {
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
    is listed in :data:`ARCH3_BODY_DICT_ALLOWLIST`. Pure over source text so the guard can be
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
            if f"{module_label}:{node.name}" in ARCH3_BODY_DICT_ALLOWLIST:
                continue
            offenders.append(
                f"{module_label}: {node.name}(body: {ast.unparse(arg.annotation)}) "
                "— must be a typed pydantic model, not dict"
            )
    return offenders


def test_arch3_mcp_write_tool_bodies_are_typed():
    """An MCP write tool's ``body`` parameter is a typed pydantic model, never bare ``dict``.

    docs/conventions/resources.md §4: the model becomes the tool's input schema, so an agent
    sees field names/types/aliases instead of an opaque ``object``, and a malformed payload
    fails schema validation before the HTTP call. Fail-closed: only the one documented
    ``ARCH3_BODY_DICT_ALLOWLIST`` entry is exempt.
    """
    offenders = []
    for mcp_py in YANDEX.rglob("mcp.py"):
        rel = str(mcp_py.relative_to(SRC))
        offenders += _untyped_body_offenders(mcp_py.read_text(encoding="utf-8"), rel)
    assert not offenders, (
        "MCP write-tool `body` parameters must be typed pydantic models, not dict — convert the "
        f"parameter, or add a documented ARCH3_BODY_DICT_ALLOWLIST entry: {offenders}"
    )


def test_arch3_typed_body_guard_bites():
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

    allowlisted_key = next(iter(ARCH3_BODY_DICT_ALLOWLIST))
    module_label, func_name = allowlisted_key.rsplit(":", 1)
    allowlisted = (
        f'@mcp.tool(name="{func_name}")\n'
        f"def {func_name}(body: dict, client=Depends(x)) -> Permissions:\n"
        "    return client.entities.set_permissions(body)\n"
    )
    assert _untyped_body_offenders(allowlisted, module_label) == []


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


# ARCH-4 carve-out (D1): the only two CLI files allowed a bare ``print(`` — the scalar
# ``count`` result (carve-out a) and the wiki raw-markdown dump (carve-out c). Any other bare
# print in a cli.py bypasses ``Serializer.serialize`` and trips the guard below.
_ARCH4_BARE_PRINT_ALLOWLIST = frozenset(
    {
        Path("yandex/tracker/issues/cli.py"),
        Path("yandex/wiki/pages/cli.py"),
    }
)
# The builtin ``print`` as a call — not an attribute access (``console.print(``, Rich) and not
# the tail of a longer name (``pprint(``): preceded by neither ``.`` nor a word character.
_BARE_PRINT_RE = re.compile(r"(?<![.\w])print\s*\(")


def test_arch4_no_bare_print_in_cli():
    """A CLI command renders model output through the Serializer, never a bare ``print(``.

    ARCH-4 confines rendering to ``Serializer.serialize``; a bare ``print(model)`` slips a
    surface past it. ``console.print(`` (Rich status text) and ``pprint(`` are not the builtin
    and are fine. The two intentional bare prints — the scalar ``count`` (carve-out a) and the
    wiki raw-markdown dump (carve-out c) — are allowlisted.
    """
    offenders = []
    for cli_py in SRC.rglob("cli.py"):
        rel = cli_py.relative_to(SRC)
        if rel in _ARCH4_BARE_PRINT_ALLOWLIST:
            continue
        if _BARE_PRINT_RE.search(cli_py.read_text(encoding="utf-8")):
            offenders.append(str(rel))
    assert not offenders, (
        f"bare print() bypasses Serializer.serialize in CLI files: {offenders} — render via "
        "Serializer, or add a documented ARCH-4 carve-out to _ARCH4_BARE_PRINT_ALLOWLIST"
    )


def test_arch4_bare_print_guard_bites():
    """Prove-it: the guard flags the builtin ``print`` but not ``console.print`` / ``pprint``."""
    assert _BARE_PRINT_RE.search("    print(model)")
    assert _BARE_PRINT_RE.search("print(app_ctx.tracker.issues.count(body=body))")
    assert not _BARE_PRINT_RE.search("    console.print(f'Opening {url}')")
    assert not _BARE_PRINT_RE.search("    pprint(model)")
    assert not _BARE_PRINT_RE.search("    fingerprint(value)")


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
    docs/conventions/**/*.md, plugins/**/*.md.
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
