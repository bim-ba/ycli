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
import inspect
import re
import sys
import typing
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import PydanticUserError, RootModel, TypeAdapter

ROOT = Path(__file__).resolve().parent.parent
# Run as a file, a script sees only its own directory: tests/ and scripts/ hang off the root.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import api_drift, api_surface  # noqa: E402

from ycli.yandex.core.profile import ORG_HEADER  # noqa: E402
from ycli.yandex.registry import SERVICES  # noqa: E402

if TYPE_CHECKING:
    from pydantic.json_schema import JsonSchemaMode
    from scripts.api_drift import Recorded

SCHEMAS = "#/components/schemas/"
TITLES = {
    "tracker": "Yandex Tracker",
    "wiki": "Yandex Wiki",
    "forms": "Yandex Forms",
    "datalens": "Yandex DataLens",
}
_PLACEHOLDER = re.compile(r"\{([^}]*)\}|<([^>]*)>")
_JSON = "application/json"
_QUALIFIED = re.compile(r"ycli__yandex__[a-z]+__(\w+?)__models__(\w+)")
_GENERIC = re.compile(r"(CursorPage)_(\w+)_")


def _readable(name: str) -> str:
    """A component name people can read, for a name pydantic had to make unique.

    Two resources of one service may each define ``Comment``, which pydantic names by their
    full module path; a generic class is named with its parameter in underscores.

    Examples:
        >>> _readable("ycli__yandex__tracker__import___models__Comment")
        'ImportComment'
        >>> _readable("CursorPage_PageRef_")
        'PageRefPage'
        >>> _readable("PageDetails")
        'PageDetails'
    """
    if (generic := _GENERIC.fullmatch(name)) is not None:
        container, item = generic.groups()
        return _readable(item) + container.removeprefix("Cursor")
    qualified = _QUALIFIED.fullmatch(name)
    if qualified is None:
        return name
    resource, model = qualified.groups()
    return "".join(part.capitalize() for part in resource.split("_")) + model


def _renamed(node: Any, names: dict[str, str]) -> Any:
    """``node`` with every component reference pointed at its readable name."""
    if isinstance(node, dict):
        return {
            key: SCHEMAS + names[value.removeprefix(SCHEMAS)]
            if key == "$ref"
            else _renamed(value, names)
            for key, value in node.items()
        }
    return [_renamed(item, names) for item in node] if isinstance(node, list) else node


def _unwrapped(annotation: Any) -> Any:
    """What a root model wraps: a document says "an array of boards", not ``ItemList[Board]``."""
    if isinstance(annotation, type) and issubclass(annotation, RootModel):
        return annotation.model_fields["root"].annotation
    return annotation


def _schemas(found: list[Recorded], schemas: dict[str, Any]) -> dict[tuple[str, str], Any]:
    """The schema of every response type and typed body among ``found``; models go to ``schemas``.

    Keys are ``("response" | "body", case id + template)``. One pydantic pass over all of them,
    so two models that share a class name get distinct component names.
    """
    typed: dict[tuple[str, str], Any] = {}
    for recording in found:
        key = recording.case.id + recording.template
        if recording.endpoint.response_type not in (None, bytes):
            typed["response", key] = _unwrapped(recording.endpoint.response_type)
        if (body := api_drift.typed_body(recording)) is not None:
            typed["body", key] = _unwrapped(body)
    inputs: list[tuple[tuple[str, str], JsonSchemaMode, TypeAdapter[Any]]] = [
        (key, "validation", TypeAdapter(annotation)) for key, annotation in typed.items()
    ]
    by_key, shared = TypeAdapter.json_schemas(
        inputs, by_alias=True, ref_template=SCHEMAS + "{model}"
    )
    definitions = shared.get("$defs", {})
    names = {name: _readable(name) for name in definitions}
    if len(set(names.values())) != len(names):
        raise ValueError("two models of one resource share a class name")
    schemas.update({names[name]: _renamed(schema, names) for name, schema in definitions.items()})
    return {key: _renamed(schema, names) for (key, _mode), schema in by_key.items()}


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


