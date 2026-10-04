"""The kind of action of every listed operation: the rules, the hand decisions and their checks.

``scripts/api_kinds.py`` proposes a kind from the operation's own name and the shape of its
request; ``<service>.decisions.json`` decides what the script cannot, each row with a reason.
"""

from __future__ import annotations

import doctest
import json

import pytest
from scripts import api_kinds, api_surface
from scripts.api_kinds import Kind, classify, own_verb, proposed, shape_kind
from scripts.api_surface import Operation

BY = {"name", "shape", "name+shape", "hand"}


def test_docstring_examples_hold():
    """``scripts/`` is outside pytest's doctest paths, so its examples run here."""
    assert doctest.testmod(api_kinds).failed == 0


@pytest.mark.parametrize("service", api_surface.LISTED)
def test_every_operation_has_exactly_one_kind_from_the_closed_lists(service):
    rows = json.loads((api_surface.SNAPSHOTS / f"{service}.kinds.json").read_text("utf-8"))
    operations = api_surface.load(service)
    keys = [(row["method"], row.get("base", ""), row["path"], row.get("name", "")) for row in rows]
    assert keys == [(o.method, o.base, o.path, o.name) for o in operations]
    for row in rows:
        assert row["kind"] in api_kinds.KINDS, row
        assert row.get("aspect", "") in ("", *api_kinds.ASPECTS), row
        assert row["by"] in BY or row["by"].startswith("rule:"), row
        # A hand decision says why, and nothing else does.
        assert bool(row.get("why")) is (row["by"] == "hand"), row


@pytest.mark.parametrize("service", api_surface.LISTED)
def test_committed_kinds_are_what_the_script_writes(service):
    text = (api_surface.SNAPSHOTS / f"{service}.kinds.json").read_text(encoding="utf-8")
    assert text == api_kinds.dump(classify(service))


def test_every_decisions_file_belongs_to_a_listed_service():
    files = {path.name.split(".")[0] for path in api_surface.SNAPSHOTS.glob("*.decisions.json")}
    assert files <= set(api_surface.LISTED)
    assert {path.name.split(".")[0] for path in api_surface.SNAPSHOTS.glob("*.kinds.json")} == set(
        api_surface.LISTED
    )


@pytest.fixture
def one_service(monkeypatch, tmp_path):
    """A snapshot directory of the test's own, holding one service with two operations."""
    monkeypatch.setattr(api_surface, "SNAPSHOTS", tmp_path)
    operations = [
        Operation("GET", "/queues/{id}", base="/v3", name="get-queue", source="docs"),
        Operation("POST", "/queues/{id}", base="/v3", name="frob", source="docs"),
    ]
    (tmp_path / "tracker.json").write_text(api_surface.dump(operations), encoding="utf-8")

    def decide(*rows: dict[str, str]) -> None:
        (tmp_path / "tracker.decisions.json").write_text(json.dumps(list(rows)), encoding="utf-8")

    return decide


FROB = {"method": "POST", "base": "/v3", "path": "/queues/{id}", "name": "frob"}


def test_an_operation_without_a_kind_is_refused(one_service):
    """The probe: `frob` is no known verb and a POST to an item says nothing."""
    with pytest.raises(ValueError, match="1 operations have no kind: POST /v3/queues/"):
        classify("tracker")


def test_a_hand_decision_gives_it_one(one_service):
    one_service({**FROB, "kind": "state", "aspect": "bulk", "why": "it frobnicates"})
    get, frob = classify("tracker")
    assert (get.verb, get.kind, get.by, get.why) == ("get", "get", "name", "")
    assert frob == Kind(
        "POST",
        "/v3",
        "/queues/{id}",
        "frob",
        verb="",
        kind="state",
        aspect="bulk",
        by="hand",
        why="it frobnicates",
    )


def test_a_hand_decision_for_no_operation_is_refused(one_service):
    """The probe: a decision left behind by an operation that is gone."""
    gone = {"method": "DELETE", "base": "/v3", "path": "/gone", "kind": "delete", "why": "x"}
    one_service({**FROB, "kind": "state", "why": "it frobnicates"}, gone)
    with pytest.raises(ValueError, match="hand decisions for no operation"):
        classify("tracker")


@pytest.mark.parametrize(
    "decision",
    [
        {"kind": "frobnicate", "why": "not a kind of the closed list"},
        {"kind": "state", "aspect": "magic", "why": "not an aspect of the closed list"},
        {"kind": "state"},
        {"why": "no kind at all"},
    ],
)
def test_a_hand_decision_outside_the_closed_lists_or_without_a_reason_is_refused(
    one_service, decision
):
    one_service({**FROB, **decision})
    with pytest.raises(ValueError, match="needs a kind of"):
        classify("tracker")


@pytest.mark.parametrize(
    ("operation", "verb"),
    [
        (Operation("POST", "/rpc/getDashboard", name="getDashboard"), "get"),
        (Operation("PUT", "/resources/publish", name="PublishResource"), "publish"),
        (Operation("GET", "/x", name="wiki_api_v2_public_grids_views_get_grid_view"), "get"),
        (Operation("POST", "/json/v5/ads", name="add"), "add"),
        # A view's name carries its module path; what follows `_views_` names the operation.
        (
            Operation(
                "POST",
                "/upload_sessions/abort_active_uploads",
                name="wiki_api_v2_public_upload_sessions_views_abort_all_view",
            ),
            "abort",
        ),
        # A name without a verb leaves the address to say it.
        (Operation("POST", "/revoke_token", name="token-invalidate"), "revoke"),
        (Operation("GET", "/counters", name="counters"), ""),
        # A GET reads: another verb in its name belongs to the object.
        (Operation("GET", "/recrawl/queue", name="host-recrawl-get"), "get"),
        (Operation("GET", "/bulkchange/{id}", name="bulk-move-info"), "info"),
    ],
)
def test_the_apis_own_verb_is_read_from_the_name_then_from_the_address(operation, verb):
    assert own_verb(operation) == verb


