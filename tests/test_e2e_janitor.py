"""The janitor touches only stale e2e- objects, at most ``--max`` (``e2e/janitor.py``)."""

from __future__ import annotations

import argparse
import json
from typing import TYPE_CHECKING

import pytest
from e2e.janitor import parse_duration, sweep
from e2e.runner import CommandResult, Driver

if TYPE_CHECKING:
    from collections.abc import Sequence

NOW = 1_790_000_000
OLD = f"e2e-{NOW - 7200}-aaaa"
FRESH = f"e2e-{NOW - 60}-bbbb"


class FakeOrganization(Driver):
    """Listings for each service; records every write the janitor sends."""

    def __init__(self, transitions: list[dict[str, object]]) -> None:
        self.transitions = transitions
        self.writes: list[list[str]] = []

    def run(self, arguments: Sequence[str]) -> CommandResult:
        listings: dict[str, object] = {
            "tracker issues list": [
                {"key": "Q-1", "summary": f"{OLD} lifecycle", "status": "inProgress"},
                {"key": "Q-2", "summary": f"{OLD} lifecycle", "status": "closed"},
                {"key": "Q-3", "summary": f"{FRESH} lifecycle", "status": "open"},
                {"key": "Q-4", "summary": "a human's issue", "status": "open"},
            ],
            "wiki pages descendants": [
                {"id": 11, "slug": OLD},
                {"id": 12, "slug": "e2e-handmade"},
                {"id": 13, "slug": "users/someone"},
            ],
            "forms surveys list": [
                {"id": "f1", "name": f"{OLD} survey"},
                {"id": "f2", "name": None},
            ],
            "tracker transitions list": self.transitions,
        }
        command = " ".join(arguments[:3])
        if command in listings:
            return CommandResult(0, json.dumps(listings[command]), "")
        self.writes.append(list(arguments))
        return CommandResult(0, "", "")


CLOSE: list[dict[str, object]] = [
    {"id": "resolve", "to": {"key": "resolved"}},
    {"id": "close", "to": {"key": "closed"}},
]


def test_only_stale_run_named_objects_are_touched(capsys):
    organization = FakeOrganization(CLOSE)
    assert sweep(organization, "Q", 3600, 200, dry_run=False, now=NOW) == 0
    assert organization.writes == [
        ["tracker", "transitions", "execute", "Q-1", "close", "--field", "resolution=fixed"],
        ["wiki", "pages", "delete", "11"],
        ["forms", "surveys", "delete", "f1"],
    ]
    output = capsys.readouterr().out
    assert "skipped wiki 12 'e2e-handmade': no run stamp" in output
    assert "janitor: 5 e2e- objects, 3 stale, removed 3, 0 failed, 1 too recent" in output


def test_the_cap_holds_back_writes(capsys):
    organization = FakeOrganization(CLOSE)
    sweep(organization, "Q", 3600, 1, dry_run=False, now=NOW)
    assert [write[:4] for write in organization.writes] == [
        ["tracker", "transitions", "execute", "Q-1"]
    ]
    assert "cap reached: 2 stale objects left" in capsys.readouterr().out


def test_a_dry_run_writes_nothing(capsys):
    organization = FakeOrganization(CLOSE)
    sweep(organization, "Q", 3600, 200, dry_run=True, now=NOW)
    assert organization.writes == []
    output = capsys.readouterr().out
    assert "would remove tracker Q-1" in output
    assert "3 stale, would remove 3, 0 failed" in output


def test_an_issue_without_a_close_transition_is_reported(capsys):
    organization = FakeOrganization([{"id": "start", "to": {"key": "inProgress"}}])
    assert sweep(organization, "Q", 3600, 1, dry_run=False, now=NOW) == 1
    assert "FAILED tracker Q-1: Q-1: no transition leads to closed" in capsys.readouterr().err


def test_parse_duration():
    assert parse_duration("6h") == 21600
    assert parse_duration("0s") == 0
    with pytest.raises(argparse.ArgumentTypeError):
        parse_duration("6 hours")
