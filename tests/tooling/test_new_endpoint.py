"""The ``/new-endpoint`` scaffold imports, and passes the gates a resource meets, as generated."""

import asyncio
import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
from fastmcp import Client

import ycli.yandex.tracker
from tests.architecture import test_arch1, test_arch4, test_arch5, test_arch8
from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.core.resource import Resource

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "new_endpoint.py"


def _load_scaffolder():
    spec = importlib.util.spec_from_file_location("new_endpoint", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RESOURCE = "scaffold_probe"
PACKAGE = f"ycli.yandex.tracker.{RESOURCE}"


@pytest.fixture
def scaffolded(tmp_path, monkeypatch):
    """Scaffold ``tracker/scaffold_probe`` into tmp_path and make it importable."""
    _load_scaffolder().scaffold("tracker", RESOURCE, root=tmp_path)
    # Let ``ycli.yandex.tracker.scaffold_probe`` resolve from tmp_path without touching src/.
    monkeypatch.setattr(
        ycli.yandex.tracker, "__path__", [*ycli.yandex.tracker.__path__, str(tmp_path / "tracker")]
    )
    for name in [n for n in sys.modules if n.startswith(PACKAGE)]:
        monkeypatch.delitem(sys.modules, name)


@pytest.mark.parametrize("layer", ["models", "endpoints", "client", "cli", "mcp"])
def test_scaffolded_layer_imports(layer, scaffolded):
    """Each generated module imports against the current package layout."""
    module = importlib.import_module(f"{PACKAGE}.{layer}")

    assert module.__name__ == f"{PACKAGE}.{layer}"


def test_scaffolded_client_sends_its_endpoint_on_the_core(scaffolded):
    """A new resource starts on the httpx2 core: its client sends a declared ``Endpoint``."""
    client_module = importlib.import_module(f"{PACKAGE}.client")
    sent = []

    class _Session:
        def send(self, endpoint: Endpoint) -> str:
            sent.append(endpoint)
            return "parsed"

    client = client_module.ScaffoldProbeClient(session=_Session())

    assert isinstance(client, Resource)
    assert client.get("7") == "parsed"
    assert (sent[0].method, sent[0].path) == ("GET", f"FILL/{RESOURCE}/7")


def _generated(tmp_path: Path) -> dict[str, str]:
    """The scaffold's files, keyed by the path they would have in the repository."""
    target = _load_scaffolder().scaffold("tracker", RESOURCE, root=tmp_path)
    return {
        f"src/ycli/yandex/tracker/{RESOURCE}/{path.name}": path.read_text(encoding="utf-8")
        for path in sorted(target.iterdir())
    }


@pytest.mark.parametrize("command", [["check"], ["format", "--check"]])
def test_the_scaffold_passes_ruff_as_generated(command, tmp_path):
    """No generated file needs a fix: the lint and the format gate pass on the raw output."""
    for filename, source in _generated(tmp_path).items():
        ruff = subprocess.run(
            [sys.executable, "-m", "ruff", *command, "--stdin-filename", filename, "-"],
            input=source,
            capture_output=True,
            text=True,
            cwd=SCRIPT.parent.parent,
            check=False,
        )
        assert ruff.returncode == 0, f"{filename}:\n{ruff.stdout}{ruff.stderr}"


def test_the_scaffold_passes_the_architecture_checks(tmp_path):
    """The per-file ARCH checks find nothing in the raw output."""
    offenders = []
    for filename, source in _generated(tmp_path).items():
        relative = Path(filename).relative_to("src/ycli")
        offenders += test_arch4._stdout_writes(source)
        offenders += test_arch4._serializations(source)
        offenders += test_arch5._single_source_offenders(relative, source)
        offenders += test_arch8._error_mapping_offenders(relative, source)
    assert offenders == []


def test_the_scaffolded_tool_meets_the_metadata_standard(scaffolded):
    """The generated tool is an annotated read whose description, parameters and output are set."""
    server = importlib.import_module(f"{PACKAGE}.mcp").mcp

    async def listed():
        async with Client(server) as client:
            return await client.list_tools()

    (tool,) = asyncio.run(listed())
    assert tool.name == f"{RESOURCE}_get"
    assert tool.description and tool.output_schema is not None
    assert tool.annotations.read_only_hint and tool.annotations.title
    assert all(schema.get("description") for schema in tool.input_schema["properties"].values())


def test_the_scaffolded_model_describes_every_field(scaffolded):
    model = importlib.import_module(f"{PACKAGE}.models").ScaffoldProbe

    assert all(field.description for field in model.model_fields.values())


def test_a_reserved_name_is_refused_as_a_resource(monkeypatch, capsys):
    """``<domain>/mcp/`` is the service's MCP server, so no resource can take the name."""
    module = _load_scaffolder()
    assert module.RESERVED_NAMES == test_arch1.RESERVED_NAMES
    monkeypatch.setattr(sys, "argv", ["new_endpoint.py", "tracker", "mcp"])
    with pytest.raises(SystemExit) as refused:
        module.main()
    assert refused.value.code == 2
    assert "'mcp' is reserved" in capsys.readouterr().err


def test_the_scaffold_names_the_services_client_class_as_it_is(tmp_path):
    """``DataLensClient``, not the service's name capitalized."""
    target = _load_scaffolder().scaffold("datalens", "probe", root=tmp_path)
    assert "import DataLensClient" in (target / "cli.py").read_text(encoding="utf-8")
