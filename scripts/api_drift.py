#!/usr/bin/env python
"""Compare what ycli sends with what Yandex publishes, and the snapshot with the live API.

Two questions, one per mode:

* **Does ycli match the published API?** Every contract case (``tests/contract.py``) is replayed
  through the SDK against its canned replies, which yields the endpoints ycli really sends:
  method, path, query parameters and the response model. They are matched to the
  committed snapshots (``scripts/api_snapshot/``, see ``scripts/api_surface.py``). The result is
  the *gaps*: published operations ycli does not wrap, query parameters it cannot send, response
  fields its models drop. ``scripts/gen_coverage.py`` prints them in README. Offline.
* **Has the published API changed?** ``--live`` fetches the surfaces again and lists what
  differs from the snapshots; ``.github/workflows/api-drift.yml`` runs it weekly and keeps one
  issue open while they differ. ``--refresh`` rewrites the snapshots.

Usage::

    python scripts/api_drift.py                    # print the gaps (offline)
    python scripts/api_drift.py --live             # print what Yandex changed since the snapshot
    python scripts/api_drift.py --refresh          # fetch and rewrite the snapshots

Kill criterion: if Tracker ever publishes its OpenAPI document, the reference-page parser in
``api_surface`` goes; if Yandex stops publishing Wiki's and Forms', this whole check does.
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import re
import sys
import typing
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from pydantic import BaseModel, RootModel

ROOT = Path(__file__).resolve().parent.parent
# Run as a file, a script sees only its own directory: tests/ and scripts/ hang off the root.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import api_surface  # noqa: E402
from scripts.api_surface import Operation, shape  # noqa: E402
from tests.contract import Case, Sibling, load_cases  # noqa: E402
from tests.full_server import mcp  # noqa: E402
from tests.mock_api import MockAPI  # noqa: E402

from ycli.yandex.core.endpoint import ENDPOINT_EXTENSION, PAGED_EXTENSION  # noqa: E402
from ycli.yandex.registry import SERVICES  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Callable

    import httpx2

    from ycli.yandex.core.endpoint import Endpoint, Paged
    from ycli.yandex.core.pagination import Pagination

# Tracker's reference pages are prose and omit paging parameters: only what a page lists counts.
EXHAUSTIVE = frozenset(api_surface.OPENAPI_URLS)

# Published operations ycli deliberately does not wrap, each with its reason.
NOT_WRAPPED: dict[tuple[str, str, str], str] = {
    ("tracker", "GET", "/boards"): "`boards list` reads the paginated `GET /boards/_paginate`",
    ("tracker", "GET", "/users"): "`users list` reads the paginated `GET /users/_relative`",
}


@dataclass(frozen=True)
class Call:
    """One endpoint an SDK operation sends: what ycli can put on the wire and read back.

    ``response`` is the field names of the model the reply parses into (``None``: no model);
    ``request`` those of its typed body (``None``: no body, a free-form one, or one that takes
    any field).
    """

    operation: str
    method: str
    path: str
    query: frozenset[str]
    response: frozenset[str] | None
    template: str = ""
    request: frozenset[str] | None = None


@dataclass(frozen=True)
class Recorded:
    """One endpoint a contract case made the SDK send, with the requests that carried it.

    ``template`` is the endpoint's path with each segment that came from an argument of the
    SDK call named after it: ``/issues/DE-7`` sent by ``issues.get(key="DE-7")`` is
    ``/issues/{key}``.
    """

    case: Case
    endpoint: Endpoint
    pagination: Pagination | None
    requests: tuple[httpx2.Request, ...]
    template: str


@dataclass(frozen=True)
class Gap:
    """Where ycli and one published operation disagree; every tuple is sorted names."""

    published: Operation
    operations: tuple[str, ...]
    missing_query: tuple[str, ...] = ()
    unknown_query: tuple[str, ...] = ()
    missing_request: tuple[str, ...] = ()
    unknown_request: tuple[str, ...] = ()
    dropped_response: tuple[str, ...] = ()
    unknown_response: tuple[str, ...] = ()

    @property
    def empty(self) -> bool:
        """Whether ycli and the published operation agree."""
        return not any(getattr(self, kind) for kind in GAP_KINDS)


# The kinds of difference a gap holds, in the order they are reported.
GAP_KINDS = (
    "missing_query",
    "unknown_query",
    "missing_request",
    "unknown_request",
    "dropped_response",
    "unknown_response",
)


@dataclass(frozen=True)
class Drift:
    """One service: the published operations, and how ycli differs from them.

    ``bodies_published`` counts the wrapped operations whose published request body lists its
    fields; ``bodies_compared`` those of them ycli has a typed body for.
    """

    service: str
    published: tuple[Operation, ...]
    not_wrapped: tuple[Operation, ...]
    excluded: tuple[tuple[Operation, str], ...]
    unpublished: tuple[Call, ...]
    gaps: tuple[Gap, ...]
    bodies_published: int = 0
    bodies_compared: int = 0

    @property
    def wrapped(self) -> int:
        """How many published operations ycli wraps."""
        return len(self.published) - len(self.not_wrapped) - len(self.excluded)


def _models(annotation: Any) -> list[type[BaseModel]]:
    """The pydantic models behind a response type: a list, a union and a root model unwrap."""
    if isinstance(annotation, type) and issubclass(annotation, RootModel):
        return _models(annotation.model_fields["root"].annotation)
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return [annotation]
    return [model for argument in typing.get_args(annotation) for model in _models(argument)]


def _fields(response_type: Any) -> frozenset[str] | None:
    """The names a reply parsed as ``response_type`` keeps (``None``: it is no model)."""
    models = _models(response_type)
    if not models:
        return None
    return frozenset(
        field.alias or name for model in models for name, field in model.model_fields.items()
    )


def _template(case: Case, operation: Callable[..., Any], path: str) -> str:
    """``path`` with the segments that are arguments of ``operation`` replaced by their names."""
    bound = inspect.signature(operation).bind(*case.args, **case.kwargs)
    names: dict[str, list[str]] = {}
    for name, value in bound.arguments.items():
        if isinstance(value, str | int) and not isinstance(value, bool):
            names.setdefault(quote(str(value), safe=""), []).append(name)
    parts = []
    for part in path.strip("/").split("/"):
        owners = names.get(part, [])
        if len(owners) > 1:
            # docs/conventions/testing.md: every parameter of a case has its own value.
            raise SystemExit(f"api_drift: {case.id}: {owners} share the value {part!r}")
        parts.append(f"{{{owners[0]}}}" if owners else part)
    return "/" + "/".join(parts)


def replay(case: Case) -> list[Recorded]:
    """Run ``case`` through the SDK against its canned replies and report what it sent."""
    domain, resource, method = case.operation.split(".")
    service = next(service for service in SERVICES if service.name == domain)
    base_url = service.profile.base_url.rstrip("/")
    api = MockAPI()
    for sent, reply in case.exchanges:
        api.add(
            sent.method,
            f"{base_url}/{sent.path}",
            json=reply.json,
            status=reply.status,
            headers=dict(reply.headers),
            content=reply.content,
        )
    announced: list[httpx2.Request] = []
    client_class = service.client_class()
    # The session calls the hook once per endpoint, with the request that carries it.
    with client_class(
        oauth_token="t",
        organization_id="o",
        transport=api.transport(),
        before_send=lambda _effect, request: announced.append(request),
    ) as client:
        operation = getattr(getattr(client, resource), method)
        args = [getattr(client, a.resource) if isinstance(a, Sibling) else a for a in case.args]
        operation(*args, **case.kwargs)
    found = []
    for first in announced:
        endpoint: Endpoint = first.extensions[ENDPOINT_EXTENSION]
        paged: Paged | None = first.extensions.get(PAGED_EXTENSION)
        pagination = paged.pagination if paged else None
        url = f"{base_url}/{endpoint.path.strip('/')}"
        requests = tuple(
            request
            for request in api.calls
            if request.method == endpoint.method
            and str(request.url.copy_with(query=None)).rstrip("/") == url
        )
        template = _template(case, operation, endpoint.path)
        found.append(Recorded(case, endpoint, pagination, requests, template))
    return found


@cache
def _mcp_tools() -> dict[str, Any]:
    """Every MCP tool by name; their ``body`` parameters are ycli's typed request bodies."""
    return {tool.name: tool for tool in asyncio.run(mcp.list_tools())}


