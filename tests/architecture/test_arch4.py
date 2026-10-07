"""ARCH-4 — One output path (see ARCHITECTURE.md)."""

import ast
from pathlib import Path

from tests.architecture.scanners import SRC, _dotted, _import_aliases, unexplained

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
    Path("yandex/sync/formats.py"): "writes a file of a repository, not a result of a command",
    Path("yandex/sync/document.py"): "the canonical form a fingerprint is taken from",
}


def _serializations(source: str) -> list[str]:
    """Calls in ``source`` that serialize a value.

    They are ``json.dumps``, ``yaml.safe_dump``, ``pydantic_core.to_json`` (import aliases
    resolved) or a ``.model_dump_json()``.
    """
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
# Where stdout may be written, and why: the renderer itself. Any other place that touches
# stdout says why on the line above, `# violation(arch-4): <reason>`.
ARCH4_STDOUT_HOMES = {Path("cli/output.py"): "output.render, the one output path"}


def _stdout_lines(source: str) -> list[tuple[int, str]]:
    """(line, finding) for the places in ``source`` that write to stdout.

    They are ``print`` in any spelling (``builtins.print``, ``rich.print``, ``pprint``, an import
    alias), ``typer.echo`` / ``secho`` and ``Console(...)`` without a stderr flag, ``os.write``,
    and any use of ``stdout`` / ``__stdout__``. Messages to stderr are UI, not output.
    """
    tree = ast.parse(source)
    aliases = _import_aliases(tree)
    found = []
    for top in tree.body:
        for node in ast.walk(top):
            if isinstance(node, ast.Call):
                name = _dotted(node.func, aliases)
                last = name.rpartition(".")[2] or getattr(node.func, "attr", "")
                if name in _PRINTERS:
                    found.append((node.lineno, f"print (line {node.lineno})"))
                elif last in {"echo", "secho", "Console"} and not _to_stderr(node):
                    found.append((node.lineno, f"{last} (line {node.lineno})"))
                elif name == "os.write":
                    found.append((node.lineno, f"os.write (line {node.lineno})"))
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
                found.append((node.lineno, f"stdout (line {node.lineno})"))
    return found


def _stdout_writes(source: str, path: str = "<source>") -> list[str]:
    """Stdout writes of ``source`` with no ``# violation(arch-4)`` above, and markers above none."""
    return unexplained(_stdout_lines(source), source, "arch-4", path)


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
        if writes := _stdout_writes(p.read_text(encoding="utf-8"), str(rel)):
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
    # Both sides: a marked write passes, an unmarked one and a marker above no write do not.
    version = (
        "def _version_callback(value):\n"
        "    # violation(arch-4): eager, there is no result to return\n"
        "    typer.echo(value)\n"
    )
    assert _stdout_writes(version) == []
    assert _stdout_writes(version.replace("arch-4", "arch-9")) == ["echo (line 3)"]
    assert _stdout_writes(version.replace("typer.echo(value)", "return value"), "cli/app.py") == [
        "cli/app.py:2: violation(arch-4) marks nothing the check finds"
    ]
