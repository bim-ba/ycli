"""A read repeated through MCP and the SDK (``e2e/surfaces.py``), offline.

The API is a ``httpx2.MockTransport`` here; the CLI, the tool and the method are the real ones.
"""

from collections.abc import Iterator, Sequence
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
