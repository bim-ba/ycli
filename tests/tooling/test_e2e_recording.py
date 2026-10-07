"""Recording real replies as fixtures (``e2e/recording.py``, ``e2e/scrub.py``), offline.

The API is a ``httpx2.MockTransport`` here; everything between the command and the fixture
file is the real thing.
"""

from __future__ import annotations

import datetime
import json
from typing import TYPE_CHECKING, Any, Literal

import httpx2
import pytest
from e2e.models import Scenario
from e2e.recording import (
    InProcessDriver,
    NotAReadError,
    load,
    operations,
    recording,
    reply_type,
)
from e2e.runner import run_scenario
from e2e.scrub import DATE, DATE_TIME, scrub, strings
from pydantic import BaseModel

from tests.hosts import TRACKER_BASE

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from e2e.recording import Recorder

# What must never reach a fixture: a value, a key the model does not know, a key of a map.
PERSONAL_VALUE = "Ivan Petrov wrote this"
PERSONAL_KEY = "ivanPetrovsOwnField"
PERSONAL_MAP_KEY = "ivan.petrov"
ISSUE = {
    "key": "SECRET-7",
    "summary": PERSONAL_VALUE,
    "description": PERSONAL_VALUE,
    PERSONAL_KEY: PERSONAL_VALUE,
    "createdBy": {"id": "1130000012345678", "display": PERSONAL_VALUE},
    "tags": [PERSONAL_VALUE],
    "votes": 3,
}


class _API:
    """Answers every request with ``reply`` and remembers what it was asked."""

    def __init__(self, reply: Any) -> None:
        self.reply = reply
        self.calls: list[httpx2.Request] = []

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        self.calls.append(request)
        return httpx2.Response(200, json=self.reply)


@pytest.fixture
def api() -> _API:
    return _API(ISSUE)


@pytest.fixture
def recorder(api: _API, tmp_path: Path, monkeypatch) -> Iterator[Recorder]:
    with recording(monkeypatch, tmp_path / "replies", httpx2.MockTransport(api)) as recorder:
        yield recorder


def _driver() -> InProcessDriver:
    return InProcessDriver(pause_seconds=0)


def test_a_command_leaves_the_reply_of_its_operation_as_a_fixture(recorder, api, tmp_path):
    completed = _driver().run(["tracker", "issues", "get", "SECRET-7"])
    assert completed.exit_code == 0, completed.stderr
    assert str(api.calls[0].url) == f"{TRACKER_BASE}/issues/SECRET-7"
    assert list(recorder.recorded) == ["tracker.issues.get"]
    fixture = load(tmp_path / "replies" / "tracker" / "issues" / "get.json")
    assert fixture["status"] == 200
    assert fixture["body"]["summary"] == "<summary>"
    assert fixture["unknown_keys"] == len(recorder.unknown_keys["tracker.issues.get"]) > 0


def test_nothing_personal_reaches_the_file(recorder, api, tmp_path):
    """The probe: a personal string as a value, as an unknown key and as a key of a map."""
    api.reply = {**ISSUE, "localFields": {PERSONAL_MAP_KEY: PERSONAL_VALUE}}
    _driver().run(["tracker", "issues", "get", "SECRET-7"])
    text = (tmp_path / "replies" / "tracker" / "issues" / "get.json").read_text(encoding="utf-8")
    for personal in (
        PERSONAL_VALUE,
        PERSONAL_KEY,
        PERSONAL_MAP_KEY,
        "SECRET-7",
        "1130000012345678",
    ):
        assert personal not in text
    # The developer still learns which key the model does not know; a public log does not.
    assert PERSONAL_KEY in recorder.details()
    assert PERSONAL_KEY not in recorder.summary()


def test_the_probe_bites(tmp_path):
    """Written without scrubbing, the same reply carries every personal string."""
    kept = strings(ISSUE)
    assert {PERSONAL_VALUE, PERSONAL_KEY} <= kept


def test_the_fullest_reply_of_an_operation_is_kept(recorder, api, tmp_path):
    fixture = tmp_path / "replies" / "tracker" / "issues" / "get.json"
    _driver().run(["tracker", "issues", "get", "A-1"])
    api.reply = {"key": "A-2", "votes": 1}
    _driver().run(["tracker", "issues", "get", "A-2"])
    assert "summary" in load(fixture)["body"]  # a poorer reply does not replace a fuller one
    api.reply = {**ISSUE, "resolution": {"key": "fixed"}}
    _driver().run(["tracker", "issues", "get", "A-3"])
    assert "resolution" in load(fixture)["body"]


