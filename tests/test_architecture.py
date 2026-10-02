"""Architecture invariants as tests — see ARCHITECTURE.md (ARCH-1..8).

A failure means a change drifted from the architecture. Fix the code, or — if the
change is intentional — update ARCHITECTURE.md and this check together in one PR.
"""

from __future__ import annotations

import ast
import asyncio
import functools
import re
from pathlib import Path

from fastmcp import Client

from ycli.mcp.server import mcp as root_mcp
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


def _served_cli_groups() -> set[str]:
    """``domain.group`` for every resource group the ``ycli`` CLI dispatches to.

    Read from the built Click tree, each lazy service group loaded (``ycli.cli.lazy``), so a
    sub-app that is never ``add_typer``-ed into its domain is absent.
    """
    import typer.main

    from ycli.cli.app import app
    from ycli.cli.lazy import LazyGroup, RootGroup

    root = typer.main.get_command(app)
    assert isinstance(root, RootGroup)
    groups = set()
    for domain in DOMAINS:
        service = root.commands[domain]
        assert isinstance(service, LazyGroup)
        groups |= {f"{domain}.{group}" for group in service.load().commands}
    return groups


def _surface_names(resource: str) -> tuple[str, str]:
    """A resource directory's CLI group and MCP tool prefix.

    ``tracker.import_`` -> ``("tracker.import", "tracker_import_")``.
    """
    domain, _, name = resource.partition(".")
    name = name.rstrip("_")
    return f"{domain}.{name}", f"{domain}_{name}_"


def _served_gaps(
    on_disk: set[str], wired: set[str], cli_groups: set[str], tools: set[str], cli_only: set[str]
) -> list[str]:
    """Resources the running surfaces do not serve, and served names with no resource.

    ``on_disk`` and ``wired`` are ``domain.resource`` (the directory and the domain client's
    attribute, e.g. ``tracker.import_``); ``cli_groups`` are ``domain.group`` and ``tools`` the
    served MCP tool names. A resource in ``cli_only`` (every operation a listed CLI-only
    asymmetry) needs no MCP tool.
    """
    gaps = []
    for resource in sorted(on_disk | wired):
        domain = resource.partition(".")[0]
        group, prefix = _surface_names(resource)
        if resource not in on_disk:
            gaps.append(f"{resource}: wired into {domain}/client.py but has no directory")
            continue
        if resource not in wired:
            gaps.append(f"{resource}: not wired into {domain}/client.py")
        if group not in cli_groups:
            gaps.append(f"{resource}: no CLI group — not add_typer-ed in {domain}/cli.py")
        if resource not in cli_only and not any(tool.startswith(prefix) for tool in tools):
            gaps.append(f"{resource}: serves no MCP tool — not mounted in {domain}/mcp.py")
    names = [_surface_names(resource) for resource in on_disk]
    groups = {group for group, _ in names}
    prefixes = tuple(prefix for _, prefix in names)
    gaps += [
        f"{group}: a CLI group with no resource directory" for group in sorted(cli_groups - groups)
    ]
    gaps += [
        f"{tool}: an MCP tool with no resource directory"
        for tool in sorted(tools)
        if not tool.startswith(prefixes)
    ]
    return gaps


def test_arch1_every_resource_is_served():
    """Each resource directory is wired into its domain client and served by the running CLI
    and MCP server, and nothing is served without a directory (ARCH-1).

    The file and operation checks above read source files, so a resource never wired into
    ``client.py`` or never mounted (``app.add_typer`` / ``mcp.mount``) passes them; this reads
    what the surfaces actually serve.
    """
    on_disk = {f"{d.parent.name}.{d.name}" for d in _resource_dirs()}
    operations = {f"{slug}.{attr}": ops for slug, attr, ops in _resource_operations()}
    cli_only = {
        resource
        for resource, ops in operations.items()
        if ops and all(f"{resource}.{op}" in ARCH1_SURFACE_ASYMMETRIES for op in ops)
    }
    # status_* belongs to no resource: `status/` is a cross-cutting surface (see ARCHITECTURE.md).
    tools = {tool.name for tool in _mcp_tools() if not tool.name.startswith("status_")}
    gaps = _served_gaps(on_disk, set(operations), _served_cli_groups(), tools, cli_only)
    assert not gaps, gaps


