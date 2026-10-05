"""Scaffold a new Yandex resource that satisfies the architecture by construction.

    python scripts/new_endpoint.py tracker macros

Creates src/ycli/yandex/tracker/macros/{__init__,endpoints,client,cli,mcp,models}.py on the
httpx2 core (the pattern of ``tracker/issues/``): each operation declared once in
``endpoints.py``, a ``Resource`` client that sends it, the render output path, and honest MCP
annotations (ARCH-3). The scaffold generates one read (`RO` annotations); write tools take the
`WRITE` / `WRITE_IDEMPOTENT` / `DESTRUCTIVE` annotation sets plus the `write` tag and must agree
with their endpoint's effect. Fill the marked spots with the real endpoint; the structure
already satisfies ARCH-1..4 and import-linter, and passes ruff as generated.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ycli.yandex.registry import SERVICES

DOMAINS = tuple(service.name for service in SERVICES)
ROOT = Path(__file__).resolve().parent.parent / "src" / "ycli" / "yandex"
# Directory names of a service that are not resources (tests/architecture/test_arch1.py agrees).
RESERVED_NAMES = {
    "mcp": "<domain>/mcp/ is the service's MCP server",
    "schemas": "<domain>/schemas/ holds models generated from the service's specification",
}

INIT = '"""Yandex {domain} /{resource} resource (endpoints · client · cli · mcp · models)."""\n'

MODELS = '''"""Pydantic models for {domain} /{resource}."""

from pydantic import Field

from ycli.yandex.models import APIModel


class {cls}(APIModel):
    """One {resource} record. FILL: add the real fields, each with its description."""

    id: str = Field(default="", description="The {resource} id.")
'''

ENDPOINTS = '''"""{domain} ``/{resource}`` operations, each declared once (sans-IO).

A listing returns ``Paged(Endpoint(...), <the service's Pagination>, <the items of a page>)``
and its client method a flat ``ItemList``; ``tracker/issues/`` is the worked example.
A shape another resource of the service already reads is imported from the service's
``models.py``, not declared again.
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.{domain}.{resource}.models import {cls}


def get(item_id: str) -> Endpoint[{cls}]:
    # FILL: the real path.
    return Endpoint(HTTPMethod.GET, f"FILL/{resource}/{{segment(item_id)}}", {cls})
'''

CLIENT = '''"""{domain} ``/{resource}`` client on the httpx2 core — sends ``endpoints``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.{domain}.{resource} import endpoints

if TYPE_CHECKING:
    from ycli.yandex.{domain}.{resource}.models import {cls}


class {cls}Client(Resource):
    """{domain} /{resource} (scaffolded with one read; add the real operations)."""

    def get(self, item_id: str) -> {cls}:
        """``GET /FILL/{resource}/{{item_id}}`` → one ``{cls}``.

        Args:
            item_id: The {resource} id.

        Returns:
            The {resource}.

        Examples:
            >>> {domain}.{resource}.get("1")
        """
        return self._session.send(endpoints.get(item_id))
'''

CLI = '''"""{domain} /{resource} Typer commands — each returns its result; the root prints it."""

from typing import Annotated

import typer

from ycli.yandex.{domain}.client import {domain_cls}Client
from ycli.yandex.{domain}.{resource}.models import {cls}

app = typer.Typer(name="{resource}", help="{domain} /{resource}.", no_args_is_help=True)


@app.command()
def get(
    item_id: Annotated[str, typer.Argument(help="The {resource} id.")],
    *,
    {domain}: {domain_cls}Client,
) -> {cls}:
    """Fetch one {resource} by id."""
    return {domain}.{resource}.get(item_id)
'''

MCP = '''"""{domain} /{resource} FastMCP tools (honest annotations, ARCH-3).

The scaffolded tool is a read (`RO` annotations). For write tools use the `WRITE` /
`WRITE_IDEMPOTENT` / `DESTRUCTIVE` annotation sets from ``ycli.yandex.mcp`` plus the
`write` tag; ARCH-3 checks each tool's hints against the effect of the endpoint it sends.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.{domain}.client import {domain_cls}Client
from ycli.yandex.{domain}.dependencies import RO, {domain}_client
from ycli.yandex.{domain}.{resource}.models import {cls}

mcp = FastMCP("{domain}-{resource}")


@mcp.tool(
    name="{resource}_get",
    annotations={{**RO, "title": "Get {domain} {resource}"}},
    # The docstring below IS the client-facing description (the LLM\'s selector) —
    # required; do not pass description= to @mcp.tool.
    # The return type annotation IS the output schema (auto-derived by fastmcp) —
    # required; do not pass output_schema= to @mcp.tool.
)
def get(
    item_id: Annotated[str, Field(description="The {resource} id.")],
    client: {domain_cls}Client = Depends({domain}_client),
) -> {cls}:
    """Fetch one {resource} by id."""
    return client.{resource}.get(item_id)
'''


def _cls(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def scaffold(domain: str, resource: str, root: Path = ROOT) -> Path:
    """Write the resource package under ``root/<domain>/<resource>`` and return its path.

    >>> scaffold("tracker", "macros")  # doctest: +SKIP
    PosixPath('.../src/ycli/yandex/tracker/macros')
    """
    target = root / domain / resource
    if target.exists():
        raise SystemExit(f"{target} already exists")
    target.mkdir(parents=True)

    ctx = {
        "domain": domain,
        "resource": resource,
        "cls": _cls(resource),
        # The client's own class name: ``DataLensClient`` is not ``Datalens`` capitalized.
        "domain_cls": next(
            service.client.rpartition(":")[2].removesuffix("Client")
            for service in SERVICES
            if service.name == domain
        ),
    }
    for filename, template in (
        ("__init__.py", INIT),
        ("models.py", MODELS),
        ("endpoints.py", ENDPOINTS),
        ("client.py", CLIENT),
        ("cli.py", CLI),
        ("mcp.py", MCP),
    ):
        (target / filename).write_text(template.format(**ctx), encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new Yandex resource.")
    parser.add_argument("domain", choices=DOMAINS)
    parser.add_argument("resource", help="resource name, e.g. macros")
    args = parser.parse_args()

    resource = args.resource.replace("-", "_")
    if resource in RESERVED_NAMES:
        parser.error(f"{resource!r} is reserved: {RESERVED_NAMES[resource]}")
    target = scaffold(args.domain, resource)

    cls = _cls(resource)
    print(f"scaffolded {target.relative_to(ROOT.parent.parent.parent)}")
    print(
        "next:\n"
        "  1. replace the FILL markers in endpoints.py/client.py/models.py with the real path,\n"
        "     operations and fields\n"
        f"  2. register the resource in {args.domain}/client.py `_wire`:\n"
        f"     self.{resource} = {cls}Client(session=session)\n"
        f"  3. mount the sub-app into {args.domain}/cli.py (app.add_typer) and the subserver into\n"
        f"     {args.domain}/mcp/server.py (mcp.mount), mirroring a sibling resource\n"
        "  4. add contract cases in tests/unit/yandex/<domain>/<resource>/cases.py "
        "(docs/conventions/testing.md)\n"
        "  5. run: uv run pytest && "
        "uv run python -m tests.snapshots --update"
    )


if __name__ == "__main__":
    main()
