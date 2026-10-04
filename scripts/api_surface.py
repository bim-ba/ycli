"""The API Yandex publishes for each service, reduced to names.

A surface is a list of operations: HTTP method, address (``base`` up to the version, then
``path``), the service's own name for the operation and its group, query parameter names and
the top-level field names of the request and response bodies. Names only, never Yandex's
prose, so the snapshots under ``scripts/api_snapshot/`` can be committed.

Two kinds of service live there. The ones ycli covers (:data:`SERVICES`, the registry's)
are compared by ``scripts/api_drift.py`` with what ycli sends and with a fresh fetch. The others
(:data:`LISTED`) are only listed: the inventory behind one system of names (issue #268).

Where each surface is read from is in :data:`SOURCES`: an OpenAPI document (Wiki, Forms,
Telemost, DataLens; Market's is split into files in a repository), a Swagger 1.2 listing (Disk),
a WSDL per service (Direct, Speller), or the reference pages an index lists (api360,
Metrika, Audience, AdMetrica: Diplodoc generates them from an OpenAPI document that is not
published itself; Webmaster, AppMetrica, Messenger, Yandex ID, Weather, Travel partners: written
by hand). Disk's schema is narrower than its documentation, which adds the rest. Tracker's
OpenAPI document is closed (401), so its operations are read from
the API reference too: ``llms.txt`` lists the pages and each page's
Markdown source states its request (``GET /v3/issues/{issue_id}``) and its query parameters.

Examples:
    >>> shape("/v1/pages/{idx}/grids/")
    '/pages/{}/grids'
    >>> [(o.base, o.path) for o in openapi_operations({"paths": {"/v1/me": {"get": {}}}})]
    [('/v1', '/me')]
"""

from __future__ import annotations

import io
import json
import posixpath
import re
import tarfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal
from xml.etree import ElementTree

import httpx2
import stamina
import yaml

if TYPE_CHECKING:
    from collections.abc import Iterable

SNAPSHOTS = Path(__file__).resolve().parent / "api_snapshot"
OPENAPI_URLS = {
    "wiki": "https://api.wiki.yandex.net/v1/openapi.json",
    "forms": "https://api.forms.yandex.net/v1/openapi.json",
}
TRACKER_INDEX = "https://yandex.ru/support/tracker/en/llms.txt"
TRACKER_PAGE = re.compile(r"https://yandex\.ru/support/tracker/en/(api/[^)\s]+)\.md")
# The services ycli covers: compared with what ycli sends. A test keeps it equal to the registry.
SERVICES = ("tracker", *OPENAPI_URLS)


@dataclass(frozen=True)
class Source:
    """Where a service publishes its operations, and in which form.

    ``url`` is the document (``openapi``, ``swagger``), the repository archive (``openapi-files``,
    with ``root`` the document inside it) or a template with ``{service}`` (``wsdl``, one
    document per name in ``parts``). ``rpc`` marks an API whose operations are all
    ``POST /rpc/<name>``: the name is the operation's own.
    """

    kind: Literal["openapi", "openapi-files", "swagger", "wsdl", "docs"]
    url: str
    root: str = ""
    parts: tuple[str, ...] = ()
    rpc: bool = False
    # The service's own prefix after the version (``/disk``): part of ``base`` (#276).
    prefix: str = ""
    # The JSON address of a WSDL service, a template with ``{service}`` (#276).
    address: str = ""
    # The index of the reference pages that add what the specification leaves out (Disk).
    docs: str = ""


