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

from ycli.models import APIModel


class {cls}(APIModel):
    """One {resource} record. FILL: add the real fields."""

    id: str = ""
'''

CLIENT = '''"""{domain} /{resource} SDK calls (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly. Subclasses the domain base for session + base_url DI.
"""
import uplink

from ycli.yandex.{domain}._base import {domain_cls}Resource
from ycli.yandex.{domain}.{resource}.models import {cls}


class {cls}Client({domain_cls}Resource):
    """Declarative HTTP for /{resource} (read-only to start)."""

    @uplink.returns.json()
    @uplink.get("FILL/{resource}/{{item_id}}")  # FILL: real path
    def get(self, item_id: uplink.Path) -> {cls}:  # type: ignore[empty-body]
        """GET one {resource} by id."""
'''

CLI = '''"""{domain} /{resource} Typer commands."""
from __future__ import annotations

import typer

from ycli.context import AppContext
from ycli.output import Serializer

app = typer.Typer(name="{resource}", help="{domain} /{resource}.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(ctx: typer.Context, item_id: str) -> None:
    """Fetch one {resource} by id."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.{domain}.{resource}.get(item_id), app_ctx.strategy, app_ctx.console)
'''

MCP = '''"""{domain} /{resource} FastMCP tools (read-only)."""
from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex._mcp import RO
from ycli.yandex.{domain}._deps import TAGS, {domain}_client
from ycli.yandex.{domain}.client import {domain_cls}Client
from ycli.yandex.{domain}.{resource}.models import {cls}

mcp = FastMCP("{domain}-{resource}")


@mcp.tool(name="{resource}_get", annotations={{**RO, "title": "Get {domain} {resource}"}}, tags=TAGS)
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

    cls = ctx["cls"]
    print(f"scaffolded {target.relative_to(ROOT.parent.parent.parent)}")
    print(
        "next:\n"
        "  1. replace the FILL markers in client.py/models.py with the real path + fields\n"
        f"  2. register the resource on the domain client: in {args.domain}/client.py __init__ add\n"
        f"     self.{resource} = {cls}Client(session=session)\n"
        f"  3. mount the sub-app into {args.domain}/cli.py (app.add_typer) and the subserver into\n"
        f"     {args.domain}/mcp.py (mcp.mount), mirroring a sibling resource\n"
        "  4. add tests under tests/yandex/ and run: uv run pytest && "
        "uv run python -m tests.snapshots --update"
    )


if __name__ == "__main__":
    main()
