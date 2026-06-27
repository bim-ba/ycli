"""The bundled plugin MCP config auto-wires the read-only server without leaking secrets.

Installing the yandex-360 plugin should register the MCP server with no hand-copied
JSON. This locks the command form and guarantees credentials are passed by env-var
reference, never as literal values.
"""
from __future__ import annotations

import json
from pathlib import Path

_MCP = Path(__file__).resolve().parent.parent / "plugins" / "yandex-360" / ".mcp.json"


def test_plugin_mcp_declares_readonly_server():
    config = json.loads(_MCP.read_text(encoding="utf-8"))
    servers = config["mcpServers"]
    assert "yandex-360" in servers
    server = servers["yandex-360"]
    assert server["command"] == "uvx"
    assert server["args"] == ["--from", "yandex-cli[mcp]", "ycli", "mcp"]


def test_plugin_mcp_passes_secrets_by_reference():
    config = json.loads(_MCP.read_text(encoding="utf-8"))
    env = config["mcpServers"]["yandex-360"]["env"]
    assert set(env) == {"YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID"}
    for value in env.values():
        assert value.startswith("${") and value.endswith("}")
