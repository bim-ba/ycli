"""Remove what interrupted live runs left behind: ``uv run python -m e2e.janitor --older-than 6h``.

Only objects named by a run (``e2e-<unix seconds>-…``, see ``e2e/conftest.py``) older than the
cutoff are touched: open Tracker issues in the sandbox queue are closed (the API cannot delete
an issue), Wiki pages and Forms surveys are deleted. At most ``--max`` objects per call, and
every object touched is printed.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from e2e.runner import CliDriver, Driver, ScenarioError, run_json
from e2e.settings import sandbox_queue

if TYPE_CHECKING:
    from collections.abc import Sequence

PREFIX = "e2e-"
_STAMP = re.compile(r"^e2e-(\d{10})-")
_DURATION = re.compile(r"^(\d+)([smhd])$")
_SECONDS_PER_UNIT = {"s": 1, "m": 60, "h": 3600, "d": 86400}


@dataclass(frozen=True, slots=True)
class Leftover:
    """An object a run created: ``service`` plus the id its delete or close command takes."""

    service: str
    identifier: str
    name: str

    @property
    def started_at(self) -> int | None:
        """The run's unix time from the name: ``e2e-1759370000-ab12 page`` -> ``1759370000``."""
        match = _STAMP.match(self.name)
        return int(match.group(1)) if match else None


def parse_duration(text: str) -> int:
    """``parse_duration("6h") -> 21600`` (seconds); units s, m, h, d."""
    match = _DURATION.match(text)
    if match is None:
        raise argparse.ArgumentTypeError(f"expected a duration like 30m or 6h, got {text!r}")
    return int(match.group(1)) * _SECONDS_PER_UNIT[match.group(2)]


def find_leftovers(driver: Driver, queue: str) -> list[Leftover]:
    """Every run-named object still alive: open issues in ``queue``, root pages, surveys."""
    issues = run_json(driver, ["tracker", "issues", "list", "--queue", queue, "--all"])
    pages = run_json(driver, ["wiki", "pages", "descendants-list", "", "--all"])
    surveys = run_json(driver, ["forms", "surveys", "list", "--all"])
    return [
        *(
            Leftover("tracker", issue["key"], issue["summary"])
            for issue in issues
            if issue["summary"].startswith(PREFIX) and issue["status"] != "closed"
        ),
        *(
            Leftover("wiki", str(page["id"]), page["slug"])
            for page in pages
            if page["slug"].startswith(PREFIX)
        ),
        *(
            Leftover("forms", survey["id"], survey["name"])
            for survey in surveys
            if (survey["name"] or "").startswith(PREFIX)
        ),
    ]


def remove(driver: Driver, leftover: Leftover) -> str:
    """Close the issue or delete the page or survey; return what was done."""
    if leftover.service == "tracker":
        # The listing comes from the search, which lags: a run may have closed the issue since.
        if (
            run_json(driver, ["tracker", "issues", "get", leftover.identifier])["status"]
            == "closed"
        ):
            return "already closed"
        transitions = run_json(driver, ["tracker", "transitions", "list", leftover.identifier])
        close = next(
            (item["id"] for item in transitions if (item.get("to") or {}).get("key") == "closed"),
            None,
        )
        if close is None:
            raise ScenarioError(f"{leftover.identifier}: no transition leads to closed")
        run_json(
            driver,
            [
                "tracker",
                "transitions",
                "execute",
                leftover.identifier,
                close,
                "--field",
                "resolution=fixed",
            ],
        )
        return "closed"
    if leftover.service == "wiki":
        run_json(driver, ["wiki", "pages", "delete", leftover.identifier])
        return "deleted"
    run_json(driver, ["forms", "surveys", "delete", leftover.identifier])
    return "deleted"


def sweep(
    driver: Driver,
    queue: str,
    older_than_seconds: int,
    maximum: int,
    dry_run: bool,
    now: float,
    runs: frozenset[str] | None = None,
) -> int:
    """Touch at most ``maximum`` stale leftovers; print each. Returns the process exit code.

    ``runs`` keeps the sweep to the objects those runs named (``e2e-1759370000-ab12``): a live
    run cleaning up after itself must not delete what another run, started meanwhile on a
    developer's machine, is still using.
    """
    leftovers = find_leftovers(driver, queue)
    if runs is not None:
        leftovers = [item for item in leftovers if item.name.startswith(tuple(runs))]
    cutoff = now - older_than_seconds
    stale = [item for item in leftovers if (item.started_at or now) <= cutoff]
    unnamed = [item for item in leftovers if item.started_at is None]
    for item in unnamed:
        print(f"skipped {item.service} {item.identifier} {item.name!r}: no run stamp in the name")
    failures = 0
    for item in stale[:maximum]:
        if dry_run:
            print(f"would remove {item.service} {item.identifier} {item.name!r}")
            continue
        try:
            outcome = remove(driver, item)
        except ScenarioError as error:
            failures += 1
            print(f"FAILED {item.service} {item.identifier}: {error}", file=sys.stderr)
            continue
        print(f"{outcome} {item.service} {item.identifier} {item.name!r}")
    if len(stale) > maximum:
        print(f"cap reached: {len(stale) - maximum} stale objects left for the next run")
    fresh = len(leftovers) - len(stale) - len(unnamed)
    verb = "would remove" if dry_run else "removed"
    print(
        f"janitor: {len(leftovers)} e2e- objects, {len(stale)} stale, "
        f"{verb} {min(len(stale), maximum) - failures}, {failures} failed, {fresh} too recent"
    )
    return 1 if failures else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m e2e.janitor", description=__doc__)
    parser.add_argument("--older-than", type=parse_duration, default=parse_duration("6h"))
    parser.add_argument("--max", type=int, default=200, dest="maximum")
    parser.add_argument("--queue", default=sandbox_queue())
    parser.add_argument("--dry-run", action="store_true", help="List, touch nothing.")
    parser.add_argument(
        "--runs-file",
        type=Path,
        help="Touch only what the runs listed in this file named (one run name per line).",
    )
    arguments = parser.parse_args(argv)
    runs = None
    if arguments.runs_file is not None:
        # No file: no scenario started, so there is nothing of this run to remove.
        listed = arguments.runs_file.read_text().split() if arguments.runs_file.exists() else []
        runs = frozenset(listed)
    return sweep(
        CliDriver(),
        arguments.queue,
        arguments.older_than,
        arguments.maximum,
        arguments.dry_run,
        time.time(),
        runs,
    )


if __name__ == "__main__":
    sys.exit(main())
