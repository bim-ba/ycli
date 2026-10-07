"""``ycli api`` — any endpoint through the service's own client, output and exit codes."""

import json
import re
import sys

import pytest
from typer.testing import CliRunner

from tests.hosts import FORMS_BASE, TRACKER_BASE, WIKI_BASE
from tests.mock_api import MockAPI
from ycli.cli.app import app, main

runner = CliRunner()
ISSUE_URL = f"{TRACKER_BASE}/issues/DE-1"
LISTING_URL = f"{WIKI_BASE}/pages/descendants"


def _api(*args: str, stdin: str | None = None):
    return runner.invoke(app, ["api", *args], input=stdin)


def _said(result) -> str:
    """The output as one line of words, without the box rich draws around a usage error."""
    return " ".join(re.sub(r"[│╭╮╰╯─]", " ", result.output).split())


def _exit_code(monkeypatch, *args: str) -> str | int | None:
    """The exit status ``ycli api ...`` ends the process with (errors go through ``main``)."""
    monkeypatch.setattr(sys, "argv", ["ycli", "api", *args])
    with pytest.raises(SystemExit) as exited:
        main()
    return exited.value.code


# --- reads, methods and fields -----------------------------------------------------------------


def test_a_get_prints_the_json_answer(api: MockAPI):
    api.add("GET", ISSUE_URL, json={"key": "DE-1", "summary": "Fix", "n": 3})
    result = _api("issues/DE-1", "--service", "tracker")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"key": "DE-1", "summary": "Fix", "n": 3}
    assert [(call.method, str(call.url)) for call in api.calls] == [("GET", ISSUE_URL)]
    assert api.calls[0].headers["X-Org-Id"] == "o"  # the same transport as every command
    assert api.calls[0].headers["Authorization"] == "OAuth t"


def test_the_answer_goes_through_the_format_option(api: MockAPI):
    api.add("GET", ISSUE_URL, json={"key": "DE-1"})
    result = runner.invoke(app, ["-o", "yaml", "api", "issues/DE-1", "--service", "tracker"])
    assert result.stdout == "key: DE-1\n"


@pytest.mark.parametrize(
    ("args", "method"),
    [
        (["-f", "a=1"], "POST"),
        (["-F", "a=1"], "POST"),
        ([], "GET"),
        (["-f", "a=1", "-X", "PUT"], "PUT"),
        (["-X", "PATCH"], "PATCH"),
        (["-f", "a=1", "-X", "get"], "GET"),
    ],
)
def test_the_method_defaults_to_get_and_to_post_once_there_are_fields(api: MockAPI, args, method):
    api.add(method, f"{TRACKER_BASE}/things", json={})
    assert _api("things", "--service", "tracker", *args).exit_code == 0
    assert api.calls[0].method == method


def test_an_input_makes_the_default_method_post(api: MockAPI):
    api.add("POST", f"{TRACKER_BASE}/things", json={})
    assert _api("things", "--service", "tracker", "--input", "-", stdin="{}").exit_code == 0


@pytest.mark.parametrize("method", [[], ["-X", "POST"], ["-X", "PATCH"]])
def test_a_body_file_alone_is_the_body_of_a_write(api: MockAPI, tmp_path, method):
    """No ``-F`` beside it: the file is the whole body, and the method defaults to POST."""
    body = tmp_path / "body.json"
    body.write_text('{"scope": "dash", "filters": {"name": "Sales"}}')
    verb = method[1] if method else "POST"
    api.add(verb, f"{TRACKER_BASE}/things", json={})
    result = _api("things", "--service", "tracker", *method, "--body-file", str(body))
    assert result.exit_code == 0, result.output
    assert (api.calls[0].method, json.loads(api.calls[0].content)) == (
        verb,
        {"scope": "dash", "filters": {"name": "Sales"}},
    )


def test_a_body_file_of_a_read_is_still_refused(api: MockAPI, tmp_path):
    """A GET carries its fields in the query: there is no object to lay the file under."""
    body = tmp_path / "body.json"
    body.write_text('{"a": 1}')
    result = _api("things", "--service", "tracker", "-X", "GET", "--body-file", str(body))
    assert result.exit_code == 2
    assert "this command sends no JSON object to add fields to" in _said(result)
    assert api.calls == []


def test_fields_of_a_get_go_to_the_query_string(api: MockAPI):
    api.add("GET", f"{TRACKER_BASE}/issues", json=[])
    result = _api(
        "issues?filter=x",
        "--service",
        "tracker",
        "-X",
        "GET",
        "-f",
        "queue=DE",
        "-F",
        "perPage=5",
        "-F",
        "expand[]=a",
        "-F",
        "expand[]=b",
        "-F",
        "q[k]=true",
        "-F",
        "gone=null",
    )
    assert result.exit_code == 0, result.output
    assert api.calls[0].content == b""
    assert api.calls[0].url.params.multi_items() == [
        ("filter", "x"),
        ("queue", "DE"),
        ("perPage", "5"),
        ("expand", "a"),
        ("expand", "b"),
        ("q[k]", "true"),
    ]


