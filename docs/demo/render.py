"""Render real `ycli` CLI output from a committed fixture — the demo's leak-free data source.

Used only by docs/demo/bin/ycli (the vhs shim). Stubs the matching API endpoint with
`responses`, sets dummy creds, and invokes the real Typer app in-process so the printed
output is genuine rendering of committed data — deterministic, offline, no real org data.

    python docs/demo/render.py tracker issues get TRACKER-1
    python docs/demo/render.py wiki pages get onboarding

Notes:
- wiki pages get: GET /pages?slug=<slug>&fields=content (query param, not path segment).
  The CLI prints page.content directly — --format has no effect on this command.
- tracker issues get: GET /issues/<key> (path param). Goes through Serializer with
  --format json for reliable output under typer.testing.CliRunner (no TTY).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import responses
from typer.testing import CliRunner

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
TRACKER = "https://api.tracker.yandex.net/v3"
WIKI = "https://api.wiki.yandex.net/v1"

# Map a demo command (argv tuple) to (HTTP method, URL, fixture file, cli_argv).
# wiki pages get: the client calls GET /pages?slug=onboarding&fields=content.
# responses matches on URL prefix by default; the query params are matched separately
# via match_querystring=False (default), so stub URL needs no query string.
ROUTES: dict[tuple[str, ...], tuple[str, str, str, list[str]]] = {
    ("tracker", "issues", "get", "TRACKER-1"): (
        responses.GET,
        f"{TRACKER}/issues/TRACKER-1",
        "tracker-issue.json",
        ["--format", "json", "tracker", "issues", "get", "TRACKER-1"],
    ),
    ("wiki", "pages", "get", "onboarding"): (
        responses.GET,
        f"{WIKI}/pages",
        "wiki-page.json",
        ["wiki", "pages", "get", "onboarding"],
    ),
}


def main(argv: list[str]) -> int:
    route = ROUTES.get(tuple(argv))
    if route is None:
        print(f"demo render: unknown command {argv}", file=sys.stderr)
        return 2
    method, url, fixture, cli_argv = route
    body = json.loads((FIXTURES / fixture).read_text(encoding="utf-8"))

    from ycli import cli

    runner = CliRunner()
    with responses.RequestsMock() as rsps:
        rsps.add(method, url, json=body, status=200)
        # Dummy creds satisfy Credentials(); responses intercepts the call (no real network).
        env = {"YANDEX_ID_OAUTH_TOKEN": "demo", "YANDEX_ID_ORGANIZATION_ID": "demo"}
        result = runner.invoke(cli.app, cli_argv, env=env)
    sys.stdout.write(result.stdout)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
