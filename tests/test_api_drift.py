"""ycli against the API Yandex publishes: the snapshots, the comparison and the weekly check.

``scripts/api_surface.py`` reduces what Yandex publishes to operations; ``scripts/api_drift.py``
compares them with what the contract cases send. The network is never touched here: a fetch
runs against ``httpx2.MockTransport``.
"""

from __future__ import annotations

import doctest
import json

import httpx2
import pytest
from scripts import api_drift, api_surface
from scripts.api_drift import Call, compare
from scripts.api_surface import Operation

from tests.contract import load_cases

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
        )
    ]


def _query_cut(name: str) -> str:
    """A reference page's query-parameter block listing ``name``."""
    return f'{{% cut "Request parameters" %}}\n| {name} | Text |\n{{% endcut %}}'


def test_tracker_page_drops_path_parameters_and_prose_pages_yield_nothing():
    text = f"PATCH /v3/filters/{{filter_id}}\n{_query_cut('filter_id')}"
    assert api_surface.tracker_operations("x", text) == [
        Operation("PATCH", "/filters/{filter_id}", page="x")
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
        Operation(
            "GET",
            "/queues/<queue_id>/triggers",
            query=("expand", "id", "perPage", "version"),
            page="p",
        ),
        Operation("GET", "/queues/<queue_id>/triggers/_relative", query=("from",), page="p"),
        Operation("POST", "/worklog/_search", page="p"),
    ]


def _serve(monkeypatch, routes: dict[str, str | int]) -> list[str]:
    """Answer ``api_surface`` from ``routes`` (a body, or a status); returns the URLs asked."""
    asked: list[str] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        asked.append(str(request.url))
        answer = routes[str(request.url)]
        return (
            httpx2.Response(answer)
            if isinstance(answer, int)
            else httpx2.Response(200, text=answer)
        )

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
        Operation("POST", "/issues/_search", query=("expand", "scrollId"), page="api/search")
    ]
    assert f"{base}/common-format.md" not in asked


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


@pytest.mark.parametrize("service", api_surface.SERVICES)
def test_committed_snapshot_is_canonical(service):
    """A snapshot is exactly what ``dump`` writes: sorted, one operation per method and path."""
    operations = api_surface.load(service)
    keys = [operation.key for operation in operations]
    assert operations and len(keys) == len(set(keys))
    text = (api_surface.SNAPSHOTS / f"{service}.json").read_text(encoding="utf-8")
    assert text == api_surface.dump(operations)
    assert operations == sorted(
        operations, key=lambda operation: (operation.path, operation.method)
    )


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
        _call("wiki.pages.descendants", "GET", "/pages/descendants", query=("cursor",)),
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
    assert (get.dropped_response, get.unknown_response) == (("slug",), ("x",))
    assert create.unknown_response == ("slug",) and not create.dropped_response


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
    assert not (gap.unknown_query or gap.dropped_response or gap.unknown_response)


def test_replaying_the_cases_yields_what_each_operation_sends():
    sent = api_drift.calls()
    assert {call.operation for call in sent} == {case.operation for case in load_cases()}
    by_operation = {call.operation: call for call in sent}
    get = by_operation["wiki.pages.get"]
    # `fields` is declared on the endpoint even when a case leaves it out; `slug` is always sent.
    assert (get.method, get.path) == ("GET", "/pages") and {"slug", "fields"} <= get.query
    assert get.response is not None and "id" in get.response
    descendants = by_operation["wiki.pages.descendants"]
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
    it, or the difference is listed in ``EXPLAINED`` / ``EXPLAINED_EVERYWHERE``; a listed
    difference that is gone fails as well.
    """
    bare, stale = api_drift.unexplained(
        api_drift.drifts(), api_drift.EXPLAINED, api_drift.EXPLAINED_EVERYWHERE
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
            "wiki GET /pages/{} dropped_response tags",
        ],
        [],
    )
    per_operation = {("wiki", "GET", "/pages/{}", "missing_query", "depth"): "paging only"}
    per_name = {("wiki", "dropped_response", "tags"): "always empty"}
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
MARKED_BUT_PUBLISHED = {
    ("forms", "POST", "/surveys/{}/questions", "items"),
    ("forms", "PATCH", "/surveys/{}/questions/{}", "items"),
}


def test_a_field_the_api_ignores_says_so_where_it_is_declared():
    """An ``IGNORED`` reason and the ``IGNORED_BY_API`` mark of a body field go together.

    The reason keeps the comparison green; the mark is what a caller reads in ``--help``, in
    the MCP input schema and on the site, and what makes setting the field log a warning.
    """
    explained = {
        (service, method, path, name)
        for (service, method, path, kind, name), why in api_drift.EXPLAINED.items()
        if why == api_drift.IGNORED and kind == "unknown_request"
    }
    marked = api_drift.ignored_marks()
    assert explained - marked == set(), "explained as ignored, not marked in the body model"
    assert marked - explained == MARKED_BUT_PUBLISHED, "marked in the body model, not explained"


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


def test_default_mode_prints_the_gaps(capsys):
    assert api_drift.main([]) == 0
    out = capsys.readouterr().out
    wiki = len(api_surface.load("wiki"))
    assert f"wiki: {wiki} of {wiki} published operations wrapped" in out
    assert "unknown_request: " in out