def test_arch1_served_check_bites():
    """Prove-it: a ghost directory, an unmounted CLI group or MCP server, and served names with
    no directory are each reported; a CLI-only resource needs no MCP tool."""
    disk = {"forms.keysets", "tracker.import_"}
    groups = {"forms.keysets", "tracker.import"}
    tools = {"forms_keysets_get", "tracker_import_task"}
    assert _served_gaps(disk, disk, groups, tools, set()) == []
    assert _served_gaps(disk | {"forms.ghost"}, disk, groups, tools, set()) == [
        "forms.ghost: not wired into forms/client.py",
        "forms.ghost: no CLI group — not add_typer-ed in forms/cli.py",
        "forms.ghost: serves no MCP tool — not mounted in forms/mcp.py",
    ]
    assert _served_gaps(disk, disk | {"forms.ghost"}, groups, tools, set()) == [
        "forms.ghost: wired into forms/client.py but has no directory"
    ]
    assert _served_gaps(disk, disk, groups, {"tracker_import_task"}, set()) == [
        "forms.keysets: serves no MCP tool — not mounted in forms/mcp.py"
    ]
    assert _served_gaps(disk, disk, groups, {"tracker_import_task"}, {"forms.keysets"}) == []
    assert _served_gaps(disk, disk, {"forms.keysets"}, tools, set()) == [
        "tracker.import_: no CLI group — not add_typer-ed in tracker/cli.py"
    ]
    assert _served_gaps(
        disk, disk, groups | {"forms.stray"}, tools | {"wiki_stray_get"}, set()
    ) == [
        "forms.stray: a CLI group with no resource directory",
        "wiki_stray_get: an MCP tool with no resource directory",
    ]


# Resources still on uplink. The set may only shrink: a new resource starts on the httpx2 core
# (`/new-endpoint` scaffolds it there), and a resource that moves leaves this list; E2 empties it.
UPLINK_RESOURCES = frozenset(
    {
        *(f"wiki.{name}" for name in (
            "attachments", "comments", "grids", "me", "operations", "pages", "recovery",
            "resources", "uploadsessions",
        )),
    }
)  # fmt: skip


def _uplink_drift(on_uplink: set[str], frozen: frozenset[str]) -> list[str]:
    """New resources on uplink, and listed ones that have moved to the core."""
    return [
        f"{resource}: a new resource on uplink — build it on the httpx2 core (/new-endpoint)"
        for resource in sorted(on_uplink - frozen)
    ] + [
        f"{resource}: now on the core — remove it from UPLINK_RESOURCES"
        for resource in sorted(frozen - on_uplink)
    ]


def test_uplink_resources_only_shrink():
    """No new resource lands on the uplink stack that E2 deletes; the list tracks the move."""
    from ycli.yandex.core.resource import Resource

    on_uplink = {
        f"{slug}.{attr}"
        for slug, attr, _ in _resource_operations()
        if not isinstance(getattr(_clients()[slug], attr), Resource)
    }
    drift = _uplink_drift(on_uplink, UPLINK_RESOURCES)
    assert not drift, drift


def test_uplink_ratchet_bites():
    frozen = frozenset({"wiki.pages", "forms.surveys"})
    assert _uplink_drift({"wiki.pages", "forms.surveys"}, frozen) == []
    assert _uplink_drift({"wiki.pages", "forms.surveys", "forms.ghost"}, frozen) == [
        "forms.ghost: a new resource on uplink — build it on the httpx2 core (/new-endpoint)"
    ]
    assert _uplink_drift({"forms.surveys"}, frozen) == [
        "wiki.pages: now on the core — remove it from UPLINK_RESOURCES"
    ]


