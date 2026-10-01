"""The service registry is the only list of services; every surface derives from it."""

import asyncio

import pytest
from fastmcp import Client
from typer.main import get_command

from ycli.cli.app import app
from ycli.mcp import mcp as root_mcp
from ycli.yandex.base import DomainClient
from ycli.yandex.registry import SERVICES


def test_service_names_are_unique():
    names = [service.name for service in SERVICES]
    assert len(names) == len(set(names))


@pytest.mark.parametrize("service", SERVICES, ids=lambda service: service.name)
def test_service_import_paths_resolve(service):
    assert issubclass(service.client_class(), DomainClient)
    assert service.cli_app().info.name == service.name
    assert service.mcp_server().name == service.name


@pytest.mark.integration
def test_cli_root_mounts_every_service_with_its_help():
    groups = get_command(app).commands  # ty: ignore[unresolved-attribute]
    for service in SERVICES:
        assert groups[service.name].help == service.help


@pytest.mark.integration
def test_mcp_root_namespaces_every_service():
    async def tool_names():
        async with Client(root_mcp) as client:
            return {tool.name for tool in await client.list_tools()}

    names = asyncio.run(tool_names())
    for service in SERVICES:
        assert any(name.startswith(f"{service.name}_") for name in names), service.name
