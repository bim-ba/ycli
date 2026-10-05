"""ARCH-4 — One output path (see ARCHITECTURE.md)."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.architecture.scanners import SRC, _dotted, _import_aliases

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
# Where stdout may be written, and why: the renderer itself, and one eager option.
ARCH4_STDOUT_HOMES = {Path("cli/output.py"): "output.render, the one output path"}
ARCH4_STDOUT_FUNCTIONS = {
    # Eager: it runs before any command, so there is no result to return. Routing it through
    # output.render would import yaml/rich/pydantic first (measured 48 -> 110 ms for --version).
    "cli/app.py:_version_callback": "`ycli --version` prints the version and exits",
    # Reads whether stdout is a terminal (to know if a person can be asked); it writes nothing.
    "cli/guard.py:attended": "the confirmation prompt needs a terminal on stdin and stdout",
}


def _stdout_writes(source: str, exempt_functions: frozenset[str] = frozenset()) -> list[str]:
    """Places in ``source`` that write to stdout.

    They are ``print`` in any spelling (``builtins.print``, ``rich.print``, ``pprint``, an import
    alias), ``typer.echo`` / ``secho`` and ``Console(...)`` without a stderr flag, ``os.write``,
    and any use of ``stdout`` / ``__stdout__``. Messages to stderr are UI, not output. Top-level
    functions named in ``exempt_functions`` are skipped.
    """
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
