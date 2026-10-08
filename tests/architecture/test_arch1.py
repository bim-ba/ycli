"""ARCH-1 — Surface parity (see ARCHITECTURE.md)."""

import ast
import asyncio
import builtins
import functools
import importlib
import inspect
import keyword
import textwrap
from pathlib import Path

from tests.architecture.scanners import DOMAINS, SRC, YANDEX, _mcp_tools, violation_markers
from tests.snapshots._surface import cli_leaves
from ycli.mcp.profiles import ALWAYS_SERVED
from ycli.yandex.registry import SERVICES

# `models.py` is not among them: a resource whose replies are shared models has none.
CANONICAL = {"__init__.py", "endpoints.py", "client.py", "cli.py", "mcp.py"}
# Directories of a service that are not resources, and why (scripts/new_endpoint.py refuses
# them as a resource name).
RESERVED_NAMES = {
    "mcp": "<domain>/mcp/ is the service's MCP server",
    "schemas": "<domain>/schemas/ holds models generated from the service's specification",
}


def _is_resource_dir(path: Path) -> bool:
    """Whether a directory of a service holds a resource: all but the reserved names."""
    return path.is_dir() and not path.name.startswith("_") and path.name not in RESERVED_NAMES


def _resource_dirs():
    for domain in DOMAINS:
        for child in sorted((YANDEX / domain).iterdir()):
            if _is_resource_dir(child):
                yield child


def _missing_canonical(directory: Path) -> list[str]:
    return sorted(CANONICAL - {p.name for p in directory.iterdir() if p.is_file()})


def test_arch1_a_reserved_directory_is_not_a_resource(tmp_path):
    """``<domain>/mcp/`` is the service's MCP server; every other directory is a resource."""
    for name in ("mcp", "boards", "__pycache__"):
        (tmp_path / name).mkdir()
    (tmp_path / "client.py").touch()
    assert [p.name for p in sorted(tmp_path.iterdir()) if _is_resource_dir(p)] == ["boards"]
    assert "mcp" not in {directory.name for directory in _resource_dirs()}
    for domain in DOMAINS:  # the reserved name is taken by the server it is reserved for
        assert (YANDEX / domain / "mcp" / "server.py").is_file()


def test_arch1_four_surface_symmetry():
    directories = list(_resource_dirs())
    assert directories, "no resource directory found"  # the served check counts them
    for directory in directories:
        missing = _missing_canonical(directory)
        assert not missing, f"{directory.relative_to(SRC)} missing canonical files: {missing}"


def test_arch1_symmetry_check_bites(tmp_path):
    for name in CANONICAL - {"endpoints.py", "mcp.py"}:
        (tmp_path / name).touch()
    assert _missing_canonical(tmp_path) == ["endpoints.py", "mcp.py"]


def _defines_nothing(source: str) -> bool:
    """Whether a module holds only a docstring and imports: no class, function or assignment."""
    return all(
        isinstance(node, ast.Import | ast.ImportFrom)
        or (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant))
        for node in ast.parse(source).body
    )


def test_arch1_a_models_file_defines_a_model():
    """A resource with no model of its own has no ``models.py``, rather than an empty one."""
    empty = [
        str(path.relative_to(SRC))
        for directory in _resource_dirs()
        if (path := directory / "models.py").is_file()
        and _defines_nothing(path.read_text(encoding="utf-8"))
    ]
    assert empty == []


def test_arch1_empty_models_check_bites():
    assert _defines_nothing('"""No model of its own."""\n\nfrom __future__ import annotations\n')
    assert not _defines_nothing('"""Models."""\n\nclass Board(APIModel): ...\n')
    assert not _defines_nothing('"""Models."""\n\nBoardID = Annotated[int, Field()]\n')


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
        service.name: service.client_class()(
            oauth_token="x", organization_id="x", cloud_organization_id="x"
        )
        for service in SERVICES
    }


def _resource_operations():
    """Yield ``(domain_slug, resource_attr, sdk_ops)`` for every domain resource client."""
    gen = _load_gen_coverage()
    for slug, client in _clients().items():
        for attr, resource in sorted(vars(client).items()):
            if isinstance(resource, gen.Resource):
                yield slug, attr, set(gen._sdk_operations(resource))


def _wrapped_ops_in_source(source: str, resource_attr: str) -> set[str]:
    """Op names invoked as ``….<resource_attr>.<op>(…)`` anywhere in ``source`` (AST).

    Structural, not name-based: the CLI and MCP wrappers reference the client operation
    directly (``app_ctx.tracker.issues.get(…)`` / ``client.issues.get(…)``), so this sees the
    real coverage even where the surface command/tool is *named* differently from the op
    (``issues.search`` → CLI ``issues list``; ``pages.get`` → MCP ``pages_get_meta``). A same-named
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


def _first_line(function: object) -> tuple[Path, int]:
    """The file and the first line of a function's definition (its first decorator, if any)."""
    function = inspect.unwrap(function)  # ty: ignore[invalid-argument-type]
    return Path(inspect.getsourcefile(function)), function.__code__.co_firstlineno  # ty: ignore


