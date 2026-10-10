"""The three handles of a listing: `limit`, everything, and `next`, the same on every surface."""

import asyncio
import inspect
import json
import shlex
from typing import Annotated

import pytest
import typer
import yaml
from fastmcp import Client
from fastmcp.exceptions import ToolError
from pydantic import SecretStr
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.full_server import mcp
from ycli.cli import inject
from ycli.cli.errors import exit_code_for
from ycli.cli.exit_codes import ExitCode
from ycli.yandex.core.auth import IAMTokenAuth
from ycli.yandex.core.continuation import NOTHING_ELSE, RULE
from ycli.yandex.core.listing import Listing
from ycli.yandex.core.resource import Resource
from ycli.yandex.errors import YandexInvalidRequestError
from ycli.yandex.registry import SERVICES
from ycli.yandex.service import Service
from ycli.yandex.tracker.client import TrackerClient

BOARDS = "https://api.tracker.yandex.net/v3/boards/_paginate"


@pytest.fixture
def boards(api):
    """Five boards, two to a page: every next page is asked for by the id of the last one."""
    for page in ([1, 2], [3, 4], [5], []):
        api.add("GET", BOARDS, json=[{"id": number, "name": f"B{number}"} for number in page])
    return api


def _cli(*argv: str) -> tuple[list[int], str]:
    result = CliRunner().invoke(cli.app, ["-o", "json", "tracker", "boards", "list", *argv])
    assert result.exit_code == 0, result.output
    return [board["id"] for board in json.loads(result.stdout)["items"]], result.stderr


async def _call(name: str, **arguments: object) -> dict:
    async with Client(mcp) as client:
        return (await client.call_tool(name, arguments)).structured_content


def _tool(**arguments: object) -> dict:
    return asyncio.run(_call("tracker_boards_list", **arguments))


def test_the_cli_prints_the_list_and_says_how_to_go_on_beside_it(boards, monkeypatch):
    monkeypatch.setenv("YCLI__HTTP__MAX_ITEMS", "2")
    ids, said = _cli()
    assert ids == [1, 2]
    # stdout is the list it always was; where it stopped is on stderr, ready to paste.
    token = said.split("--next ")[1].split()[0]
    assert (
        said.strip()
        == f"stopped at 2; go on with: ycli tracker boards list --next {token}  (or --all)"
    )
    # Another limit goes on from the same place: the token carries its listing.
    ids, said = _cli("--next", token, "--limit", "10")
    assert ids == [3, 4, 5]
    assert said == ""


def test_all_and_a_limit_that_reaches_the_end_say_nothing_more(boards):
    ids, said = _cli("--all")
    assert ids == [1, 2, 3, 4, 5] and said == ""


def test_a_listing_given_whole_says_nothing_where_the_service_tells_how_many_there_are(api):
    """Two boards and a limit of two: nothing is left, so there is nothing to go on from."""
    two = [{"id": 1, "name": "B1"}, {"id": 2, "name": "B2"}]
    api.add("GET", BOARDS, json=two, headers={"X-Total-Count": "2"})
    ids, said = _cli("--limit", "2")
    assert (ids, said) == ([1, 2], "")
    whole = _tool(limit=2)
    assert (whole["truncated"], whole["next"], whole["total"]) == (False, None, 2)


SEARCH = "https://api.tracker.yandex.net/v3/issues/_search"


def test_a_search_by_a_scroll_goes_on_from_its_token_with_no_word_of_the_scroll(api):
    """One command serves a search by pages and by a scroll: the token says which it is of."""
    for keys in (["DE-1", "DE-2"], ["DE-3"], []):
        issues = [{"key": key} for key in keys]
        api.add("POST", SEARCH, json=issues, headers={"X-Scroll-Id": "scroll-1"})
    search = ["-o", "json", "tracker", "issues", "search", "Queue: DE"]
    first = CliRunner().invoke(
        cli.app, [*search, "--scroll-type", "unsorted", "--per-scroll", "2", "--limit", "2"]
    )
    assert first.exit_code == 0, first.output
    token = first.stderr.split("--next ")[1].split()[0]
    # Beside `--next` nothing but the limit is given, and the scroll goes on all the same.
    rest = CliRunner().invoke(cli.app, [*search, "--next", token, "--limit", "2"])
    assert rest.exit_code == 0, rest.output
    assert [issue["key"] for issue in json.loads(rest.stdout)["items"]] == ["DE-3"]
    assert api.calls[-1].url.params["scrollId"] == "scroll-1"


