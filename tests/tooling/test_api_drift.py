"""ycli against the API Yandex publishes: the snapshots, the comparison and the weekly check.

``scripts/api_surface.py`` reduces what Yandex publishes to operations; ``scripts/api_drift.py``
compares them with what the contract cases send. The network is never touched here: a fetch
runs against ``httpx2.MockTransport``.
"""

from __future__ import annotations

import doctest
import io
import json
import re
import tarfile
from dataclasses import replace

import httpx2
import pytest
from scripts import api_drift, api_surface
from scripts.api_drift import Call, compare
from scripts.api_surface import Operation

from tests.architecture.scanners import SRC, violation_markers
from tests.contract import load_cases
from ycli.yandex.registry import SERVICES

OPENAPI = {
    "paths": {
        "/v1/pages/{idx}/": {
            "parameters": [{"$ref": "#/components/parameters/Fields"}],
            "get": {
                "parameters": [
                    {"name": "revision_id", "in": "query"},
                    {"name": "idx", "in": "path"},
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Page"}}
                        }
                    }
                },
            },
            "post": {
                "requestBody": {"$ref": "#/components/requestBodies/Update"},
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "anyOf": [
                                            {"$ref": "#/components/schemas/Page"},
                                            {"properties": {"redirect": {}}},
                                            {"type": "null"},
                                        ]
                                    },
                                }
                            }
                        }
                    }
                },
            },
            "delete": {"responses": {"204": {}}},
        }
    },
    "components": {
        "parameters": {"Fields": {"name": "fields", "in": "query"}},
        "requestBodies": {
            "Update": {"content": {"application/json": {"schema": {"properties": {"title": {}}}}}}
        },
        "schemas": {"Page": {"allOf": [{"properties": {"id": {}}}, {"properties": {"slug": {}}}]}},
    },
}


def test_docstring_examples_hold():
    """``scripts/`` is outside pytest's doctest paths, so its examples run here."""
    for module in (api_surface, api_drift):
        assert doctest.testmod(module).failed == 0


def test_openapi_operations_read_parameters_and_top_level_fields():
    delete, get, post = api_surface.openapi_operations(OPENAPI)
    assert (get.method, get.path, get.query) == ("GET", "/pages/{idx}", ("fields", "revision_id"))
    assert get.response == ("id", "slug") and get.request == ()
    assert post.request == ("title",) and post.query == ("fields",)
    assert post.response == ("id", "redirect", "slug")
    assert (delete.method, delete.request, delete.response) == ("DELETE", (), ())


@pytest.mark.parametrize(
    "table",
    [
        "#|\n|| Parameter | Text ||\n|| expand | X\n\nMore | String ||\n|| perPage | Size ||\n|#",
        "| Parameter | Description |\n| ----- | ----- |\n| expand | Extra |\n| perPage | Size |",
        "Parameter | Description\n----- | -----\nexpand | Extra\nperPage | Size",
        "| Parameter | Description |\n| [expand](a.md#x) | Extra |\n| `perPage` | Size |",
    ],
)
def test_tracker_page_yields_its_request_and_query_parameters(table):
    text = (
        "GET /v3/queues/{queue_id}/tags\nHost: api.tracker.yandex.net\n"
        f'{{% cut "Request parameters" %}}\n\n{table}\n\n{{% endcut %}}\n'
        '{% cut "Request body parameters" %}\n| summary | Text |\n{% endcut %}\n'
        "> GET https://api.tracker.yandex.net/v3/queues/TEST/tags?fromExample=1\n"
    )
    assert api_surface.tracker_operations("api/queues/get-tags", text) == [
        Operation(
            "GET",
            "/queues/{queue_id}/tags",
            query=("expand", "perPage"),
            page="api/queues/get-tags",
            base="/v3",
            name="get-tags",
            group="queues",
            source="docs",
        )
    ]


def _documented(operation: Operation, group: str) -> Operation:
    """``operation`` as a Tracker reference page yields it: named by the page, grouped by path."""
    name = operation.page.rsplit("/", 1)[-1]
    return replace(operation, base="/v3", name=name, group=group, source="docs")


def _query_cut(name: str) -> str:
    """A reference page's query-parameter block listing ``name``."""
    return f'{{% cut "Request parameters" %}}\n| {name} | Text |\n{{% endcut %}}'


def test_tracker_page_drops_path_parameters_and_prose_pages_yield_nothing():
    text = f"PATCH /v3/filters/{{filter_id}}\n{_query_cut('filter_id')}"
    assert api_surface.tracker_operations("x", text) == [
        _documented(Operation("PATCH", "/filters/{filter_id}", page="x"), "filters")
    ]
    assert api_surface.tracker_operations("api/access", "How to get a token.") == []


def test_tracker_page_with_several_requests_yields_each_and_folds_its_examples():
    """The table belongs to the page's first request; a literal key is an example of it."""
    text = (
        f"GET /v3/queues/<queue_id>/triggers?version=1\n{_query_cut('expand')}\n"
        "   GET /v3/queues/DESIGN/triggers?perPage=20&id=7\n"
        "GET /v3/queues/<queue_id>/triggers/_relative?from=1\n"
        "POST /v3/worklog/_search\n"
    )
    assert api_surface.tracker_operations("p", text) == [
        _documented(
            Operation(
                "GET",
                "/queues/<queue_id>/triggers",
                query=("expand", "id", "perPage", "version"),
                page="p",
            ),
            "queues",
        ),
        _documented(
            Operation("GET", "/queues/<queue_id>/triggers/_relative", query=("from",), page="p"),
            "queues",
        ),
        _documented(Operation("POST", "/worklog/_search", page="p"), "worklog"),
    ]


def _serve(monkeypatch, routes: dict[str, str | bytes | int]) -> list[str]:
    """Answer ``api_surface`` from ``routes`` (a body, or a status); returns the URLs asked."""
    asked: list[str] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        asked.append(str(request.url))
        answer = routes[str(request.url)]
        if isinstance(answer, int):
            return httpx2.Response(answer)
        if isinstance(answer, bytes):
            return httpx2.Response(200, content=answer)
        return httpx2.Response(200, text=answer)

    monkeypatch.setattr(
        api_surface, "_client", lambda: httpx2.Client(transport=httpx2.MockTransport(handle))
    )
    return asked