@functools.cache
def _markers() -> dict[tuple[Path, int], int]:
    """Every ``# violation(arch-1)`` of the services: (file, the line it explains) -> its line."""
    return {
        (path, line): marker
        for path in sorted(YANDEX.rglob("*.py"))
        for line, marker in violation_markers(path.read_text(encoding="utf-8"), "arch-1").items()
    }


def _is_marked(function: object) -> bool:
    return _first_line(function) in _markers()


def _operation_methods():
    """Yield ``(domain.resource.op, the client method)`` for every client operation."""
    for slug, attr, sdk_ops in _resource_operations():
        resource = type(getattr(_clients()[slug], attr))
        for op in sorted(sdk_ops):
            yield f"{slug}.{attr}.{op}", getattr(resource, op)


def _moves_a_file(method: object) -> bool:
    """Whether a client method gives the caller the bytes of a file, or takes them.

    What works with a file on the caller's disk is not served over MCP: a server has no disk of
    the caller, and bytes do not round-trip a tool result. The signature says it, so no marker
    does: ``-> bytes`` or a ``bytes`` argument.
    """
    signature = inspect.signature(inspect.unwrap(method))  # ty: ignore[invalid-argument-type]
    held = [signature.return_annotation, *(one.annotation for one in signature.parameters.values())]
    return any(annotation in (bytes, "bytes") for annotation in held)


def _marked_asymmetries() -> set[str]:
    return {operation for operation, method in _operation_methods() if _is_marked(method)}


def _file_operations() -> set[str]:
    return {operation for operation, method in _operation_methods() if _moves_a_file(method)}


def surface_asymmetries() -> set[str]:
    """The client operations served by one surface only, ``domain.resource.op``.

    ARCH-1 operation-level parity (D2): every public client operation is wrapped on BOTH the CLI
    and the MCP surface, except a method that moves a file (the rule, read off its signature)
    and the methods with ``# violation(arch-1): <reason>`` above them.
    """
    return _marked_asymmetries() | _file_operations()


def test_arch1_operation_level_parity():
    """Every client operation is wrapped on both the CLI and MCP surfaces (ARCH-1).

    Strengthens the four-file existence check: a client method with no CLI command *and* no MCP
    tool — or one wrapped on only one surface — is caught. Coverage is read structurally from
    each surface's calls into the client, so a command/tool named differently from the op still
    counts. An intentional asymmetry is marked above the client method (``surface_asymmetries``).
    """
    gaps: dict[str, tuple[bool, bool]] = {}
    for slug, attr, sdk_ops in _resource_operations():
        rdir = YANDEX / slug / attr
        cli_ops = _wrapped_ops(rdir / "cli.py", attr)
        mcp_ops = _wrapped_ops(rdir / "mcp.py", attr)
        for op in _surface_gaps(sdk_ops, cli_ops, mcp_ops):
            gaps[f"{slug}.{attr}.{op}"] = (op in cli_ops, op in mcp_ops)
    marked = _marked_asymmetries()
    # A file is the CLI's to move: such an operation may lack a tool, never a command.
    files = {op for op in _file_operations() if op in gaps and gaps[op][0]}
    unexpected = sorted(set(gaps) - marked - files)
    resolved = sorted(marked - set(gaps))
    needless = sorted(marked & _file_operations())
    assert not unexpected and not resolved and not needless, (
        "operation-level surface parity drifted. Every client op must be wrapped on BOTH the "
        "CLI and MCP surfaces, or have `# violation(arch-1): <reason>` above the client method.\n"
        f"  newly unwrapped (wrap on both surfaces, or mark with a reason): {unexpected}\n"
        f"  now wrapped (remove the marker): {resolved}\n"
        f"  moves a file, which says it already (remove the marker): {needless}"
    )


def test_arch1_a_file_operation_is_known_by_its_signature():
    """Prove-it: bytes given or taken say a method moves a file; anything else does not."""

    def download(self, file_id: str) -> bytes:
        return b""

    def upload(self, *, filename: str, data: bytes) -> dict:
        return {}

    def get(self, file_id: str) -> dict:
        return {}

    def deferred(self, file_id: str) -> "bytes":
        return b""

    assert [_moves_a_file(one) for one in (download, upload, get, deferred)] == [
        True,
        True,
        False,
        True,
    ]
    # The real ones are found, and each has a command: a file is the CLI's to move.
    assert "tracker.attachments.download" in _file_operations()
    assert "tracker.attachments.list" not in _file_operations()