def test_what_is_not_a_token_is_a_usage_error(boards):
    refused = CliRunner().invoke(cli.app, ["tracker", "boards", "list", "--next", "nonsense"])
    assert isinstance(refused.exception, YandexInvalidRequestError)
    assert "this is not a token a listing gave" in str(refused.exception)
    assert exit_code_for(refused.exception) is ExitCode.USAGE and boards.calls == []


WIKI = "https://api.wiki.yandex.net/v1/pages/descendants"


def test_beside_next_nothing_but_the_limit_is_given_on_either_surface(api):
    """A filter given anew would be passed over silently: both surfaces refuse it, in one text."""
    refs = [{"id": number, "slug": f"team/p{number}"} for number in (1, 2, 3)]
    api.add("GET", WIKI, json={"results": refs, "next_cursor": None})  # one page, cut in two
    said = NOTHING_ELSE

    first = asyncio.run(_call("wiki_pages_descendants_list", slug="team", limit=2))
    token = first["next"]
    assert first["truncated"] and token
    # The page a listing is of must be named, and is checked; a filter is the token's.
    command = ["wiki", "pages", "descendants-list", "team", "--next", token]
    refused = CliRunner().invoke(cli.app, [*command, "--include-self"])
    plain = " ".join(refused.output.replace("│", " ").split())  # the box wraps the text
    assert refused.exit_code == 2 and said in plain and "(given: --include-self)" in plain
    with pytest.raises(ToolError, match=r"nothing else but the limit.*given: include_self"):
        asyncio.run(
            _call("wiki_pages_descendants_list", slug="team", next=token, include_self=True)
        )
    # With the limit alone, both go on.
    went_on = CliRunner().invoke(cli.app, ["-o", "json", *command, "--limit", "5"])
    assert went_on.exit_code == 0, went_on.output
    assert [ref["id"] for ref in json.loads(went_on.stdout)["items"]] == [3]
    tool = asyncio.run(_call("wiki_pages_descendants_list", slug="team", next=token, limit=5))
    assert [ref["id"] for ref in tool["items"]] == [3]


def test_a_tool_returns_the_items_and_where_the_listing_stopped(boards):
    first = _tool(limit=2)
    assert [board["id"] for board in first["items"]] == [1, 2]
    assert first["truncated"] is True and first["next"]
    rest = _tool(limit=10, next=first["next"])
    assert [board["id"] for board in rest["items"]] == [3, 4, 5]
    assert (rest["truncated"], rest["next"]) == (False, None)


def test_a_tool_gives_everything_when_asked(boards, monkeypatch):
    monkeypatch.setenv("YCLI__HTTP__MAX_TOOL_ITEMS", "2")
    assert len(_tool()["items"]) == 2  # the cap, when nothing is said
    boards.calls.clear()
    everything = _tool(all=True)
    assert [board["id"] for board in everything["items"]] == [3, 4, 5]  # the pages left to serve
    assert everything["truncated"] is False


def test_the_sdk_gives_everything_lazily_and_goes_on_from_a_token(boards, monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "y0_token")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    with TrackerClient(oauth_token="y0_token", organization_id="org") as tracker:
        some = tracker.boards.list(limit=2)
        assert isinstance(some, Listing) and boards.calls == []  # nothing asked until it is read
        assert [board.id for board in some] == [1, 2]
        assert some.truncated and some.next
        rest = tracker.boards.list(next=some.next)
        assert [board.id for board in rest] == [3, 4, 5] and not rest.truncated