def typed_body(found: Recorded) -> dict[str, Any] | None:
    """The schema of the body ``found`` sends, when its MCP tool declares a body model.

    The SDK itself takes a free-form mapping, so the MCP tool's ``body`` parameter is the one
    typed description of a request body; it stands for the request only when the operation
    sends nothing else. ``$defs`` rides along for the references to resolve.
    """
    tool = _mcp_tools().get(found.case.mcp[0]) if found.case.mcp else None
    body = (tool.parameters.get("properties", {}) if tool else {}).get("body")
    if tool is None or body is None or len(replay(found.case)) != 1:
        return None
    return {**body, "$defs": tool.parameters.get("$defs", {})}


@cache
def recorded() -> tuple[Recorded, ...]:
    """Every endpoint every SDK operation sends, from replaying the contract cases once."""
    return tuple(found for case in load_cases() for found in replay(case))


def _call(found: Recorded) -> Call:
    """What ``found`` says ycli can put on the wire and read back."""
    # A pager's parameters count even when the case's listing fits one page.
    pager = vars(found.pagination) if found.pagination else {}
    paging = [value for name, value in pager.items() if name.endswith("_param")]
    sent_params = [request.url.params for request in found.requests]
    return Call(
        operation=found.case.operation,
        method=found.endpoint.method,
        path="/" + found.endpoint.path.strip("/"),
        query=frozenset(found.endpoint.params).union(paging, *sent_params),
        # A listing's envelope is read by the pager; callers only ever see its items.
        response=None if found.pagination else _fields(found.endpoint.response_type),
        template=found.template,
        request=_body_fields(typed_body(found)),
    )


