"""MCP over HTTP: callers sign in through Yandex ID, and each tool call runs as its caller."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

import httpx2
import pytest
from fastmcp import FastMCP
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.debug import DebugTokenVerifier
from pydantic import SecretStr, ValidationError
from typer.testing import CliRunner

from tests.hosts import TRACKER_BASE
from ycli.cli.app import app as ycli_app
from ycli.mcp import server as server_module
from ycli.mcp.http_auth import YandexTokenVerifier, yandex_oauth
from ycli.mcp.selection import Selection
from ycli.mcp.server import build_server, serve_http
from ycli.settings import HTTPConfig, MCPHTTPConfig

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

ID_URL = "https://login.yandex.ru/info"
BASE_URL = "https://mcp.example.com"
APP_ID = "app-1"
ACCEPT = {"Accept": "application/json, text/event-stream"}


@asynccontextmanager
async def _http(server: FastMCP) -> AsyncIterator[httpx2.AsyncClient]:
    """An HTTP client wired straight into ``server``'s ASGI app, with its lifespan running."""
    app = server.http_app(stateless_http=True, json_response=True)
    async with (
        app.router.lifespan_context(app),
        httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url=BASE_URL) as client,
    ):
        yield client


async def _call(client: httpx2.AsyncClient, tool: str, token: str | None) -> httpx2.Response:
    headers = {**ACCEPT, **({"Authorization": f"Bearer {token}"} if token else {})}
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": {"key": "DE-1"}},
    }
    return await client.post("/mcp", headers=headers, json=request)


def _result(response: httpx2.Response) -> dict[str, Any]:
    return response.json()["result"]


# --- each tool call runs with the signed-in caller's token -----------------------------------


async def test_a_tool_call_over_http_uses_the_callers_token_not_the_environments(api, monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "server-env-token")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org-env")
    monkeypatch.setenv("YCLI__MCP__BASE_URL", BASE_URL)
    api.add("GET", f"{TRACKER_BASE}/issues/DE-1", json={"key": "DE-1"})
    server = build_server(Selection(toolsets=("tracker",)), auth=DebugTokenVerifier())
    async with _http(server) as client:
        response = await _call(client, "tracker_issues_get", "caller-token")
    assert _result(response)["structuredContent"]["key"] == "DE-1"
    assert api.calls[0].headers["Authorization"] == "OAuth caller-token"
    assert api.calls[0].headers["X-Org-Id"] == "org-env"


async def test_an_http_call_works_in_the_organization_the_server_checked_at_start(
    api, monkeypatch, tmp_path
):
    """Configured only as YCLI__MCP__ORGANIZATION_ID, the organization still reaches the call."""
    monkeypatch.chdir(tmp_path)  # a developer's own .env names an organization too
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.setenv("YCLI__MCP__ORGANIZATION_ID", "org-mcp")
    monkeypatch.setenv("YCLI__MCP__BASE_URL", BASE_URL)
    api.add("GET", f"{TRACKER_BASE}/issues/DE-1", json={"key": "DE-1"})
    server = build_server(Selection(toolsets=("tracker",)), auth=DebugTokenVerifier())
    async with _http(server) as client:
        response = await _call(client, "tracker_issues_get", "caller-token")
    assert _result(response)["structuredContent"]["key"] == "DE-1"
    assert api.calls[0].headers["X-Org-Id"] == "org-mcp"


def test_a_bare_organization_id_variable_does_not_configure_the_http_server(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # no repo .env
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.setenv("YCLI__MCP__BASE_URL", BASE_URL)
    monkeypatch.setenv("ORGANIZATION_ID", "222")
    with pytest.raises(ValidationError):
        MCPHTTPConfig()  # ty: ignore[missing-argument]  # pydantic-settings reads the env


def test_the_http_organization_comes_from_its_named_variables_or_the_field_name(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("YCLI__MCP__BASE_URL", BASE_URL)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.setenv("ORGANIZATION_ID", "222")
    monkeypatch.setenv("YCLI__MCP__ORGANIZATION_ID", "333")
    assert MCPHTTPConfig().organization_id == "333"  # ty: ignore[missing-argument]
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "444")
    assert MCPHTTPConfig().organization_id == "444"  # ty: ignore[missing-argument]
    by_name = MCPHTTPConfig.model_validate({"base_url": BASE_URL, "organization_id": "555"})
    assert by_name.organization_id == "555"


async def test_an_http_call_without_a_signed_in_caller_never_falls_back_to_the_environment(
    api, monkeypatch
):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "server-env-token")
    server = build_server(Selection(toolsets=("tracker",)))  # no auth: nobody is signed in
    async with _http(server) as client:
        response = await _call(client, "tracker_issues_get", None)
    result = _result(response)
    assert result["isError"] is True
    assert "no authenticated caller" in result["content"][0]["text"]
    assert api.calls == []


