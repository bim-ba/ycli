"""The service registry is the only list of services; every surface derives from it."""

import asyncio

import pytest
import typer
from fastmcp import Client
from typer.main import get_command

from tests.full_server import mcp as root_mcp
from ycli.cli.app import app
from ycli.yandex.base import DomainClient
from ycli.yandex.registry import SERVICES
from ycli.yandex.tracker.pages import LINK_NEXT
from ycli.yandex.wiki.cursor import WIKI_CURSOR


def test_service_names_are_unique():
    names = [service.name for service in SERVICES]
    assert len(names) == len(set(names))


@pytest.mark.parametrize("service", SERVICES, ids=lambda service: service.name)
def test_service_import_paths_resolve(service):
    assert issubclass(service.client_class(), DomainClient)
    assert service.cli_app().info.name == service.name
    assert service.mcp_server().name == service.name


def test_cli_root_mounts_every_service_with_its_help():
    root = get_command(app)
    context = typer.Context(root)
    for service in SERVICES:
        group = root.get_command(context, service.name)  # ty: ignore[unresolved-attribute]
        assert group.help == service.help


def test_mcp_root_namespaces_every_service():
    async def tool_names():
        async with Client(root_mcp) as client:
            return {tool.name for tool in await client.list_tools()}

    names = asyncio.run(tool_names())
    for service in SERVICES:
        assert any(name.startswith(f"{service.name}_") for name in names), service.name


def test_only_a_service_with_one_pagination_for_every_listing_names_it():
    by_name = {service.name: service.listing_pagination() for service in SERVICES}
    assert by_name["wiki"] is WIKI_CURSOR
    assert by_name["tracker"] is LINK_NEXT
    assert by_name["forms"] is None