def test_fields_of_a_write_are_a_typed_json_body(api: MockAPI, tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# 5\n")
    api.add("POST", f"{TRACKER_BASE}/issues", json={"key": "DE-2"})
    result = _api(
        "issues",
        "--service",
        "tracker",
        "-f",
        "summary=true",
        "-F",
        "count=3",
        "-F",
        "flag=false",
        "-F",
        "parent=null",
        "-F",
        f"description=@{note}",
        "-F",
        "queue[key]=DE",
        "-F",
        "tags[]=a",
        "-F",
        "tags[]=7",
    )
    assert result.exit_code == 0, result.output
    assert api.body() == {
        "summary": "true",  # -f is never typed
        "count": 3,
        "flag": False,
        "parent": None,
        "description": "# 5\n",  # a file is text, not JSON
        "queue": {"key": "DE"},
        "tags": ["a", 7],
    }
    assert "json" in api.calls[0].headers["Content-Type"]


def test_a_field_can_read_stdin(api: MockAPI):
    api.add("POST", f"{TRACKER_BASE}/comments", json={})
    assert (
        _api("comments", "--service", "tracker", "-F", "text=@-", stdin="from stdin").exit_code == 0
    )
    assert api.body() == {"text": "from stdin"}


def test_a_delete_sends_its_fields_in_the_query(api: MockAPI):
    api.add("DELETE", f"{TRACKER_BASE}/boards/7", status=204)
    result = _api("boards/7", "--service", "tracker", "-X", "DELETE", "-f", "force=1", "--yes")
    assert result.exit_code == 0, result.output
    assert api.calls[0].url.params["force"] == "1"
    assert api.calls[0].content == b""


@pytest.mark.parametrize(
    "field",
    ["a", "a[b=1", "a[][b]=1", "[b]=1"],
    ids=["no-equals", "unclosed", "array-in-the-middle", "no-name"],
)
def test_a_malformed_field_is_a_usage_error(api: MockAPI, field):
    assert _api("x", "--service", "tracker", "-F", field).exit_code == 2
    assert api.calls == []


@pytest.mark.parametrize("fields", [["a=1", "a[b]=2"], ["a[b]=1", "a=2"], ["a=1", "a[]=2"]])
def test_fields_that_clash_are_a_usage_error(api: MockAPI, fields):
    args = [part for field in fields for part in ("-F", field)]
    result = _api("x", "--service", "tracker", *args)
    assert result.exit_code == 2
    assert "clashes" in _said(result)
    assert api.calls == []


def test_a_missing_field_file_is_a_usage_error(api: MockAPI, tmp_path):
    result = _api("x", "--service", "tracker", "-F", f"a=@{tmp_path / 'nope'}")
    assert result.exit_code == 2
    assert "cannot read" in result.output


def test_an_unknown_method_is_a_usage_error(api: MockAPI):
    result = _api("x", "--service", "tracker", "-X", "FETCH")
    assert result.exit_code == 2
    assert "unknown HTTP method" in result.output
    assert api.calls == []


# --- headers and a raw body --------------------------------------------------------------------


def test_headers_are_sent(api: MockAPI):
    api.add("GET", f"{TRACKER_BASE}/x", json={})
    result = _api("x", "--service", "tracker", "-H", "X-Test: 1", "-H", "Accept:text/plain")
    assert result.exit_code == 0, result.output
    assert api.calls[0].headers["X-Test"] == "1"
    assert api.calls[0].headers["Accept"] == "text/plain"


@pytest.mark.parametrize("header", ["no-colon", ": value"])
def test_a_malformed_header_is_a_usage_error(api: MockAPI, header):
    assert _api("x", "--service", "tracker", "-H", header).exit_code == 2
    assert api.calls == []


def test_an_input_file_is_the_raw_body_and_fields_go_to_the_query(api: MockAPI, tmp_path):
    body = tmp_path / "body.json"
    body.write_bytes(b'{"summary": "S"}')
    api.add("PATCH", ISSUE_URL, json={})
    result = _api(
        "issues/DE-1", "--service", "tracker", "-X", "PATCH", "--input", str(body), "-f", "v=2"
    )
    assert result.exit_code == 0, result.output
    assert api.calls[0].content == b'{"summary": "S"}'
    assert api.calls[0].headers["Content-Type"] == "application/json"
    assert api.calls[0].url.params["v"] == "2"


def test_an_input_from_stdin_can_state_its_own_content_type(api: MockAPI):
    api.add("PUT", f"{TRACKER_BASE}/x", json={})
    result = _api(
        "x", "--service", "tracker", "-X", "PUT", "--input", "-", "-H", "content-type: text/yaml",
        stdin="a: 1",
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    assert api.calls[0].content == b"a: 1"
    assert api.calls[0].headers["Content-Type"] == "text/yaml"


def test_an_unreadable_input_is_a_usage_error(api: MockAPI, tmp_path):
    result = _api("x", "--service", "tracker", "--input", str(tmp_path / "nope"))
    assert result.exit_code == 2
    assert "cannot read" in result.output


# --- which service, and which hosts ------------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "name"),
    [
        (f"{TRACKER_BASE}/issues/DE-1", "tracker"),
        (f"{WIKI_BASE}/pages?slug=a%2Fb", "wiki"),
        (f"{FORMS_BASE}/surveys", "forms"),
    ],
)
def test_a_full_url_of_a_service_infers_it(api: MockAPI, url, name):
    base = url.partition("?")[0]
    api.add("GET", base, json={"ok": name})
    result = _api(url)
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"ok": name}
    assert str(api.calls[0].url) == url