# Direct publishes no list of its services: the docs index names 25 of these, and
# ``dynamictextadtargets``, ``smartadtargets`` and ``vcards`` answer with a WSDL all the same.
DIRECT_SERVICES = (
    "adextensions",
    "adgroups",
    "adimages",
    "ads",
    "advideos",
    "agencyclients",
    "audiencetargets",
    "bidmodifiers",
    "bids",
    "businesses",
    "campaigns",
    "changes",
    "clients",
    "creatives",
    "dictionaries",
    "dynamictextadtargets",
    "feeds",
    "keywordbids",
    "keywords",
    "keywordsresearch",
    "leads",
    "negativekeywordsharedsets",
    "retargetinglists",
    "sitelinks",
    "smartadtargets",
    "strategies",
    "turbopages",
    "vcards",
)
SOURCES: dict[str, Source] = {
    "tracker": Source("docs", TRACKER_INDEX),
    **{service: Source("openapi", url) for service, url in OPENAPI_URLS.items()},
    "telemost": Source(
        "openapi", "https://doc-static.yandex.net/dev/telemost/api-specification.yaml"
    ),
    "disk": Source(
        "swagger",
        "https://cloud-api.yandex.net/v1/schema",
        prefix="/disk",
        docs="https://yandex.ru/dev/disk-api/doc/sitemap.xml",
    ),
    "datalens": Source("openapi", "https://api.datalens.tech/json/", rpc=True),
    "market": Source(
        "openapi-files",
        "https://codeload.github.com/yandex-market/yandex-market-partner-api/tar.gz/refs/heads/main",
        root="openapi/openapi.yaml",
    ),
    # Every operation of a WSDL is also taken as JSON, by name, at `/json/v5/<service>`: the
    # docs say so for the whole API; it was not checked operation by operation.
    "direct": Source(
        "wsdl",
        "https://api.direct.yandex.com/v5/{service}?wsdl",
        parts=DIRECT_SERVICES,
        address="/json/v5/{service}",
    ),
    "speller": Source("wsdl", "https://speller.yandex.net/services/spellservice?WSDL"),
    # No specification is published for these: the index lists the reference pages.
    "api360": Source("docs", "https://yandex.ru/dev/api360/doc/ru/llms.txt", prefix="/api360"),
    "metrika": Source("docs", "https://yandex.ru/dev/metrika/ru/llms.txt"),
    "audience": Source("docs", "https://yandex.ru/dev/audience/ru/llms.txt"),
    "admetrica": Source("docs", "https://yandex.ru/dev/admetrica/doc/ru/llms.txt"),
    "webmaster": Source("docs", "https://yandex.ru/dev/webmaster/doc/ru/llms.txt"),
    "appmetrica": Source("docs", "https://appmetrica.yandex.ru/docs/ru/llms.txt"),
    "messenger": Source("docs", "https://yandex.ru/dev/messenger/doc/ru/llms.txt"),
    "id": Source("docs", "https://yandex.ru/dev/id/doc/ru/llms.txt"),
    "weather": Source("docs", "https://yandex.ru/dev/weather/doc/ru/llms.txt"),
    "travel": Source("docs", "https://yandex.ru/dev/travel-partners-api/doc/sitemap.xml"),
}
# Every service with a snapshot: the covered ones, then the ones that are only listed.
LISTED = tuple(SOURCES)
# The services of the roadmap with no snapshot, and why a script cannot read their operations.
NOT_LISTED = {
    "rasp": "a page shows the address alone, with no method",
    "maps": "no index of reference pages was found (Geocoder, Geosuggest, Router, Static)",
    "direct-reports": "Direct's `reports` has no WSDL and its page states no request line",
    "calendar": "CalDAV, a protocol: no HTTP operations to name",
    "contacts": "CardDAV, a protocol: no HTTP operations to name",
    "mail": "IMAP and SMTP, protocols: no HTTP operations to name",
}

USER_AGENT = "ycli-api-drift/1.0 (+https://github.com/bim-ba/ycli)"
REQUEST_TIMEOUT_SECONDS = 30
CONNECT_RETRIES = 3
FETCH_ATTEMPTS = 3
FETCH_WORKERS = 8

METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")
_VERSION_PREFIX = re.compile(r"^/v\d+(?=/)")
# A version as Yandex APIs write it: `v1`, `v4.1`, `v3.0`, `v1beta`, `v2alpha`, `v1beta1` (#283).
# A word that only starts with `v` (`virtual-disks`, `versions`, `vcards`) is not one.
_VERSION_SEGMENT = re.compile(r"v\d+(?:\.\d+)?(?:(?:alpha|beta)\d*)?")
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
# A page of an index: ``[title](https://…/page.md)``.
_INDEX_PAGE = re.compile(r"\]\((https?://[^)\s]+)\.md\)")
# A page of a sitemap.
_SITEMAP_PAGE = re.compile(r"<loc>([^<\s]+)</loc>")
_METHOD = "|".join(METHODS)
_ADDRESS = r"https?://[^\s`<\"')]+"
# A reference page Diplodoc generated from an OpenAPI document: the method, then the address.
_GENERATED_REQUEST = re.compile(
    rf"^({_METHOD})\s*\{{\.openapi__method\}}\s*\n+```[^\n]*\n(\S+)", re.MULTILINE
)
# The forms a page written by hand states its request in.
# ``GET https://host/path`` on a line of its own (Webmaster, AppMetrica, Weather):
_HOSTED_REQUEST = re.compile(rf"^[ \t>]*({_METHOD})[ \t]+({_ADDRESS})", re.MULTILINE)
# ``POST /token`` followed by its ``Host:`` header (Yandex ID):
_HEADER_REQUEST = re.compile(
    rf"^[ \t>]*({_METHOD})[ \t]+(/[^\s`<\"']*)[^\n]*\n[ \t>]*Host:[ \t]*(?:https?://)?([^\s/]+)",
    re.MULTILINE,
)
# A labelled method, then the address in a code span or a block within a few lines
# (Messenger: ``HTTP метод: `POST```, ``URL: `https://…```; Disk: ``Метод: ##POST##.``):
_LABELLED_REQUEST = re.compile(
    rf"^(?:HTTP[ -]метод|Метод|HTTP method|Method)[^\n]{{0,12}}?[`#*]*\b({_METHOD})\b[^\n]*\n"
    rf"(?:[^\n]*\n){{0,4}}?(?:URL:[ \t]*`|[ \t]*)({_ADDRESS})",
    re.MULTILINE,
)
# A placeholder written as a link to its description: ``{[user-id](*user-id)}``.
_LINKED_PLACEHOLDER = re.compile(r"\{\[([^\]]+)\]\([^)]*\)\}")


@dataclass(frozen=True)
class Operation:
    """One published operation.

    The published address is ``base + path``: ``base`` ends with the version (``/v1``,
    ``/directory/v1``, ``/v1/disk`` with the service's own prefix) and is empty when the address
    has none. ``method`` is the HTTP method, or ``SOAP`` for an operation of a WSDL with no JSON
    address; operations that share an address are told apart by ``name``. ``name`` is the
    service's own name for the operation (``operationId``, a Swagger ``nickname``, a WSDL or
    RPC operation, a reference page's slug), ``group`` its tag there, else the first noun of
    the path. ``source`` says what it was read from; ``page`` is the reference page (Tracker).
    """

    method: str
    path: str
    query: tuple[str, ...] = ()
    request: tuple[str, ...] = ()
    response: tuple[str, ...] = ()
    page: str = ""
    base: str = ""
    name: str = ""
    group: str = ""
    source: str = ""

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


def split_version(published: str, prefix: str = "") -> tuple[str, str]:
    """A published path as ``(base, path)``: ``base`` ends with the first version segment.

    A service whose name follows the version (``/v1/disk/…``) has that name in ``base`` too:
    ``prefix`` says what it is, and an address that does not continue with it keeps the plain
    base. The trailing slash and a query string are dropped, as the comparison ignores them.

    Args:
        published: The path as the service publishes it.
        prefix: The service's own prefix after the version, ``/disk``.

    Returns:
        The base and the rest of the path; the rest is ``/`` for the service's root.

    Examples:
        >>> split_version("/directory/v1/org/{orgId}/users/")
        ('/directory/v1', '/org/{orgId}/users')
        >>> split_version("/v1/disk/trash/resources", "/disk")
        ('/v1/disk', '/trash/resources')
        >>> split_version("/rpc/getDashboard")
        ('', '/rpc/getDashboard')
    """
    segments = published.split("?", 1)[0].strip("/").split("/")
    cut = next((i + 1 for i, part in enumerate(segments) if _VERSION_SEGMENT.fullmatch(part)), 0)
    own = prefix.strip("/").split("/") if prefix.strip("/") else []
    if cut and own and segments[cut : cut + len(own)] == own:
        cut += len(own)
    return "/".join(["", *segments[:cut]]) if cut else "", "/" + "/".join(segments[cut:])


