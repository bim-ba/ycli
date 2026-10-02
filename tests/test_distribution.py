"""Every distribution channel advertises the version in pyproject, and says the same thing.

python-semantic-release stamps the files below on each release (``version_variables`` in
pyproject.toml). A pin that PSR cannot match goes stale silently and ships a plugin, a Registry
entry or a Docker tag that points at an old release, so this fails the build instead.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_PYPROJECT = tomllib.loads((_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
_VERSION = _PYPROJECT["project"]["version"]
_SERVER_NAME = "io.github.bim-ba/ycli"

# (file, pattern capturing the stamped version, how many times it appears)
_STAMPS = [
    ("plugins/yandex-360/.claude-plugin/plugin.json", r'"version": "([^"]+)"', 1),
    ("plugins/yandex-360/.mcp.json", r"yandex-cli\[mcp\]==([^\"]+)\"", 1),
    ("server.json", r'^  "version": "([^"]+)"', 1),
    ("server.json", r'^      "version": "([^"]+)"', 1),
    ("server.json", r"yandex-cli\[mcp\]==([^\"]+)\"", 1),
    ("server.json", r"ghcr\.io/bim-ba/ycli:([^\"]+)\"", 1),
    ("mcpb/manifest.json", r'"version": "([^"]+)"', 1),
    ("mcpb/pyproject.toml", r'^version = "([^"]+)"', 1),
    ("mcpb/pyproject.toml", r"yandex-cli\[mcp\]==([^\"]+)\"", 1),
]


@pytest.mark.parametrize(("path", "pattern", "count"), _STAMPS)
def test_stamped_version_matches_pyproject(path: str, pattern: str, count: int) -> None:
    text = (_ROOT / path).read_text(encoding="utf-8")
    assert re.findall(pattern, text, flags=re.MULTILINE) == [_VERSION] * count


def test_every_stamped_file_is_registered_with_psr() -> None:
    """A file in the table above that PSR does not stamp would drift on the next release."""
    configured = {
        entry.split(":", maxsplit=1)[0]
        for entry in _PYPROJECT["tool"]["semantic_release"]["version_variables"]
    }
    assert {path for path, _, _ in _STAMPS} <= configured


def test_server_json_describes_the_pypi_and_oci_packages() -> None:
    server = json.loads((_ROOT / "server.json").read_text(encoding="utf-8"))
    assert server["name"] == _SERVER_NAME
    assert len(server["description"]) <= 100  # the registry rejects longer descriptions
    pypi, oci = server["packages"]
    assert (pypi["registryType"], pypi["identifier"]) == ("pypi", _PYPROJECT["project"]["name"])
    assert (oci["registryType"], oci["identifier"]) == ("oci", f"ghcr.io/bim-ba/ycli:{_VERSION}")
    for package in (pypi, oci):
        assert package["transport"] == {"type": "stdio"}
        secrets = {v["name"]: v.get("isSecret", False) for v in package["environmentVariables"]}
        assert secrets == {"YANDEX_ID_OAUTH_TOKEN": True, "YANDEX_ID_ORGANIZATION_ID": False}


def test_registry_ownership_markers_match_server_name() -> None:
    """The registry verifies PyPI ownership from the README and the image from its label."""
    assert f"<!-- mcp-name: {_SERVER_NAME} -->" in (_ROOT / "README.md").read_text(encoding="utf-8")
    dockerfile = (_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert f'io.modelcontextprotocol.server.name="{_SERVER_NAME}"' in dockerfile
