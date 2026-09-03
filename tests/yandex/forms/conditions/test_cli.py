"""TDD for `forms conditions` CLI (three family sub-apps; reads, writes, usage errors)."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import FORMS_BASE as BASE

pytestmark = pytest.mark.integration

SID = "6818ceffe010db4f59d11329"
QID = "17"
PID = 3
CID = 5
GROUP = {
    "id": CID,
    "operator": "and",
    "items": [{"type": "question", "condition": "eq", "question": "q1", "value": "yes"}],
}
ENVELOPE = {"operator": "and", "items": [GROUP]}
ITEM_JSON = '{"type": "question", "condition": "eq", "question": "q1", "value": "yes"}'
WIRE_BODY = {
    "operator": "and",
    "items": [{"type": "question", "condition": "eq", "question": "q1", "value": "yes"}],
}

FAMILIES = [
    ("question", f"surveys/{SID}/questions/{QID}/conditions", [SID, QID]),
    ("page", f"surveys/{SID}/pages/{PID}/conditions", [SID, str(PID)]),
    ("submit", f"surveys/{SID}/conditions", [SID]),
]
DELETE_DETAIL = {
    "question": f"deleted condition {CID} from question {QID}",
    "page": f"deleted condition {CID} from page {PID}",
    "submit": f"deleted condition {CID} from survey {SID}",
}
runner = CliRunner()


@pytest.mark.parametrize(("family", "path", "args"), FAMILIES)
@responses.activate
def test_list_dumps_envelope(family, path, args):
    responses.add(responses.GET, f"{BASE}/{path}", json=ENVELOPE, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "forms", "conditions", family, "list", *args])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["operator"] == "and"


@pytest.mark.parametrize(("family", "path", "args"), FAMILIES)
@responses.activate
def test_get_dumps_group(family, path, args):
    responses.add(responses.GET, f"{BASE}/{path}/{CID}", json=GROUP, status=200)
    res = runner.invoke(
        cli.app, ["--format", "json", "forms", "conditions", family, "get", *args, str(CID)]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == CID


@pytest.mark.parametrize(("family", "path", "args"), FAMILIES)
@responses.activate
def test_create_sends_typed_body(family, path, args):
    responses.add(responses.POST, f"{BASE}/{path}", json=GROUP, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "conditions",
            family,
            "create",
            *args,
            "--operator",
            "and",
            "--item",
            ITEM_JSON,
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == WIRE_BODY  # ty: ignore[invalid-argument-type]


@responses.activate
def test_create_accepts_body_file(tmp_path):
    responses.add(
        responses.POST, f"{BASE}/surveys/{SID}/questions/{QID}/conditions", json=GROUP, status=200
    )
    body_file = tmp_path / "group.json"
    body_file.write_text(json.dumps(WIRE_BODY), encoding="utf-8")
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "conditions",
            "question",
            "create",
            SID,
            QID,
            "--body-file",
            str(body_file),
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == WIRE_BODY  # ty: ignore[invalid-argument-type]


@responses.activate
def test_create_requires_operator_and_item_or_body_file():
    res = runner.invoke(cli.app, ["forms", "conditions", "question", "create", SID, QID])
    assert res.exit_code != 0
    assert len(responses.calls) == 0  # rejected at usage-error time; nothing was sent


@pytest.mark.parametrize(("family", "path", "args"), FAMILIES)
@responses.activate
def test_modify_patches_full_group(family, path, args):
    responses.add(responses.PATCH, f"{BASE}/{path}/{CID}", json=GROUP, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "conditions",
            family,
            "modify",
            *args,
            str(CID),
            "--operator",
            "and",
            "--item",
            ITEM_JSON,
        ],
    )
    assert res.exit_code == 0
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == WIRE_BODY  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(("family", "path", "args"), FAMILIES)
@responses.activate
def test_delete_dumps_ack(family, path, args):
    responses.add(responses.DELETE, f"{BASE}/{path}/{CID}", status=200)
    res = runner.invoke(
        cli.app, ["--format", "json", "forms", "conditions", family, "delete", *args, str(CID)]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": DELETE_DETAIL[family]}


@pytest.mark.parametrize(("family", "path", "args"), FAMILIES)
@responses.activate
def test_set_operator_sends_operator_body(family, path, args):
    responses.add(responses.PATCH, f"{BASE}/{path}", json=ENVELOPE, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "conditions",
            family,
            "set-operator",
            *args,
            "--operator",
            "or",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {"operator": "or"}  # ty: ignore[invalid-argument-type]
    assert json.loads(res.stdout)["operator"] == "and"  # the mocked envelope, verbatim


@responses.activate
def test_set_operator_rejects_bogus_operator():
    res = runner.invoke(
        cli.app, ["forms", "conditions", "question", "set-operator", SID, QID, "--operator", "xor"]
    )
    assert res.exit_code != 0
    assert len(responses.calls) == 0  # rejected at usage-error time; nothing was sent
