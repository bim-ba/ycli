#!/usr/bin/env python
"""Generate an OpenAPI 3.1 document per service from what ycli itself sends and parses.

Yandex publishes a specification for Wiki and Forms and none for Tracker. These documents
describe the API *as ycli wraps it*, in one format for all three services: the paths, methods
and query parameters the contract cases make the SDK send (``scripts/api_drift.py``), the
schemas of the pydantic models the replies parse into, and, where an MCP tool takes a typed
body, that body's schema. They are derived, unofficial and only as complete as ycli is.

ycli's own facts ride in extensions: ``x-ycli-operations`` (the SDK operations that send the
request), ``x-ycli-effect`` (ARCH-3), ``x-ycli-pagination`` and ``x-ycli-body`` (``typed``: the
schema is the MCP tool's body model; ``untyped``: the SDK takes a free-form mapping).

The documents are about a megabyte and change with every model, so they are not committed:
the docs workflow writes them into the site, next to the reference.

Usage::

    uv run scripts/gen_openapi.py site/openapi    # write site/openapi/<service>.yaml

Kill criterion: if nothing reads these documents (no spec-to-spec comparison, no refract
import, no reader of the site) within two milestones, delete the script and the files.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from collections import defaultdict
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import TypeAdapter

ROOT = Path(__file__).resolve().parent.parent
# Run as a file, a script sees only its own directory: tests/ and scripts/ hang off the root.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import api_drift, api_surface  # noqa: E402
from tests.full_server import mcp  # noqa: E402

from ycli.yandex.core.profile import ORG_HEADER  # noqa: E402
from ycli.yandex.registry import SERVICES  # noqa: E402

if TYPE_CHECKING:
    from pydantic.json_schema import JsonSchemaMode
    from scripts.api_drift import Recorded

SCHEMAS = "#/components/schemas/"
TITLES = {"tracker": "Yandex Tracker", "wiki": "Yandex Wiki", "forms": "Yandex Forms"}
_PLACEHOLDER = re.compile(r"\{([^}]*)\}|<([^>]*)>")
_JSON = "application/json"


@cache
def _mcp_tools() -> dict[str, Any]:
    """Every MCP tool by name; their ``body`` parameters are ycli's typed request bodies."""
    return {tool.name: tool for tool in asyncio.run(mcp.list_tools())}


def _hoisted(schema: dict[str, Any], schemas: dict[str, Any]) -> dict[str, Any]:
    """``schema`` with its ``$defs`` moved into ``schemas`` and its references pointed there.

    A definition whose name is taken by a different schema (a request model named like a
    response model) gets a numbered name.
    """
    renamed: dict[str, str] = {}

    def moved(node: Any) -> Any:
        if isinstance(node, dict):
            return {
                key: SCHEMAS + renamed.get(name := value.rsplit("/", 1)[1], name)
                if key == "$ref"
                else moved(value)
                for key, value in node.items()
                if key != "$defs"
            }
        return [moved(item) for item in node] if isinstance(node, list) else node

    definitions = schema.get("$defs", {})
    for name, definition in definitions.items():
        candidates = (name, *(f"{name}{number}" for number in range(2, 100)))
        mine = moved(definition)
        renamed[name] = next(c for c in candidates if schemas.get(c, mine) == mine)
    for name, definition in definitions.items():
        schemas[renamed[name]] = moved(definition)
    return moved(schema)


def _response_schemas(found: list[Recorded], schemas: dict[str, Any]) -> dict[str, Any]:
    """The schema of every response type among ``found``, by case id; models go to ``schemas``.

    One pydantic pass over all of them, so two models that share a class name get distinct
    component names.
    """
    typed = {
        recording.case.id + recording.template: recording.endpoint.response_type
        for recording in found
        if recording.endpoint.response_type not in (None, bytes)
    }
    inputs: list[tuple[str, JsonSchemaMode, TypeAdapter[Any]]] = [
        (key, "validation", TypeAdapter(response_type)) for key, response_type in typed.items()
    ]
    by_key, shared = TypeAdapter.json_schemas(
        inputs,
        by_alias=True,
        ref_template=SCHEMAS + "{model}",
    )
    schemas.update(shared.get("$defs", {}))
    return {key: schema for (key, _mode), schema in by_key.items()}


def _path(found: Recorded, published: list[api_surface.Operation]) -> str:
    """The request's path template, borrowing a name for a segment no argument supplied.

    An id taken from an earlier reply (an upload session) is a literal in the case; the
    operation Yandex publishes for the same request names it.
    """
    match = api_drift.published_for(
        published, found.endpoint.method, "/" + found.endpoint.path.strip("/")
    )
    parts = found.template.strip("/").split("/")
    if match is not None:
        theirs = match.path.strip("/").split("/")
        for index, (ours, published_part) in enumerate(zip(parts, theirs, strict=True)):
            name = _PLACEHOLDER.fullmatch(published_part)
            if name and not ours.startswith("{"):
                parts[index] = "{" + re.sub(r"\W", "_", name.group(1) or name.group(2)) + "}"
    return "/" + "/".join(parts)


def _primary(group: list[Recorded]) -> Recorded:
    """The recording whose SDK operation the request belongs to: one that sends nothing else."""
    alone = defaultdict(int)
    for found in api_drift.recorded():
        alone[found.case.id] += 1
    return min(group, key=lambda found: (alone[found.case.id], found.case.operation))


