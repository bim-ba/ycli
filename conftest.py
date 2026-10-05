"""The examples in docstrings run as doctests, answered by the contract cases.

An example in ``src/`` uses ready clients named after their service (``tracker``, ``wiki``,
``forms``). Every request they send is answered from the contract cases in
``tests/unit/yandex/<domain>/<resource>/cases.py``, route by route in the cases' order, as
``MockAPI`` serves several answers for one route. So an example reads like real use, never
reaches the network, and fails once it stops matching the replies the contract pins: give it
the arguments of the first case for its operation.

This file sits at the repository root because a conftest applies only to its own directory
tree, and ``src/`` must not ship one.
"""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

import pytest
from tests.mock_api import MockAPI

from ycli.yandex.registry import SERVICES

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@cache
def _contract_api() -> MockAPI:
    # Imported on the first doctest only: the cases import the MCP layer, which the live e2e
    # run (pytest e2e, no `mcp` extra) must not need.
    from tests.contract import load_cases

    api = MockAPI()
    base_urls = {service.name: service.profile.base_url.rstrip("/") for service in SERVICES}
    for case in load_cases():
        for sent, reply in case.exchanges:
            api.add(
                sent.method,
                f"{base_urls[case.domain]}/{sent.path}",
                json=reply.json,
                status=reply.status,
                headers=dict(reply.headers),
                content=reply.content,
            )
    return api


@pytest.fixture(autouse=True)
def _no_developer_dotenv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Run from an empty directory: the settings read ``.env`` of the working directory.

    A developer keeps real credentials in the ``.env`` of the repository root. Removing a
    variable from the environment is not enough to unset it there, so a test would pass or
    fail by whose machine it runs on, and an error could quote a real value.
    """
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def _doctest_clients(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> Iterator[None]:
    """Put a client per service into a doctest's namespace, answered by the contract cases."""
    if not isinstance(request.node, pytest.DoctestItem):
        yield
        return
    monkeypatch.setattr(
        "ycli.yandex.core.session.default_transport", _contract_api().copy().transport
    )
    clients = {
        service.name: service.client_class()(
            oauth_token="token", organization_id="org", cloud_organization_id="cloud-org"
        )
        for service in SERVICES
    }
    request.node.dtest.globs.update(clients)
    yield
    for client in clients.values():
        client.close()