def _uplink_tools() -> list:
    """MCP tools of resources still on uplink — the ones the verb maps must classify."""
    gen = _load_gen_coverage()
    uplink = tuple(
        f"{slug}_{attr.rstrip('_')}_"
        for slug, attr, _ in _resource_operations()
        if isinstance(getattr(_clients()[slug], attr), gen.BaseYandex)
    )
    return [tool for tool in _mcp_tools() if tool.name.startswith(uplink)]


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
    # status_get belongs to no resource; it is a read probe, so it is checked here too.
    tools = [*_uplink_tools(), *(tool for tool in _mcp_tools() if tool.name == "status_get")]
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
            assert ann.read_only_hint is True, f"{t.name!r} is a read but readOnlyHint is not True"
        else:
            assert ann.read_only_hint is False, (
                f"{t.name!r} is a write but readOnlyHint is not False"
            )
            assert ann.destructive_hint is (cls == "destructive"), (
                f"{t.name!r} verb class {cls!r} demands destructiveHint="
                f"{cls == 'destructive'}, got {ann.destructive_hint}"
            )
            assert ann.idempotent_hint is (cls == "write_idempotent"), (
                f"{t.name!r} verb class {cls!r} demands idempotentHint="
                f"{cls == 'write_idempotent'}, got {ann.idempotent_hint}"
            )