def _request_body(
    group: list[Recorded], found: dict[tuple[str, str], Any]
) -> dict[str, Any] | None:
    """The request body of an operation, typed when its MCP tool declares a body model."""
    requests = [request for recording in group for request in recording.requests if request.content]
    if not requests:
        return None
    kind = requests[0].headers.get("Content-Type", "application/octet-stream").split(";")[0]
    if kind != _JSON:
        return {"content": {kind: {}}}
    primary = _primary(group)
    schema = found.get(("body", primary.case.id + primary.template))
    if schema is None:
        return {"content": {_JSON: {}}, "x-ycli-body": "untyped"}
    return {"content": {_JSON: {"schema": schema}}, "x-ycli-body": "typed"}


def _response(recording: Recorded, found: dict[tuple[str, str], Any]) -> dict[str, Any]:
    """The success response: the schema of the type ycli parses the reply into."""
    response_type = recording.endpoint.response_type
    if response_type is None:
        return {"description": "ycli reads no body."}
    if response_type is bytes:
        return {"description": "Raw bytes.", "content": {"application/octet-stream": {}}}
    schema = found["response", recording.case.id + recording.template]
    return {"description": "Parsed by ycli.", "content": {_JSON: {"schema": schema}}}


_BY_VALUE: dict[type, str] = {
    bool: "boolean",
    int: "integer",
    float: "number",
    str: "string",
    list: "array",
}


def _wire_schema(annotation: Any) -> dict[str, Any]:
    """The schema of a parameter annotated ``annotation`` as it goes on the wire.

    ``None`` in a union means "not sent", so it is dropped; a type whose schema needs shared
    definitions (an enum class) is left untyped rather than half-described.
    """
    options = [option for option in typing.get_args(annotation) if option is not type(None)]
    if type(None) in typing.get_args(annotation) and len(options) == 1:
        annotation = options[0]
    if annotation is Any or annotation is inspect.Parameter.empty:
        return {}
    try:
        schema = TypeAdapter(annotation).json_schema(mode="serialization")
    except PydanticUserError:
        return {}
    return {} if "$defs" in schema else schema


def _query_schema(name: str, group: list[Recorded]) -> dict[str, Any]:
    """The type of query parameter ``name``: the SDK argument it carries, else its value's.

    A parameter is tied to an argument when exactly one argument of the call has its value.
    """
    for recording in sorted(group, key=lambda recording: recording.case.id):
        value = recording.endpoint.params.get(name)
        if value is None:
            continue
        owners = [
            argument
            for argument, given in recording.arguments.items()
            if type(given) is type(value) and given == value
        ]
        if len(owners) == 1 and (schema := _wire_schema(recording.hints.get(owners[0], Any))):
            return schema
        return {"type": _BY_VALUE[type(value)]} if type(value) in _BY_VALUE else {}
    return {}


def _path_schema(name: str, group: list[Recorded]) -> dict[str, Any]:
    """The type of path parameter ``name``: its SDK argument's, or a string for a borrowed name."""
    hints = [recording.hints[name] for recording in group if name in recording.hints]
    return (_wire_schema(hints[0]) if hints else {}) or {"type": "string"}


def _operation(
    group: list[Recorded], path: str, found: dict[tuple[str, str], Any]
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
        "x-ycli-effect": str(primary.endpoint.effect),
    }
    if primary.pagination is not None:
        operation["x-ycli-pagination"] = type(primary.pagination).__name__
    parameters = [
        {"name": name, "in": "path", "required": True, "schema": _path_schema(name, group)}
        for name in re.findall(r"\{(\w+)\}", path)
    ]
    parameters += [
        {"name": name, "in": "query", "schema": _query_schema(name, group)} for name in query
    ]
    if parameters:
        operation["parameters"] = parameters
    if (body := _request_body(group, found)) is not None:
        operation["requestBody"] = body
    operation["responses"] = {"200": _response(primary, found)}
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
    found = _schemas([recording for group in groups.values() for recording in group], schemas)
    paths: dict[str, dict[str, Any]] = defaultdict(dict)
    operation_ids: dict[str, str] = {}
    for (path, method), group in sorted(groups.items()):
        operation = _operation(group, path, found)
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
    try:
        documents = {service: dump(service) for service in api_surface.SERVICES}
    except ValueError as error:
        raise SystemExit(f"gen_openapi: {error}") from error
    for service, text in documents.items():
        (args.directory / f"{service}.yaml").write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