def test_arch1_parity_check_bites():
    """Prove-it: the gap detector flags an op missing from a surface; the reader counts real calls.

    The structural reader counts a real client call but not a same-named call on another object.
    """
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


def _served_cli_groups() -> set[str]:
    """``domain.group`` for every resource group the ``ycli`` CLI dispatches to.

    Read from the built Click tree, each lazy service group loaded (``ycli.cli.lazy``), so a
    sub-app that is never ``add_typer``-ed into its domain is absent.
    """
    import typer.main
    from typer.core import TyperGroup

    from ycli.cli.app import app
    from ycli.cli.lazy import LazyGroup, RootGroup

    root = typer.main.get_command(app)
    assert isinstance(root, RootGroup)
    groups = set()
    for domain in DOMAINS:
        service = root.commands[domain]
        assert isinstance(service, LazyGroup)
        loaded = service.load()
        assert isinstance(loaded, TyperGroup)
        groups |= {f"{domain}.{group}" for group in loaded.commands}
    return groups


def _surface_names(resource: str) -> tuple[str, str]:
    """A resource directory's CLI group and MCP tool prefix.

    ``tracker.import_`` -> ``("tracker.import", "tracker_import_")``.
    """
    domain, _, name = resource.partition(".")
    name = name.rstrip("_")
    return f"{domain}.{name}", f"{domain}_{name}_"


# CLI groups every service mounts that are not a resource, and why. A group listed here needs no
# resource directory; one that is not listed and has none is reported.
ARCH1_NON_RESOURCE_CLI_GROUPS = {
    "auth": "`ycli <service> auth status`: one generic probe built from the registry's Service",
}


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
            gaps.append(f"{resource}: serves no MCP tool — not mounted in {domain}/mcp/server.py")
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
    """Each resource directory is wired and served by the CLI and MCP server, and nothing else is.

    A directory is wired into its domain client, and nothing is served without one (ARCH-1).

    The file and operation checks above read source files, so a resource never wired into
    ``client.py`` or never mounted (``app.add_typer`` / ``mcp.mount``) passes them; this reads
    what the surfaces actually serve.
    """
    on_disk = {f"{d.parent.name}.{d.name}" for d in _resource_dirs()}
    operations = {f"{slug}.{attr}": ops for slug, attr, ops in _resource_operations()}
    asymmetries = surface_asymmetries()
    cli_only = {
        resource
        for resource, ops in operations.items()
        if ops and all(f"{resource}.{op}" in asymmetries for op in ops)
    }
    # status_* and schema_* belong to no resource: cross-cutting surfaces (see ARCHITECTURE.md).
    tools = {tool.name for tool in _mcp_tools() if not tool.name.startswith(("status_", "schema_"))}
    cli_groups = _served_cli_groups() - {
        f"{domain}.{group}" for domain in DOMAINS for group in ARCH1_NON_RESOURCE_CLI_GROUPS
    }
    gaps = _served_gaps(on_disk, set(operations), cli_groups, tools, cli_only)
    assert not gaps, gaps


