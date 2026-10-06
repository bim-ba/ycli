"""ARCH-7 — Dependency injection (see ARCHITECTURE.md)."""

import ast
from pathlib import Path

import pytest

from tests.architecture.scanners import SRC

# The composition roots: the only modules that build settings from the environment.
ARCH7_ROOTS = {
    Path("cli/app.py"): "CLI root callback (logging config)",
    Path("cli/context.py"): "CLI dependency container",
    Path("mcp/__main__.py"): "python -m ycli.mcp entry point",
    Path("mcp/cli.py"): "`mcp start --profile` names the profile its providers read",
    Path("mcp/server.py"): "MCP over HTTP reads its address and the OAuth app at start",
    Path("yandex/mcp.py"): "MCP per-request providers",
    Path("yandex/status/cli.py"): "auth status/login read and write credentials by design",
}
# The settings models, and the functions that read the active profile for them.
_SETTINGS_MODELS = {
    "AppConfig",
    "Credentials",
    "MCPHTTPConfig",
    "OAuthAppConfig",
    "active_profile",
    "name_profile",
}


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
        # ``AppConfig.__name__`` reads the class and builds none; ``Credentials.load()`` builds.
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
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


def test_arch7_every_root_still_builds_settings():
    """A root that no longer builds a settings model is removed from the allowlist."""
    stale = [
        str(rel)
        for rel in ARCH7_ROOTS
        if not (SRC / rel).is_file()
        or not _settings_constructions((SRC / rel).read_text(encoding="utf-8"))
    ]
    assert stale == []


def test_arch7_stale_root_check_bites(monkeypatch):
    monkeypatch.setitem(ARCH7_ROOTS, Path("yandex/models.py"), "builds no settings")
    with pytest.raises(AssertionError):
        test_arch7_every_root_still_builds_settings()


def test_arch7_guard_bites():
    assert _settings_constructions("config = AppConfig()\ncreds = Credentials()") == [1, 2]
    assert _settings_constructions("creds = settings.Credentials()") == [1]
    assert _settings_constructions("from ycli.settings import AppConfig as C\nC()") == [2]
    assert _settings_constructions("field(default_factory=AppConfig)") == [1]
    assert _settings_constructions("def f(config: AppConfig) -> AppConfig: return config") == []
    assert _settings_constructions("title = AppConfig.__name__") == []
    assert _settings_constructions("creds = Credentials.load('work')") == [1]
    assert _settings_constructions("creds = Credentials.from_profile('work')") == [1]
    assert _settings_constructions("profile = active_profile()") == [1]