def test_fetch_reads_an_openapi_service(monkeypatch):
    _serve(monkeypatch, {api_surface.OPENAPI_URLS["wiki"]: json.dumps(OPENAPI)})
    assert [operation.method for operation in api_surface.fetch("wiki")] == [
        "DELETE",
        "GET",
        "POST",
    ]


def test_fetch_reads_tracker_pages_merging_twins_and_skipping_prose(monkeypatch):
    base = "https://yandex.ru/support/tracker/en/api"
    index = "\n".join(
        f"- [x]({base}/{page}.md)" for page in ("common-format", "about-api", "query", "search")
    )
    asked = _serve(
        monkeypatch,
        {
            api_surface.TRACKER_INDEX: index,
            f"{base}/about-api.md": "---\nProse only.",
            f"{base}/query.md": "---\nPOST /v3/issues/_search?scrollId=1\n",
            f"{base}/search.md": f"---\nPOST /v3/issues/_search\n{_query_cut('expand')}perPage | x",
        },
    )
    # One operation, linked to the page that lists its parameters, not the first by name.
    assert api_surface.fetch("tracker") == [
        _documented(
            Operation("POST", "/issues/_search", query=("expand", "scrollId"), page="api/search"),
            "issues",
        )
    ]
    assert f"{base}/common-format.md" not in asked


@pytest.mark.parametrize(
    ("published", "base", "path"),
    [
        ("/v1/pages/{idx}/", "/v1", "/pages/{idx}"),
        ("/directory/v1/org/{orgId}/users", "/directory/v1", "/org/{orgId}/users"),
        ("/json/v5/ads", "/json/v5", "/ads"),
        ("/rpc/getDashboard", "", "/rpc/getDashboard"),
        # The first version segment is the boundary; a later one stays in the path.
        ("/v1/disk/v2/x?fields=a", "/v1", "/disk/v2/x"),
        # Every way Yandex APIs write a version (#283).
        ("/v4.1/user/{user-id}/hosts", "/v4.1", "/user/{user-id}/hosts"),
        ("/v3.0/search", "/v3.0", "/search"),
        ("/v2beta/x", "/v2beta", "/x"),
        ("/v2alpha/x", "/v2alpha", "/x"),
        ("/api/v1beta1/x", "/api/v1beta1", "/x"),
        # A word that only starts with `v` is not a version.
        ("/virtual-disks/{id}", "", "/virtual-disks/{id}"),
        ("/versions/v", "", "/versions/v"),
        ("/vcards", "", "/vcards"),
        ("/v2ray/x", "", "/v2ray/x"),
        ("/v1.x/y", "", "/v1.x/y"),
    ],
)
def test_a_published_address_splits_at_its_version(published, base, path):
    assert api_surface.split_version(published) == (base, path)


def _v_segments() -> tuple[set[str], set[str]]:
    """Across every snapshot: the `v…` segments of a base, and those left in a path."""
    in_base: set[str] = set()
    in_path: set[str] = set()
    for service in api_surface.LISTED:
        for operation in api_surface.load(service):
            in_base |= {part for part in operation.base.split("/") if part.startswith("v")}
            in_path |= {part for part in operation.path.split("/") if part.startswith("v")}
    return in_base, in_path


def test_only_a_version_ends_a_base_in_every_snapshot():
    """A word that starts with `v` stays in the path; a version never does."""
    in_base, in_path = _v_segments()
    assert in_base and all(api_surface._VERSION_SEGMENT.fullmatch(part) for part in in_base)
    assert {"virtual-disks", "vcards"} <= in_path
    assert not {part for part in in_path if api_surface._VERSION_SEGMENT.fullmatch(part)}


def test_a_looser_version_rule_would_swallow_words(monkeypatch):
    """The probe: were any `v…` segment a version, the snapshots' words would become bases."""
    monkeypatch.setattr(api_surface, "_VERSION_SEGMENT", re.compile(r"v.*"))
    _, in_path = _v_segments()
    assert {part for part in in_path if api_surface._VERSION_SEGMENT.fullmatch(part)}
    assert api_surface.split_version("/v1/disk/virtual-disks")[0] == "/v1"
    assert api_surface.split_version("/virtual-disks/x") == ("/virtual-disks", "/x")


@pytest.mark.parametrize(
    ("published", "base", "path"),
    [
        ("/v1/disk/trash/resources", "/v1/disk", "/trash/resources"),
        # The root of the service, and an address of the same host outside the service.
        ("/v1/disk", "/v1/disk", "/"),
        ("/v1/data/admin/settings", "/v1", "/data/admin/settings"),
        # Without a version there is no base for a prefix to join.
        ("/disk/resources", "", "/disk/resources"),
    ],
)
def test_the_services_own_prefix_belongs_to_the_base(published, base, path):
    assert api_surface.split_version(published, "/disk") == (base, path)


def test_an_openapi_operation_carries_its_own_name_and_group():
    document = {
        "servers": [{"url": "https://cloud-api.yandex.net/v1/telemost-api"}],
        "paths": {
            "/conferences/{id}": {
                "get": {"operationId": "getConference", "tags": ["Conferences", "Other"]},
                "delete": {},
            }
        },
    }
    delete, get = api_surface.openapi_operations(document)
    # The paths of a document are relative to its server, and the service's own name after
    # the version belongs to the base (#276).
    assert (get.base, get.path) == ("/v1/telemost-api", "/conferences/{id}")
    assert (get.name, get.group, get.source) == ("getConference", "Conferences", "openapi")
    # No operationId means no name; no tag means the first noun of the path.
    assert (delete.name, delete.group) == ("", "conferences")


def test_an_rpc_operation_is_named_by_its_path():
    document = {"servers": [{"url": "/"}], "paths": {"/rpc/getDashboard": {"post": {}}}}
    (operation,) = api_surface.openapi_operations(document, rpc=True)
    assert (operation.base, operation.path, operation.name) == (
        "",
        "/rpc/getDashboard",
        "getDashboard",
    )


MARKET_FILES = {
    "openapi/openapi.yaml": "paths:\n  /v2/campaigns:\n    $ref: paths/v2_campaigns.yaml\n",
    "openapi/paths/v2_campaigns.yaml": (
        "get:\n  operationId: getCampaigns\n  tags: [campaigns, fbs]\n"
        "  responses:\n    '200':\n      content:\n        application/json:\n"
        "          schema:\n            $ref: ../components/schemas/campaigns.yaml#/Response\n"
    ),
    "openapi/components/schemas/campaigns.yaml": (
        "Response:\n  properties:\n    campaigns: {}\n    pager:\n      $ref: '#/Pager'\n"
    ),
}