def test_a_full_url_may_repeat_its_service(api: MockAPI):
    api.add("GET", ISSUE_URL, json={})
    assert _api(ISSUE_URL, "--service", "tracker").exit_code == 0


@pytest.mark.parametrize(
    "path",
    [
        "https://evil.example/v3/issues/DE-1",
        "https://api.tracker.yandex.net.evil.example/v3/x",
        "https://user@api.tracker.yandex.net/v3/x",
        "http://api.tracker.yandex.net/v3/x",
        "//evil.example/v3/x",
        "http:evil",
    ],
)
def test_a_host_that_is_no_service_is_refused_before_anything_is_sent(api: MockAPI, path):
    result = _api(path, "--service", "tracker")
    assert result.exit_code == 2
    assert "refusing to send credentials" in _said(result)
    assert api.calls == []


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ([f"{WIKI_BASE}/pages", "--service", "tracker"], "contradicts the URL"),
        (["https://api.tracker.yandex.net/v2/issues"], "is not under"),
        (["https://api.tracker.yandex.net/v3"], "is not under"),
        (["issues/DE-1"], "needs --service"),
        (["issues/DE-1", "--service", "mail"], "unknown service"),
    ],
)
def test_a_path_that_names_no_service_endpoint_is_a_usage_error(api: MockAPI, args, message):
    result = _api(*args)
    assert result.exit_code == 2
    assert message in _said(result)
    assert api.calls == []


@pytest.mark.parametrize(
    "path", ["../queues/DE", "/issues/../../queues", "issues/%2e%2e/x", f"{TRACKER_BASE}/../v2/x"]
)
def test_a_path_that_climbs_out_of_the_base_url_is_refused(api: MockAPI, path):
    result = _api(path, "--service", "tracker")
    assert result.exit_code == 2
    assert "leaves its endpoint" in _said(result)
    assert api.calls == []


# --- output by content type --------------------------------------------------------------------


def test_a_text_body_prints_as_text(api: MockAPI):
    api.add("GET", f"{WIKI_BASE}/x", content=b"# Title", headers={"Content-Type": "text/markdown"})
    result = _api("x", "--service", "wiki")
    assert result.stdout == "# Title\n"


def test_a_binary_body_is_written_to_stdout_as_it_is(api: MockAPI):
    api.add("GET", f"{WIKI_BASE}/f", content=b"\x00\x01", headers={"Content-Type": "image/png"})
    result = _api("f", "--service", "wiki")
    assert result.stdout_bytes == b"\x00\x01"


def test_an_empty_body_prints_nothing(api: MockAPI):
    api.add("DELETE", f"{WIKI_BASE}/x", status=204)
    result = _api("x", "--service", "wiki", "-X", "DELETE", "--yes")
    assert result.exit_code == 0, result.output
    assert result.stdout == ""


def test_json_that_is_not_json_prints_as_text(api: MockAPI):
    api.add("GET", f"{WIKI_BASE}/x", content=b"oops", headers={"Content-Type": "application/json"})
    assert _api("x", "--service", "wiki").stdout == "oops\n"


# --- writes: --dry-run and --yes ---------------------------------------------------------------