def test_a_failed_reply_is_not_a_fixture(recorder, tmp_path, monkeypatch):
    def refuse(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(404, json={"errorMessages": ["no such issue"]})

    with recording(monkeypatch, tmp_path / "other", httpx2.MockTransport(refuse)) as other:
        completed = _driver().run(["tracker", "issues", "get", "A-1"])
    assert completed.exit_code == 3
    assert "no such issue" in completed.stderr
    assert other.recorded == {}


def test_while_reads_run_nothing_else_leaves_the_process(recorder, api):
    recorder.reads_only = True
    with pytest.raises(NotAReadError, match="POST /v3/issues/ is not a read"):
        _driver().run(["tracker", "issues", "create", "--queue", "Q", "--summary", "S"])
    assert api.calls == []
    # A POST that only reads is a read: the endpoint says so, not the method.
    api.reply = [ISSUE]
    assert _driver().run(["tracker", "issues", "search", "Queue: Q"]).exit_code == 0
    assert [call.method for call in api.calls] == ["POST"]


def test_the_reads_of_a_step_run_right_after_it_and_dry(recorder, api):
    scenario = Scenario.model_validate(
        {
            "name": "s",
            "steps": [
                {
                    "id": "get",
                    "run": "tracker issues get A-1",
                    "save": {"key": "key"},
                    "reads": [
                        "tracker issues get ${key}",
                        "tracker issues create --queue Q --summary S",
                        "tracker issues get",
                    ],
                }
            ],
        }
    )
    run_scenario(scenario, _driver(), {}, read=recorder.read)
    # The write among the reads became a plan (--dry-run) and never reached the API.
    assert [call.method for call in api.calls] == ["GET", "GET"]
    assert api.calls[1].url.path == "/v3/issues/SECRET-7"
    assert len(recorder.failed_reads) == 1
    assert recorder.failed_reads[0].startswith("tracker issues get:")
    assert not recorder.reads_only


def test_without_a_reader_the_reads_are_not_run(api, recorder):
    step = {"id": "get", "run": "tracker issues get A-1", "reads": ["tracker issues get A-2"]}
    run_scenario(Scenario.model_validate({"name": "s", "steps": [step]}), _driver(), {})
    assert [call.url.path for call in api.calls] == ["/v3/issues/A-1"]


def test_every_operation_has_one_name():
    names = operations()
    assert "tracker.issues.get" in names
    assert all(len(name.split(".")) == 3 for name in names)


class _Status(BaseModel):
    key: Literal["open", "closed"] | str
    display: str
    since: datetime.datetime | None = None
    day: datetime.date | None = None
    order: Literal[7] | int = 0


class _Board(BaseModel):
    name: str
    statuses: list[_Status] = []
    counts: dict[str, int] = {}


def test_a_value_stays_only_where_the_model_lists_it():
    reply = {
        "key": "open",
        "display": "open",
        "since": "2026-10-06T10:00:00.000+0000",
        "day": "2026-10-06",
        "order": 7,
        "votes": 3,
        "id": 42,
        "big": 1_130_000_012_345_678,
        "ratio": 1_500_000.5,
        "done": True,
        "gone": None,
    }
    assert scrub(
        reply, _Status, frozenset({"votes", "id", "big", "ratio", "done", "gone"})
    ).body == {
        "key": "open",
        "display": "<display>",
        "since": DATE_TIME,
        "day": DATE,
        "order": 7,
        "votes": 3,
        "id": 1,
        "big": 1,
        "ratio": 1.0,
        "done": True,
        "gone": None,
    }


def test_a_list_keeps_one_item_of_each_shape_and_a_map_loses_its_keys():
    reply = {
        "name": "Sprint",
        "statuses": [
            {"key": "open", "display": "A"},
            {"key": "closed", "display": "B"},
            {"key": "custom", "display": "C", "since": "2026-10-06T10:00:00.000+0000"},
        ],
        "counts": {"ivan": 3, "anna": 5},
    }
    scrubbed = scrub(reply, _Board)
    assert scrubbed.body == {
        "name": "<name>",
        "statuses": [
            {"key": "<key>", "display": "<display>", "since": DATE_TIME},
            {"key": "closed", "display": "<display>"},
        ],
        # Numbered in the order of the names: anna, then ivan.
        "counts": {"<key-1>": 5, "<key-2>": 3},
    }
    assert scrubbed.unknown_keys == []
    again = scrub({**reply, "statuses": reply["statuses"][::-1]}, _Board)
    assert again.body == scrubbed.body  # the order of the reply does not reach the file


def test_an_unknown_key_keeps_its_name_only_when_the_name_is_public():
    reply = {"name": "Sprint", "published": "x", "ivansField": {"published": 1, "deep": "y"}}
    scrubbed = scrub(reply, _Board, frozenset({"published"}))
    assert scrubbed.body == {
        "name": "<name>",
        "published": "<published>",
        # Inside it no model reads anything, so even a public name does not stay.
        "<unknown-1>": {"<unknown-1>": "<unknown-1>", "<unknown-2>": 1},
    }
    # Only a position that has a model can say a key is unknown to it.
    assert scrubbed.unknown_keys == ["ivansField", "published"]


def test_a_reply_with_no_model_keeps_no_name():
    """Otherwise the file would change whenever ycli learns a name somewhere else."""
    reply = {"name": "x", "ivan": [1, 2]}
    assert scrub(reply, public=frozenset({"name"})).body == {
        "<unknown-1>": [1],
        "<unknown-2>": "<unknown-2>",
    }
    assert scrub(reply, public=frozenset({"name"})).body == scrub(reply).body
    assert json.loads(json.dumps(scrub("text").body)) == "<reply>"


def test_a_reply_read_by_a_parser_takes_the_type_the_parser_returns():
    """Otherwise nothing would read it, and its fixture would be placeholders all through."""
    from ycli.yandex.forms.subscriptions import endpoints
    from ycli.yandex.forms.subscriptions.models import Subscription

    assert reply_type(endpoints.get("s", 1, 2)) == Subscription
    reply = {"id": 7, "type": "email", "subject": PERSONAL_VALUE, "active": False}
    assert scrub(reply, reply_type(endpoints.get("s", 1, 2))).body == {
        "active": False,
        "id": 1,
        "subject": "<subject>",
        "type": "email",
    }


def test_a_number_under_an_unknown_key_is_never_kept():
    """It may be an identifier: nothing says what the key means."""
    reply = {"name": "Sprint", "ivansCounter": 78, "nested": {"count": 5, "items": [3, 4]}}
    assert scrub(reply, _Board).body == {
        "name": "<name>",
        "<unknown-1>": 1,
        "<unknown-2>": {"<unknown-1>": 1, "<unknown-2>": [1]},
    }
    # Under a key the model reads, a small number stays.
    assert scrub({"name": "x", "counts": {"a": 5}}, _Board).body["counts"] == {"<key-1>": 5}


# A made-up link of the shape object storage signs: whoever holds it reads the file with no token.
SIGNED_LINK = (
    "https://storage.example.net/exports/answers.xlsx?X-Amz-Algorithm=AWS4-HMAC-SHA256"
    "&X-Amz-Credential=MADEUPKEYID%2F20261008%2Fru-central1%2Fs3%2Faws4_request"
    "&X-Amz-Expires=259200&X-Amz-Signature=0123456789abcdef0123456789abcdef"
)


class _Export(BaseModel):
    href: str | None = None
    state: Literal["ok", "failed"] | str | None = None
    files: list[str] = []
    links: dict[str, str] = {}


@pytest.mark.parametrize("annotation", [_Export, Any, dict[str, Any]])
def test_a_signed_link_never_reaches_a_fixture_whatever_field_holds_it(annotation):
    """In a field of a model, under a key nobody knows, in a list, in a map, in plain JSON."""
    reply = {
        "href": SIGNED_LINK,
        "state": SIGNED_LINK,
        "files": [SIGNED_LINK],
        "links": {"xlsx": SIGNED_LINK},
        "download_url": SIGNED_LINK,
        "result": {"url": SIGNED_LINK, "parts": [{"href": SIGNED_LINK}]},
    }
    kept = strings(scrub(reply, annotation, frozenset({"download_url", "result", "url"})).body)
    assert not [text for text in kept if "X-Amz" in text or "storage.example.net" in text]