def _plain(text: str) -> str:
    return " ".join(text.replace("│", " ").split())


def test_the_help_the_tool_the_docstring_and_the_refusal_say_the_rule_in_the_same_words():
    """One phrase, from one place: what the help tells to do is not what the command refuses."""
    assert RULE == (
        "the token carries its listing; give what is required again, and nothing else but the limit"
    )
    assert RULE in NOTHING_ELSE
    shown = CliRunner().invoke(
        cli.app, ["tracker", "boards", "list", "--help"], env={"COLUMNS": "200"}
    )
    assert RULE in _plain(shown.output)

    async def described() -> str:
        async with Client(mcp) as client:
            (tool,) = [t for t in await client.list_tools() if t.name == "tracker_boards_list"]
            return tool.input_schema["properties"]["next"]["description"]

    assert RULE in asyncio.run(described())


def test_the_help_of_a_search_says_that_a_token_of_a_scroll_works_once():
    once = "works once: used again, it gives the portion after"
    shown = CliRunner().invoke(
        cli.app, ["tracker", "issues", "search", "--help"], env={"COLUMNS": "200"}
    )
    assert once in _plain(shown.output)


def test_a_listing_taken_in_pieces_counts_what_was_given_over_all_of_them(api):
    """`stopped at 4 of 9`, not `stopped at 2`: a piece is not the whole."""
    for ids in ([1, 2], [3, 4], [5, 6]):
        boards = [{"id": number, "name": f"B{number}"} for number in ids]
        api.add("GET", BOARDS, json=boards, headers={"X-Total-Count": "9"})
    _, said = _cli("--limit", "2")
    assert said.startswith("stopped at 2 of 9; go on with: ycli tracker boards list --next ")
    _, said = _cli("--limit", "2", "--next", said.split("--next ")[1].split()[0])
    assert said.startswith("stopped at 4 of 9; go on with: ycli tracker boards list --next ")


def test_a_structural_format_prints_what_the_tool_answers(boards, monkeypatch):
    """`-o json` and `-o yaml` print what every surface gives: `{items, truncated, next, total}`."""
    monkeypatch.setenv("YCLI__HTTP__MAX_ITEMS", "2")
    cut = CliRunner().invoke(cli.app, ["-o", "json", "tracker", "boards", "list"])
    assert cut.exit_code == 0, cut.output
    shown = json.loads(cut.stdout)
    assert set(shown) == {"items", "truncated", "next", "total"}
    assert [board["id"] for board in shown["items"]] == [1, 2]
    # The token is machine-readable here, and the same one the line on stderr gives a person.
    assert shown["truncated"] is True and shown["next"] == cut.stderr.split("--next ")[1].split()[0]
    assert shown["total"] is None
    whole = CliRunner().invoke(cli.app, ["-o", "yaml", "tracker", "boards", "list", "--all"])
    assert whole.exit_code == 0, whole.output
    loaded = yaml.safe_load(whole.stdout)
    assert [board["id"] for board in loaded.pop("items")] == [3, 4, 5]  # the pages left
    assert loaded == {"truncated": False, "next": None, "total": None}
    assert whole.stderr == ""


def test_a_table_prints_the_rows_and_says_where_it_stopped_beside_them(boards, monkeypatch):
    """A table has no room for the envelope: `-o pretty` prints the items; the rest is on stderr."""
    monkeypatch.setenv("YCLI__HTTP__MAX_ITEMS", "2")
    table = CliRunner().invoke(cli.app, ["-o", "pretty", "tracker", "boards", "list"])
    assert table.exit_code == 0, table.output
    assert "B1" in table.stdout and "B2" in table.stdout and "B3" not in table.stdout
    assert "truncated" not in table.stdout and "next" not in table.stdout
    assert table.stderr.startswith("stopped at 2; go on with: ycli tracker boards list --next ")