# An endpoint may state an effect other than its method implies only here, with the reason:
# a wrong label would also make the retry policy re-send a non-idempotent request.
ARCH3_EFFECT_OVERRIDES: dict[str, str] = {
    "tracker/issues/endpoints.py:search_issues": "POST _search only reads",
    "tracker/issues/endpoints.py:count_issues": "POST _count only reads",
    "tracker/issues/endpoints.py:clear_scroll": "releasing a scroll twice is harmless",
    "tracker/worklog/endpoints.py:search_worklog": "POST _search only reads",
    "forms/files/endpoints.py:verify_files": "POST verify only reads upload statuses",
    "tracker/entities/endpoints.py:search_entities": "POST _search only reads",
    "tracker/queues/endpoints.py:remove_tag": "POST _remove strips the tag from every issue",
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
        is_write = ann.read_only_hint is False
        assert (WRITE_TAG in tags) == is_write, (
            f"{t.name!r}: readOnlyHint={ann.read_only_hint} but write-tag "
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


def _annotated_read(function: ast.FunctionDef) -> bool:
    """Whether the tool's decorator spreads the ``RO`` hints (``annotations={**RO, …}``)."""
    return any(
        isinstance(keyword.value, ast.Dict)
        and any(
            key is None and isinstance(value, ast.Name) and value.id == "RO"
            for key, value in zip(keyword.value.keys, keyword.value.values, strict=True)
        )
        for decorator in function.decorator_list
        if isinstance(decorator, ast.Call)
        for keyword in decorator.keywords
        if keyword.arg == "annotations"
    )


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
        if tool_name is None or not (_classify(tool_name) == "read" or _annotated_read(node)):
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

    # A tool named like a write but annotated read-only is a read: its writes are caught too.
    mislabelled = (
        '@mcp.tool(name="issues_move", annotations={**RO, "title": "Move"})\n'
        "def move(client):\n"
        "    client.issues.get(key)\n"
        "    return client.issues.move(key, queue)\n"
    )
    assert _read_tool_write_offenders(mislabelled) == ["read tool 'issues_move' calls .move(…)"]


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


def _import_aliases(tree: ast.AST) -> dict[str, str]:
    """Each imported local name -> the dotted name it stands for.

    ``from rich import print as rprint`` gives ``{"rprint": "rich.print"}``; ``import pprint``
    gives ``{"pprint": "pprint"}``; ``import yaml as y`` gives ``{"y": "yaml"}``.
    """
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.partition(".")[0]
                aliases[alias.asname or top] = alias.name if alias.asname else top
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return aliases


def _dotted(expr: ast.expr, aliases: dict[str, str]) -> str:
    """The dotted name ``expr`` refers to, imports resolved; ``""`` if it is not a name chain.

    ``rprint`` -> ``rich.print``; ``sys.__stdout__.write`` -> ``sys.__stdout__.write``;
    ``Console().print`` -> ``""`` (the inner ``Console()`` call is judged on its own).
    """
    parts: list[str] = []
    while isinstance(expr, ast.Attribute):
        parts.append(expr.attr)
        expr = expr.value
    if not isinstance(expr, ast.Name):
        return ""
    parts.append(aliases.get(expr.id, expr.id))
    return ".".join(reversed(parts))


# Serializers that turn a result into text. Only output.render may call them (ARCH-4).
_SERIALIZERS = frozenset(
    {"json.dump", "json.dumps", "yaml.dump", "yaml.safe_dump", "yaml.dump_all",
     "yaml.safe_dump_all", "pydantic_core.to_json"}
)  # fmt: skip
_SERIALIZER_METHODS = frozenset({"model_dump_json", "dump_json"})  # BaseModel / TypeAdapter
# Where a result may be serialized, and why.
ARCH4_SERIALIZATION_HOMES = {
    Path("cli/output.py"): "output.render, the one output path",
    Path("log.py"): "the JSON log formatter writes diagnostic records to stderr, not results",
}


def _serializations(source: str) -> list[str]:
    """Calls in ``source`` that serialize a value: ``json.dumps``, ``yaml.safe_dump``,
    ``pydantic_core.to_json`` (import aliases resolved) or a ``.model_dump_json()``."""
    tree = ast.parse(source)
    aliases = _import_aliases(tree)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _dotted(node.func, aliases)
            method = node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if name in _SERIALIZERS or method in _SERIALIZER_METHODS:
                found.append(f"{name or method} (line {node.lineno})")
    return found


def test_arch4_serialization_confined_to_output():
    """Rendering lives in output.py; nothing else serializes a result."""
    offenders = {
        str(rel): found
        for p in SRC.rglob("*.py")
        if (rel := p.relative_to(SRC)) not in ARCH4_SERIALIZATION_HOMES
        if (found := _serializations(p.read_text(encoding="utf-8")))
    }
    assert not offenders, f"serialization must live only in output.py; found in {offenders}"


def test_arch4_serialization_guard_bites():
    for source in (
        "text = json.dumps(data)",
        "import json as j\ntext = j.dumps(data)",
        "from yaml import safe_dump\ntext = safe_dump(data)",
        "text = result.model_dump_json()",
        "from pydantic_core import to_json\ndata = to_json(result)",
        "import pydantic_core\ndata = pydantic_core.to_json(result)",
    ):
        assert _serializations(source), source
    assert _serializations("data = result.model_dump(mode='json')\nvalue = json.loads(text)") == []


def _to_stderr(call: ast.Call) -> bool:
    """``err=True`` (typer) or ``stderr=True`` (rich ``Console``) among the call's keywords."""
    return any(
        k.arg in {"err", "stderr"} and isinstance(k.value, ast.Constant) and k.value.value is True
        for k in call.keywords
    )


_PRINTERS = frozenset(
    {"print", "builtins.print", "rich.print", "rich.print_json", "pprint", "pprint.pprint",
     "pprint.pp"}
)  # fmt: skip
_STDOUT_NAMES = frozenset({"stdout", "__stdout__"})
# Where stdout may be written, and why: the renderer itself, and one eager option.
ARCH4_STDOUT_HOMES = {Path("cli/output.py"): "output.render, the one output path"}
ARCH4_STDOUT_FUNCTIONS = {
    # Eager: it runs before any command, so there is no result to return. Routing it through
    # output.render would import yaml/rich/pydantic first (measured 48 -> 110 ms for --version).
    "cli/app.py:_version_callback": "`ycli --version` prints the version and exits",
}


def _stdout_writes(source: str, exempt_functions: frozenset[str] = frozenset()) -> list[str]:
    """Places in ``source`` that write to stdout: ``print`` in any spelling (``builtins.print``,
    ``rich.print``, ``pprint``, an import alias), ``typer.echo`` / ``secho`` and ``Console(...)``
    without a stderr flag, ``os.write``, and any use of ``stdout`` / ``__stdout__``. Messages to
    stderr are UI, not output. Top-level functions named in ``exempt_functions`` are skipped."""
    tree = ast.parse(source)
    aliases = _import_aliases(tree)
    found = []
    for top in tree.body:
        if isinstance(top, ast.FunctionDef) and top.name in exempt_functions:
            continue
        for node in ast.walk(top):
            if isinstance(node, ast.Call):
                name = _dotted(node.func, aliases)
                last = name.rpartition(".")[2] or getattr(node.func, "attr", "")
                if name in _PRINTERS:
                    found.append(f"print (line {node.lineno})")
                elif last in {"echo", "secho", "Console"} and not _to_stderr(node):
                    found.append(f"{last} (line {node.lineno})")
                elif name == "os.write":
                    found.append(f"os.write (line {node.lineno})")
            elif (
                (isinstance(node, ast.Attribute) and node.attr in _STDOUT_NAMES)
                or (
                    isinstance(node, ast.Name)
                    and aliases.get(node.id, node.id).rpartition(".")[2] in _STDOUT_NAMES
                )
                or (
                    isinstance(node, ast.ImportFrom)
                    and any(a.name in _STDOUT_NAMES for a in node.names)
                )
            ):
                found.append(f"stdout (line {node.lineno})")
    return found


def test_arch4_commands_return_and_never_print():
    """A CLI command returns its result; only ``output.render`` writes to stdout.

    Every module is scanned, not only ``cli.py``: a print moved into a helper next to it is the
    same write.
    """
    offenders = {}
    for p in SRC.rglob("*.py"):
        rel = p.relative_to(SRC)
        if rel in ARCH4_STDOUT_HOMES:
            continue
        exempt = frozenset(
            key.partition(":")[2] for key in ARCH4_STDOUT_FUNCTIONS if key.startswith(f"{rel}:")
        )
        if writes := _stdout_writes(p.read_text(encoding="utf-8"), exempt):
            offenders[str(rel)] = writes
    assert not offenders, f"return the value instead of printing it: {offenders}"


def test_arch4_stdout_guard_bites():
    """Prove-it: the guard flags each way to reach stdout and lets stderr messages through."""
    flagged = {
        "print(model)": "print (line 1)",
        "rich.print(model)": "print (line 1)",
        "from rich import print as rprint\nrprint(model)": "print (line 2)",
        "import builtins\nbuiltins.print(model)": "print (line 2)",
        "pprint(model)": "print (line 1)",
        "from pprint import pprint\npprint(model)": "print (line 2)",
        "import pprint\npprint.pp(model)": "print (line 2)",
        "typer.echo(name)": "echo (line 1)",
        "from typer import echo as say\nsay(name)": "echo (line 2)",
        "Console().print(model)": "Console (line 1)",
        "sys.stdout.buffer.write(data)": "stdout (line 1)",
        "sys.__stdout__.write(text)": "stdout (line 1)",
        "from sys import stdout": "stdout (line 1)",
        "from sys import stdout as out\nout.write(text)": "stdout (line 2)",
        "os.write(1, data)": "os.write (line 1)",
    }
    for source, finding in flagged.items():
        assert finding in _stdout_writes(source), source
    assert _stdout_writes("typer.echo('note', err=True)") == []
    assert _stdout_writes("Console(stderr=True).print('Opening')") == []
    assert _stdout_writes("console.print('Opening')") == []  # a stderr console made elsewhere
    version = "def _version_callback(value):\n    typer.echo(value)\n"
    assert _stdout_writes(version, frozenset({"_version_callback"})) == []
    assert _stdout_writes(version) == ["echo (line 2)"]


# `timeout=30` as a keyword argument, or `timeout: float = 30.0` as an annotated default.
_LITERAL_DEFAULT_RE = re.compile(
    r"\b(timeout|timeout_seconds|retries|max_items)\s*(:[^=\n]+)?=\s*\d"
)
_CREDENTIAL_ENV_RE = re.compile(r"YANDEX_ID_(OAUTH_TOKEN|ORGANIZATION_ID)\b")
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
        if _CREDENTIAL_ENV_RE.search(text):
            offenders.append(f"{rel}: credential variable name spelled outside settings.py")
        if re.search(r"\bos\.(environ|getenv)\b|\bfrom os import (environ|getenv)\b", text):
            offenders.append(f"{rel}: environment access outside settings.py")
        if "from_env" in text:
            offenders.append(f"{rel}: from_env reads the environment outside settings.py")
        code = "\n".join(line for line in text.splitlines() if ">>>" not in line)  # not doctests
        if _LITERAL_DEFAULT_RE.search(code):
            offenders.append(f"{rel}: a literal default shadows the HTTP settings")
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
        "token = os.getenv('T')",
        "from os import environ",
        "client = TrackerClient.from_env()",
        "session.send(request, timeout=30)",
        "def session(*, timeout_seconds: float = 30.0) -> None: ...",
        "def __init__(self, retries: int = 3) -> None: ...",
        "def items(max_items: int | None = 500) -> None: ...",
        "class Local(BaseSettings): ...",
        "@uplink.timeout(30)",
        'hint = "check YANDEX_ID_OAUTH_TOKEN"',
        'missing = {"YANDEX_ID_ORGANIZATION_ID"}',
    ):
        assert _single_source_offenders(rel, source), source
    # A comparison or a value read from the settings is not a literal default.
    for source in ("if retries == 0: ...", "timeout_seconds: float = config.timeout_seconds"):
        assert not _single_source_offenders(rel, source), source


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
    """Lines that build or hand out a settings model outside an annotation.

    Catches ``AppConfig()``, ``settings.AppConfig()``, an alias (``from ycli.settings import
    AppConfig as C``; ``C()``) and a bare reference such as ``default_factory=AppConfig``.
    """
    tree = ast.parse(source)
    names = set(_SETTINGS_MODELS)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            names |= {a.asname for a in node.names if a.name in _SETTINGS_MODELS and a.asname}
    annotations: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):  # ``AppConfig.__name__`` reads the class, builds none
            annotations.add(id(node.value))
        hints = []
        if isinstance(node, ast.arg | ast.AnnAssign) and node.annotation is not None:
            hints.append(node.annotation)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.returns is not None:
            hints.append(node.returns)
        annotations |= {id(sub) for hint in hints for sub in ast.walk(hint)}
    return sorted(
        {
            node.lineno
            for node in ast.walk(tree)
            if id(node) not in annotations
            and (
                (isinstance(node, ast.Name) and node.id in names)
                or (isinstance(node, ast.Attribute) and node.attr in _SETTINGS_MODELS)
            )
            and isinstance(node.ctx, ast.Load)
        }
    )


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
    assert _settings_constructions("creds = settings.Credentials()") == [1]
    assert _settings_constructions("from ycli.settings import AppConfig as C\nC()") == [2]
    assert _settings_constructions("field(default_factory=AppConfig)") == [1]
    assert _settings_constructions("def f(config: AppConfig) -> AppConfig: return config") == []
    assert _settings_constructions("title = AppConfig.__name__") == []


