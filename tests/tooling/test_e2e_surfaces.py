"""A read repeated through MCP and the SDK (``e2e/surfaces.py``), offline.

The API is a ``httpx2.MockTransport`` here; the CLI, the tool and the method are the real ones.
"""

import json
import subprocess
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import httpx2
import pytest
from e2e.recording import InProcessDriver
from e2e.runner import CommandResult, Driver, ScenarioError
from e2e.surfaces import Call, Listener, Report, ThreeSurfaces, differences, fail_on_data, listening

from ycli.yandex.core.endpoint import Effect


class _API:
    """Answers each request with the next of ``replies`` (the last one from then on)."""

    def __init__(self, *replies: Any) -> None:
        self.replies = list(replies)
        self.calls: list[httpx2.Request] = []

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        self.calls.append(request)
        reply = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        return httpx2.Response(200, json=reply)


@pytest.fixture
def api(monkeypatch) -> _API:
    api = _API({"key": "A-1", "summary": "one"})
    monkeypatch.setattr(
        "ycli.yandex.core.session.default_transport", lambda: httpx2.MockTransport(api)
    )
    return api


@pytest.fixture
def listener(api: _API, monkeypatch) -> Iterator[Listener]:
    with listening(monkeypatch) as listener:
        yield listener


@pytest.fixture
def driver(listener: Listener) -> Iterator[ThreeSurfaces]:
    driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), listener)
    yield driver
    driver.close()


def test_a_read_is_asked_three_times_and_the_replies_agree(driver, api):
    completed = driver.run(["tracker", "issues", "get", "A-1"])
    assert completed.exit_code == 0, completed.stderr
    assert [call.url.path for call in api.calls] == ["/v3/issues/A-1"] * 3
    assert driver.report.compared == {"mcp": {"tracker.issues.get"}, "sdk": {"tracker.issues.get"}}
    assert driver.report.findings == []


def test_a_write_runs_once(driver, api):
    driver.run(["tracker", "issues", "create", "--queue", "Q", "--summary", "S"])
    assert [call.method for call in api.calls] == ["POST"]
    assert driver.report.left_out == {"a write runs once": {"tracker.issues.create"}}
    assert driver.report.compared == {"mcp": set(), "sdk": set()}


def test_a_surface_that_answers_differently_is_a_defect(driver, api):
    """The CLI says ``one`` before and after; the other two surfaces were told ``two``."""
    one, two = {"key": "A-1", "summary": "one"}, {"key": "A-1", "summary": "two"}
    api.replies = [one, two, two, one]
    driver.run(["tracker", "issues", "get", "A-1"])
    assert [(f.surface, f.kind, f.what) for f in driver.report.findings] == [
        ("sdk", "data", "$.summary: str != str"),
        ("mcp", "data", "$.summary: str != str"),
    ]
    assert "two" not in driver.report.text()
    with pytest.raises(ScenarioError, match=r"2 differences .* tracker.issues.get \[sdk\]"):
        fail_on_data(driver.report, 0)
    fail_on_data(driver.report, 2)


def test_a_list_the_service_orders_anew_is_time_at_every_item(driver, api):
    """Two reads of the CLI differ at one item and, by chance, agree at the other."""
    api.replies = [
        {"tags": ["a", "b", "c"]},
        {"tags": ["b", "c", "a"]},
        {"tags": ["b", "c", "a"]},
        {"tags": ["a", "c", "b"]},
    ]
    driver.run(["tracker", "issues", "get", "A-1"])
    assert {(f.kind, f.what) for f in driver.report.findings} == {("time", "$.tags[]: str != str")}


def test_what_the_cli_itself_answers_differently_a_moment_later_is_time(driver, api):
    api.replies = [
        {"key": "A-1", "summary": "one"},
        {"key": "A-1", "summary": "two"},
        {"key": "A-1", "summary": "two"},
        {"key": "A-1", "summary": "three"},
    ]
    driver.run(["tracker", "issues", "get", "A-1"])
    assert {finding.kind for finding in driver.report.findings} == {"time"}
    assert driver.report.data() == []
    assert "TIME: the object changed between the calls (noise of the runner): 2" in (
        driver.report.text()
    )


