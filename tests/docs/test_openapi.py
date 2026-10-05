"""The OpenAPI documents ``scripts/gen_openapi.py`` derives from ycli are valid and honest.

They are not committed (about a megabyte, rewritten by every model change): the docs workflow
generates them into the site. These tests build them in memory.
"""

from __future__ import annotations

import inspect

import pytest
import yaml
from openapi_spec_validator import validate
from scripts import api_drift, api_surface, gen_openapi

from tests.contract import Case, Reply, Sent, load_cases
from ycli.yandex.models import APIModel
from ycli.yandex.registry import SERVICES

DOCUMENTS = {service: gen_openapi.document(service) for service in api_surface.SERVICES}


def _operations(service: str) -> dict[tuple[str, str], dict]:
    return {
        (method.upper(), path): operation
        for path, item in DOCUMENTS[service]["paths"].items()
        for method, operation in item.items()
    }


@pytest.mark.parametrize("service", api_surface.SERVICES)
def test_document_is_valid_openapi(service):
    validate(DOCUMENTS[service])
    profile = next(found for found in SERVICES if found.name == service).profile
    assert DOCUMENTS[service]["servers"] == [{"url": profile.base_url}]
    assert "unofficial" in DOCUMENTS[service]["info"]["title"]


@pytest.mark.parametrize("service", api_surface.SERVICES)
def test_every_sdk_operation_is_in_its_document(service):
    listed = {
        f"{service}.{name}"
        for operation in _operations(service).values()
        for name in operation["x-ycli-operations"]
    }
    assert listed == {case.operation for case in load_cases() if case.domain == service}
    ids = [operation["operationId"] for operation in _operations(service).values()]
    assert len(ids) == len(set(ids))


def test_path_parameters_are_named_after_the_sdk_arguments():
    get = _operations("tracker")[("GET", "/issues/{issue_key}")]
    assert get["operationId"] == "issues_get" and get["x-ycli-effect"] == "read"
    key = {"name": "issue_key", "in": "path", "required": True, "schema": {"type": "string"}}
    assert get["parameters"][0] == key
    # No published page documents this request, so only the SDK's arguments name it.
    assert ("GET", "/attachments/{file_id}/{filename}") in _operations("tracker")


def test_a_segment_no_argument_supplied_takes_the_published_name():
    """An upload session id comes from an earlier reply, so the case holds it as a literal."""
    assert ("PUT", "/upload_sessions/{session_id}/upload_part") in _operations("wiki")
    paths = DOCUMENTS["wiki"]["paths"]
    assert not [path for path in paths if "3f2b1a0c" in path]


def test_two_arguments_with_one_value_are_refused():
    """Otherwise a path segment could be named after either (docs/conventions/testing.md)."""

    def move(source: str, target: str) -> None: ...

    case = Case(
        "tracker.issues.move",
        args=("DE-7", "DE-7"),
        cli=None,
        mcp=None,
        exchanges=[(Sent("POST", "issues/DE-7/_move"), Reply())],
    )
    with pytest.raises(ValueError, match=r"\['source', 'target'\] share the value 'DE-7'"):
        api_drift._template(case, move, "issues/DE-7/_move")
    assert inspect.signature(move).parameters  # the stub is only ever inspected


def test_a_typed_body_comes_from_the_request_model_and_a_free_form_one_says_so():
    create = _operations("tracker")[("POST", "/issues")]["requestBody"]
    assert create["x-ycli-body"] == "typed"
    reference = create["content"]["application/json"]["schema"]["$ref"]
    model = DOCUMENTS["tracker"]["components"]["schemas"][reference.rsplit("/", 1)[1]]
    assert "summary" in model["properties"]
    update = _operations("wiki")[("POST", "/pages/{page_id}")]["requestBody"]
    assert update["x-ycli-body"] == "typed"
    clear = _operations("tracker")[("POST", "/system/search/scroll/_clear")]["requestBody"]
    assert clear == {"content": {"application/json": {}}, "x-ycli-body": "untyped"}


