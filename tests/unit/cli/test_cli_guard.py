"""The CLI's gate on destructive operations: asks first, ``--yes`` skips, no terminal refuses."""

import asyncio
from http import HTTPMethod

import httpx2
import pytest
import typer
from fastmcp import Client
from typer.testing import CliRunner

from tests import full_server
from tests.contract import help_of, load_cases
from tests.hosts import TRACKER_BASE
from ycli.cli import guard
from ycli.cli.app import app
from ycli.cli.exit_codes import ExitCode
from ycli.cli.guard import guard_of
from ycli.yandex.core.endpoint import Effect, Endpoint

runner = CliRunner()
DELETE_BOARD = ["tracker", "boards", "delete", "7"]
BOARD_URL = f"{TRACKER_BASE}/boards/7"
REQUEST = httpx2.Request("DELETE", "https://api.test/v1/items/7?token=secret")


def _check(options: dict, effect: Effect = Effect.DESTRUCTIVE) -> None:
    """Pass the request of an operation of ``effect`` through the rule, as the CLI sets it."""
    guard_of(options).check(Endpoint(HTTPMethod.POST, "items/7", effect=effect), REQUEST)


@pytest.fixture
def asked(monkeypatch) -> list[str]:
    """Every prompt ``typer.confirm`` is asked, answered ``y`` (a person at a terminal)."""
    prompts: list[str] = []

    def answer(text: str, *, abort: bool, err: bool) -> bool:
        assert abort
        assert err  # the prompt goes to stderr: stdout stays data
        prompts.append(text)
        return True

    monkeypatch.setattr(guard.typer, "confirm", answer)
    return prompts


def _attended(monkeypatch, value: bool) -> None:
    monkeypatch.setattr(guard, "attended", lambda: value)


@pytest.mark.parametrize("effect", [Effect.READ, Effect.WRITE, Effect.IDEMPOTENT_WRITE])
def test_only_a_destructive_effect_asks(asked, monkeypatch, effect):
    _attended(monkeypatch, True)
    _check({}, effect)
    assert asked == []


def test_a_destructive_effect_asks_on_a_terminal_and_masks_secrets(asked, monkeypatch):
    _attended(monkeypatch, True)
    _check({})
    assert asked == [
        "DELETE https://api.test/v1/items/7?token=%2A%2A%2A — this deletes data. Continue?"
    ]
    assert "secret" not in asked[0]


def test_yes_skips_the_question(asked, monkeypatch):
    _attended(monkeypatch, True)
    _check({"yes": True})
    assert asked == []


def test_without_a_terminal_it_is_a_usage_error_that_says_to_pass_yes(asked, monkeypatch, capsys):
    _attended(monkeypatch, False)
    with pytest.raises(typer.Exit) as stopped:
        _check({})
    assert stopped.value.exit_code == ExitCode.USAGE
    assert "Pass --yes" in capsys.readouterr().err
    assert asked == []


def test_a_declined_prompt_aborts(monkeypatch):
    _attended(monkeypatch, True)

    def decline(text: str, *, abort: bool, err: bool) -> bool:
        raise typer.Abort

    monkeypatch.setattr(guard.typer, "confirm", decline)
    with pytest.raises(typer.Abort):
        _check({})


def test_attended_needs_a_terminal_on_stdin_and_stdout(monkeypatch):
    class Stream:
        def __init__(self, tty: bool) -> None:
            self._tty = tty

        def isatty(self) -> bool:
            return self._tty

    for stdin, stdout, expected in [(True, True, True), (True, False, False), (False, True, False)]:
        monkeypatch.setattr("sys.stdin", Stream(stdin))
        monkeypatch.setattr("sys.stdout", Stream(stdout))
        assert guard.attended() is expected


# --- through the CLI, on a real command -------------------------------------------------------


def test_a_destructive_command_without_a_terminal_sends_nothing_and_exits_2(api):
    result = runner.invoke(app, DELETE_BOARD)
    assert result.exit_code == 2
    assert "--yes" in result.output
    assert api.calls == []


@pytest.mark.parametrize(
    "args",
    [
        ["--yes", *DELETE_BOARD],
        ["-y", *DELETE_BOARD],
        [*DELETE_BOARD, "--yes"],
        [*DELETE_BOARD, "-y"],
    ],
)
def test_yes_lets_it_through_on_either_side_of_the_subcommand(api, args):
    api.add("DELETE", BOARD_URL, status=204)
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    assert [call.method for call in api.calls] == ["DELETE"]


def test_on_a_terminal_a_yes_answer_sends_it(api, monkeypatch):
    _attended(monkeypatch, True)
    api.add("DELETE", BOARD_URL, status=204)
    result = runner.invoke(app, DELETE_BOARD, input="y\n")
    assert result.exit_code == 0, result.output
    assert "this deletes data. Continue?" in result.output
    assert len(api.calls) == 1