def test_while_a_read_is_repeated_nothing_else_leaves_the_process(listener, api):
    listener.reads_only = True
    completed = None
    with pytest.raises(Exception, match="POST /v3/issues/ is not a read"):
        completed = InProcessDriver(pause_seconds=0).run(
            ["tracker", "issues", "create", "--queue", "Q", "--summary", "S"]
        )
    assert completed is None and api.calls == []


class _Said(Driver):
    """A driver that ran nothing: it reports the call it is given and prints ``stdout``."""

    def __init__(self, listener: Listener, call: Call, stdout: str) -> None:
        self._listener, self._call, self._stdout = listener, call, stdout

    def run(self, arguments: Sequence[str]) -> CommandResult:
        self._listener.calls.append(self._call)
        return CommandResult(0, self._stdout, "")


def _read(operation: str, arguments: dict[str, Any], defaults: dict[str, Any]) -> Call:
    return Call(operation, arguments, defaults, effects=[Effect.READ])


def test_an_argument_the_tool_does_not_take_keeps_mcp_out_and_is_named(listener, api):
    call = _read("wiki.pages.get", {"slug": "a/b", "fields": "content"}, {"fields": None})
    driver = ThreeSurfaces(_Said(listener, call, '{"key": "A-1", "summary": "one"}'), listener)
    driver.run(["wiki", "pages", "get", "a/b"])
    driver.close()
    assert driver.report.left_out == {
        "the method takes what the tool does not": {"wiki.pages.get: fields"}
    }
    assert driver.report.compared == {"mcp": set(), "sdk": {"wiki.pages.get"}}


def test_an_argument_left_at_its_default_is_not_sent_to_the_tool(listener, api):
    call = _read("wiki.pages.get", {"slug": "a/b", "fields": None}, {"fields": None})
    driver = ThreeSurfaces(_Said(listener, call, '{"key": "A-1", "summary": "one"}'), listener)
    driver.run(["wiki", "pages", "get", "a/b"])
    driver.close()
    assert driver.report.left_out == {}
    assert driver.report.compared["mcp"] == {"wiki.pages.get"}


def test_the_report_lists_where_the_surfaces_are_not_one_operation(driver):
    unequal = driver.report.unequal
    assert "tracker.attachments.download" in unequal["operations with no tool"]
    assert (
        "wiki.pages.get: fields"
        in (unequal["operations whose method takes what the tool does not"])
    )
    # A method named with a trailing underscore has its tool under the name without it.
    assert "tracker.comments.import_" not in unequal["operations with no tool"]


def test_a_key_that_no_model_names_is_not_printed():
    report = Report(public=frozenset({"fields", "id"}))
    assert report.path("$.fields.ivan-petrov[0]: str != str") == "$.fields.<key>: str != str"
    assert report.path("$[4].id: str != str") == "$[].id: str != str"
    assert report.path("$.fields[12].id: list[2] != list[3]") == (
        "$.fields[].id: list[2] != list[3]"
    )


def test_differences_are_paths_and_shapes():
    one = {"a": 1, "b": [1], "c": {"d": "x"}, "e": 1}
    other = {"a": 2, "b": [1, 2], "c": {"d": "y"}, "f": 1}
    assert differences(one, other) == [
        "$.a: int != int",
        "$.b: list[1] != list[2]",
        "$.c.d: str != str",
        "$.e: only in the first",
        "$.f: only in the second",
    ]
    assert differences([{"a": 1}], [{"a": 1}]) == []