def first_noun(path: str) -> str:
    """The first segment of ``path`` that is not a placeholder: an operation's group by default.

    Examples:
        >>> first_noun("/{org_id}/users/{id}")
        'users'
    """
    return next((part for part in path.strip("/").split("/") if not _PLACEHOLDER.search(part)), "")


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


def openapi_operations(document: dict[str, Any], *, rpc: bool = False) -> list[Operation]:
    """Every operation of an OpenAPI ``document``, sorted by path and method.

    Args:
        document: The parsed OpenAPI document.
        rpc: Whether an operation without an ``operationId`` is named by its last path segment.

    Returns:
        The operations.
    """
    operations = []
    # A document may state its paths relative to its server (Telemost: `/v1/telemost-api`).
    servers = document.get("servers") or [{}]
    server = httpx2.URL(servers[0].get("url", "")).path.rstrip("/")
    # What follows the version in the server's address is the service's own prefix.
    prefix = split_version(server)[1] if split_version(server)[0] else ""
    for published, item in document["paths"].items():
        item = _resolved(document, item)
        base, path = split_version(server + published, prefix)
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
                    path=path,
                    base=base,
                    name=operation.get("operationId") or (path.rsplit("/", 1)[-1] if rpc else ""),
                    group=next(iter(operation.get("tags", [])), "") or first_noun(path),
                    source="openapi",
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
    return sorted(operations, key=_order)


def _order(operation: Operation) -> tuple[str, str, str]:
    """How a snapshot is sorted."""
    return operation.path, operation.method, operation.name


def joined_files(files: dict[str, str], root: str) -> dict[str, Any]:
    """An OpenAPI document split into files, as one document with local references.

    Every file becomes an entry of ``files`` in the result, and a reference to a file
    (``$ref: ../components/schemas/x.yaml``, relative to the file that holds it) a reference to
    that entry. Market publishes its specification this way.

    Args:
        files: The YAML text of each file, by its path in the repository.
        root: The path of the root document.

    Returns:
        The root document with every file under ``files``.

    Examples:
        >>> files = {
        ...     "api/a.yaml": "paths: {/v2/x: {$ref: paths/x.yaml}}",
        ...     "api/paths/x.yaml": "get: {}",
        ... }
        >>> joined_files(files, "api/a.yaml")["paths"]
        {'/v2/x': {'$ref': '#/files/api|paths|x.yaml'}}
    """

    def localised(node: Any, folder: str) -> Any:
        if isinstance(node, dict):
            return {
                key: _file_reference(value, folder)
                if key == "$ref" and isinstance(value, str)
                else localised(value, folder)
                for key, value in node.items()
            }
        if isinstance(node, list):
            return [localised(item, folder) for item in node]
        return node

    parsed = {
        path.replace("/", "|"): localised(yaml.safe_load(text), posixpath.dirname(path))
        for path, text in files.items()
    }
    return {**parsed[root.replace("/", "|")], "files": parsed}


def _file_reference(reference: str, folder: str) -> str:
    """``reference`` to another file as a reference into ``files``; a local one unchanged."""
    target, _, fragment = reference.partition("#")
    if not target:
        return reference
    path = posixpath.normpath(posixpath.join(folder, target)).replace("/", "|")
    return f"#/files/{path}{fragment}"