def test_the_line_on_stderr_is_the_command_that_goes_on(api):
    """What a command cannot be called without is in the line; what the token holds is not."""
    refs = [{"id": number, "slug": f"team/p{number}"} for number in (1, 2, 3)]
    api.add("GET", WIKI, json={"results": refs, "next_cursor": None})
    command = ["wiki", "pages", "descendants-list", "team space"]
    first = CliRunner().invoke(cli.app, [*command, "--include-self", "--limit", "2"])
    assert first.exit_code == 0, first.output
    line = first.stderr.split("go on with: ")[1].split("  (or --all)")[0]
    assert line.startswith("ycli wiki pages descendants-list 'team space' --next ")
    rest = CliRunner().invoke(cli.app, ["-o", "json", *shlex.split(line)[1:]])
    assert rest.exit_code == 0, rest.output
    assert [ref["id"] for ref in json.loads(rest.stdout)["items"]] == [3]


def test_the_command_that_goes_on_gives_again_every_required_option_and_value():
    app, lines = typer.Typer(), []

    @app.command()
    def search(
        context: typer.Context,
        users: list[str],
        from_: Annotated[str, typer.Option("--from")],
        queue: Annotated[list[str], typer.Option("-q", "--queue")],
        to: Annotated[str | None, typer.Option()] = None,
    ) -> None:
        lines.append(inject._again(context))

    given = ["dee", "eve", "--from", "1 May", "-q", "A", "--queue", "B", "--to", "x"]
    assert CliRunner().invoke(app, given, prog_name="ycli gaps search").exit_code == 0
    assert lines == ["ycli gaps search dee eve --from '1 May' --queue A --queue B"]


def test_what_is_given_again_and_differs_from_the_token_is_refused_by_its_name(api):
    """A token of one page tree is not passed over for another: both surfaces name what differs."""
    refs = [{"id": number, "slug": f"team/p{number}"} for number in (1, 2, 3)]
    api.add("GET", WIKI, json={"results": refs, "next_cursor": None})
    token = asyncio.run(_call("wiki_pages_descendants_list", slug="team", limit=2))["next"]
    asked = len(api.calls)
    said = "what is given again must be what the token holds; it differs in: slug"
    refused = CliRunner().invoke(
        cli.app, ["wiki", "pages", "descendants-list", "other", "--next", token]
    )
    assert isinstance(refused.exception, YandexInvalidRequestError)
    assert said in str(refused.exception)
    assert exit_code_for(refused.exception) is ExitCode.USAGE
    with pytest.raises(ToolError, match=said):
        asyncio.run(_call("wiki_pages_descendants_list", slug="other", next=token))
    assert len(api.calls) == asked  # nothing was sent


def test_a_field_of_the_body_beside_next_is_refused_like_any_other_argument(api, tmp_path):
    """`-F` and `--body-file` would be passed over without a word: the body is the token's."""
    found = {"values": [{"id": "p1"}, {"id": "p2"}, {"id": "p3"}], "hits": 3, "pages": 1}
    api.add("POST", "https://api.tracker.yandex.net/v3/entities/project/_search", json=found)
    search = ["-o", "json", "tracker", "entities", "search", "project"]
    first = CliRunner().invoke(cli.app, [*search, "-F", "input=Q4", "--limit", "2"])
    assert first.exit_code == 0, first.output
    token, asked = json.loads(first.stdout)["next"], len(api.calls)
    (tmp_path / "body.json").write_text('{"input": "OTHER"}', encoding="utf-8")
    for beside in (["-F", "input=OTHER"], ["--body-file", str(tmp_path / "body.json")]):
        refused = CliRunner().invoke(cli.app, [*search, *beside, "--next", token])
        plain = " ".join(refused.output.replace("│", " ").split())
        assert refused.exit_code == 2 and NOTHING_ELSE in plain, refused.output
        assert f"(given: {beside[0]})" in plain
    assert len(api.calls) == asked  # nothing was sent