def test_the_live_suite_is_collected_where_fastmcp_is_not_installed():
    """CI runs ``pytest e2e`` without the ``mcp`` extra: nothing may import fastmcp unasked.

    ``sys.modules["fastmcp"] = None`` makes every import of it fail, as on a machine without
    the extra; ``--doctest-modules`` (the repository's own option) imports every module there.
    """
    blocked = (
        "import sys; sys.modules['fastmcp'] = None; import pytest; "
        "sys.exit(pytest.main(['e2e', '--collect-only', '-q', '--no-cov', '-n', '0', "
        "'-p', 'no:cacheprovider']))"
    )
    collected = subprocess.run(
        [sys.executable, "-c", blocked],
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
        check=False,
    )
    assert collected.returncode == 0, collected.stdout[-2000:]


@pytest.mark.parametrize("surface", ["mcp", "sdk"])
def test_a_write_is_carried_out_once_by_the_surface_of_the_run(listener, api, surface):
    driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), listener, writes_through=surface)
    completed = driver.run(["tracker", "issues", "create", "--queue", "Q", "--summary", "S"])
    driver.close()
    assert completed.exit_code == 0, completed.stderr
    # What the surface answered is what the command printed.
    assert json.loads(completed.stdout)["key"] == "A-1"
    assert [(call.method, json.loads(call.content)) for call in api.calls] == [
        ("POST", {"queue": "Q", "summary": "S"})
    ]
    assert driver.report.written[surface] == {"tracker.issues.create"}
    assert f"1 {'operations by MCP' if surface == 'mcp' else 'by the SDK'}" in driver.report.text()


@pytest.mark.parametrize(
    "command",
    [
        "tracker boards create --name B --owner me --permissions private --backlog --sprints",
        "tracker queues versions-create --queue Q --name V --start-date 2027-01-04",
        "tracker comments create A-1 --text hello",
        # The bytes of a file: a tool takes them as base64.
        f"tracker attachments upload A-1 {Path(__file__)}",
    ],
)
def test_mcp_sends_the_request_the_command_would(listener, api, command):
    """A body with fields the API names differently, and a reply a client only names."""
    alone = ThreeSurfaces(InProcessDriver(pause_seconds=0), listener)
    assert alone.run(command.split()).exit_code == 0
    alone.close()
    driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), listener, writes_through="mcp")
    completed = driver.run(command.split())
    driver.close()
    assert completed.exit_code == 0, completed.stderr
    own, through = api.calls
    assert (through.method, through.url) == (own.method, own.url)
    # A multipart body draws a boundary of its own each time: the lengths are equal.
    multipart = "multipart" in own.headers.get("content-type", "")
    assert len(through.content) == len(own.content) if multipart else through.content == own.content
    assert len(driver.report.written["mcp"]) == 1
    assert "a write runs once" not in driver.report.left_out


def test_a_read_is_left_to_the_command_and_still_compared(listener, api):
    driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), listener, writes_through="mcp")
    driver.run(["tracker", "issues", "get", "A-1"])
    driver.close()
    assert len(api.calls) == 3
    assert driver.report.written == {"mcp": set(), "sdk": set()}
    assert driver.report.compared["mcp"] == {"tracker.issues.get"}


def test_a_write_that_returns_nothing_prints_nothing_through_mcp(listener, api):
    """The tool answers a delete with an ``Ack`` of its own; the method returns ``None``."""
    driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), listener, writes_through="mcp")
    completed = driver.run(["tracker", "components", "delete", "7"])
    driver.close()
    assert completed.exit_code == 0, completed.stderr
    assert [call.method for call in api.calls] == ["DELETE"]
    assert driver.report.written["mcp"] == {"tracker.components.delete"}


def test_a_command_that_adds_to_the_body_itself_is_not_handed_over(listener, api):
    """``-F`` reaches only the request the command sends: no other surface would send it."""
    driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), listener, writes_through="mcp")
    completed = driver.run(
        ["tracker", "issues", "create", "--queue", "Q", "--summary", "S", "-F", "x=1"]
    )
    driver.close()
    assert completed.exit_code == 0, completed.stderr
    assert json.loads(api.calls[0].content) == {"queue": "Q", "summary": "S", "x": 1}
    assert driver.report.written == {"mcp": set(), "sdk": set()}
    assert driver.report.left_out == {
        "the command adds to the body itself (-F)": {"tracker.issues.create"},
        "a write runs once": {"tracker.issues.create"},
    }