def swagger_operations(resources: list[dict[str, Any]], prefix: str = "") -> list[Operation]:
    """Every operation of a Swagger 1.2 API, given the documents of its resources (Disk).

    Args:
        resources: The API declaration of each resource the listing names.
        prefix: The service's own prefix after the version, part of ``base``.

    Returns:
        The operations.
    """
    operations = []
    for resource in resources:
        models = resource.get("models", {})
        for api in resource.get("apis", []):
            base, path = split_version(api["path"], prefix)
            for operation in api.get("operations", []):
                parameters = operation.get("parameters", [])
                bodies = [p.get("type", "") for p in parameters if p.get("paramType") == "body"]
                operations.append(
                    Operation(
                        method=operation["method"].upper(),
                        path=path,
                        base=base,
                        name=operation.get("nickname", ""),
                        group=first_noun(path),
                        source="swagger",
                        query=tuple(
                            sorted(p["name"] for p in parameters if p.get("paramType") == "query")
                        ),
                        request=_model_fields(models, *bodies),
                        response=_model_fields(models, operation.get("type", "")),
                    )
                )
    return _merged(operations)


def _model_fields(models: dict[str, Any], *names: str) -> tuple[str, ...]:
    """The property names of the Swagger models ``names``; a type that is no model has none."""
    return tuple(
        sorted({field for name in names for field in models.get(name, {}).get("properties", {})})
    )


_WSDL = "{http://schemas.xmlsoap.org/wsdl/}"
_XSD = "{http://www.w3.org/2001/XMLSchema}"


