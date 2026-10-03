"""The documentation site's contract (Diátaxis, issue #102), checked without building it.

Every page is in its site's navigation and every navigation entry is a page; a page's front
matter `type` names the Diátaxis folder it sits in; every relative link points at a file that
exists; the generated reference matches the code. The site build (`zensical build --strict` in
the docs workflow) additionally checks the anchors.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
SITES = {"en": ROOT / "zensical.toml", "ru": ROOT / "zensical.ru.toml"}
# The Diátaxis folder → the `type` its pages declare.
TYPES = {
    "tutorials": "tutorial",
    "how-to": "how-to",
    "reference": "reference",
    "explanation": "explanation",
}
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK = re.compile(r"\]\(([^)\s]+)\)")


def _load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "gen_reference", ROOT / "scripts" / "gen_reference.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _nav_pages(nav: Any) -> list[str]:
    """The page paths of a Zensical ``nav`` in order: sections flattened, external links out."""
    if isinstance(nav, str):
        return [] if nav.startswith("https://") else [nav]
    if isinstance(nav, list):
        return [page for entry in nav for page in _nav_pages(entry)]
    return [page for value in nav.values() for page in _nav_pages(value)]


def _site(language: str) -> tuple[Path, list[str]]:
    config = tomllib.loads(SITES[language].read_text(encoding="utf-8"))["project"]
    return ROOT / config["docs_dir"], _nav_pages(config["nav"])


def nav_problems(docs_dir: Path, nav: list[str]) -> list[str]:
    """Pages missing from ``nav``, and ``nav`` entries with no page."""
    pages = {path.relative_to(docs_dir).as_posix() for path in docs_dir.rglob("*.md")}
    return [f"not in nav: {page}" for page in sorted(pages - set(nav))] + [
        f"no such page: {page}" for page in nav if page not in pages
    ]


def type_problems(docs_dir: Path) -> list[str]:
    """Pages under a Diátaxis folder whose front matter ``type`` is missing or names another."""
    problems = []
    for path in sorted(docs_dir.rglob("*.md")):
        folder = path.relative_to(docs_dir).parts[0]
        if folder not in TYPES:
            continue
        match = FRONT_MATTER.match(path.read_text(encoding="utf-8"))
        declared = re.search(r"^type:\s*(\S+)", match.group(1), re.MULTILINE) if match else None
        if declared is None or declared.group(1) != TYPES[folder]:
            found = declared.group(1) if declared else None
            problems.append(
                f"{path.relative_to(docs_dir)}: type {found!r}, expected {TYPES[folder]!r}"
            )
    return problems


def link_problems(docs_dir: Path) -> list[str]:
    """Relative links whose target file does not exist."""
    problems = []
    for path in sorted(docs_dir.rglob("*.md")):
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            if re.match(r"[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            file = target.split("#", 1)[0]
            if not (path.parent / file).resolve().is_file():
                problems.append(f"{path.relative_to(docs_dir)}: broken link {target}")
    return problems


@pytest.mark.parametrize("language", sorted(SITES))
def test_every_page_is_in_the_navigation(language):
    assert nav_problems(*_site(language)) == []


@pytest.mark.parametrize("language", sorted(SITES))
def test_every_page_declares_the_type_of_its_folder(language):
    assert type_problems(_site(language)[0]) == []


@pytest.mark.parametrize("language", sorted(SITES))
def test_every_relative_link_resolves(language):
    assert link_problems(_site(language)[0]) == []


def test_the_generated_reference_is_fresh():
    assert _load_generator().main(["--check"]) == 0, "run: uv run scripts/gen_reference.py"


def test_the_checks_bite(tmp_path):
    """Each check reports the defect it exists for."""
    (tmp_path / "how-to").mkdir()
    (tmp_path / "how-to" / "a.md").write_text("---\ntype: tutorial\n---\n[x](missing.md)\n")
    (tmp_path / "orphan.md").write_text("# orphan\n")
    assert nav_problems(tmp_path, ["how-to/a.md", "gone.md"]) == [
        "not in nav: orphan.md",
        "no such page: gone.md",
    ]
    assert type_problems(tmp_path) == ["how-to/a.md: type 'tutorial', expected 'how-to'"]
    assert link_problems(tmp_path) == ["how-to/a.md: broken link missing.md"]
