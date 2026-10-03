"""The API Yandex publishes for each service, reduced to the facts ycli compares itself with.

Wiki and Forms serve an OpenAPI document without authorization. Tracker's is closed (401), so
its operations are read from the API reference: ``llms.txt`` lists the pages and each page's
Markdown source states its request (``GET /v3/issues/{issue_id}``) and its query parameters.

A surface is a list of operations: HTTP method, path template, query parameter names and the
top-level field names of the request and response bodies. Names only, never Yandex's prose, so
the snapshots under ``scripts/api_snapshot/`` can be committed. ``scripts/api_drift.py`` compares
them with what ycli sends and with a fresh fetch.

Examples:
    >>> shape("/v1/pages/{idx}/grids/")
    '/pages/{}/grids'
    >>> openapi_operations({"paths": {"/v1/me": {"get": {}}}})
    [Operation(method='GET', path='/me', query=(), request=(), response=(), page='')]
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx2
import stamina

if TYPE_CHECKING:
    from collections.abc import Iterable

SNAPSHOTS = Path(__file__).resolve().parent / "api_snapshot"
OPENAPI_URLS = {
    "wiki": "https://api.wiki.yandex.net/v1/openapi.json",
    "forms": "https://api.forms.yandex.net/v1/openapi.json",
}
TRACKER_INDEX = "https://yandex.ru/support/tracker/en/llms.txt"
TRACKER_PAGE = re.compile(r"https://yandex\.ru/support/tracker/en/(api/[^)\s]+)\.md")
SERVICES = ("tracker", *OPENAPI_URLS)

USER_AGENT = "ycli-api-drift/1.0 (+https://github.com/bim-ba/ycli)"
REQUEST_TIMEOUT_SECONDS = 30
CONNECT_RETRIES = 3
FETCH_ATTEMPTS = 3
FETCH_WORKERS = 8

METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")
_VERSION_PREFIX = re.compile(r"^/v\d+(?=/)")
_PLACEHOLDER = re.compile(r"\{[^}]*\}|<[^>]*>")
# A reference page states its request once, as the first line of a code block; later lines
# that look the same are examples with literal keys.
_TRACKER_REQUEST = re.compile(rf"^\s*({'|'.join(METHODS)})\s+(/v\d+/\S+)", re.MULTILINE)
_TRACKER_QUERY_BLOCK = re.compile(r'\{% cut "Request parameters" %\}(.*?)\{% endcut %\}', re.DOTALL)
# A parameter table's row in the reference's Markdown tables: ``| name |``, ``name | …`` and
# ``| [name](link) |``; a YFM table (``#|``) starts every row with ``||``.
_TRACKER_TABLE_ROW = re.compile(
    r"^\|?[ \t]*\[?`?([A-Za-z_][\w.]*)`?\]?(?:\([^)]*\))?[ \t]*\|", re.MULTILINE
)
_TRACKER_YFM_ROW = re.compile(r"^\|\|[ \t]*`?([A-Za-z_][\w.]*)`?[ \t]*\|", re.MULTILINE)
# Pages of the reference that explain the API and whose request lines are only examples.
TRACKER_PROSE_PAGES = frozenset({"api/common-format"})
_SUCCESS_CODES = ("200", "201", "202")


@dataclass(frozen=True)
class Operation:
    """One published operation; ``page`` is the reference page it was read from (Tracker)."""

    method: str
    path: str
    query: tuple[str, ...] = ()
    request: tuple[str, ...] = ()
    response: tuple[str, ...] = ()
    page: str = ""

    @property
    def key(self) -> tuple[str, str]:
        """What identifies the operation whatever its placeholders are called."""
        return self.method, shape(self.path)


def shape(path: str) -> str:
    """``path`` without the API version, the trailing slash and the placeholder names.

    Examples:
        >>> shape("/v3/issues/<issue-id>/comments")
        '/issues/{}/comments'
    """
    path = _VERSION_PREFIX.sub("", "/" + path.split("?", 1)[0].strip("/"))
    return _PLACEHOLDER.sub("{}", path)


def _resolved(document: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    """``node`` with a local ``$ref`` followed (``#/components/schemas/Page``)."""
    while "$ref" in node:
        target: Any = document
        for part in node["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        node = target
    return node


def field_names(document: dict[str, Any], schema: dict[str, Any] | None) -> tuple[str, ...]:
    """The top-level property names a body of ``schema`` can carry, sorted.

    A list is described by its items, and a union (``anyOf``/``oneOf``/``allOf``) by every
    member's properties: the question is which names can appear, not which combination.

    Examples:
        >>> document = {"components": {"schemas": {"Page": {"properties": {"id": {}}}}}}
        >>> field_names(document, {"type": "array", "items": {"$ref": "#/components/schemas/Page"}})
        ('id',)
    """
    names: set[str] = set()
    pending = [schema] if schema else []
    while pending:
        node = _resolved(document, pending.pop())
        names.update(node.get("properties", {}))
        pending += [*node.get("allOf", []), *node.get("anyOf", []), *node.get("oneOf", [])]
        if isinstance(node.get("items"), dict):
            pending.append(node["items"])
    return tuple(sorted(names))


def _json_schema(body: dict[str, Any] | None) -> dict[str, Any] | None:
    """The schema of ``body``'s JSON representation, if it has one."""
    content = (body or {}).get("content", {})
    return next((media.get("schema") for kind, media in content.items() if "json" in kind), None)


def openapi_operations(document: dict[str, Any]) -> list[Operation]:
    """Every operation of an OpenAPI ``document``, sorted by path and method."""
    operations = []
    for path, item in document["paths"].items():
        for method in METHODS:
            operation = item.get(method.lower())
            if operation is None:
                continue
            parameters = [
                _resolved(document, parameter)
                for parameter in [*item.get("parameters", []), *operation.get("parameters", [])]
            ]
            responses = operation.get("responses", {})
            success = next((responses[code] for code in _SUCCESS_CODES if code in responses), None)
            operations.append(
                Operation(
                    method=method,
                    path=_VERSION_PREFIX.sub("", path).rstrip("/"),
                    query=tuple(sorted(p["name"] for p in parameters if p["in"] == "query")),
                    request=field_names(
                        document, _json_schema(_resolved(document, operation["requestBody"]))
                    )
                    if "requestBody" in operation
                    else (),
                    response=field_names(
                        document, _json_schema(_resolved(document, success) if success else None)
                    ),
                )
            )
    return sorted(operations, key=lambda operation: (operation.path, operation.method))


def _stands_for(template: Operation, example: Operation) -> bool:
    """Whether ``example`` is ``template`` with a literal key (``/queues/DESIGN``, ``/queues/{}``).

    A literal that starts with ``_`` is an operation of its own (``/boards/_paginate``).
    """
    if template.method != example.method or "{}" not in shape(template.path):
        return False
    parts = map(re.escape, shape(template.path).split("{}"))
    return re.fullmatch("[^/_][^/]*".join(parts), shape(example.path)) is not None


def tracker_operations(page: str, text: str) -> list[Operation]:
    """The operations a Tracker reference ``page`` documents (none for a prose page).

    A page states each request as a line of a code block; an example of the same request with a
    literal key folds into it. Query parameters are the names in a request line's query string
    plus, for the page's first operation, those in its "Request parameters" table.
    """
    blocks = _TRACKER_QUERY_BLOCK.findall(text)
    table = {
        name
        for block in blocks
        for name in (_TRACKER_YFM_ROW if "#|" in block else _TRACKER_TABLE_ROW).findall(block)
    } - {"Parameter"}
    found: dict[tuple[str, str], Operation] = {}
    for method, target in _TRACKER_REQUEST.findall(text):
        path, _, query = target.partition("?")
        line = Operation(
            method=method,
            path=_VERSION_PREFIX.sub("", path).rstrip("/"),
            query=tuple(re.findall(r"(?:^|&)([A-Za-z_][\w.]*)=", query)),
            page=page.removesuffix(".md"),
        )
        key = next((key for key, known in found.items() if _stands_for(known, line)), line.key)
        known = found.setdefault(key, line)
        names = {
            *known.query,
            *line.query,
            *(table if key == next(iter(found)) else ()),
        }
        # Some pages list path parameters in the same table.
        names -= set(re.findall(r"\{(\w+)\}", known.path))
        found[key] = replace(known, query=tuple(sorted(names)))
    return list(found.values())


def _client() -> httpx2.Client:
    return httpx2.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT_SECONDS,
        follow_redirects=True,
        transport=httpx2.HTTPTransport(retries=CONNECT_RETRIES),
    )


def _text(client: httpx2.Client, url: str) -> str:
    """The body of ``url``, asked again before giving up: a busy server answers 429 or 5xx."""
    try:
        for attempt in stamina.retry_context(on=httpx2.HTTPStatusError, attempts=FETCH_ATTEMPTS):
            with attempt:
                return client.get(url).raise_for_status().text
    except httpx2.HTTPStatusError as error:
        raise SystemExit(f"api_surface: {url} answered {error.response.status_code}") from error
    raise AssertionError("stamina returns or raises inside the loop")


def fetch(service: str) -> list[Operation]:
    """The operations Yandex publishes for ``service`` right now (network)."""
    with _client() as client:
        if service in OPENAPI_URLS:
            return openapi_operations(json.loads(_text(client, OPENAPI_URLS[service])))
        pages = sorted(
            set(TRACKER_PAGE.findall(_text(client, TRACKER_INDEX))) - TRACKER_PROSE_PAGES
        )
        if not pages:
            raise SystemExit(f"api_surface: {TRACKER_INDEX} lists no API reference page")
        with ThreadPoolExecutor(FETCH_WORKERS) as pool:
            texts = pool.map(
                lambda page: _text(client, f"https://yandex.ru/support/tracker/en/{page}.md"),
                pages,
            )
            fetched = zip(pages, texts, strict=True)
            # The page with the parameter table comes first, so a shared operation links to it.
            by_table = sorted(fetched, key=lambda item: not _TRACKER_QUERY_BLOCK.search(item[1]))
            found = [
                operation
                for page, text in by_table
                for operation in tracker_operations(page, _reference_page(page, text))
            ]
    return _merged(found)


def _reference_page(page: str, text: str) -> str:
    """``text`` if it is a reference page's Markdown source, which opens with its front matter."""
    if not text.startswith("---"):
        raise SystemExit(f"api_surface: {page} is not a reference page (blocked or moved?)")
    return text


def _merged(operations: Iterable[Operation]) -> list[Operation]:
    """``operations`` with one entry per method and path, kept from the first page that has it."""
    merged: dict[tuple[str, str], Operation] = {}
    for operation in operations:
        first = merged.setdefault(operation.key, operation)
        query = tuple(sorted({*first.query, *operation.query}))
        merged[operation.key] = replace(first, query=query)
    return sorted(merged.values(), key=lambda operation: (operation.path, operation.method))


def dump(operations: list[Operation]) -> str:
    """The snapshot text of ``operations``: one JSON object per line, empty fields left out."""
    rows = [
        json.dumps({name: value for name, value in asdict(operation).items() if value})
        for operation in operations
    ]
    return "[\n" + ",\n".join(rows) + "\n]\n"


def load(service: str) -> list[Operation]:
    """The committed snapshot of ``service``."""
    rows = json.loads((SNAPSHOTS / f"{service}.json").read_text(encoding="utf-8"))
    return [
        Operation(
            method=row["method"],
            path=row["path"],
            query=tuple(row.get("query", ())),
            request=tuple(row.get("request", ())),
            response=tuple(row.get("response", ())),
            page=row.get("page", ""),
        )
        for row in rows
    ]