# Who may turn a status into a typed error, and why. ``raise_for_status`` (httpx/requests)
# would bypass the mapping and raise a library error instead of a YandexError.
ARCH8_ERROR_MAPPERS = {
    Path("yandex/errors.py"): "defines error_for_status",
    Path("yandex/transport.py"): "the uplink response hook",
    Path("yandex/core/session.py"): "the httpx2 core sessions",
    Path("yandex/core/auth.py"): "the IAM token exchange outside the sessions",
    Path("yandex/status/client.py"): (
        "the OAuth login flow: a 400/401 with an OAuth error code is a device-flow polling "
        "state (RFC 6749 §5.2), so it cannot use the transport's raise-on-4xx hook"
    ),
}
# Functions that raise a status-carrying YandexError with no response to map, and why.
ARCH8_LOCAL_RAISES = {
    "yandex/core/endpoint.py:check_path": "refuses a path before any request is sent",
    # An empty 2xx body has no status to map; E2 moves this check into the clients.
    "yandex/models.py:require_found": "a 2xx whose body parsed into an empty model",
}
# YandexError subclasses that carry no HTTP status: raising one maps no status.
ARCH8_STATUSLESS_ERRORS = {
    "YandexTimeoutError": "a local polling deadline (polling.poll)",
    "YandexConnectionError": "no HTTP response at all",
}