def wsdl_operations(
    text: str, *, address: str, group: str = "", method: str = "SOAP"
) -> list[Operation]:
    """Every operation of a WSDL document: one row per operation of its port type.

    The request and response fields are the element names of the operation's input and output
    messages, read from the document's own schema.

    Args:
        text: The WSDL document.
        address: The published path the operations are sent to.
        group: The group of every operation; the first noun of ``address`` by default.
        method: ``SOAP``, or ``POST`` when ``address`` is the service's JSON address, which
            takes the same operations by name.

    Returns:
        The operations.
    """
    root = ElementTree.fromstring(text)
    elements = {
        element.get("name"): tuple(
            sorted(
                child.get("name", "")
                for child in element.iter(f"{_XSD}element")
                if child is not element
            )
        )
        for element in root.iter(f"{_XSD}element")
        if element.find(f"{_XSD}complexType") is not None
    }
    messages = {
        message.get("name"): next(
            (part.get("element", "").rpartition(":")[2] for part in message.iter(f"{_WSDL}part")),
            "",
        )
        for message in root.iter(f"{_WSDL}message")
    }

    def fields(operation: ElementTree.Element, direction: str) -> tuple[str, ...]:
        node = operation.find(f"{_WSDL}{direction}")
        message = "" if node is None else node.get("message", "").rpartition(":")[2]
        return elements.get(messages.get(message, ""), ())

    base, path = split_version(address)
    return sorted(
        (
            Operation(
                method=method,
                path=path,
                base=base,
                name=operation.get("name", ""),
                group=group or first_noun(path),
                source="wsdl",
                request=fields(operation, "input"),
                response=fields(operation, "output"),
            )
            for port in root.iter(f"{_WSDL}portType")
            for operation in port.iter(f"{_WSDL}operation")
        ),
        key=_order,
    )


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
        base, path = split_version(path)
        slug = page.removesuffix(".md")
        line = Operation(
            method=method,
            path=path,
            base=base,
            name=slug.rsplit("/", 1)[-1],
            group=first_noun(path),
            source="docs",
            query=tuple(re.findall(r"(?:^|&)([A-Za-z_][\w.]*)=", query)),
            page=slug,
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


def page_operations(page: str, text: str, prefix: str = "") -> list[Operation]:
    """The operations a reference ``page`` of a docs-only service documents.

    A page Diplodoc generated from an OpenAPI document states one operation: its method and its
    full address. The page's slug is the operation's own name there (``DomainService_Delete``)
    and its directory the group (the tag the page was generated under).

    A page written by hand states its request in one of three forms (a line with the method
    and the full address, a request line with its ``Host`` header, a labelled method followed
    by the address); the group is then the first noun of the path. An address that is only a
    host, or a link into the documentation, is not a request.

    Args:
        page: The page's path under the index, without ``.md``.
        text: The page's Markdown source.
        prefix: The service's own prefix after the version, part of ``base``.

    Returns:
        The operations; none for a page that documents no request.
    """
    folder, _, slug = page.rpartition("/")
    # `logs/openapi/<page>`: the folder Diplodoc generates into is not a tag.
    group = next((part for part in reversed(folder.split("/")) if part != "openapi"), "")
    # First, so that an address with such a placeholder is read whole.
    text = _LINKED_PLACEHOLDER.sub(r"{\1}", text)
    generated = _GENERATED_REQUEST.findall(text)
    written = [
        *_HOSTED_REQUEST.findall(text),
        *(
            (method, f"https://{host}{path}")
            for method, path, host in _HEADER_REQUEST.findall(text)
        ),
        *_LABELLED_REQUEST.findall(text),
    ]
    operations: dict[tuple[str, str, str], Operation] = {}
    for method, address in generated or written:
        address = address.split("?", 1)[0].rstrip(".,;")
        if address.endswith(".md") or "/doc/" in address:
            continue  # a link to another page
        base, path = split_version(httpx2.URL(address).path, prefix)
        if not base and path == "/":
            continue  # a host alone
        operations.setdefault(
            (method, base, path),
            Operation(
                method=method,
                path=path,
                base=base,
                name=slug,
                group=group if generated else first_noun(path),
                source="docs",
                page=page,
            ),
        )
    found = list(operations.values())
    # An example on the same page may even use another method than the request it shows.
    return [
        operation
        for operation in found
        if not any(
            other.base == operation.base
            and _stands_for(replace(other, method=operation.method), operation)
            for other in found
            if other is not operation
        )
    ]


def _docs_service(client: httpx2.Client, index: str, prefix: str) -> list[Operation]:
    """The operations of the reference pages ``index`` lists (an ``llms.txt`` or a sitemap).

    A sitemap lists every language: the Russian pages are read, as an ``llms.txt`` is per
    language. An example of a request with a literal key folds into the request it is an
    example of (``/application/1111`` into ``/application/{id}``).
    """
    listing = _text(client, index)
    if index.endswith(".xml"):
        root = index.rpartition("/")[0] + "/ru/"
        found = set(_SITEMAP_PAGE.findall(listing))
    else:
        root = index.rpartition("/")[0] + "/"
        found = set(_INDEX_PAGE.findall(listing))
    # The root of a sitemap's language is its landing page, not a page with a source.
    urls = sorted(url for url in found if url.startswith(root) and url != root)
    if not urls:
        raise SystemExit(f"api_surface: {index} lists no page")
    with ThreadPoolExecutor(FETCH_WORKERS) as pool:
        texts = pool.map(lambda url: _text(client, f"{url}.md"), urls)
        operations = _merged(
            operation
            for url, text in zip(urls, texts, strict=True)
            for operation in page_operations(
                url.removeprefix(root), _reference_page(url.removeprefix(root), text), prefix
            )
        )
    return [
        operation
        for operation in operations
        if not any(
            other.base == operation.base and _stands_for(other, operation)
            for other in operations
            if other is not operation
        )
    ]


def _supplemented(published: list[Operation], documented: list[Operation]) -> list[Operation]:
    """A specification's operations, and the ones only the documentation describes (#268).

    The specification wins where both have an operation: its name is the service's own.
    """
    known = {(operation.base, *operation.key) for operation in published}
    extra = [o for o in documented if (o.base, *o.key) not in known]
    return sorted([*published, *extra], key=_order)


def _client() -> httpx2.Client:
    return httpx2.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT_SECONDS,
        follow_redirects=True,
        transport=httpx2.HTTPTransport(retries=CONNECT_RETRIES),
    )