async def test_the_oauth_server_refuses_a_request_without_its_token(api):
    auth = yandex_oauth(
        MCPHTTPConfig.model_validate({"base_url": BASE_URL, "organization_id": "1"}),
        APP_ID,
        SecretStr("secret"),
        HTTPConfig(),
    )
    server = build_server(Selection(toolsets=("tracker",)), auth=auth)
    async with _http(server) as client:
        refused = await _call(client, "tracker_issues_get", "y0_raw-yandex-token")
        metadata = await client.get("/.well-known/oauth-protected-resource/mcp")
        authorization_server = await client.get("/.well-known/oauth-authorization-server")
    assert refused.status_code == 401
    assert "resource_metadata" in refused.headers["WWW-Authenticate"]
    assert metadata.json()["resource"] == f"{BASE_URL}/mcp"
    endpoints = authorization_server.json()
    assert endpoints["authorization_endpoint"] == f"{BASE_URL}/authorize"
    assert "S256" in endpoints["code_challenge_methods_supported"]
    assert api.calls == []  # nothing reached Yandex


def test_the_proxy_signs_in_through_yandex_oauth():
    auth = yandex_oauth(
        MCPHTTPConfig.model_validate(
            {"base_url": BASE_URL, "organization_id": "1", "jwt_signing_key": "k" * 32}
        ),
        APP_ID,
        SecretStr("secret"),
        HTTPConfig(),
    )
    assert isinstance(auth, OAuthProxy)
    assert auth._upstream_authorization_endpoint == "https://oauth.yandex.ru/authorize"
    assert auth._upstream_token_endpoint == "https://oauth.yandex.ru/token"


# --- the verifier: a Yandex token of this app only ------------------------------------------


def _verifier(cache_seconds: int = 300) -> YandexTokenVerifier:
    return YandexTokenVerifier(client_id=APP_ID, http=HTTPConfig(), cache_seconds=cache_seconds)


async def test_a_token_of_this_app_is_accepted_and_remembered(api):
    api.add("GET", ID_URL, json={"id": "42", "login": "alice", "client_id": APP_ID})
    verifier = _verifier()
    access = await verifier.verify_token("y0_alice")
    again = await verifier.verify_token("y0_alice")
    assert access is not None
    assert (access.token, access.subject, access.claims["login"]) == ("y0_alice", "42", "alice")
    assert again == access
    assert len(api.calls) == 1  # the second check came from the cache
    assert api.calls[0].headers["Authorization"] == "OAuth y0_alice"


async def test_a_token_issued_to_another_app_is_refused(api):
    api.add("GET", ID_URL, json={"id": "42", "login": "alice", "client_id": "someone-else"})
    assert await _verifier().verify_token("y0_alice") is None


async def test_a_token_yandex_rejects_is_refused_and_not_remembered(api):
    api.add("GET", ID_URL, status=401, json={"error": "invalid_token"})
    verifier = _verifier()
    assert await verifier.verify_token("y0_revoked") is None
    assert await verifier.verify_token("y0_revoked") is None
    assert len(api.calls) == 2


# --- starting the HTTP server ---------------------------------------------------------------


@pytest.fixture
def http_env(monkeypatch):
    monkeypatch.setenv("YCLI__MCP__BASE_URL", BASE_URL)
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org-1")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", APP_ID)
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "secret")


def test_serve_http_runs_stateless_streamable_http_on_the_configured_address(http_env, monkeypatch):
    ran: dict[str, Any] = {}
    monkeypatch.setattr(FastMCP, "run", lambda server, **options: ran.update(options))
    serve_http(Selection(toolsets=("wiki",)), port=9000)
    assert ran == {"transport": "http", "host": "127.0.0.1", "port": 9000, "stateless_http": True}


def test_serve_http_names_the_missing_settings(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # no repo .env
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    with pytest.raises(ValueError, match="YCLI__MCP__BASE_URL") as raised:
        serve_http(Selection())
    assert "YANDEX_ID_ORGANIZATION_ID" in str(raised.value)


def test_serve_http_needs_the_oauth_app(http_env, monkeypatch):
    monkeypatch.delenv("YANDEX_OAUTH_CLIENT_SECRET")
    monkeypatch.setattr(server_module, "OAuthAppConfig", lambda: _NoSecret())
    with pytest.raises(ValueError, match="YANDEX_OAUTH_CLIENT_SECRET"):
        serve_http(Selection())


class _NoSecret:
    client_id = APP_ID
    client_secret = None


def test_mcp_start_over_http_without_configuration_is_a_usage_error(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(ycli_app, ["mcp", "start", "--transport", "http"])
    assert result.exit_code == 2
    assert "YCLI__MCP__BASE_URL" in result.output


def test_mcp_start_over_http_serves(http_env, monkeypatch):
    served: list[tuple[str | None, int | None]] = []
    monkeypatch.setattr(
        server_module, "serve_http", lambda selection, host, port: served.append((host, port))
    )
    result = CliRunner().invoke(
        ycli_app, ["mcp", "start", "--transport", "http", "--host", "0.0.0.0", "--port", "8080"]
    )
    assert result.exit_code == 0, result.output
    assert served == [("0.0.0.0", 8080)]


@pytest.mark.parametrize("args", [["mcp", "start", "--dry-run"], ["--dry-run", "mcp", "start"]])
def test_mcp_start_refuses_dry_run_it_could_not_honour(args, monkeypatch):
    monkeypatch.setattr(server_module, "main", lambda selection: pytest.fail("server started"))
    result = CliRunner().invoke(ycli_app, args)
    assert result.exit_code == 2
    assert "--read-only" in result.output