@functools.cache
def _status_errors() -> frozenset[str]:
    """Every ``YandexError`` class in ``ycli.yandex.errors`` that stands for an HTTP status."""
    from ycli.yandex import errors

    defined = {
        name
        for name, value in vars(errors).items()
        if isinstance(value, type) and issubclass(value, errors.YandexError)
    }
    assert set(ARCH8_STATUSLESS_ERRORS) <= defined, "ARCH8_STATUSLESS_ERRORS names a gone class"
    return frozenset(defined - set(ARCH8_STATUSLESS_ERRORS))


def _error_mapping_offenders(rel: Path, source: str) -> list[str]:
    """Places in ``source`` that map an HTTP status by hand (import aliases resolved).

    Anywhere: ``raise_for_status``. Outside ``ARCH8_ERROR_MAPPERS``: any use of
    ``error_for_status``, building a status-carrying ``YandexError`` (``YandexNotFoundError(…)``)
    and reading a response's ``status_code``. A top-level function listed in
    ``ARCH8_LOCAL_RAISES`` may build such an error.
    """
    tree = ast.parse(source)
    aliases = _import_aliases(tree)
    mapper = rel in ARCH8_ERROR_MAPPERS
    offenders = []
    for top in tree.body:
        local_raise = f"{rel}:{getattr(top, 'name', '')}" in ARCH8_LOCAL_RAISES
        offenders += _mapping_offenders_in(
            top, rel, aliases, mapper=mapper, local_raise=local_raise
        )
    return offenders