def test_a_specification_split_into_files_reads_as_one_document():
    (operation,) = api_surface.openapi_operations(
        api_surface.joined_files(MARKET_FILES, "openapi/openapi.yaml")
    )
    assert (operation.method, operation.base, operation.path) == ("GET", "/v2", "/campaigns")
    # The group is the first tag: the subject, before the fulfilment models.
    assert (operation.name, operation.group) == ("getCampaigns", "campaigns")
    assert operation.response == ("campaigns", "pager")


def _archive(files: dict[str, str]) -> bytes:
    """A repository archive as GitHub serves it: one top directory, then the files."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for path, text in {**files, "README.md": "not YAML", "docs/x.yaml": "elsewhere: 1"}.items():
            data = text.encode()
            member = tarfile.TarInfo(f"repository-main/{path}")
            member.size = len(data)
            tar.addfile(member, io.BytesIO(data))
    return buffer.getvalue()


def test_fetch_reads_a_specification_from_a_repository_archive(monkeypatch):
    _serve(monkeypatch, {api_surface.SOURCES["market"].url: _archive(MARKET_FILES)})
    assert [operation.name for operation in api_surface.fetch("market")] == ["getCampaigns"]


SWAGGER_LISTING = {
    "basePath": "https://cloud-api.yandex.net/v1/schema/resources",
    "apis": [{"path": "/v1/disk/resources"}],
}
SWAGGER_RESOURCE = {
    "apis": [
        {
            "path": "/v1/disk/resources",
            "operations": [
                {
                    "method": "get",
                    "nickname": "GetResource",
                    "type": "Resource",
                    "parameters": [
                        {"name": "path", "paramType": "query"},
                        {"name": "fields", "paramType": "query"},
                    ],
                },
                {
                    "method": "PATCH",
                    "nickname": "UpdateResource",
                    "type": "void",
                    "parameters": [
                        {"name": "path", "paramType": "query"},
                        {"name": "body", "paramType": "body", "type": "ResourcePatch"},
                    ],
                },
            ],
        }
    ],
    "models": {
        "Resource": {"properties": {"name": {}, "path": {}}},
        "ResourcePatch": {"properties": {"custom_properties": {}}},
    },
}


def test_fetch_reads_a_swagger_listing_and_its_resources(monkeypatch):
    listing = api_surface.SOURCES["disk"].url
    _serve(
        monkeypatch,
        {
            listing: json.dumps(SWAGGER_LISTING),
            f"{SWAGGER_LISTING['basePath']}/v1/disk/resources": json.dumps(SWAGGER_RESOURCE),
            # The documentation, which adds nothing here.
            api_surface.SOURCES["disk"].docs: "<loc>https://yandex.ru/dev/disk-api/doc/ru/x</loc>",
            "https://yandex.ru/dev/disk-api/doc/ru/x.md": "---\nProse only.",
        },
    )
    get, patch = api_surface.fetch("disk")
    assert (get.method, get.base, get.path) == ("GET", "/v1/disk", "/resources")
    assert (get.name, get.group, get.source) == ("GetResource", "resources", "swagger")
    assert (get.query, get.response) == (("fields", "path"), ("name", "path"))
    # A body parameter's model is the request; a type that is no model has no fields.
    assert (patch.name, patch.request, patch.response) == (
        "UpdateResource",
        ("custom_properties",),
        (),
    )


WSDL = """<?xml version="1.0"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ns="urn:x">
  <wsdl:types><xsd:schema>
    <xsd:element name="SetRequest"><xsd:complexType><xsd:sequence>
      <xsd:element name="Bids" type="ns:BidSetItem"/>
    </xsd:sequence></xsd:complexType></xsd:element>
    <xsd:element name="SetResponse"><xsd:complexType><xsd:sequence>
      <xsd:element name="SetResults" type="ns:Result"/>
    </xsd:sequence></xsd:complexType></xsd:element>
  </xsd:schema></wsdl:types>
  <wsdl:message name="SetOperationRequest">
    <wsdl:part name="p" element="ns:SetRequest"/>
  </wsdl:message>
  <wsdl:message name="SetOperationResponse">
    <wsdl:part name="p" element="ns:SetResponse"/>
  </wsdl:message>
  <wsdl:portType name="BidsPort">
    <wsdl:operation name="set">
      <wsdl:input message="ns:SetOperationRequest"/>
      <wsdl:output message="ns:SetOperationResponse"/>
    </wsdl:operation>
    <wsdl:operation name="get"/>
  </wsdl:portType>
  <wsdl:binding name="BidsSOAP"><wsdl:operation name="set"/></wsdl:binding>
