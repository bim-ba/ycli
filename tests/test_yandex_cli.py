"""TDD for the `yandex` CLI — tracker group smoke test + forms group smoke test."""

from types import SimpleNamespace

import pytest
import typer
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.cli.context import AppContext
from ycli.mcp.selection import Selection
from ycli.settings import AppConfig
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.me.models import Me

runner = CliRunner()


def test_cli_main_module_importable():
    """``python -m ycli.cli`` entry resolves — covers the __main__.py import line."""
    import ycli.cli.__main__  # noqa: F401


def test_version_flag_prints_version_and_exits():
    from ycli import __version__

    res = runner.invoke(cli.app, ["--version"])
    assert res.exit_code == 0
    assert __version__ in res.stdout


# ---------------------------------------------------------------------------
# Tracker CLI smoke tests
# ---------------------------------------------------------------------------


def test_app_has_tracker_issues_group():
    res = runner.invoke(cli.app, ["tracker", "issues", "--help"])
    assert res.exit_code == 0
    assert "get" in res.stdout and "create" in res.stdout


def test_app_has_forms_surveys_group():
    res = runner.invoke(cli.app, ["forms", "surveys", "--help"])
    assert res.exit_code == 0
    assert "list" in res.stdout and "get" in res.stdout


def test_mcp_start_launches_server(monkeypatch):
    """`ycli mcp start` resolves the optional MCP server and runs it with every service."""
    calls: list[Selection] = []
    monkeypatch.setattr("ycli.mcp.server.main", calls.append)
    res = runner.invoke(cli.app, ["mcp", "start"])
    assert res.exit_code == 0
    assert calls == [Selection()]


def test_mcp_start_passes_every_selection_flag(monkeypatch):
    """The flags reach the server as one typed selection."""
    calls: list[Selection] = []
    monkeypatch.setattr("ycli.mcp.server.main", calls.append)
    args = [
        "mcp",
        "start",
        "--toolsets=core, wiki",
        "--tools=forms_surveys_get",
        "--exclude-tools=wiki_pages_get",
        "--read-only",
        "--tool-search",
    ]
    res = runner.invoke(cli.app, args)
    assert res.exit_code == 0
    assert calls == [
        Selection(
            toolsets=("core", "wiki"),
            tools=("forms_surveys_get",),
            exclude_tools=("wiki_pages_get",),
            read_only=True,
            tool_search=True,
        )
    ]


@pytest.mark.parametrize("command", ["start", "methods"])
@pytest.mark.parametrize(
    ("flag", "message"),
    [
        ("--toolsets=nope", "valid: tracker, wiki, forms, core, all"),
        ("--exclude-tools=status_get", "always served"),
        ("--tools=nope_thing", "unknown tool"),
        ("--tools=tracker_issues_gett", "tracker_issues_gett"),
    ],
)
def test_mcp_bad_selection_is_a_usage_error(monkeypatch, command, flag, message):
    """A bad name is a usage error naming the fix, and nothing is served."""
    monkeypatch.setattr("ycli.mcp.server.FastMCP.run", lambda self: pytest.fail("served"))
    res = runner.invoke(cli.app, ["mcp", command, flag])
    assert res.exit_code == 2
    assert message in " ".join(res.output.replace("│", " ").split())  # the error box wraps lines


def test_mcp_sub_app_registered():
    from typer.main import get_command

    root = get_command(cli.app)
    assert "mcp" in root.list_commands(typer.Context(root))  # ty: ignore[unresolved-attribute]


def test_mcp_methods_lists_tool_names():
    """`ycli mcp methods` prints sorted MCP tool names, one per line."""
    res = runner.invoke(cli.app, ["mcp", "methods"])
    assert res.exit_code == 0
    assert "tracker_issues_get" in res.stdout


def test_mcp_methods_honours_the_selection_flags():
    """`ycli mcp methods` lists what a server with the same flags would serve."""
    res = runner.invoke(
        cli.app,
        [
            "mcp",
            "methods",
            "--toolsets",
            "core",
            "--read-only",
            "--exclude-tools",
            "tracker_me_get",
        ],
    )
    assert res.exit_code == 0
    names = res.stdout.split()
    assert "tracker_issues_get" in names and "status_get" in names
    assert "tracker_me_get" not in names  # excluded
    assert "tracker_issues_create" not in names  # a write tool, hidden by --read-only
    assert "forms_surveys_delete" not in names  # outside the core profile


def test_appcontext_resolves_config_and_builds_each_client_once():
    config = AppConfig(http={"retries": 1})  # ty: ignore[invalid-argument-type]
    app_context = AppContext(config=config)
    assert app_context.resolve(AppConfig) is config
    tracker = app_context.resolve(TrackerClient)
    assert isinstance(tracker, TrackerClient)
    assert app_context.resolve(TrackerClient) is tracker
    assert AppContext.provides(TrackerClient)
    assert AppContext.provides(AppConfig)
    assert not AppContext.provides(str)
    assert not AppContext.provides("TrackerClient")


def test_appcontext_refuses_a_kind_it_does_not_provide():
    with pytest.raises(TypeError, match="str"):
        AppContext().resolve(str)


def test_a_caller_supplied_context_is_used(monkeypatch):
    """The root callback keeps an ``obj`` handed in by the caller — the DI seam for embedding."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")

    class FakeMe:
        def get(self) -> Me:
            return Me(login="injected")

    fake = SimpleNamespace(me=FakeMe())
    app_context = AppContext()
    app_context._clients[TrackerClient] = fake  # ty: ignore[invalid-assignment]
    res = runner.invoke(cli.app, ["-o", "json", "tracker", "me", "get"], obj=app_context)
    assert res.exit_code == 0, res.output
    assert '"login":"injected"' in res.stdout


def test_completion_is_enabled():
    """Shell completion is enabled: the completion options are registered on the root app.

    Checked via the resolved Click command's params (width-independent) rather than the
    rendered --help text, which rich truncates the option name on a narrow terminal.
    """
    from typer.main import get_command

    params = {p.name for p in get_command(cli.app).params}
    assert "install_completion" in params
    assert "show_completion" in params


def test_a_usage_error_wins_over_missing_credentials(monkeypatch, tmp_path):
    """Clients are built on first use, so a command's own argument check runs first (exit 2)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    res = runner.invoke(cli.app, ["forms", "answers", "get"])
    assert res.exit_code == 2, res.output  # a credentials error would exit 1
