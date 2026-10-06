"""The documentation site's contract (Diátaxis, issue #102), checked without building it.

Every page is in its site's navigation and every navigation entry is a page; a page's front
matter `type` names the Diátaxis folder it sits in; every relative link points at a file that
exists; the generated reference matches the code. The site build (`zensical build --strict` in
the docs workflow) additionally checks the anchors.
"""

import importlib.util
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
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


def test_the_one_click_links_install_the_documented_server():
    """The Cursor and VS Code links on the install page decode to the server its snippets show."""
    import base64
    import json
    from urllib.parse import parse_qs, urlsplit

    page = (ROOT / "docs/en/how-to/install-in-your-harness.md").read_text(encoding="utf-8")
    command = {"command": "uvx", "args": ["--from", "yandex-cli[mcp]", "ycli", "mcp", "start"]}
    variables = ("YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID")

    cursor = set(re.findall(r"\((cursor://[^)\s]+)\)", page))
    assert len(cursor) == 1, "the matrix and the Cursor section must carry the same link"
    query = parse_qs(urlsplit(cursor.pop()).query)
    assert query["name"] == ["yandex-360"]
    assert json.loads(base64.b64decode(query["config"][0])) == {
        **command,
        "env": {name: f"${{env:{name}}}" for name in variables},
    }

    vscode = set(
        re.findall(r"\((https://insiders\.vscode\.dev/redirect/mcp/install[^)\s]+)\)", page)
    )
    assert len(vscode) == 1, "the matrix and the VS Code section must carry the same link"
    query = parse_qs(urlsplit(vscode.pop()).query)
    config = json.loads(query["config"][0])
    inputs = {entry["id"] for entry in json.loads(query["inputs"][0])}
    assert query["name"] == ["yandex-360"]
    assert {key: config[key] for key in command} == command
    assert {value[len("${input:") : -1] for value in config["env"].values()} == inputs
    assert set(config["env"]) == set(variables)