def test_a_dry_run_prints_the_post_it_would_send(api: MockAPI):
    result = runner.invoke(
        app,
        [
            "-o",
            "json",
            "api",
            "issues",
            "--service",
            "tracker",
            "-F",
            "n=1",
            "-f",
            "s=x",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {
        "method": "POST",
        "url": f"{TRACKER_BASE}/issues",
        "body": {"s": "x", "n": 1},
    }
    assert api.calls == []


def test_a_delete_needs_yes_when_there_is_no_terminal(api: MockAPI):
    result = _api("boards/7", "--service", "tracker", "-X", "DELETE")
    assert result.exit_code == 2
    assert "--yes" in result.output
    assert api.calls == []


def test_a_delete_with_yes_is_sent(api: MockAPI):
    api.add("DELETE", f"{TRACKER_BASE}/boards/7", status=204)
    assert _api("boards/7", "--service", "tracker", "-X", "DELETE", "-y").exit_code == 0
    assert [call.method for call in api.calls] == ["DELETE"]


def test_a_post_is_not_asked_about(api: MockAPI):
    api.add("POST", f"{TRACKER_BASE}/x", json={})
    assert _api("x", "--service", "tracker", "-f", "a=1").exit_code == 0


# --- errors ------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("status", "code"), [(401, 4), (403, 4), (404, 3), (409, 1), (429, 5), (503, 6)]
)
def test_an_error_answer_exits_by_its_kind(api: MockAPI, monkeypatch, capsys, status, code):
    api.add("GET", f"{TRACKER_BASE}/x", json={"errorMessages": ["nope"]}, status=status)
    assert _exit_code(monkeypatch, "x", "--service", "tracker") == code
    assert "nope" in capsys.readouterr().err


# --- --paginate --------------------------------------------------------------------------------


def _two_wiki_pages(api: MockAPI) -> None:
    api.add(
        "GET", LISTING_URL, json={"results": [{"slug": "a"}, {"slug": "b"}], "next_cursor": "c2"}
    )
    api.add("GET", LISTING_URL, json={"results": [{"slug": "c"}], "next_cursor": None})


def test_paginate_prints_every_item_as_one_array(api: MockAPI):
    _two_wiki_pages(api)
    result = runner.invoke(
        app,
        [
            "-o",
            "json",
            "api",
            "pages/descendants",
            "--service",
            "wiki",
            "-f",
            "slug=x",
            "--paginate",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == [{"slug": "a"}, {"slug": "b"}, {"slug": "c"}]
    assert [call.url.params.get("cursor") for call in api.calls] == [None, "c2"]
    assert api.calls[0].url.params["slug"] == "x"


def test_paginate_stops_at_the_item_cap(api: MockAPI):
    _two_wiki_pages(api)
    result = _api("pages/descendants", "--service", "wiki", "--paginate", "--limit", "2")
    assert len(json.loads(result.stdout)) == 2
    assert len(api.calls) == 1


@pytest.mark.parametrize(("extra", "count"), [([], 1), (["--all"], 3)])
def test_paginate_all_ignores_the_configured_cap(api: MockAPI, monkeypatch, extra, count):
    monkeypatch.setenv("YCLI__HTTP__MAX_ITEMS", "1")
    _two_wiki_pages(api)
    result = _api("pages/descendants", "--service", "wiki", "--paginate", *extra)
    assert len(json.loads(result.stdout)) == count


def test_paginate_follows_trackers_next_link(api: MockAPI):
    queues = f"{TRACKER_BASE}/queues"
    api.add(
        "GET",
        queues,
        json=[{"key": "A"}, {"key": "B"}],
        headers={"Link": '<https://api.tracker.yandex.net/v3/queues?page=2&perPage=2>; rel="next"'},
    )
    api.add("GET", queues, json=[{"key": "C"}])
    result = _api("queues", "--service", "tracker", "--paginate")
    assert [queue["key"] for queue in json.loads(result.stdout)] == ["A", "B", "C"]
    assert [call.url.params.get("page") for call in api.calls] == [None, "2"]


def test_paginate_refuses_a_service_whose_listings_page_differently(api: MockAPI):
    result = _api("surveys", "--service", "forms", "--paginate")
    assert result.exit_code == 2
    assert "do not share one pagination scheme" in _said(result)
    assert "works for tracker, wiki" in _said(result)
    assert api.calls == []


def test_paginate_is_for_get_only(api: MockAPI):
    result = _api("pages/descendants", "--service", "wiki", "--paginate", "-X", "POST")
    assert result.exit_code == 2
    assert "GET only" in result.output
    assert api.calls == []


def test_a_cap_option_needs_paginate(api: MockAPI):
    for option in (["--limit", "5"], ["--all"]):
        result = _api("x", "--service", "wiki", *option)
        assert result.exit_code == 2
        assert "need --paginate" in result.output


@pytest.mark.parametrize(
    "answer",
    [
        {"json": {"slug": "a"}},
        {"content": b"text", "headers": {"Content-Type": "text/plain"}},
    ],
    ids=["object-without-results", "text"],
)
def test_paginate_over_something_that_is_no_listing_is_a_usage_error(api: MockAPI, answer):
    api.add("GET", f"{WIKI_BASE}/pages", **answer)
    result = _api("pages", "--service", "wiki", "--paginate")
    assert result.exit_code == 2
    assert "did not answer with a listing" in _said(result)
