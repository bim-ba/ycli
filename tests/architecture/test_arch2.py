"""ARCH-2: a layer that knows no service names every service there is."""

import tomllib
from pathlib import Path

from tests.architecture.scanners import DOMAINS

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"
SERVICES = {f"ycli.yandex.{domain}" for domain in DOMAINS}


def _contracts() -> list[dict]:
    document = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return document["tool"]["importlinter"]["contracts"]


def _services_not_forbidden(contracts: list[dict]) -> dict[str, list[str]]:
    """Per contract that forbids a service: the services of the registry it does not forbid."""
    return {
        contract["name"]: sorted(SERVICES - forbidden)
        for contract in contracts
        if (forbidden := set(contract.get("forbidden_modules", ()))) & SERVICES
    }


def test_arch2_a_layer_that_knows_no_service_forbids_every_service():
    """The list in a contract is written by hand; the registry says what it must hold."""
    found = _services_not_forbidden(_contracts())
    assert len(found) >= 2, "the core and the file engine each have such a contract"
    assert {name: missing for name, missing in found.items() if missing} == {}


def test_arch2_the_service_list_check_bites():
    all_but_one = sorted(SERVICES)[1:]
    partial = {"name": "core", "forbidden_modules": [*all_but_one, "typer"]}
    whole = {"name": "engine", "forbidden_modules": sorted(SERVICES)}
    other = {"name": "surfaces", "forbidden_modules": ["fastmcp"]}
    assert _services_not_forbidden([partial, whole, other]) == {
        "core": [sorted(SERVICES)[0]],
        "engine": [],
    }