def _load_examples() -> Any:
    spec = importlib.util.spec_from_file_location(
        "gen_examples", ROOT / "scripts" / "gen_examples.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_generated_examples_are_fresh():
    assert _load_examples().main(["--check"]) == 0, "run: uv run scripts/gen_examples.py"


def test_an_example_is_the_contract_case_on_each_surface():
    from tests.contract import Case, Reply, Sent
    from ycli.yandex.tracker.boards.models import BoardCreate

    examples = _load_examples()
    case = Case(
        "tracker.boards.create",
        args=(BoardCreate(name="Release train", owner="alice"),),
        kwargs={"notify": False},
        cli=["tracker", "boards", "create", "--name", "Release train"],
        mcp=("tracker_boards_create", {"body": {"name": "Release train"}}),
        exchanges=[(Sent("POST", "liveBoards/"), Reply(json={"id": 1}))],
    )
    text = examples.snippet(case)
    assert "ycli tracker boards create --name 'Release train'" in text
    assert '"name": "tracker_boards_create"' in text
    assert (
        'tracker.boards.create(BoardCreate(name="Release train", owner="alice"), notify=False)'
        in text
    )
    sdk_only = Case("forms.answers.list", args=("s1",), cli=None, mcp=None, exchanges=[])
    assert [line for line in examples.snippet(sdk_only).splitlines() if line.startswith("===")] == [
        '=== "SDK"'
    ]


def test_the_examples_check_bites(tmp_path, monkeypatch, capsys):
    """A stale snippet, an unused one and an operation with no case are each reported."""
    examples = _load_examples()
    docs = tmp_path / "docs"
    snippets = docs / "examples" / "operations"
    snippets.mkdir(parents=True)
    (docs / "page.md").write_text('--8<-- "docs/examples/operations/tracker.issues.get.md"\n')
    (snippets / "tracker.issues.get.md").write_text("old\n")
    (snippets / "unused.md").write_text("x\n")
    monkeypatch.setattr(examples, "ROOT", tmp_path)
    monkeypatch.setattr(examples, "DOCS", docs)
    monkeypatch.setattr(examples, "SNIPPETS", snippets)
    monkeypatch.setattr(examples, "TERMINALS", docs / "examples" / "terminal")
    monkeypatch.setattr(examples, "SIGN_IN", {})  # no terminal snippet in this tree
    assert examples.main(["--check"]) == 1
    err = capsys.readouterr().err
    assert "stale: docs/examples/operations/tracker.issues.get.md" in err
    assert "stale: docs/examples/operations/unused.md" in err
    assert examples.main([]) == 0
    assert examples.main(["--check"]) == 0
    assert not (snippets / "unused.md").exists()
    (docs / "page.md").write_text('--8<-- "docs/examples/operations/tracker.nope.get.md"\n')
    with pytest.raises(SystemExit, match=r"no contract case for tracker\.nope\.get"):
        examples.main(["--check"])


def test_the_terminal_example_prints_what_ycli_prints():
    """The home page's terminal shows the demo fixture as the real CLI renders it."""
    text = _load_examples().first_call("en")
    assert "$ ycli tracker issues get DEMO-42\nkey       DEMO-42\n" in text
    assert "\x1b" not in text
    assert all(line == line.rstrip() for line in text.splitlines())


def _front_matter(path: Path) -> str:
    match = FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    return match.group(1) if match else ""


def undescribed(docs_dir: Path) -> list[str]:
    """Hand-written pages with no ``description`` of at most 160 characters (the search snippet)."""
    problems = []
    for path in sorted(docs_dir.rglob("*.md")):
        meta = _front_matter(path)
        if "generated: true" in meta:
            continue
        found = re.search(r'^description: "(.+)"$', meta, re.MULTILINE)
        if found is None or len(found.group(1)) > 160:
            problems.append(path.relative_to(docs_dir).as_posix())
    return problems


def outside_llms_txt(language: str) -> list[str]:
    """Hand-written pages that no ``llms.txt`` section lists (the home page is its header)."""
    from fnmatch import fnmatch

    config = tomllib.loads(SITES[language].read_text(encoding="utf-8"))["project"]
    docs_dir = ROOT / config["docs_dir"]
    patterns = [p for section in config["plugins"]["llmstxt"]["sections"].values() for p in section]
    return [
        page
        for page in _nav_pages(config["nav"])
        if page != "index.md"
        and "generated: true" not in _front_matter(docs_dir / page)
        and not any(fnmatch(page, pattern) for pattern in patterns)
    ]


@pytest.mark.parametrize("language", sorted(SITES))
def test_every_hand_written_page_has_a_description(language):
    assert undescribed(_site(language)[0]) == []


@pytest.mark.parametrize("language", sorted(SITES))
def test_llms_txt_lists_every_hand_written_page(language):
    assert outside_llms_txt(language) == []


@pytest.mark.parametrize("language", sorted(SITES))
def test_the_comparison_page_quotes_the_coverage_block(language):
    """The comparison page quotes the README's generated figures for ycli."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    operations = re.search(r"wraps \*\*(\d+) operations", readme)
    total = re.search(r"(\d+) \*\*MCP\*\* tools", readme)
    assert operations is not None and total is not None
    per_service = re.findall(r"operations · (\d+) MCP tools", readme)
    page = (_site(language)[0] / "explanation" / "comparison.md").read_text(encoding="utf-8")
    row = next(line for line in page.splitlines() if line.startswith("| ycli |"))
    assert re.findall(r"\d+", row) == [total[1], *per_service]
    assert f" {operations[1]} " in page


def test_the_description_check_bites(tmp_path):
    (tmp_path / "a.md").write_text("---\ntype: how-to\n---\n# A\n")
    (tmp_path / "b.md").write_text(f'---\ndescription: "{"x" * 161}"\n---\n# B\n')
    (tmp_path / "c.md").write_text('---\ndescription: "Fine."\n---\n# C\n')
    (tmp_path / "d.md").write_text("---\ngenerated: true\n---\n# D\n")
    assert undescribed(tmp_path) == ["a.md", "b.md"]