</wsdl:definitions>
"""


def test_a_wsdl_yields_one_soap_operation_per_port_operation():
    get, set_ = api_surface.wsdl_operations(WSDL, address="/v5/bids", group="bids")
    assert (set_.method, set_.base, set_.path, set_.name) == ("SOAP", "/v5", "/bids", "set")
    assert (set_.group, set_.source) == ("bids", "wsdl")
    assert (set_.request, set_.response) == (("Bids",), ("SetResults",))
    # An operation without messages has no fields; the binding's copy of an operation is not one.
    assert (get.name, get.request, get.response) == ("get", (), ())


def test_fetch_reads_one_wsdl_per_part_or_a_single_one(monkeypatch):
    direct = api_surface.SOURCES["direct"]
    _serve(
        monkeypatch,
        {
            **{direct.url.format(service=part): WSDL for part in direct.parts},
            api_surface.SOURCES["speller"].url: WSDL,
        },
    )
    operations = api_surface.fetch("direct")
    assert len(operations) == 2 * len(direct.parts)
    assert {operation.group for operation in operations} == set(direct.parts)
    # Direct is listed by its JSON address, which takes the WSDL's operations by name (#276).
    assert {(o.method, o.base, o.path) for o in operations if o.group == "vcards"} == {
        ("POST", "/json/v5", "/vcards")
    }
    speller = api_surface.fetch("speller")
    assert {(o.method, o.base, o.path, o.group) for o in speller} == {
        ("SOAP", "", "/services/spellservice", "services")
    }


def _generated(method: str, address: str) -> str:
    """A reference page as Diplodoc generates it from an OpenAPI document."""
    return (
        "---\ntitle: x\n---\n# Title\n\n## Request\n\n"
        f'<div class="openapi__request">\n\n{method} {{.openapi__method}}\n'
        f"```text translate=no\n{address}\n```\n\n</div>\n"
    )


def test_a_generated_reference_page_states_one_operation():
    text = _generated(
        "DELETE", "https://api360.yandex.net/directory/v1/org/{orgId}/domains/{domain}"
    )
    assert api_surface.page_operations("ref/DomainService/DomainService_Delete", text) == [
        Operation(
            "DELETE",
            "/org/{orgId}/domains/{domain}",
            base="/directory/v1",
            name="DomainService_Delete",
            group="DomainService",
            source="docs",
            page="ref/DomainService/DomainService_Delete",
        )
    ]
    assert api_surface.page_operations("access", "---\nHow to get a token.") == []
    newer = _generated(
        "GET", "https://cloud-api.yandex.net/v1/api360/directory/org/{org_id}/groups"
    )
    (group,) = api_surface.page_operations("directory/get-groups", newer, "/api360")
    assert (group.base, group.path) == ("/v1/api360", "/directory/org/{org_id}/groups")
    # The folder Diplodoc generates into is not a group; the one above it is.
    (logs,) = api_surface.page_operations("logs/openapi/createLogRequest", text)
    assert (logs.name, logs.group) == ("createLogRequest", "logs")


@pytest.mark.parametrize(
    ("text", "method", "base", "path"),
    [
        # A line with the method and the full address; a placeholder may link to its description.
        (
            "```\nDELETE https://api.webmaster.yandex.net/v4/user/{[user-id](*user-id)}"
            "/hosts/{[host-id](*host-id)}\n```",
            "DELETE",
            "/v4",
            "/user/{user-id}/hosts/{host-id}",
        ),
        # A placeholder of alternatives written with spaces is read whole.
        (
            "GET https://api.appmetrica.yandex.ru/logs/v1/export/clicks.{csv | json}\n",
            "GET",
            "/logs/v1",
            "/export/clicks.{csv|json}",
        ),
        # A request line with its Host header, which may carry a scheme.
        ("POST /token HTTP/1.1\nHost: https://oauth.yandex.ru/\n", "POST", "", "/token"),
        # A labelled method, then the address in a code span.
        (
            "HTTP метод: `POST`\n\nURL: `https://botapi.messenger.yandex.net/bot/v1/messages/sendText/`\n",
            "POST",
            "/bot/v1",
            "/messages/sendText",
        ),
        # ... or in a block, with the query spelled out below it.
        (
            "Метод: ##POST##.\n\n```\nhttps://cloud-api.yandex.net/v1/disk/resources/move\n"
            " ? from=<x>\n```",
            "POST",
            "/v1",
            "/disk/resources/move",
        ),
    ],
)
def test_a_handwritten_page_states_its_request_in_one_of_three_forms(text, method, base, path):
    (operation,) = api_surface.page_operations("reference/the-page", f"---\n---\n{text}")
    assert (operation.method, operation.base, operation.path) == (method, base, path)
    assert (operation.name, operation.source) == ("the-page", "docs")
    assert operation.group == api_surface.first_noun(path)


def test_what_is_not_a_request_is_not_read_as_one():
    text = (
        "Метод: POST, see [the page](https://yandex.ru/dev/x/doc/ru/refund.md)\n\n"
        "Метод: POST\n`https://oauth.yandex.ru/`\n\n"
        "GET /only/an/example HTTP/1.1\n"
    )
    # A link into the documentation, a host alone, a request line with no Host header.
    assert api_surface.page_operations("p", text) == []


def test_an_example_on_the_page_folds_into_its_request_whatever_its_method():
    text = (
        "DELETE https://api.appmetrica.yandex.ru/management/v1/application/{id}/grant\n"
        "GET /management/v1/application/1111/grant HTTP/1.1\nHost: api.appmetrica.yandex.ru\n"
    )
    (operation,) = api_surface.page_operations("access/delete", text)
    assert (operation.method, operation.path) == ("DELETE", "/application/{id}/grant")


def test_fetch_reads_a_sitemap_and_folds_examples_across_pages(monkeypatch):
    source = api_surface.SOURCES["travel"]
    root = source.url.rpartition("/")[0]
    host = "https://whitelabel.travel.yandex-net.ru"
    sitemap = "".join(
        f"<url><loc>{root}/{page}</loc></url>"
        for page in ("ru/", "ru/booking-getOrder", "ru/examples", "en/booking-getOrder")
    )
    asked = _serve(
        monkeypatch,
        {
            source.url: sitemap,
            f"{root}/ru/booking-getOrder.md": f"---\nGET {host}/v2/orders/{{order_id}}\n",
            f"{root}/ru/examples.md": f"---\nGET {host}/v2/orders/12345\n",
        },
    )
    (operation,) = api_surface.fetch("travel")
    assert (operation.base, operation.path, operation.name) == (
        "/v2",
        "/orders/{order_id}",
        "booking-getOrder",
    )
    # The landing page of the language and the other language are not asked.
    assert len(asked) == 3


def test_documentation_adds_what_a_specification_leaves_out(monkeypatch):
    source = api_surface.SOURCES["disk"]
    root = source.docs.rpartition("/")[0]
    _serve(
        monkeypatch,
        {
            source.url: json.dumps(SWAGGER_LISTING),
            f"{SWAGGER_LISTING['basePath']}/v1/disk/resources": json.dumps(SWAGGER_RESOURCE),
            source.docs: (
                f"<loc>{root}/ru/reference/meta</loc><loc>{root}/ru/reference/shd-del</loc>"
            ),
            f"{root}/ru/reference/meta.md": (
                "---\nMethod: ##GET##.\n\n```\nhttps://cloud-api.yandex.net/v1/disk/resources\n```"
            ),
            f"{root}/ru/reference/shd-del.md": (
                "---\nMethod: ##DELETE##.\n\n```\nhttps://cloud-api.yandex.net/v1/disk/virtual-disks\n```"
            ),
        },
    )
    operations = api_surface.fetch("disk")
    assert [(o.method, o.path, o.name, o.source) for o in operations] == [
        # The specification's operation keeps the service's own name ...
        ("GET", "/resources", "GetResource", "swagger"),
        ("PATCH", "/resources", "UpdateResource", "swagger"),
        # ... and the one only the documentation describes is added, marked as such.
        ("DELETE", "/virtual-disks", "shd-del", "docs"),
    ]
    assert {operation.base for operation in operations} == {"/v1/disk"}


def test_a_service_without_a_snapshot_says_why():
    assert not set(api_surface.NOT_LISTED) & set(api_surface.LISTED)
    assert all(api_surface.NOT_LISTED.values())


def test_fetch_reads_the_pages_an_index_lists(monkeypatch):
    source = api_surface.SOURCES["audience"]
    root = source.url.rpartition("/")[0]
    index = "\n".join(
        [
            f"- [Segments]({root}/ref/openapi/segments/getSegments.md)",
            f"- [The same, linked twice]({root}/ref/openapi/segments/getSegments.md)",
            f"- [Delete]({root}/ref/openapi/segments/deleteSegment.md)",
            f"- [Prose]({root}/intro.md)",
            "- [Another product](https://yandex.ru/dev/metrika/ru/intro.md)",
        ]
    )
    host = "https://api-audience.yandex.ru"
    asked = _serve(
        monkeypatch,
        {
            source.url: index,
            f"{root}/ref/openapi/segments/getSegments.md": _generated(
                "GET", f"{host}/v1/management/segments"
            ),
            f"{root}/ref/openapi/segments/deleteSegment.md": _generated(
                "DELETE", f"{host}/v1/management/segment/{{segmentId}}"
            ),
            f"{root}/intro.md": "---\nProse only.",
        },
    )
    delete, get = api_surface.fetch("audience")
    assert (get.method, get.base, get.path) == ("GET", "/v1", "/management/segments")
    assert (get.name, get.group, get.page) == (
        "getSegments",
        "segments",
        "ref/openapi/segments/getSegments",
    )
    assert (delete.name, delete.path) == ("deleteSegment", "/management/segment/{segmentId}")
    # A page of another product is not this service's, and a page is asked once.
    assert len(asked) == 4


def test_fetch_of_a_docs_service_fails_loudly(monkeypatch):
    source = api_surface.SOURCES["admetrica"]
    root = source.url.rpartition("/")[0]
    _serve(monkeypatch, {source.url: "nothing here"})
    with pytest.raises(SystemExit, match="lists no page"):
        api_surface.fetch("admetrica")
    _serve(
        monkeypatch,
        {source.url: f"- [x]({root}/get.md)", f"{root}/get.md": "<html>Are you a robot?</html>"},
    )
    with pytest.raises(SystemExit, match="get is not a reference page"):
        api_surface.fetch("admetrica")


def test_one_path_under_two_bases_is_two_operations():
    """Metrika serves `/counters` under `/management/v1` and under `/stat/v1`-like bases."""
    first = Operation("GET", "/counters", base="/management/v1", source="docs")
    second = Operation("GET", "/counters", base="/export/v1", source="docs")
    assert len(api_surface._merged([first, second, first])) == 2


def test_a_snapshot_keeps_a_name_that_is_not_ascii(monkeypatch, tmp_path):
    """Forms tags its operations in Russian; the snapshot shows the tag as it is."""
    monkeypatch.setattr(api_surface, "SNAPSHOTS", tmp_path)
    operation = Operation(
        "GET", "/answers", base="/v1", name="get", group="ответы", source="openapi"
    )
    (tmp_path / "forms.json").write_text(api_surface.dump([operation]), encoding="utf-8")
    assert "ответы" in (tmp_path / "forms.json").read_text(encoding="utf-8")
    assert api_surface.load("forms") == [operation]


def test_fetch_refuses_a_page_that_is_not_a_reference_page(monkeypatch):
    """A block page answers 200 too; read as prose it would look like a removed operation."""
    base = "https://yandex.ru/support/tracker/en/api"
    _serve(
        monkeypatch,
        {
            api_surface.TRACKER_INDEX: f"- [x]({base}/get.md)",
            f"{base}/get.md": "<html>Are you a robot?</html>",
        },
    )
    with pytest.raises(SystemExit, match="api/get is not a reference page"):
        api_surface.fetch("tracker")


def test_fetch_asks_a_busy_server_again(monkeypatch):
    answers = iter([httpx2.Response(503), httpx2.Response(200, text=json.dumps(OPENAPI))])
    transport = httpx2.MockTransport(lambda request: next(answers))
    monkeypatch.setattr(api_surface, "_client", lambda: httpx2.Client(transport=transport))
    assert len(api_surface.fetch("forms")) == 3


def test_fetch_fails_loudly(monkeypatch):
    _serve(
        monkeypatch, {api_surface.OPENAPI_URLS["forms"]: 503, api_surface.TRACKER_INDEX: "nothing"}
    )
    with pytest.raises(SystemExit, match="answered 503"):
        api_surface.fetch("forms")
    with pytest.raises(SystemExit, match="lists no API reference page"):
        api_surface.fetch("tracker")


@pytest.mark.parametrize("service", api_surface.LISTED)
def test_committed_snapshot_is_canonical(service):
    """A snapshot is exactly what ``dump`` writes: sorted, one row per operation.

    An operation is its method and path; several operations of a WSDL share both and differ
    by name.
    """
    operations = api_surface.load(service)
    keys = [(*operation.key, operation.base, operation.name) for operation in operations]
    assert operations and len(keys) == len(set(keys))
    if service in api_surface.SERVICES:  # the comparison matches by method and path alone
        assert len({operation.key for operation in operations}) == len(operations)
    text = (api_surface.SNAPSHOTS / f"{service}.json").read_text(encoding="utf-8")
    assert text == api_surface.dump(operations)
    assert operations == sorted(
        operations, key=lambda operation: (operation.path, operation.method, operation.name)
    )
    assert all(operation.source for operation in operations)


def test_the_compared_services_are_the_registry():
    """A service is compared with ycli once it is in the registry; nothing marks it by hand."""
    assert set(api_surface.SERVICES) == {service.name for service in SERVICES}
    assert set(api_surface.SERVICES) <= set(api_surface.LISTED)


def test_every_snapshot_file_is_a_listed_service():
    files = {path.stem for path in api_surface.SNAPSHOTS.glob("*.json")}
    assert files == set(api_surface.LISTED)


def _listed_only() -> list[str]:
    """The listed services ycli does not cover: the ones outside the registry."""
    covered = {service.name for service in SERVICES}
    return [service for service in api_surface.LISTED if service not in covered]


def test_a_listed_only_service_never_enters_the_gaps(capsys):
    """Its operations are not "unwrapped": ycli does not cover the service at all yet."""
    assert _listed_only()
    assert api_drift.main([]) == 0
    out = capsys.readouterr().out
    for service in _listed_only():
        assert f"{service}:" not in out, service
    assert {drift.service for drift in api_drift.drifts()} == set(api_surface.SERVICES)


def test_a_service_wrapped_by_sections_is_compared_in_the_sections_begun():
    """A section counts from its first wrapped operation; the ones not begun are only listed.

    Both sides: in a begun section an operation without a wrapper is missing, as anywhere; a
    service that is not wrapped by sections has every unwrapped operation missing.
    """
    published = [
        Operation("POST", "/rpc/getWorkbook", name="getWorkbook", group="Workbook"),
        Operation("POST", "/rpc/deleteWorkbook", name="deleteWorkbook", group="Workbook"),
        Operation("POST", "/rpc/getDashboard", name="getDashboard", group="Dashboard"),
    ]
    sent = [Call("datalens.workbooks.get", "POST", "/rpc/getWorkbook", frozenset(), None)]
    assert "datalens" in api_surface.BY_SECTION
    by_section = compare("datalens", published, sent)
    assert [operation.name for operation in by_section.not_wrapped] == ["deleteWorkbook"]
    assert [operation.name for operation in by_section.pending] == ["getDashboard"]
    whole = compare("forms", published, sent)
    assert [operation.name for operation in whole.not_wrapped] == ["deleteWorkbook", "getDashboard"]
    assert whole.pending == ()
    assert by_section.wrapped == whole.wrapped == 1
    # Nothing wrapped yet: no section is begun, so nothing is missing.
    assert compare("datalens", published, []).not_wrapped == ()


def test_a_listed_only_service_that_is_compared_is_caught(monkeypatch, capsys):
    """The probe: compared by mistake, Telemost would be reported as nine unwrapped operations."""
    monkeypatch.setattr(api_surface, "SERVICES", (*api_surface.SERVICES, "telemost"))
    with pytest.raises(AssertionError):
        test_the_compared_services_are_the_registry()
    with pytest.raises((AssertionError, SystemExit)):
        test_a_listed_only_service_never_enters_the_gaps(capsys)


def _call(operation: str, method: str, path: str, **parts) -> Call:
    return Call(
        operation,
        method,
        path,
        query=frozenset(parts.get("query", ())),
        response=frozenset(parts["response"]) if "response" in parts else None,
        request=frozenset(parts["request"]) if "request" in parts else None,
    )


PUBLISHED = [
    Operation("GET", "/pages/{idx}", query=("fields", "revision_id"), response=("id", "slug")),
    Operation("GET", "/pages/descendants", query=("cursor",)),
    Operation("POST", "/pages", request=("title",), response=("id",)),
    Operation("DELETE", "/pages/{idx}"),
    Operation("GET", "/legacy"),
]


def test_compare_reports_every_kind_of_difference(monkeypatch):
    monkeypatch.setitem(api_drift.NOT_WRAPPED, ("wiki", "GET", "/legacy"), "replaced")
    sent = [
        _call("wiki.pages.get", "GET", "/pages/7", query=("fields", "raw"), response=("id", "x")),
        _call("wiki.pages.descendants_list", "GET", "/pages/descendants", query=("cursor",)),
        _call("wiki.pages.create", "POST", "/pages", response=("id", "slug")),
        _call("wiki.pages.purge", "POST", "/pages/7/purge"),
    ]
    drift = compare("wiki", PUBLISHED, sent)
    assert [operation.path for operation in drift.not_wrapped] == ["/pages/{idx}"]
    assert [(operation.path, why) for operation, why in drift.excluded] == [("/legacy", "replaced")]
    assert [call.operation for call in drift.unpublished] == ["wiki.pages.purge"]
    assert drift.wrapped == 3
    get, create = drift.gaps
    assert get.operations == ("wiki.pages.get",)
    assert (get.missing_query, get.unknown_query) == (("revision_id",), ("raw",))
    assert (get.untyped_response, get.unknown_response) == (("slug",), ("x",))
    assert create.unknown_response == ("slug",) and not create.untyped_response


def test_compare_reports_body_fields_only_for_a_typed_body():
    published = [Operation("POST", "/pages", request=("title", "slug"))]
    typed = _call("wiki.pages.create", "POST", "/pages", request=("title", "typo"))
    drift = compare("wiki", published, [typed])
    (gap,) = drift.gaps
    assert (gap.missing_request, gap.unknown_request) == (("slug",), ("typo",))
    assert (drift.bodies_compared, drift.bodies_published) == (1, 1)
    # A free-form body, or one that takes any field, says nothing about what ycli can send.
    free_form = compare("wiki", published, [_call("wiki.pages.create", "POST", "/pages")])
    assert free_form.gaps == () and (free_form.bodies_compared, free_form.bodies_published) == (
        0,
        1,
    )


def test_a_typed_body_lists_its_fields_and_an_open_one_does_not():
    by_operation = {call.operation: call for call in api_drift.calls()}
    assert {"name", "language"} <= (by_operation["forms.surveys.create"].request or set())
    assert by_operation["tracker.issues.create"].request is None  # extra="allow": any field
    assert by_operation["wiki.pages.get"].request is None  # no body


def test_compare_trusts_a_reference_page_only_for_what_it_lists():
    """Tracker pages are prose: a parameter ycli sends and the page omits is no finding."""
    published = [Operation("GET", "/issues/{issue_ID}", query=("expand",), page="api/issues/get")]
    sent = [
        _call("tracker.issues.get", "GET", "/issues/DE-7", query=("perPage",), response=("id",))
    ]
    (gap,) = compare("tracker", published, sent).gaps
    assert gap.missing_query == ("expand",)
    assert not (gap.unknown_query or gap.untyped_response or gap.unknown_response)


def test_replaying_the_cases_yields_what_each_operation_sends():
    sent = api_drift.calls()
    assert {call.operation for call in sent} == {case.operation for case in load_cases()}
    by_operation = {call.operation: call for call in sent}
    get = by_operation["wiki.pages.get"]
    # `fields` is declared on the endpoint even when a case leaves it out; `slug` is always sent.
    assert (get.method, get.path) == ("GET", "/pages") and {"slug", "fields"} <= get.query
    assert get.response is not None and "id" in get.response
    descendants = by_operation["wiki.pages.descendants_list"]
    # The pager reads the envelope, and its cursor counts though the case has one page.
    assert descendants.response is None and "cursor" in descendants.query


def test_every_published_operation_is_wrapped_or_excluded_on_purpose():
    """A refreshed snapshot that gains an operation fails here until ycli wraps or excludes it."""
    drifts = api_drift.drifts()
    assert {drift.service: drift.not_wrapped for drift in drifts} == dict.fromkeys(
        api_surface.SERVICES, ()
    )
    excluded = {(drift.service, *op.key) for drift in drifts for op, _ in drift.excluded}
    assert excluded == set(api_drift.NOT_WRAPPED), (
        "NOT_WRAPPED names an operation Yandex no longer publishes"
    )


def test_no_service_has_an_unexplained_difference_or_a_stale_reason():
    """A difference with the published API is fixed or carries its reason (#196).

    A refreshed snapshot that gains a parameter or a field fails here until ycli sends or reads
    it, or the difference is listed in ``EXPLAINED`` / ``EXPLAINED_EVERYWHERE``, or the body
    field carries the ``IGNORED_BY_API`` mark; a reason or a mark whose difference is gone fails
    as well.
    """
    bare, stale = api_drift.unexplained(
        api_drift.drifts(), api_drift.explained(), api_drift.EXPLAINED_EVERYWHERE
    )
    assert not bare, "differs from the published API with no reason:\n" + "\n".join(bare)
    assert not stale, "explains a difference that is gone:\n" + "\n".join(stale)


def test_the_explained_check_bites_in_both_directions():
    """A field added to a snapshot is reported until explained; a spare reason is reported too."""
    sent = [_call("wiki.pages.get", "GET", "/pages/7", query=("fields",), response=("id",))]
    agreed = [Operation("GET", "/pages/{idx}", query=("fields",), response=("id",))]
    assert api_drift.unexplained([compare("wiki", agreed, sent)], {}, {}) == ([], [])

    grown = [Operation("GET", "/pages/{idx}", query=("fields", "depth"), response=("id", "tags"))]
    drift = compare("wiki", grown, sent)
    assert api_drift.unexplained([drift], {}, {}) == (
        [
            "wiki GET /pages/{} missing_query depth",
            "wiki GET /pages/{} untyped_response tags",
        ],
        [],
    )
    per_operation = {("wiki", "GET", "/pages/{}", "missing_query", "depth"): "paging only"}
    per_name = {("wiki", "untyped_response", "tags"): "always empty"}
    assert api_drift.unexplained([drift], per_operation, per_name) == ([], [])

    spare = {
        **per_operation,
        ("wiki", "GET", "/pages/{}", "missing_query", "gone"): "was removed",
        ("forms", "GET", "/surveys", "missing_query", "x"): "another service is not judged",
    }
    assert api_drift.unexplained(
        [drift], spare, {**per_name, ("wiki", "unknown_query", "y"): ""}
    ) == (
        [],
        ["wiki GET /pages/{} missing_query gone", "wiki unknown_query y"],
    )


# A marked field the comparison cannot see: its name is published for another question type.
def test_a_body_field_is_explained_where_it_is_declared():
    """A body field that differs says why in the code: a mark in its description or above it.

    ``IGNORED_BY_API`` at the start of the description is what a caller reads in ``--help``, in
    the MCP input schema and on the site, and what makes setting the field log a warning;
    ``# violation(api-drift): <reason>`` above the field is for a reason of ycli's own. The
    comparison takes its reasons from both. Both directions on the real code: with the marks
    every difference is explained and none is stale; without them the marked fields are
    differences with no reason; and a mark on a field that makes no difference is stale unless
    ``IGNORED_THOUGH_PUBLISHED`` names it.
    """
    drifts = api_drift.drifts()
    ignored = api_drift.ignored_marks()
    departures = set(api_drift.violation_marks())
    assert ignored >= api_drift.IGNORED_THOUGH_PUBLISHED
    assert departures and not departures & ignored
    bare, _ = api_drift.unexplained(drifts, api_drift.EXPLAINED, api_drift.EXPLAINED_EVERYWHERE)
    assert sorted(bare) == sorted(
        " ".join((service, method, path, "unknown_request", name))
        for service, method, path, name in (ignored - api_drift.IGNORED_THOUGH_PUBLISHED)
        | departures
    )
    every_mark = {
        (service, method, path, "unknown_request", name): api_drift.IGNORED
        for service, method, path, name in ignored | departures
    }
    _, stale = api_drift.unexplained(
        drifts, {**every_mark, **api_drift.EXPLAINED}, api_drift.EXPLAINED_EVERYWHERE
    )
    assert sorted(stale) == sorted(
        " ".join((service, method, path, "unknown_request", name))
        for service, method, path, name in api_drift.IGNORED_THOUGH_PUBLISHED
    )


def test_a_departure_marker_is_read_with_its_reason_and_none_is_left_unread():
    """``# violation(api-drift)`` above a body field gives the comparison its reason.

    A marker that stands above something the comparison does not read (not a field of a body
    model) would explain nothing and hide nothing, so every one in the package must be read.
    """
    from ycli.yandex.forms.subscriptions.models import EmailSubscription, SubscriptionHeader

    reason, path, line = api_drift.marked_fields(EmailSubscription)["id"]
    assert reason == "one model builds the body and reads the reply, which carries `id`"
    assert path.endswith("forms/subscriptions/models.py") and line > 1
    assert api_drift.marked_fields(SubscriptionHeader) == {}
    marks = api_drift.violation_marks()
    assert {key[-1] for key in marks} == {"id"}
    assert (
        api_drift.explained()[
            "forms", "POST", "/surveys/{}/hooks/{}/subscriptions", "unknown_request", "id"
        ]
        == reason
    )
    read = {(path, line) for _, path, line in marks.values()}
    written = {
        (str(path), marker)
        for path in sorted(SRC.rglob("*.py"))
        for marker in violation_markers(
            path.read_text(encoding="utf-8"), api_drift.MARKER_RULE
        ).values()
    }
    assert written == read


def test_the_ignored_mark_warns_when_the_field_is_set(caplog):
    from ycli.yandex.forms.questions.models import Question
    from ycli.yandex.forms.surveys.models import Survey, SurveyCreate

    SurveyCreate(name="Quiet")
    SurveyCreate(name="Unset", is_published=None)  # what the CLI passes without the option
    # A reply that carries the same names is read without a word: only a body warns.
    Survey.model_validate({"id": "686d", "is_published": True, "is_public": True, "language": "ru"})
    Question.model_validate({"id": 7, "type": "series", "items": [{"id": 8, "type": "string"}]})
    assert caplog.records == []
    SurveyCreate(name="Loud", is_published=True)
    assert [record.getMessage() for record in caplog.records] == [
        "`is_published` is ignored by the API: publish a form with ``surveys publish`` instead."
    ]


def test_two_arguments_sharing_a_value_stop_the_report(monkeypatch):
    def clash() -> list[api_drift.Drift]:
        raise ValueError("wiki.x: ['a', 'b'] share the value '7'")

    monkeypatch.setattr(api_drift, "drifts", clash)
    with pytest.raises(SystemExit, match=r"api_drift: wiki\.x"):
        api_drift.main([])


def test_changes_lists_added_removed_and_altered_operations():
    old = [Operation("GET", "/a", query=("x",), response=("id",)), Operation("GET", "/gone")]
    new = [Operation("GET", "/a", query=("y",), response=("id", "name")), Operation("POST", "/a")]
    assert api_drift.changes(old, new) == [
        "- added `POST /a`",
        "- removed `GET /gone`",
        "- `GET /a`: query +`y` -`x`; response +`name`",
    ]
    # A renamed placeholder is the same operation.
    assert api_drift.changes([Operation("GET", "/a/{id}")], [Operation("GET", "/a/{idx}")]) == []


def test_live_mode_is_quiet_while_the_api_matches_the_snapshot(monkeypatch, capsys):
    monkeypatch.setattr(api_surface, "fetch", api_surface.load)
    assert api_drift.main(["--live"]) == 0
    assert capsys.readouterr().out == ""


def test_live_mode_reports_what_yandex_changed(monkeypatch, capsys):
    def fetch(service: str) -> list[Operation]:
        operations = api_surface.load(service)
        return [*operations, Operation("PUT", "/brand-new")] if service == "forms" else operations

    monkeypatch.setattr(api_surface, "fetch", fetch)
    assert api_drift.main(["--live"]) == 0
    assert capsys.readouterr().out == "### Forms\n\n- added `PUT /brand-new`\n"


def test_refresh_rewrites_the_snapshots(monkeypatch, tmp_path):
    monkeypatch.setattr(api_surface, "SNAPSHOTS", tmp_path)
    monkeypatch.setattr(api_surface, "fetch", lambda service: [Operation("GET", f"/{service}")])
    assert api_drift.main(["--refresh"]) == 0
    assert api_surface.load("wiki") == [Operation("GET", "/wiki")]
    assert (tmp_path / "tracker.json").read_text(encoding="utf-8") == (
        '[\n{"method": "GET", "path": "/tracker"}\n]\n'
    )
    # Every listed service is rewritten, the ones ycli does not cover yet included.
    assert {path.stem for path in tmp_path.glob("*.json")} == set(api_surface.LISTED)


def test_refresh_of_named_services_rewrites_only_those(monkeypatch, tmp_path):
    monkeypatch.setattr(api_surface, "SNAPSHOTS", tmp_path)
    monkeypatch.setattr(api_surface, "fetch", lambda service: [Operation("GET", f"/{service}")])
    assert api_drift.main(["--refresh", "disk", "wiki"]) == 0
    assert {path.stem for path in tmp_path.glob("*.json")} == {"disk", "wiki"}


def test_live_mode_asks_only_the_services_ycli_covers(monkeypatch):
    asked = []

    def fetch(service: str) -> list[Operation]:
        asked.append(service)
        return api_surface.load(service)

    monkeypatch.setattr(api_surface, "fetch", fetch)
    assert api_drift.main(["--live"]) == 0
    assert asked == list(api_surface.SERVICES)


def test_default_mode_prints_the_gaps(capsys):
    assert api_drift.main([]) == 0
    out = capsys.readouterr().out
    wiki = len(api_surface.load("wiki"))
    assert f"wiki: {wiki} of {wiki} published operations wrapped" in out
    assert "unknown_request: " in out


def test_a_pager_adds_its_parameters_where_it_sends_them():
    """A query pager's parameters are query parameters; a body pager's are fields of the body."""
    by_operation = {call.operation: call for call in api_drift.calls()}
    in_body = by_operation["datalens.collections.content_list"]
    assert in_body.query == frozenset()
    assert in_body.request is not None and {"page", "pageSize"} <= in_body.request
    in_query = by_operation["wiki.comments.list"]
    assert "cursor" in in_query.query


RPC_DOCUMENT = {
    "paths": {
        "/rpc/getThing": {"post": {"tags": ["Thing"], "responses": {"200": {}}}},
        "/rpc/dropThing": {"post": {"tags": ["Thing"], "responses": {"200": {}}}},
    }
}


def test_fetch_gives_an_rpc_operation_the_reference_page_the_docs_list(monkeypatch):
    """The page is read from the files there are: an operation without a file has none."""
    source = api_surface.SOURCES["datalens"]
    tree = {"tree": [{"path": "Things/rpcgetThing-post.md"}, {"path": "Things/index.md"}]}
    _serve(monkeypatch, {source.url: json.dumps(RPC_DOCUMENT), source.pages: json.dumps(tree)})
    pages = {operation.name: operation.page for operation in api_surface.fetch("datalens")}
    assert pages == {"getThing": "Things/rpcgetThing-post", "dropThing": ""}


@pytest.mark.parametrize(
    "tree",
    [
        {"tree": [{"path": "Things/rpcgetThing-post.md"}], "truncated": True},
        {"tree": [{"path": "Things/index.md"}]},
        {"message": "API rate limit exceeded"},
        # A section without its own page: the coverage tables link a resource to it.
        {"tree": [{"path": "Things/rpcgetThing-post.md"}]},
    ],
)
def test_a_listing_of_pages_that_is_cut_short_or_empty_stops_the_refresh(monkeypatch, tree):
    """A refresh must not write a snapshot that lost the pages it had."""
    source = api_surface.SOURCES["datalens"]
    _serve(monkeypatch, {source.url: json.dumps(RPC_DOCUMENT), source.pages: json.dumps(tree)})
    with pytest.raises(SystemExit, match=r"cut short or empty|no index\.md"):
        api_surface.fetch("datalens")