def test_on_a_terminal_a_no_answer_aborts_with_exit_1(api, monkeypatch):
    _attended(monkeypatch, True)
    result = runner.invoke(app, DELETE_BOARD, input="n\n")
    assert result.exit_code == 1
    assert "Aborted" in result.output
    assert api.calls == []


def test_a_read_never_asks(api):
    api.add("GET", f"{TRACKER_BASE}/boards/7", json={"id": 7, "name": "B"})
    assert runner.invoke(app, ["tracker", "boards", "get", "7"]).exit_code == 0


def test_a_command_with_its_own_yes_keeps_its_meaning(api, monkeypatch):
    """``auth login --yes`` is "write .env without asking", not the global confirmation."""
    from ycli.yandex.status import cli as status_cli

    monkeypatch.setattr(status_cli, "OAuthAppConfig", lambda: type("C", (), {"client_id": ""})())
    result = runner.invoke(app, ["auth", "login", "--yes"])
    assert "No OAuth app configured" in result.output  # it parsed `--yes` and ran


def _check_grant(options: dict) -> None:
    """The same, for a write that grants access and destroys nothing."""
    grant = Endpoint(HTTPMethod.POST, "items/7", effect=Effect.WRITE, grants_access=True)
    guard_of(options).check(grant, httpx2.Request("POST", "https://api.test/v1/items/7"))


def test_a_grant_asks_in_words_of_its_own(asked, monkeypatch, capsys):
    _attended(monkeypatch, True)
    _check_grant({})
    assert asked == ["POST https://api.test/v1/items/7 — this grants access. Continue?"]
    _check_grant({"yes": True})
    assert len(asked) == 1  # --yes asks nothing
    _attended(monkeypatch, False)
    with pytest.raises(typer.Exit) as stopped:
        _check_grant({})
    assert stopped.value.exit_code == ExitCode.USAGE
    said = capsys.readouterr().err
    assert "this grants access. Pass --yes to confirm; there is no terminal" in said


def test_without_a_terminal_a_delete_and_a_grant_say_which_they_are(monkeypatch, capsys):
    _attended(monkeypatch, False)
    with pytest.raises(typer.Exit):
        _check({})
    assert "this deletes data. Pass --yes" in capsys.readouterr().err


GRANT_ACCESS = ["wiki", "access", "create", "7", "--role", "editor", "--user-uid", "9001"]


def test_a_command_that_grants_access_asks_and_a_dry_run_of_it_does_not(api, asked, monkeypatch):
    """Through the real entry point: the prompt, `--yes`, and `--dry-run`, which asks nobody."""
    api.add(
        "POST", "https://api.wiki.yandex.net/v1/pages/7/access", json={"id": "a1", "role": "editor"}
    )
    _attended(monkeypatch, True)
    planned = runner.invoke(app, ["-o", "json", *GRANT_ACCESS, "--dry-run"])
    assert planned.exit_code == 0, planned.output
    assert asked == [] and api.calls == []
    sent = runner.invoke(app, ["-o", "json", *GRANT_ACCESS])
    assert sent.exit_code == 0, sent.output
    assert len(asked) == 1 and asked[0].endswith("/pages/7/access — this grants access. Continue?")
    runner.invoke(app, ["-o", "json", *GRANT_ACCESS, "--yes"])
    assert len(asked) == 1 and len(api.calls) == 2
    _attended(monkeypatch, False)
    refused = runner.invoke(app, GRANT_ACCESS)
    assert refused.exit_code == ExitCode.USAGE and len(api.calls) == 2
    assert "this grants access. Pass --yes" in refused.stderr


def test_the_help_of_a_command_says_it_grants_access_where_its_tool_is_marked():
    """One fact, on both surfaces: the contract test holds the tool's mark to the operation.

    The count is pinned on purpose: a mark and its meta taken off together agree with each
    other and with the help, and only the number says that an operation stopped asking.
    """

    async def marked() -> set[str]:
        async with Client(full_server.mcp) as client:
            return {
                tool.name
                for tool in await client.list_tools()
                if (tool.meta or {}).get("anthropic/requiresUserInteraction") is True
            }

    marks = asyncio.run(marked())
    said, wrong = set(), []
    for case in load_cases():
        if case.cli is None or case.mcp is None:
            continue
        says = guard.GRANTS_ACCESS_HELP in help_of(case.cli)
        said |= {case.mcp[0]} if says else set()
        if says != (case.mcp[0] in marks):
            wrong.append(case.id)
    assert not wrong
    assert said == marks and len(marks) == 14