def test_a_write_the_tool_refuses_fails_the_step(listener, monkeypatch):
    refuse = httpx2.MockTransport(lambda request: httpx2.Response(403, json={"errors": {}}))
    monkeypatch.setattr("ycli.yandex.core.session.default_transport", lambda: refuse)
    with listening(monkeypatch) as heard:
        driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), heard, writes_through="mcp")
        with pytest.raises(ScenarioError, match=r"tracker\.issues\.create through MCP: "):
            driver.run(["tracker", "issues", "create", "--queue", "Q", "--summary", "S"])
        driver.close()


class _Limited:
    """Answers ``429`` to the first request, then ``{}``: the core sends that request again."""

    def __init__(self) -> None:
        self.calls: list[httpx2.Request] = []

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        self.calls.append(request)
        if len(self.calls) == 1:
            return httpx2.Response(429, json={}, headers={"Retry-After": "0"})
        return httpx2.Response(200, json={"key": "A-1"})


def test_a_request_the_core_sent_again_is_said_and_nothing_personal_with_it(monkeypatch):
    """A write the service limited goes out twice: the report says so, by method and path."""
    limited = _Limited()
    transport = httpx2.MockTransport(limited)
    monkeypatch.setattr("ycli.yandex.core.session.default_transport", lambda: transport)
    with listening(monkeypatch) as heard:
        driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), heard)
        # A user's uid in the path, as Tracker's own addresses have it.
        assert driver.run(["tracker", "users", "get", "1130000012345678"]).exit_code == 0
        assert driver.run(["tracker", "issues", "get", "A-1"]).exit_code == 0
        driver.close()
    assert [call.method for call in limited.calls[:2]] == ["GET", "GET"]
    assert driver.report.resent == ["GET /v3/users/<uid>"]
    text = driver.report.text()
    assert "requests the core sent again: 1\n  GET /v3/users/<uid>\n" in text
    assert "1130000012345678" not in text and "issues/A-1" not in text


def test_a_surface_failure_is_worded_without_what_the_run_learned(listener, monkeypatch):
    """The report of a run is public: a login a step saved is said by its name there too."""
    refuse = httpx2.MockTransport(
        lambda request: httpx2.Response(403, json={"errorMessages": ["no access for ivan.petrov"]})
    )
    monkeypatch.setattr("ycli.yandex.core.session.default_transport", lambda: refuse)
    with listening(monkeypatch) as heard:
        driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), heard, writes_through="mcp")
        driver.knows({"RUN": "e2e-1-ab12", "login": "ivan.petrov"})
        with pytest.raises(ScenarioError) as failed:
            driver.run(["tracker", "issues", "create", "--queue", "Q", "--summary", "S"])
        driver.close()
    # The test's own credentials are single letters, which the scrub cuts out of every word:
    # what is held is that the login is gone and its name stands where it was, before the hint.
    assert "ivan.petrov" not in str(failed.value)
    assert "gin>\nHin" in str(failed.value)


def test_a_request_sent_again_is_worded_without_what_the_run_learned(monkeypatch):
    """A path holds what a step saved, a login or a queue's key: the report names it instead."""
    limited = _Limited()
    transport = httpx2.MockTransport(limited)
    monkeypatch.setattr("ycli.yandex.core.session.default_transport", lambda: transport)
    with listening(monkeypatch) as heard:
        driver = ThreeSurfaces(InProcessDriver(pause_seconds=0), heard)
        driver.knows({"RUN": "e2e-1-ab12", "login": "ivan.petrov"})
        assert driver.run(["tracker", "users", "get", "ivan.petrov"]).exit_code == 0
        driver.close()
    # As above: the scrub cuts the test's one-letter credentials out of the name too.
    (line,) = driver.report.resent
    assert "ivan.petrov" not in line
    assert line.startswith("GET /v3/users/<") and line.endswith("gin>")