def _request_body(group: list[Recorded], schemas: dict[str, Any]) -> dict[str, Any] | None:
    """The request body of an operation, typed when its MCP tool declares a body model."""
    requests = [request for found in group for request in found.requests if request.content]
    if not requests:
        return None
    kind = requests[0].headers.get("Content-Type", "application/octet-stream").split(";")[0]
    if kind != _JSON:
        return {"content": {kind: {}}}
    primary = _primary(group)
    tool = _mcp_tools().get(primary.case.mcp[0]) if primary.case.mcp else None
    body = (tool.parameters.get("properties", {}) if tool else {}).get("body")
    if tool is None or body is None or len(api_drift.replay(primary.case)) != 1:
        return {"content": {_JSON: {}}, "x-ycli-body": "untyped"}
    schema = _hoisted({**body, "$defs": tool.parameters.get("$defs", {})}, schemas)
    return {"content": {_JSON: {"schema": schema}}, "x-ycli-body": "typed"}


def _response(found: Recorded, responses: dict[str, Any]) -> dict[str, Any]:
    """The success response: the schema of the type ycli parses the reply into."""
    response_type = found.endpoint.response_type
    if response_type is None:
        return {"description": "ycli reads no body."}
    if response_type is bytes:
        return {"description": "Raw bytes.", "content": {"application/octet-stream": {}}}
    schema = responses[found.case.id + found.template]
    return {"description": "Parsed by ycli.", "content": {_JSON: {"schema": schema}}}


def _operation(
    group: list[Recorded], path: str, schemas: dict[str, Any], responses: dict[str, Any]
) -> dict[str, Any]:
    """One OpenAPI operation from every recording of the same method and path."""
    primary = _primary(group)
    _, resource, method = primary.case.operation.split(".")
    calls = [api_drift._call(found) for found in group]
    query = sorted(frozenset().union(*(call.query for call in calls)))
    operation: dict[str, Any] = {
        "operationId": f"{resource}_{method}",
        "tags": [resource],
        "x-ycli-operations": sorted({call.operation.split(".", 1)[1] for call in calls}),
        "x-ycli-effect": primary.endpoint.effect,
    }
    if primary.pagination is not None:
        operation["x-ycli-pagination"] = type(primary.pagination).__name__
    parameters = [
        {"name": name, "in": "path", "required": True, "schema": {"type": "string"}}
        for name in re.findall(r"\{(\w+)\}", path)
    ]
    parameters += [{"name": name, "in": "query", "schema": {}} for name in query]
    if parameters:
        operation["parameters"] = parameters
    if (body := _request_body(group, schemas)) is not None:
        operation["requestBody"] = body
    operation["responses"] = {"200": _response(primary, responses)}
    return operation


def document(service: str) -> dict[str, Any]:
    """The OpenAPI document of ``service`` as ycli wraps it."""
    profile = next(found for found in SERVICES if found.name == service).profile
    published = api_surface.load(service)
    groups: dict[tuple[str, str], list[Recorded]] = defaultdict(list)
    for found in api_drift.recorded():
        if found.case.domain == service:
            groups[(_path(found, published), found.endpoint.method)].append(found)

    schemas: dict[str, Any] = {}
    responses = _response_schemas([found for group in groups.values() for found in group], schemas)
    paths: dict[str, dict[str, Any]] = defaultdict(dict)
    operation_ids: dict[str, str] = {}
    for (path, method), group in sorted(groups.items()):
        operation = _operation(group, path, schemas, responses)
        # One operation may send two requests (a listing and its paged twin): keep ids unique.
        if operation["operationId"] in operation_ids:
            suffix = re.sub(r"\W+", "_", path).strip("_")
            operation["operationId"] = f"{operation['operationId']}_{method.lower()}_{suffix}"
        operation_ids[operation["operationId"]] = path
        paths[path][method.lower()] = operation

    title = TITLES[service]
    return {
        "openapi": "3.1.0",
        "info": {
            "title": f"{title} API as wrapped by ycli (unofficial)",
            "version": profile.base_url.rstrip("/").rsplit("/", 1)[1],
            "description": (
                f"Derived from ycli's own code, not published by Yandex: the requests ycli sends "
                f"to {title} and the models it parses the replies into. It is only as complete "
                'as ycli; README\'s "Against the published API" lists where the two differ. '
                "Generated by scripts/gen_openapi.py; do not edit by hand."
            ),
        },
        "servers": [{"url": profile.base_url}],
        "security": [{"oauth": [], "organization": []}],
        "paths": dict(paths),
        "components": {
            "securitySchemes": {
                "oauth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "Authorization",
                    "description": "`OAuth <token>`",
                },
                "organization": {"type": "apiKey", "in": "header", "name": ORG_HEADER},
            },
            "schemas": dict(sorted(schemas.items())),
        },
    }


def dump(service: str) -> str:
    """The YAML text of ``service``'s document."""
    return yaml.safe_dump(document(service), sort_keys=False, allow_unicode=True, width=100)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: write ``<directory>/<service>.yaml`` for every service."""
    parser = argparse.ArgumentParser(description="Generate OpenAPI documents from ycli.")
    parser.add_argument("directory", type=Path, help="where to write <service>.yaml")
    args = parser.parse_args(argv)
    args.directory.mkdir(parents=True, exist_ok=True)
    for service in api_surface.SERVICES:
        (args.directory / f"{service}.yaml").write_text(dump(service), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