def _body_fields(schema: dict[str, Any] | None) -> frozenset[str] | None:
    """The top-level names a typed body can carry; ``None`` when it is open to any field."""
    if schema is None or _resolved_body(schema).get("additionalProperties"):
        return None
    return frozenset(api_surface.field_names(schema, schema))


def _resolved_body(schema: dict[str, Any]) -> dict[str, Any]:
    """``schema`` with a top-level reference into its own ``$defs`` followed."""
    while "$ref" in schema:
        schema = {**schema["$defs"][schema["$ref"].rsplit("/", 1)[1]], "$defs": schema["$defs"]}
    return schema


def calls() -> list[Call]:
    """Every endpoint every SDK operation sends, as the names the comparison needs."""
    return [_call(found) for found in recorded()]


def published_for(published: list[Operation], method: str, path: str) -> Operation | None:
    """The ``published`` operation a concrete request stands for, the most literal one.

    ``/pages/descendants`` is both itself and an instance of ``/pages/{idx}``.
    """
    candidates = [
        operation
        for operation in published
        if operation.method == method and _matcher(operation).fullmatch(path)
    ]
    return max(candidates, key=_literals) if candidates else None


@cache
def _matcher(operation: Operation) -> re.Pattern[str]:
    """A pattern for the concrete paths ``operation``'s template stands for."""
    parts = re.split(r"\{\}", shape(operation.path))
    return re.compile("[^/]+".join(map(re.escape, parts)))


def _literals(operation: Operation) -> int:
    return len([part for part in shape(operation.path).split("/") if part and "{}" not in part])


def compare(service: str, published: list[Operation], sent: list[Call]) -> Drift:
    """How the ``sent`` calls of ``service`` differ from its ``published`` operations."""
    reached: dict[tuple[str, str], list[Call]] = {}
    unpublished = []
    for call in sent:
        operation = published_for(published, call.method, call.path)
        if operation is None:
            unpublished.append(call)
        else:
            reached.setdefault(operation.key, []).append(call)

    exhaustive = service in EXHAUSTIVE
    gaps = []
    bodies_published = bodies_compared = 0
    for operation in published:
        found = reached.get(operation.key)
        if not found:
            continue
        query = frozenset().union(*(call.query for call in found))
        bodies = [call.request for call in found if call.request is not None]
        body = frozenset().union(*bodies)
        compare_request = bool(exhaustive and bodies and operation.request)
        bodies_published += bool(exhaustive and operation.request)
        bodies_compared += compare_request
        models = [call.response for call in found if call.response is not None]
        fields = frozenset().union(*models)
        compare_response = bool(models and operation.response)
        gap = Gap(
            published=operation,
            operations=tuple(sorted({call.operation for call in found})),
            missing_query=tuple(sorted(set(operation.query) - query)),
            unknown_query=tuple(sorted(query - set(operation.query))) if exhaustive else (),
            missing_request=tuple(sorted(set(operation.request) - body)) if compare_request else (),
            unknown_request=tuple(sorted(body - set(operation.request))) if compare_request else (),
            dropped_response=tuple(sorted(set(operation.response) - fields))
            if compare_response
            else (),
            unknown_response=tuple(sorted(fields - set(operation.response)))
            if compare_response
            else (),
        )
        if not gap.empty:
            gaps.append(gap)

    missing = [operation for operation in published if operation.key not in reached]
    reasons = {key[1:]: reason for key, reason in NOT_WRAPPED.items() if key[0] == service}
    return Drift(
        service=service,
        published=tuple(published),
        not_wrapped=tuple(operation for operation in missing if operation.key not in reasons),
        excluded=tuple(
            (operation, reasons[operation.key]) for operation in missing if operation.key in reasons
        ),
        unpublished=tuple(_unique(unpublished)),
        gaps=tuple(gaps),
        bodies_published=bodies_published,
        bodies_compared=bodies_compared,
    )


