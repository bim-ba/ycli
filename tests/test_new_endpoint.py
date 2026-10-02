"""The ``/new-endpoint`` scaffolder must emit a resource package that imports cleanly."""

import importlib
import importlib.util
import sys
from pathlib import Path

import pytest

import ycli.yandex.tracker
from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.core.resource import Resource

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "new_endpoint.py"


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
