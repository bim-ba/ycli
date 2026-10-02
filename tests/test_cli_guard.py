"""The CLI's gate on destructive operations: asks first, ``--yes`` skips, no terminal refuses."""

import httpx2
import pytest
import typer
from typer.testing import CliRunner

from tests.hosts import TRACKER_BASE
from ycli.cli import guard
from ycli.cli.app import app
from ycli.cli.exit_codes import ExitCode
from ycli.cli.guard import SendGuard

runner = CliRunner()
DELETE_BOARD = ["tracker", "boards", "delete", "7"]
BOARD_URL = f"{TRACKER_BASE}/boards/7"
REQUEST = httpx2.Request("DELETE", "https://api.test/v1/items/7?token=secret")


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


@pytest.mark.parametrize("effect", ["read", "write", "idempotent_write"])
def test_only_a_destructive_effect_asks(asked, monkeypatch, effect):
    _attended(monkeypatch, True)
    SendGuard({})(effect, REQUEST)
    assert asked == []


def test_a_destructive_effect_asks_on_a_terminal_and_masks_secrets(asked, monkeypatch):
    _attended(monkeypatch, True)
    SendGuard({})("destructive", REQUEST)
    assert asked == [
        "DELETE https://api.test/v1/items/7?token=%2A%2A%2A — this deletes data. Continue?"
    ]
    assert "secret" not in asked[0]


def test_yes_skips_the_question(asked, monkeypatch):
    _attended(monkeypatch, True)
    SendGuard({"yes": True})("destructive", REQUEST)
    assert asked == []


def test_without_a_terminal_it_is_a_usage_error_that_says_to_pass_yes(asked, monkeypatch, capsys):
    _attended(monkeypatch, False)
    with pytest.raises(typer.Exit) as stopped:
        SendGuard({})("destructive", REQUEST)
    assert stopped.value.exit_code == ExitCode.USAGE
    assert "Pass --yes" in capsys.readouterr().err
    assert asked == []


def test_a_declined_prompt_aborts(monkeypatch):
    _attended(monkeypatch, True)

    def decline(text: str, *, abort: bool, err: bool) -> bool:
        raise typer.Abort

    monkeypatch.setattr(guard.typer, "confirm", decline)
    with pytest.raises(typer.Abort):
        SendGuard({})("destructive", REQUEST)


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
