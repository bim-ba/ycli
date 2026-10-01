"""The ``/new-endpoint`` scaffolder must emit a resource package that imports cleanly."""

import importlib
import importlib.util
import sys
from pathlib import Path

import pytest

import ycli.yandex.tracker

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "new_endpoint.py"


def _load_scaffolder():
    spec = importlib.util.spec_from_file_location("new_endpoint", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("layer", ["models", "client", "cli", "mcp"])
def test_scaffolded_layer_imports(layer, tmp_path, monkeypatch):
    """Each generated module imports against the current package layout."""
    resource = "scaffold_probe"
    _load_scaffolder().scaffold("tracker", resource, root=tmp_path)
    # Let ``ycli.yandex.tracker.scaffold_probe`` resolve from tmp_path without touching src/.
    monkeypatch.setattr(
        ycli.yandex.tracker, "__path__", [*ycli.yandex.tracker.__path__, str(tmp_path / "tracker")]
    )
    package = f"ycli.yandex.tracker.{resource}"
    for name in [n for n in sys.modules if n.startswith(package)]:
        monkeypatch.delitem(sys.modules, name)

    module = importlib.import_module(f"{package}.{layer}")

    assert module.__name__ == f"{package}.{layer}"