def test_the_line_on_stderr_names_the_profile_the_listing_was_asked_under(
    api, monkeypatch, profiles_directory
):
    """A token of one account run as printed under another would list the other's: not ready."""
    profiles_directory.mkdir(parents=True)
    (profiles_directory / "work.env").write_text(
        "YANDEX_ID_OAUTH_TOKEN=w\nYANDEX_ID_ORGANIZATION_ID=7\n", encoding="utf-8"
    )
    api.add("GET", BOARDS, json=[{"id": number, "name": f"B{number}"} for number in (1, 2, 3)])
    command = ["tracker", "boards", "list", "--limit", "2"]
    for given in (["--profile", "work", *command], [*command, "--profile", "work"]):
        run = CliRunner().invoke(cli.app, given)
        assert run.exit_code == 0, run.output
        assert "go on with: ycli --profile work tracker boards list --next " in run.stderr
    monkeypatch.setenv("YCLI_PROFILE", "work")  # named by the environment: it is there again
    run = CliRunner().invoke(cli.app, command)
    assert "go on with: ycli tracker boards list --next " in run.stderr


def test_an_argument_of_the_address_given_again_and_differing_is_named(api):
    """A token of one issue's comments given to another issue: the address is what differs."""
    url = "https://api.tracker.yandex.net/v3/issues/{}/comments"
    api.add("GET", url.format("DE-1"), json=[{"id": 1}, {"id": 2}, {"id": 3}])
    token = asyncio.run(_call("tracker_comments_list", issue_key="DE-1", limit=2))["next"]
    asked = len(api.calls)
    said = "this token is of another listing than GET /v3/issues/DE-2/comments"
    refused = CliRunner().invoke(cli.app, ["tracker", "comments", "list", "DE-2", "--next", token])
    assert isinstance(refused.exception, YandexInvalidRequestError)
    assert said in str(refused.exception)
    with pytest.raises(ToolError, match=said):
        asyncio.run(_call("tracker_comments_list", issue_key="DE-2", next=token))
    assert len(api.calls) == asked


def _listing_methods() -> list[tuple[str, object]]:
    """Every method of every client that goes on from a token: ``tracker.boards.list`` and all."""
    found = []
    for service in SERVICES:
        for resource_name, resource in vars(_bare(service)).items():
            if not isinstance(resource, Resource):
                continue
            for method_name, method in inspect.getmembers(type(resource), inspect.isfunction):
                if "next" in inspect.signature(method).parameters:
                    found.append((f"{service.name}.{resource_name}.{method_name}", method))
    return found


def _bare(service: Service) -> object:
    """A client of ``service`` that is asked nothing: its resources are all it is for."""
    auth = IAMTokenAuth(SecretStr("t"))
    return service.client_class()(auth=auth, organization_id="o", cloud_organization_id="c")


LISTING_METHODS = dict(_listing_methods())


@pytest.mark.parametrize("name", sorted(LISTING_METHODS))
def test_every_listing_method_of_the_sdk_says_the_rule_in_its_words(name):
    """The docstrings are copies of the phrase: each one is held to it, so none can drift."""
    assert RULE in _plain(LISTING_METHODS[name].__doc__ or "").lower()


def test_the_listing_methods_are_all_found():
    assert len(LISTING_METHODS) > 40


def test_a_tool_given_no_limit_gives_fewer_items_than_a_command(api):
    """A tool's answer is read whole into a context: 50 by default, where a command gives 500."""
    sixty = [{"id": number, "name": f"B{number}"} for number in range(1, 61)]
    for page in (sixty, sixty, []):  # one page for the tool, then the command's listing
        api.add("GET", BOARDS, json=page)
    answered = _tool()
    assert len(answered["items"]) == 50 and answered["truncated"] and answered["next"]
    ids, said = _cli()
    assert len(ids) == 60 and said == ""


def test_the_cap_of_a_tool_is_a_setting_of_its_own(boards, monkeypatch):
    monkeypatch.setenv("YCLI__HTTP__MAX_TOOL_ITEMS", "1")
    monkeypatch.setenv("YCLI__HTTP__MAX_ITEMS", "4")  # the command's cap is another setting
    answered = _tool()
    assert [board["id"] for board in answered["items"]] == [1] and answered["truncated"]
