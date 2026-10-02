"""Scaffold a new Yandex resource that satisfies the architecture by construction.

    python scripts/new_endpoint.py tracker macros

Creates src/ycli/yandex/tracker/macros/{__init__,endpoints,client,cli,mcp,models}.py on the
httpx2 core (the pattern of ``tracker/issues/``): each operation declared once in
``endpoints.py``, a ``Resource`` client that sends it, the render output path, and honest MCP
annotations (ARCH-3). The scaffold generates one read (`RO` annotations); write tools take the
`WRITE` / `WRITE_IDEMPOTENT` / `DESTRUCTIVE` annotation sets plus the `write` tag and must agree
with their endpoint's effect. Fill the marked spots with the real endpoint; the structure
already satisfies ARCH-1..4 and import-linter.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ycli.yandex.registry import SERVICES

DOMAINS = tuple(service.name for service in SERVICES)
ROOT = Path(__file__).resolve().parent.parent / "src" / "ycli" / "yandex"

INIT = '"""Yandex {domain} /{resource} resource (endpoints · client · cli · mcp · models)."""\n'

MODELS = '''"""Pydantic models for {domain} /{resource}."""

from __future__ import annotations

from ycli.yandex.models import APIModel


class {cls}(APIModel):
    """One {resource} record. FILL: add the real fields."""

    id: str = ""
'''

ENDPOINTS = '''"""{domain} ``/{resource}`` operations, each declared once (sans-IO).

A listing returns ``Paged(Endpoint(...), <the service's Pagination>, <the items of a page>)``;
``tracker/issues/endpoints.py`` is the worked example.
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.{domain}.{resource}.models import {cls}


def get_item(item_id: str) -> Endpoint[{cls}]:
    return Endpoint("GET", f"FILL/{resource}/{{segment(item_id)}}", {cls})  # FILL: real path
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

        Example:
            >>> client.{resource}.get("1")  # doctest: +SKIP
        """
        return self._session.send(endpoints.get_item(item_id))
'''

CLI = '''"""{domain} /{resource} Typer commands — each returns its result; the root prints it."""

from __future__ import annotations

import typer

from ycli.yandex.{domain}.client import {domain_cls}Client
from ycli.yandex.{domain}.{resource}.models import {cls}

app = typer.Typer(name="{resource}", help="{domain} /{resource}.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(item_id: str, *, {domain}: {domain_cls}Client) -> {cls}:
    """Fetch one {resource} by id."""
    return {domain}.{resource}.get(item_id)
'''

MCP = '''"""{domain} /{resource} FastMCP tools (honest annotations, ARCH-3).

The scaffolded tool is a read (`RO` annotations). For write tools use the `WRITE` /
`WRITE_IDEMPOTENT` / `DESTRUCTIVE` annotation sets from ``ycli.yandex.mcp`` plus the
`write` tag; ARCH-3 checks each tool's hints against the effect of the endpoint it sends.
"""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.{domain}.client import {domain_cls}Client
from ycli.yandex.{domain}.dependencies import RO, TAGS, {domain}_client
from ycli.yandex.{domain}.{resource}.models import {cls}

mcp = FastMCP("{domain}-{resource}")


@mcp.tool(
    name="{resource}_get",
    annotations={{**RO, "title": "Get {domain} {resource}"}},
    tags=TAGS,
    # The docstring below IS the client-facing description (the LLM\'s selector) —
    # required; do not pass description= to @mcp.tool.
    # The return type annotation IS the output schema (auto-derived by fastmcp) —
    # required; do not pass output_schema= to @mcp.tool.
)
def get(item_id: str, client: {domain_cls}Client = Depends({domain}_client)) -> {cls}:
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
        "domain_cls": _cls(domain),
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
    target = scaffold(args.domain, resource)

    cls = _cls(resource)
    print(f"scaffolded {target.relative_to(ROOT.parent.parent.parent)}")
    print(
        "next:\n"
        "  1. replace the FILL markers in endpoints.py/client.py/models.py with the real path,\n"
        "     operations and fields\n"
        f"  2. register the resource in {args.domain}/client.py `_wire` (import SERVICE from\n"
        f"     ycli.yandex.{args.domain}):\n"
        f"     self.{resource} = {cls}Client(session=self._connect(SERVICE.profile))\n"
        f"  3. mount the sub-app into {args.domain}/cli.py (app.add_typer) and the subserver into\n"
        f"     {args.domain}/mcp.py (mcp.mount), mirroring a sibling resource\n"
        "  4. give each new MCP tool its arguments in ARCH3_EFFECT_CASES "
        "(tests/test_architecture.py)\n"
        "  5. add tests under tests/yandex/ and run: uv run pytest && "
        "uv run python -m tests.snapshots --update"
    )


if __name__ == "__main__":
    main()