def _mapping_offenders_in(
    top: ast.stmt, rel: Path, aliases: dict[str, str], *, mapper: bool, local_raise: bool
) -> list[str]:
    """The :func:`_error_mapping_offenders` findings inside one top-level statement."""
    offenders = []
    for node in ast.walk(top):
        where = f"{rel}:{getattr(node, 'lineno', 0)}"
        if isinstance(node, ast.Attribute) and node.attr == "raise_for_status":
            offenders.append(f"{where}: raise_for_status bypasses errors.error_for_status")
        if mapper:
            continue
        if isinstance(node, ast.ImportFrom) and any(
            alias.name == "error_for_status" for alias in node.names
        ):
            offenders.append(f"{where}: imports error_for_status outside ARCH8_ERROR_MAPPERS")
        elif isinstance(node, ast.Name | ast.Attribute) and (
            _dotted(node, aliases).rpartition(".")[2] == "error_for_status"
        ):
            offenders.append(f"{where}: calls error_for_status outside ARCH8_ERROR_MAPPERS")
        elif isinstance(node, ast.Attribute) and node.attr == "status_code":
            offenders.append(f"{where}: reads status_code outside ARCH8_ERROR_MAPPERS")
        elif (
            isinstance(node, ast.Call)
            and not local_raise
            and (name := _dotted(node.func, aliases).rpartition(".")[2]) in _status_errors()
        ):
            offenders.append(f"{where}: raises {name} by hand instead of error_for_status")
    return offenders


def test_arch8_errors_are_mapped_in_one_place():
    """Non-2xx answers become typed YandexErrors through ``errors.error_for_status`` only."""
    offenders = [
        finding
        for p in SRC.rglob("*.py")
        for finding in _error_mapping_offenders(p.relative_to(SRC), p.read_text(encoding="utf-8"))
    ]
    assert not offenders, offenders


def test_arch8_error_mapping_guard_bites():
    session = Path("yandex/core/session.py")
    resource = Path("yandex/wiki/pages/client.py")
    assert _error_mapping_offenders(session, "response.raise_for_status()")
    for source in (
        "error_for_status(404, 'gone', url=u)",
        "from ycli.yandex.errors import error_for_status as efs\nraise efs(404, 'gone', url=u)",
        "from ycli.yandex import errors\nraise errors.error_for_status(404, 'gone', url=u)",
        "if response.status_code == 404:\n    raise LookupError(key)",
        "raise YandexNotFoundError('gone', status=404, url=u)",
        "from ycli.yandex.errors import YandexNotFoundError as Missing\nraise Missing('gone')",
        "raise errors.YandexError('failed', status=500)",
    ):
        assert _error_mapping_offenders(resource, source), source
    clean = (
        "raise YandexTimeoutError('late')\n"
        "try:\n    page = get(key)\nexcept YandexNotFoundError:\n    page = None\n"
        "hint = isinstance(error, YandexAuthError)\n"
    )
    assert _error_mapping_offenders(resource, clean) == []
    mapped = "raise error_for_status(response.status_code, message, url=u)"
    assert _error_mapping_offenders(session, mapped) == []
    # A listed local refusal may raise; the same raise in another function may not.
    refusal = "def {}(path):\n    raise YandexClientError(path)\n"
    endpoint = Path("yandex/core/endpoint.py")
    assert _error_mapping_offenders(endpoint, refusal.format("check_path")) == []
    assert _error_mapping_offenders(endpoint, refusal.format("build_url")) == [
        "yandex/core/endpoint.py:2: raises YandexClientError by hand instead of error_for_status"
    ]


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
        assert tool.output_schema is not None, (
            f"{tool.name!r} is missing a return type annotation (→ outputSchema)"
        )