def _unique(found: list[Call]) -> list[Call]:
    """One call per operation and path template, in a stable order."""
    seen = {(call.operation, call.method, call.template or call.path): call for call in found}
    return [seen[key] for key in sorted(seen)]


def drifts() -> list[Drift]:
    """Every service's gaps against its committed snapshot (offline)."""
    sent = calls()
    return [
        compare(
            service,
            api_surface.load(service),
            [call for call in sent if call.operation.startswith(f"{service}.")],
        )
        for service in api_surface.SERVICES
    ]


def changes(snapshot: list[Operation], live: list[Operation]) -> list[str]:
    """Markdown lines saying how ``live`` differs from ``snapshot`` (empty: it does not).

    Examples:
        >>> old = [Operation("GET", "/me", query=("fields",))]
        >>> changes(old, [Operation("GET", "/me"), Operation("POST", "/me")])
        ['- added `POST /me`', '- `GET /me`: query -`fields`']
    """
    before = {operation.key: operation for operation in snapshot}
    after = {operation.key: operation for operation in live}
    lines = [
        f"- added `{after[key].method} {after[key].path}`"
        for key in sorted(after.keys() - before.keys())
    ]
    lines += [
        f"- removed `{before[key].method} {before[key].path}`"
        for key in sorted(before.keys() - after.keys())
    ]
    for key in sorted(before.keys() & after.keys()):
        differences = []
        for part in ("query", "request", "response"):
            old, new = set(getattr(before[key], part)), set(getattr(after[key], part))
            signed = [f"+`{name}`" for name in sorted(new - old)]
            signed += [f"-`{name}`" for name in sorted(old - new)]
            if signed:
                differences.append(f"{part} {' '.join(signed)}")
        if differences:
            lines.append(f"- `{before[key].method} {before[key].path}`: {'; '.join(differences)}")
    return lines


def gaps_text(found: list[Drift]) -> str:
    """The gaps as plain text, for a terminal."""
    lines = []
    for drift in found:
        lines.append(
            f"{drift.service}: {drift.wrapped} of {len(drift.published)} published operations "
            f"wrapped, {len(drift.gaps)} differ"
        )
        lines += [f"  not wrapped: {op.method} {op.path}" for op in drift.not_wrapped]
        lines += [
            f"  not published: {call.method} {call.path} ({call.operation})"
            for call in drift.unpublished
        ]
        for gap in drift.gaps:
            lines.append(
                f"  {gap.published.method} {gap.published.path} ({', '.join(gap.operations)})"
            )
            lines += [
                f"    {kind}: {', '.join(getattr(gap, kind))}"
                for kind in GAP_KINDS
                if getattr(gap, kind)
            ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point; see the module docstring for the modes."""
    parser = argparse.ArgumentParser(description="Compare ycli with the API Yandex publishes.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--live", action="store_true", help="print how the live API differs from the snapshots"
    )
    group.add_argument("--refresh", action="store_true", help="fetch and rewrite the snapshots")
    args = parser.parse_args(argv)

    if not (args.live or args.refresh):
        print(gaps_text(drifts()))
        return 0
    report = []
    for service in api_surface.SERVICES:
        live = api_surface.fetch(service)
        if args.refresh:
            path = api_surface.SNAPSHOTS / f"{service}.json"
            path.write_text(api_surface.dump(live), encoding="utf-8")
        elif lines := changes(api_surface.load(service), live):
            report += [f"### {service.capitalize()}", "", *lines, ""]
    print("\n".join(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