def test_listings_say_how_they_page_and_keep_the_pager_parameters():
    listing = _operations("forms")[("GET", "/surveys")]
    assert listing["x-ycli-pagination"] == "OffsetLimitPagination"
    assert {"limit", "offset"} <= {parameter["name"] for parameter in listing["parameters"]}


@pytest.mark.parametrize("service", api_surface.SERVICES)
def test_schemas_use_the_api_field_names_and_say_which_models_are_closed(service):
    """A reply keeps unknown fields and a request body refuses them: the schema says the same."""
    schemas = DOCUMENTS[service]["components"]["schemas"]
    closed = {
        name for name, schema in schemas.items() if schema.get("additionalProperties") is False
    }
    for found in api_drift.recorded():
        if found.case.domain == service:
            replies = {model.__name__ for model in api_drift._models(found.endpoint.response_type)}
            assert not replies & closed, sorted(replies & closed)
    bodies = any("requestBody" in operation for operation in _operations(service).values())
    assert closed or not bodies, "no request body of the service is closed"
    for found in api_drift.recorded():
        for model in api_drift._models(found.endpoint.response_type):
            if found.case.domain != service or not issubclass(model, APIModel):
                continue
            aliased = {
                field.alias for name, field in model.model_fields.items() if field.alias != name
            } - {None}
            names = {name for name, field in model.model_fields.items() if field.alias}
            properties = set(schemas.get(model.__name__, {}).get("properties", aliased))
            assert aliased <= properties and not (names - aliased) & properties, model.__name__


def test_models_that_share_a_class_name_are_named_by_resource():
    """Tracker defines ``Comment`` for issues and for entities; neither name depends on order."""
    names = set(DOCUMENTS["tracker"]["components"]["schemas"])
    assert {"CommentsComment", "EntitiesComment"} <= names and "Comment" not in names
    for service in api_surface.SERVICES:
        schemas = DOCUMENTS[service]["components"]["schemas"]
        # pydantic numbers a name it meets twice; a generated class may end in a digit of
        # its own (``…Variant1``), so only a name numbered on top of its class counts.
        assert not [name for name in schemas if "__" in name]
        assert not [name for name in schemas if name[-1].isdigit() and name[:-1] in schemas]
    assert gen_openapi._readable("ycli__yandex__tracker__import___models__Link") == "ImportLink"


def test_a_generic_page_is_named_after_its_item():
    names = set(DOCUMENTS["wiki"]["components"]["schemas"])
    assert {"PageRefPage", "AttachmentPage", "CommentPage"} <= names
    assert not [name for name in names if name.startswith("CursorPage")]


def test_parameters_take_the_type_of_the_sdk_argument_or_of_the_value_sent():
    by_id = _operations("wiki")[("GET", "/pages/{page_id}")]
    assert by_id["parameters"][0]["schema"] == {"type": "integer"}  # ``page_id: int``
    listing = {
        p["name"]: p["schema"] for p in _operations("forms")[("GET", "/surveys")]["parameters"]
    }
    # The pager adds them to the request itself, so no value of theirs is seen: left untyped.
    assert (listing["limit"], listing["offset"]) == ({}, {})
    assert listing["published"] == {"type": "boolean"}  # ``published: bool | None``
    comments = _operations("tracker")[("GET", "/issues/{issue_key}/comments")]["parameters"]
    assert {"name": "perPage", "in": "query", "schema": {"type": "integer"}} in comments


@pytest.mark.parametrize(("service", "at_least"), [("tracker", 62), ("wiki", 35), ("forms", 31)])
def test_most_query_parameters_are_typed(service, at_least):
    """A floor, so a change that silently loses the types is seen."""
    query = [
        parameter
        for operation in _operations(service).values()
        for parameter in operation.get("parameters", [])
        if parameter["in"] == "query"
    ]
    assert sum(bool(parameter["schema"]) for parameter in query) >= at_least


def test_main_writes_one_file_per_service(tmp_path):
    assert gen_openapi.main([str(tmp_path / "openapi")]) == 0
    for service in api_surface.SERVICES:
        text = (tmp_path / "openapi" / f"{service}.yaml").read_text(encoding="utf-8")
        assert yaml.safe_load(text) == DOCUMENTS[service]