def test_arch1_served_check_bites():
    """Prove-it: a ghost directory, an unmounted group or server and orphan names are reported.

    A served name with no directory is reported too; a CLI-only resource needs no MCP tool.
    """
    disk = {"forms.keysets", "tracker.import_"}
    groups = {"forms.keysets", "tracker.import"}
    tools = {"forms_keysets_get", "tracker_import_task"}
    assert _served_gaps(disk, disk, groups, tools, set()) == []
    assert _served_gaps(disk | {"forms.ghost"}, disk, groups, tools, set()) == [
        "forms.ghost: not wired into forms/client.py",
        "forms.ghost: no CLI group — not add_typer-ed in forms/cli.py",
        "forms.ghost: serves no MCP tool — not mounted in forms/mcp/server.py",
    ]
    assert _served_gaps(disk, disk | {"forms.ghost"}, groups, tools, set()) == [
        "forms.ghost: wired into forms/client.py but has no directory"
    ]
    assert _served_gaps(disk, disk, groups, {"tracker_import_task"}, set()) == [
        "forms.keysets: serves no MCP tool — not mounted in forms/mcp/server.py"
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


# ARCH-1 name parity (#104). An operation served on both surfaces has one name: the CLI path
# (service, groups, leaf; spaces and hyphens as `_`) is the MCP tool name. An MCP tool may differ
# from the CLI command that reaches the same operation only with `# violation(arch-1): <reason>`
# above its definition.


# One verb per action (#104, #268): the synonym on the left is never a word of a name.
ARCH1_SYNONYM_VERBS: dict[str, str] = {
    "add": "create",
    "remove": "delete",
    "edit": "update",
    "modify": "update",
    "patch": "update",
    "query": "search",
}


def _synonym_verbs(names: set[str]) -> list[str]:
    """Names (``tracker_boards_edit``) with a word that has a preferred verb."""
    return [
        f"{name}: say {ARCH1_SYNONYM_VERBS[word]!r}, not {word!r}"
        for name in sorted(names)
        for word in name.split("_")
        if word in ARCH1_SYNONYM_VERBS
    ]


def _gets_returning_a_list(methods: dict[str, str]) -> list[str]:
    """Operations named exactly ``get`` (name -> return annotation) that return a list of items."""
    return [
        f"{operation}: returns a list of items, name it 'list'"
        for operation, returns in sorted(methods.items())
        if operation.rsplit(".", 1)[-1] == "get" and returns.startswith("ItemList[")
    ]


def _return_annotations() -> dict[str, str]:
    """``domain.resource.op`` -> the return annotation its client method states, as written."""
    found = {}
    for slug, client in _clients().items():
        for attr, resource in sorted(vars(client).items()):
            for name in sorted(n for n in vars(type(resource)) if not n.startswith("_")):
                annotation = inspect.get_annotations(getattr(type(resource), name)).get("return")
                if isinstance(annotation, str):
                    found[f"{slug}.{attr}.{name}"] = annotation
    return found


def test_arch1_a_get_returns_one_object():
    """A method named ``get`` returns one object; a list of items is ``list`` (ARCH-1, #268).

    The other naming rules are a convention a reviewer holds (docs/conventions/resources.md,
    "Naming an operation"); this one a machine reads off the signature.
    """
    methods = _return_annotations()
    assert "tracker.queues.get" in methods and methods["tracker.queues.list"].startswith(
        "ItemList["
    )
    problems = _gets_returning_a_list(methods)
    assert not problems, "\n  ".join(["rename these operations:", *problems])


def test_arch1_get_check_bites():
    """Prove-it: a ``get`` that returns a list is reported; a part before the verb is not."""
    assert _gets_returning_a_list(
        {
            "forms.access.get": "ItemList[Permission]",
            "tracker.autoactions.logs_get": "ItemList[AutoactionRunEntry]",
            "tracker.queues.list": "ItemList[Queue]",
            "tracker.queues.get": "Queue",
        }
    ) == ["forms.access.get: returns a list of items, name it 'list'"]


def _function_operations(function: object) -> frozenset[str]:
    """``domain.resource.op`` for every client operation ``function``'s body calls (AST)."""
    source = textwrap.dedent(inspect.getsource(inspect.unwrap(function)))  # ty: ignore[invalid-argument-type]
    return frozenset(
        f"{slug}.{attr}.{op}"
        for slug, attr, sdk_ops in _resource_operations()
        for op in _wrapped_ops_in_source(source, attr) & sdk_ops
    )


def _cli_commands_by_name() -> dict[str, frozenset[str]]:
    """Visible CLI leaf commands as ``tracker_issues_get``-style names, with their operations.

    The operations are named under their service (``tracker.issues.get``).
    """
    out: dict[str, frozenset[str]] = {}
    for path, command in cli_leaves().items():
        service = path.split()[0]
        out[path.replace(" ", "_").replace("-", "_")] = frozenset(
            op for op in _function_operations(command.callback) if op.startswith(f"{service}.")
        )
    return out


def _mcp_tool_functions():
    """Yield ``(tool name, its function)`` for every served MCP resource tool.

    Read from each resource's own server (the root server holds proxies, with no function to
    read).
    """
    for directory in _resource_dirs():
        domain = directory.parent.name
        server = importlib.import_module(f"ycli.yandex.{domain}.{directory.name}.mcp").mcp
        for tool in asyncio.run(server.list_tools()):
            yield f"{domain}_{tool.name}", asyncio.run(server.get_tool(tool.name)).fn


def _mcp_tools_by_name() -> dict[str, frozenset[str]]:
    """Served MCP resource tools by name, with the operations they call."""
    return {
        name: frozenset(
            op for op in _function_operations(function) if op.startswith(name.split("_")[0] + ".")
        )
        for name, function in _mcp_tool_functions()
    }


def _name_exceptions() -> set[str]:
    """The tools marked as named apart from their CLI command."""
    return {name for name, function in _mcp_tool_functions() if _is_marked(function)}


def _stray_markers(
    markers: dict[tuple[Path, int], int], definitions: set[tuple[Path, int]]
) -> list[str]:
    """Markers that stand above neither a client operation nor a tool."""
    return [
        f"{path.relative_to(SRC)}:{marker}: violation(arch-1) is above no operation or tool"
        for (path, line), marker in sorted(markers.items())
        if (path, line) not in definitions
    ]


def test_arch1_a_marker_stands_above_an_operation_or_a_tool():
    """A ``# violation(arch-1)`` stands above a client method or a tool, nowhere else.

    Whether a marked method or tool still needs its marker is held by
    ``test_arch1_operation_level_parity`` and ``test_arch1_cli_path_equals_mcp_name``.
    """
    definitions = {_first_line(method) for _, method in _operation_methods()}
    definitions |= {_first_line(function) for _, function in _mcp_tool_functions()}
    assert _stray_markers(_markers(), definitions) == []
    assert surface_asymmetries() and _name_exceptions()  # the markers are found where they stand


def test_arch1_stray_marker_check_bites():
    """Prove-it: a marker above something else is reported; one above a definition is not."""
    client = SRC / "yandex/tracker/boards/client.py"
    markers = {(client, 10): 9, (client, 40): 39}
    assert _stray_markers(markers, {(client, 10)}) == [
        "yandex/tracker/boards/client.py:39: violation(arch-1) is above no operation or tool"
    ]


def _counterparts(cli: dict[str, frozenset[str]], operations: frozenset[str]) -> set[str]:
    """CLI commands serving a tool's ``operations``.

    Those calling exactly them, else those calling at least them (a command that polls an async
    operation also reads its status).
    """
    exact = {name for name, ops in cli.items() if ops == operations}
    return exact or {name for name, ops in cli.items() if operations <= ops}


def _name_mismatches(
    cli: dict[str, frozenset[str]], tools: dict[str, frozenset[str]], exceptions: set[str]
) -> list[str]:
    """MCP tools named differently from the CLI command that serves the same operations.

    No counterpart is not a name problem (``test_arch1_operation_level_parity`` owns that); a
    tool calling no operation is reported, so a helper cannot hide a wrapper from this check;
    an exception that no longer applies is reported too.
    """
    problems = []
    for tool, operations in sorted(tools.items()):
        if not operations:
            problems.append(f"{tool}: calls no client operation, so its CLI name cannot be checked")
            continue
        counterparts = _counterparts(cli, operations)
        if counterparts and tool not in counterparts and tool not in exceptions:
            problems.append(f"{tool}: the CLI serves it as {sorted(counterparts)}")
    problems += [
        f"{tool}: marked `# violation(arch-1)` but no longer needs it"
        for tool in sorted(exceptions)
        if tool not in tools or tool in _counterparts(cli, tools[tool])
    ]
    return problems


def test_arch1_cli_path_equals_mcp_name():
    """An operation served on both surfaces has the same name on both (ARCH-1, #104).

    The CLI path with spaces and hyphens as ``_`` is the MCP tool name, verb last (``update``,
    never ``edit`` or ``modify``). The tools read are those of the resource servers; the root
    server must serve exactly them (plus the always-served two), so a tool cannot hide from
    this check.
    """
    tools = _mcp_tools_by_name()
    served = {tool.name for tool in _mcp_tools()} - {*ALWAYS_SERVED}
    assert set(tools) == served, sorted(set(tools) ^ served)
    cli = _cli_commands_by_name()
    problems = _name_mismatches(cli, tools, _name_exceptions())
    problems += _synonym_verbs(set(cli) | set(tools))
    assert not problems, (
        "a CLI command and an MCP tool serve the same operation under different names; rename "
        "the CLI command or the tool, or put `# violation(arch-1): <reason>` above the "
        "tool:\n  " + "\n  ".join(problems)
    )


def _sdk_name_mismatches(
    operations: set[str], cli: dict[str, frozenset[str]], tools: dict[str, frozenset[str]]
) -> list[str]:
    """SDK operations (``tracker.boards.edit``) named differently from what serves them.

    An operation answers to the name of an MCP tool that calls it, without the service and
    resource prefix; the CLI command's name stands in when no tool does. One operation may
    serve several tools (``issues.search`` behind ``issues_list`` and ``issues_search``): any
    of their names fits. An operation neither surface reaches under its own resource is a
    step of another one and has no name to match.
    """
    problems = []
    for operation in sorted(operations):
        service, resource, method = operation.split(".")
        prefix = f"{service}_{resource.rstrip('_')}_"
        served = [
            {name.removeprefix(prefix) for name in _counterparts(surface, frozenset({operation}))}
            for surface in (
                {name: ops for name, ops in tools.items() if name.startswith(prefix)},
                {name: ops for name, ops in cli.items() if name.startswith(prefix)},
            )
        ]
        # A keyword or a builtin cannot name a function: `import` is `import_`, as `list_` is.
        bare = method.removesuffix("_")
        reserved = keyword.iskeyword(bare) or hasattr(builtins, bare)
        names = served[0] or served[1]
        if names and (bare if reserved else method) not in names:
            problems.append(f"{operation}: the surfaces call it {sorted(names)}")
    return problems


def _named_functions() -> set[str]:
    """Every endpoint builder and MCP tool function, as ``tracker_boards_endpoints_update``."""
    return {
        f"{directory.parent.name}_{directory.name}_{module}_{node.name}"
        for directory in _resource_dirs()
        for module in ("endpoints", "mcp")
        for node in ast.parse((directory / f"{module}.py").read_text(encoding="utf-8")).body
        if isinstance(node, ast.FunctionDef)
    }


def _python_name(name: str) -> str:
    """``name`` as a module-level function: ``list`` is ``list_``, as in ``cli.py``."""
    return f"{name}_" if hasattr(builtins, name) or keyword.iskeyword(name) else name


def _misnamed_tool_functions(functions: dict[str, str], resource: str) -> list[str]:
    """Tool functions (tool name -> Python name) not named after their tool."""
    return [
        f"{resource}.mcp.{function}: name it {wanted!r}, after its tool {tool!r}"
        for tool, function in sorted(functions.items())
        if function != (wanted := _python_name(tool.removeprefix(f"{resource}_")))
    ]


def test_arch1_tool_function_is_named_like_its_tool():
    """The function behind a tool has the tool's name, without the resource (ARCH-1).

    ``grids_rows_create`` is ``def rows_create`` in ``wiki/grids/mcp.py``, so the SDK method, the
    tool and its function are found under one word.
    """
    problems = []
    for directory in _resource_dirs():
        domain, resource = directory.parent.name, directory.name
        server = importlib.import_module(f"ycli.yandex.{domain}.{resource}.mcp").mcp
        functions = {
            tool.name: asyncio.run(server.get_tool(tool.name)).fn.__name__
            for tool in asyncio.run(server.list_tools())
        }
        problems += _misnamed_tool_functions(functions, resource.rstrip("_"))
    assert not problems, "\n  ".join(["a tool function is not named after its tool:", *problems])


def test_arch1_tool_function_check_bites():
    """Prove-it: another word order is reported; a builtin's name takes an underscore."""
    assert _misnamed_tool_functions({"grids_rows_add": "add_rows"}, "grids") == [
        "grids.mcp.add_rows: name it 'rows_add', after its tool 'grids_rows_add'"
    ]
    assert _misnamed_tool_functions({"queues_list": "list_", "queues_get": "get"}, "queues") == []
    assert _misnamed_tool_functions({"import_task": "task"}, "import") == []


def _misnamed_endpoint_functions(endpoints: str, client: str, resource: str) -> list[str]:
    """Functions of an ``endpoints.py`` not named after the one client method that sends them.

    ``endpoints`` and ``client`` are the two modules' source. A method that sends several
    functions names each after itself: ``search`` and ``search_scroll``.
    """
    functions = [
        node.name
        for node in ast.parse(endpoints).body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    sends: dict[str, list[str]] = {}
    for method in ast.walk(ast.parse(client)):
        if isinstance(method, ast.FunctionDef):
            for node in ast.walk(method):
                if (
                    isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "endpoints"
                    and node.attr in functions
                    and node.attr not in sends.setdefault(method.name, [])
                ):
                    sends[method.name].append(node.attr)
    problems = []
    for function in functions:
        methods = [method for method, sent in sends.items() if function in sent]
        where = f"{resource}.endpoints.{function}"
        if len(methods) != 1:
            callers = ", ".join(methods) or "no method"
            problems.append(f"{where}: sent by {callers}; one function per operation, one method")
            continue
        wanted = _python_name(methods[0])
        alone = len(sends[methods[0]]) == 1
        if function != wanted and (alone or not function.startswith(f"{methods[0]}_")):
            problems.append(f"{where}: name it {wanted!r}, after the method that sends it")
    return problems


def test_arch1_endpoint_function_is_named_like_its_method():
    """A function of ``endpoints.py`` has the name of the client method that sends it (ARCH-1).

    ``boards.update`` sends ``endpoints.update``, so the request, the SDK method, the CLI
    command and the tool are found under one word, and no function serves two operations.
    """
    problems = []
    for directory in _resource_dirs():
        problems += _misnamed_endpoint_functions(
            (directory / "endpoints.py").read_text(encoding="utf-8"),
            (directory / "client.py").read_text(encoding="utf-8"),
            f"{directory.parent.name}.{directory.name}",
        )
    assert not problems, "\n  ".join(["an endpoint function is misnamed:", *problems])


def test_arch1_endpoint_function_check_bites():
    """Prove-it: the API's noun in a name, a shared function and an unsent one are reported."""
    client = (
        "class C:\n"
        "    def list(self): return self.s.send(endpoints.list_boards())\n"
        "    def get(self): return self.s.send(endpoints.get())\n"
        "    def search(self): return self.s.send(endpoints.search() or endpoints.scroll())\n"
        "    def a(self): return self.s.send(endpoints.shared())\n"
        "    def b(self): return self.s.send(endpoints.shared())\n"
    )
    names = ("list_boards", "get", "search", "scroll", "shared", "unsent", "_private")
    endpoints = "".join(f"def {name}(): ...\n" for name in names)
    assert _misnamed_endpoint_functions(endpoints, client, "tracker.boards") == [
        "tracker.boards.endpoints.list_boards: name it 'list_', after the method that sends it",
        "tracker.boards.endpoints.scroll: name it 'search', after the method that sends it",
        "tracker.boards.endpoints.shared: sent by a, b; one function per operation, one method",
        "tracker.boards.endpoints.unsent: sent by no method; one function per operation, "
        "one method",
    ]
    fixed = client.replace("list_boards", "list_").replace(
        "endpoints.scroll", "endpoints.search_scroll"
    )
    renamed = endpoints.replace("list_boards", "list_").replace("def scroll", "def search_scroll")
    assert _misnamed_endpoint_functions(renamed, fixed, "tracker.boards")[:-2] == []


def test_arch1_sdk_method_equals_tool_name():
    """An SDK method is named like the MCP tool that serves it, verb included (ARCH-1, #229).

    ``tracker_boards_update`` is ``tracker.boards.update``; the endpoint builders and the tool
    functions use the same verbs.
    """
    operations = {
        f"{slug}.{attr}.{op}" for slug, attr, sdk_ops in _resource_operations() for op in sdk_ops
    }
    problems = _sdk_name_mismatches(operations, _cli_commands_by_name(), _mcp_tools_by_name())
    problems += _synonym_verbs({operation.replace(".", "_") for operation in operations})
    problems += _synonym_verbs(_named_functions())
    assert not problems, (
        "an SDK method is named differently from the MCP tool or the CLI command that serves "
        "it; rename the method:\n  " + "\n  ".join(problems)
    )


def test_arch1_sdk_name_check_bites():
    """Prove-it: a synonym verb, a bare-noun read and a CLI-only name are reported.

    A second tool on the same operation and an operation no surface reaches are not.
    """
    edit = frozenset({"tracker.boards.edit"})
    assert _sdk_name_mismatches(set(edit), {}, {"tracker_boards_update": edit}) == [
        "tracker.boards.edit: the surfaces call it ['update']"
    ]
    assert _sdk_name_mismatches(
        {"tracker.queues.tags"},
        {},
        {"tracker_queues_tags_list": frozenset({"tracker.queues.tags"})},
    ) == ["tracker.queues.tags: the surfaces call it ['tags_list']"]
    download = frozenset({"wiki.pages.fetch"})
    assert _sdk_name_mismatches(set(download), {"wiki_pages_download": download}, {}) == [
        "wiki.pages.fetch: the surfaces call it ['download']"
    ]
    search = frozenset({"tracker.issues.search"})
    two = {"tracker_issues_list": search, "tracker_issues_search": search}
    assert _sdk_name_mismatches(set(search), {}, two) == []
    assert _sdk_name_mismatches({"forms.answers.export_results_get"}, {}, {}) == []
    # A keyword takes an underscore in the method and none in the tool; no other word may.
    imported = frozenset({"tracker.issues.import_"})
    assert _sdk_name_mismatches(set(imported), {}, {"tracker_issues_import": imported}) == []
    padded = frozenset({"tracker.boards.update_"})
    assert _sdk_name_mismatches(set(padded), {}, {"tracker_boards_update": padded}) == [
        "tracker.boards.update_: the surfaces call it ['update']"
    ]


def test_arch1_name_parity_check_bites():
    """Prove-it: a renamed command, an operation-less tool, a stale exception and a synonym verb.

    Each is reported; matching names, a polling superset and a listed exception are not.
    """
    op = frozenset({"tracker.boards.update"})
    assert (
        _name_mismatches({"tracker_boards_update": op}, {"tracker_boards_update": op}, set()) == []
    )
    assert _name_mismatches({"tracker_boards_edit": op}, {"tracker_boards_update": op}, set()) == [
        "tracker_boards_update: the CLI serves it as ['tracker_boards_edit']"
    ]
    # One command that also reads a status the tool does not: a superset counterpart still pairs.
    polling = frozenset({"wiki.pages.clone", "wiki.operations.clone_get"})
    cli = {
        "wiki_pages_clone": polling,
        "wiki_operations_clone_get": frozenset({"wiki.operations.clone_get"}),
    }
    tools = {"wiki_operations_clone_get": frozenset({"wiki.operations.clone_get"})}
    assert _name_mismatches(cli, tools, set()) == []
    assert _name_mismatches({}, {"tracker_boards_ghost": frozenset()}, set()) == [
        "tracker_boards_ghost: calls no client operation, so its CLI name cannot be checked"
    ]
    assert _synonym_verbs({"tracker_boards_update", "forms_surveys_modify"}) == [
        "forms_surveys_modify: say 'update', not 'modify'"
    ]
    renamed = {"tracker_boards_edit": op}
    assert _name_mismatches(renamed, {"tracker_boards_update": op}, {"tracker_boards_update"}) == []
    assert _name_mismatches(
        {"tracker_boards_update": op}, {"tracker_boards_update": op}, {"tracker_boards_update"}
    ) == ["tracker_boards_update: marked `# violation(arch-1)` but no longer needs it"]


def _passed(source: str, resource_attr: str, op: str) -> tuple[int, set[str], bool] | None:
    """What the calls ``….<resource_attr>.<op>(…)`` of ``source`` pass; ``None`` with no call.

    How many arguments by position, which by name, and whether one of them is unpacked
    (``*args`` / ``**kwargs``: then anything may be passed).
    """
    found: tuple[int, set[str], bool] | None = None
    for node in ast.walk(ast.parse(source)):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == op
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == resource_attr
        ):
            continue
        unpacked = any(isinstance(argument, ast.Starred) for argument in node.args) or any(
            keyword.arg is None for keyword in node.keywords
        )
        named = {keyword.arg for keyword in node.keywords if keyword.arg is not None}
        before = found or (0, set(), False)
        found = (max(before[0], len(node.args)), before[1] | named, before[2] or unpacked)
    return found


def _not_passed(parameters: list[str], passed: tuple[int, set[str], bool]) -> list[str]:
    """The parameters of a method that a surface's calls never pass."""
    by_position, named, unpacked = passed
    if unpacked:
        return []
    return [name for name in parameters[by_position:] if name not in named]


# An argument of a method that neither surface passes, and why.
ARCH1_ARGUMENTS_KEPT_FROM_SURFACES: dict[str, tuple[frozenset[str], str]] = {
    "tracker.entities.search": (
        frozenset({"per_page", "page"}),
        "the pages of a listing: #502 gives every listing one way to limit and to continue",
    ),
}


def _argument_gaps() -> dict[str, dict[str, list[str]]]:
    """``{"wiki.pages.descendants_list": {"cli": ["actuality"], "mcp": ["actuality"]}}``."""
    gaps: dict[str, dict[str, list[str]]] = {}
    for operation, method in _operation_methods():
        slug, attr, op = operation.split(".")
        parameters = [name for name in inspect.signature(method).parameters if name != "self"]
        kept = ARCH1_ARGUMENTS_KEPT_FROM_SURFACES.get(operation, (frozenset(), ""))[0]
        for surface in ("cli", "mcp"):
            path = YANDEX / slug / attr / f"{surface}.py"
            passed = _passed(path.read_text(encoding="utf-8"), attr, op) if path.exists() else None
            if passed is None:  # the operation is not on this surface: the parity check's matter
                continue
            missing = [name for name in _not_passed(parameters, passed) if name not in kept]
            if missing:
                gaps.setdefault(operation, {})[surface] = missing
    return gaps


def test_arch1_each_surface_passes_every_argument_of_the_operation():
    """An argument the SDK method takes is one the command and the tool take too (ARCH-1).

    Read from each surface's call into the client: an argument the call never passes cannot
    be given on that surface. A value a surface fixes (``fields="content"``) is passed.
    """
    assert _argument_gaps() == {}


def test_arch1_argument_check_bites():
    source = (
        "def tool(client):\n"
        "    client.pages.get(slug, fields='content')\n"
        "    client.pages.list(*where)\n"
        "    other.get(slug, revision=1)\n"
    )
    passed = _passed(source, "pages", "get")
    assert passed is not None and passed == (1, {"fields"}, False)
    assert _not_passed(["slug", "fields", "revision"], passed) == ["revision"]
    assert _not_passed(["slug", "fields"], passed) == []
    # An unpacked argument may be any of them.
    assert _passed(source, "pages", "list") == (1, set(), True)
    assert _not_passed(["slug", "limit"], (0, set(), True)) == []
    assert _passed(source, "boards", "get") is None