@pytest.mark.parametrize(
    ("operation", "kind"),
    [
        (Operation("GET", "/queues/{id}"), "get"),
        (Operation("GET", "/queues"), "list"),
        (Operation("GET", "/issues/{id}/changelog"), "list"),
        (Operation("GET", "/issues/count"), "count"),
        (Operation("GET", "/disk/"), "get"),
        (Operation("GET", "/org/{id}/settings"), "get"),
        (Operation("GET", "/resources/download", name="GetResourceDownloadLink"), "get"),
        (Operation("GET", "/v2/campaigns", name="getCampaigns"), "list"),
        (Operation("POST", "/queues"), "create"),
        (Operation("POST", "/queues/{id}"), ""),
        (Operation("POST", "/surveys/{id}/publish"), ""),
        (Operation("PATCH", "/queues/{id}"), "update"),
        (Operation("PUT", "/queues/{id}"), "replace"),
        (Operation("DELETE", "/queues/{id}"), "delete"),
        (Operation("SOAP", "/services/spellservice"), ""),
    ],
)
def test_the_shape_of_a_request_suggests_a_kind_or_says_nothing(operation, kind):
    assert shape_kind(operation) == kind


@pytest.mark.parametrize(
    ("operation", "rpc", "expected"),
    [
        # The name decides, whatever the method.
        (Operation("PUT", "/resources/publish", name="PublishResource"), False, ("state", "name")),
        (Operation("PUT", "/projects/{id}", name="update-project"), False, ("update", "name")),
        # ... the shape turns a "get" of a collection into a list ...
        (Operation("GET", "/campaigns", name="getCampaigns"), False, ("list", "name+shape")),
        (Operation("GET", "/campaigns/{id}", name="getCampaign"), False, ("get", "name")),
        # ... and answers where the name has no verb.
        (Operation("GET", "/counters", name="counters"), False, ("list", "shape")),
        # A read through POST carries its filter in the body.
        (
            Operation("POST", "/offer-mappings", name="getOfferMappings"),
            False,
            ("search", "rule:read-by-post"),
        ),
        # In an RPC or SOAP service the method says nothing, so a get stays a get ...
        (Operation("POST", "/rpc/getDashboard", name="getDashboard"), True, ("get", "name")),
        # ... or a list when its object is plural: only the name tells one from many there.
        (
            Operation("POST", "/rpc/getWorkbookEntries", name="getWorkbookEntries"),
            True,
            ("list", "rule:plural"),
        ),
        (Operation("POST", "/rpc/getEntryStatus", name="getEntryStatus"), True, ("get", "name")),
        # ... unless its request takes a selection, as Direct's does.
        (
            Operation("POST", "/ads", name="get", request=("FieldNames", "SelectionCriteria")),
            True,
            ("search", "rule:selection"),
        ),
        # Adding to a set and removing from it are not creating and deleting.
        (
            Operation("PATCH", "/groups/{id}/members/add", name="GroupService_AddMembers"),
            False,
            ("add", "rule:membership"),
        ),
        (
            Operation("DELETE", "/groups/{id}/members/{m}", name="GroupService_DeleteMember"),
            False,
            ("remove", "rule:membership"),
        ),
        (Operation("POST", "/rpc/frobnicate", name="frobnicate"), True, ("", "")),
    ],
)
def test_the_script_proposes_a_kind_and_says_how(operation, rpc, expected):
    assert proposed(operation, rpc=rpc) == expected


@pytest.mark.parametrize(
    ("operation", "aspect"),
    [
        (Operation("GET", "/surveys/{id}/access"), "access"),
        (Operation("GET", "/conferences/{id}/cohosts"), "membership"),
        (Operation("POST", "/resources/upload", name="UploadExternalResource"), "file"),
        (Operation("POST", "/bulkchange/_move", name="bulk-move-issues"), "bulk"),
        (Operation("GET", "/operations/{id}", name="GetOperationStatus"), "long-running"),
        (Operation("GET", "/data", base="/stat/v1", name="data_1"), "report"),
        (Operation("GET", "/queues/{id}", name="get-queue"), ""),
    ],
)
def test_an_aspect_is_marked_by_the_words_of_the_name_and_the_address(operation, aspect):
    assert api_kinds.aspect_of(operation) == aspect


def test_check_names_a_stale_kinds_file(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(api_surface, "SNAPSHOTS", tmp_path)
    monkeypatch.setattr(api_surface, "LISTED", ("wiki",))
    operation = Operation("GET", "/pages/{idx}", base="/v1", name="get_page", source="openapi")
    (tmp_path / "wiki.json").write_text(api_surface.dump([operation]), encoding="utf-8")
    assert api_kinds.main(["--check"]) == 1
    assert "stale: wiki.kinds.json" in capsys.readouterr().err
    assert api_kinds.main([]) == 0
    assert api_kinds.main(["--check"]) == 0


def test_the_summary_counts_kinds_verbs_and_hand_decisions(capsys):
    assert api_kinds.main(["--summary"]) == 0
    out = capsys.readouterr().out
    total = sum(len(api_surface.load(service)) for service in api_surface.LISTED)
    assert out.startswith(f"{total} operations of {len(api_surface.LISTED)} services.")
    assert "| **all** |" in out and "| create |" in out and "| access |" in out
    by_hand = sum(len(api_kinds.decisions(service)) for service in api_surface.LISTED)
    assert f"Decided by hand: {by_hand} of {total}." in out
