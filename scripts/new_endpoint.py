"""Scaffold a new Yandex resource that satisfies the architecture by construction.

    python scripts/new_endpoint.py tracker macros

Creates src/ycli/yandex/tracker/macros/{__init__,client,cli,mcp,models}.py wired to the
domain deps, the render output path, and read-only MCP annotations. Fill the marked spots
with the real endpoint; the structure already satisfies ARCH-1..4 and import-linter.
"""
from __future__ import annotations

import argparse
from pathlib import Path

DOMAINS = ("tracker", "wiki", "forms")
ROOT = Path(__file__).resolve().parent.parent / "src" / "ycli" / "yandex"

INIT = '"""Yandex {domain} /{resource} resource (client · cli · mcp · models)."""\n'

MODELS = '''"""Pydantic models for {domain} /{resource}."""
from __future__ import annotations

from pydantic import BaseModel


class {cls}(BaseModel):
    """One {resource} record. FILL: add the real fields."""

    id: str = ""
'''

CLIENT = '''"""{domain} /{resource} SDK calls (uplink). The only place HTTP happens for this resource."""
from __future__ import annotations

from uplink import Consumer, get, returns

from ycli.yandex.{domain}.{resource}.models import {cls}


class {cls}Client(Consumer):
    """Read calls for /{resource}."""

    @returns.json
    @get("FILL/{resource}/{{item_id}}")  # FILL: real path
    def get(self, item_id: str) -> {cls}:  # type: ignore[empty-body]
        """Fetch one {resource} by id."""
'''

CLI = '''"""{domain} /{resource} Typer commands. Output via ycli.output.render."""
from __future__ import annotations

import typer

from ycli.output import render
from ycli.yandex.{domain}._clideps import {domain}_client

app = typer.Typer(name="{resource}", help="{domain} /{resource}.", no_args_is_help=True)


@app.command()
def get(ctx: typer.Context, item_id: str) -> None:
    """Fetch one {resource} by id."""
    render({domain}_client(ctx).{resource}.get(item_id))
'''

MCP = '''"""{domain} /{resource} FastMCP tools (read-only)."""
from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.{domain}._deps import RO, TAGS, {domain}_client
from ycli.yandex.{domain}.client import {domain_cls}Client
from ycli.yandex.{domain}.{resource}.models import {cls}

mcp = FastMCP("{domain}-{resource}")


@mcp.tool(name="{resource}_get", annotations=RO, tags=TAGS)
def get(item_id: str, client: {domain_cls}Client = Depends({domain}_client)) -> {cls}:
    """Fetch one {resource} by id."""
    return client.{resource}.get(item_id)
'''


def _cls(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new Yandex resource.")
    parser.add_argument("domain", choices=DOMAINS)
    parser.add_argument("resource", help="resource name, e.g. macros")
    args = parser.parse_args()

    resource = args.resource.replace("-", "_")
    target = ROOT / args.domain / resource
    if target.exists():
        raise SystemExit(f"{target} already exists")
    target.mkdir(parents=True)

    ctx = {
        "domain": args.domain,
        "resource": resource,
        "cls": _cls(resource),
        "domain_cls": _cls(args.domain),
    }
    for filename, template in (
        ("__init__.py", INIT),
        ("models.py", MODELS),
        ("client.py", CLIENT),
        ("cli.py", CLI),
        ("mcp.py", MCP),
    ):
        (target / filename).write_text(template.format(**ctx), encoding="utf-8")

    print(f"scaffolded {target.relative_to(ROOT.parent.parent.parent)}")
    print("next: replace the FILL markers, wire the sub-app/subserver into the domain "
          "cli.py + mcp.py, and add tests under tests/yandex/.")


if __name__ == "__main__":
    main()