def _response(client: httpx2.Client, url: str) -> httpx2.Response:
    """The answer of ``url``, asked again before giving up: a busy server answers 429 or 5xx."""
    try:
        for attempt in stamina.retry_context(on=httpx2.HTTPStatusError, attempts=FETCH_ATTEMPTS):
            with attempt:
                return client.get(url).raise_for_status()
    except httpx2.HTTPStatusError as error:
        raise SystemExit(f"api_surface: {url} answered {error.response.status_code}") from error
    raise AssertionError("stamina returns or raises inside the loop")


def _text(client: httpx2.Client, url: str) -> str:
    """The body of ``url`` as text."""
    return _response(client, url).text


def _yaml_files(archive: bytes, root: str) -> dict[str, str]:
    """The YAML files beside ``root`` in a repository ``archive``, by their path in it."""
    folder = posixpath.dirname(root) + "/"
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        for member in tar:
            # The archive wraps the repository in one directory named after the branch.
            path = member.name.partition("/")[2]
            if member.isfile() and path.startswith(folder) and path.endswith(".yaml"):
                content = tar.extractfile(member)
                assert content is not None  # a regular file
                files[path] = content.read().decode("utf-8")
    return files


def _wsdl_service(client: httpx2.Client, source: Source) -> list[Operation]:
    """The operations of a WSDL service: of its one document, or of one document per part."""
    if not source.parts:
        address = httpx2.URL(source.url.partition("?")[0]).path
        return wsdl_operations(_text(client, source.url), address=address)
    # A service with a JSON address is listed by it: that is the call ycli would make.
    address = source.address or httpx2.URL(source.url.partition("?")[0]).path
    method = "POST" if source.address else "SOAP"
    with ThreadPoolExecutor(FETCH_WORKERS) as pool:
        texts = pool.map(lambda part: _text(client, source.url.format(service=part)), source.parts)
        return sorted(
            (
                operation
                for part, text in zip(source.parts, texts, strict=True)
                for operation in wsdl_operations(
                    text, address=address.format(service=part), group=part, method=method
                )
            ),
            key=_order,
        )


def _bytes(client: httpx2.Client, url: str) -> bytes:
    """The body of ``url`` as bytes (an archive)."""
    return _response(client, url).content


def fetch(service: str) -> list[Operation]:
    """The operations Yandex publishes for ``service`` right now (network)."""
    source = SOURCES[service]
    with _client() as client:
        if source.kind == "openapi":
            # YAML reads JSON too: Telemost publishes YAML, the others JSON.
            return openapi_operations(yaml.safe_load(_text(client, source.url)), rpc=source.rpc)
        if source.kind == "openapi-files":
            return openapi_operations(
                joined_files(_yaml_files(_bytes(client, source.url), source.root), source.root)
            )
        if source.kind == "swagger":
            listing = json.loads(_text(client, source.url))
            published = swagger_operations(
                [
                    json.loads(_text(client, listing["basePath"] + api["path"]))
                    for api in listing["apis"]
                ],
                source.prefix,
            )
            if not source.docs:
                return published
            return _supplemented(published, _docs_service(client, source.docs, source.prefix))
        if source.kind == "wsdl":
            return _wsdl_service(client, source)
        if service != "tracker":
            return _docs_service(client, source.url, source.prefix)
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
    merged: dict[tuple[str, str, str], Operation] = {}
    for operation in operations:
        key = (operation.base, *operation.key)
        first = merged.setdefault(key, operation)
        query = tuple(sorted({*first.query, *operation.query}))
        merged[key] = replace(first, query=query)
    return sorted(merged.values(), key=_order)


# The order of a snapshot row: what identifies the operation first, its fields last.
_COLUMNS = (
    "method",
    "base",
    "path",
    "name",
    "group",
    "source",
    "page",
    "query",
    "request",
    "response",
)


def dump(operations: list[Operation]) -> str:
    """The snapshot text of ``operations``: one JSON object per line, empty fields left out."""
    rows = [
        json.dumps({name: row[name] for name in _COLUMNS if row[name]}, ensure_ascii=False)
        for row in map(asdict, operations)
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
            base=row.get("base", ""),
            name=row.get("name", ""),
            group=row.get("group", ""),
            source=row.get("source", ""),
        )
        for row in rows
    ]
