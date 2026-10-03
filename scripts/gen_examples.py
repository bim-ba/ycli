"""Generate the CLI / MCP / SDK example tabs the documentation pages include.

A page shows one operation three ways by including a snippet::

    --8 < --"docs/examples/operations/tracker.issues.get.md"

Each snippet is written from the operation's contract case (``tests/yandex/*/*/cases.py``): the
same argv, tool call and SDK call that ``tests/test_contract.py`` runs through every surface, so
an example on the site cannot drift from what the code does. Only the operations some page
includes are generated.

Usage::

    uv run scripts/gen_examples.py            # write the snippets the pages include
    uv run scripts/gen_examples.py --check    # exit 1 if one is stale, missing or unused
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:  # `tests` is importable when the script runs from anywhere
    sys.path.insert(0, str(ROOT))

from tests.contract import Sibling, load_cases  # noqa: E402

DOCS = ROOT / "docs"
SNIPPETS = DOCS / "examples" / "operations"
INCLUDE = re.compile(r'--8<-- "docs/examples/operations/([\w.]+)\.md"')
TERMINALS = DOCS / "examples" / "terminal"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
# The remark under `ycli auth login`, per site language.
SIGN_IN = {
    "en": "sign in through Yandex ID: the token is saved to .env",
    "ru": "вход через Яндекс ID: токен сохраняется в .env",
}


def _cases() -> dict[str, Any]:
    """The case each operation's example comes from: its first one reachable on every surface."""
    chosen: dict[str, Any] = {}
    for case in load_cases():
        current = chosen.get(case.operation)
        if current is None or (not (current.cli and current.mcp) and case.cli and case.mcp):
            chosen[case.operation] = case
    return chosen


def literal(value: Any) -> str:
    """A value as the Python source a reader would type.

    Examples:
        >>> literal({"queue": "DE", "tags": ["ui"], "done": True})
        '{"queue": "DE", "tags": ["ui"], "done": True}'
    """
    if isinstance(value, BaseModel):
        given = {
            name: getattr(value, name)
            for name in type(value).model_fields
            if name in value.model_fields_set
        }
        # A field the model does not declare (an open body) is a keyword argument like the rest.
        given |= value.model_extra or {}
        fields = ", ".join(f"{name}={literal(item)}" for name, item in given.items())
        return f"{type(value).__name__}({fields})"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, dict):
        return "{" + ", ".join(f"{literal(k)}: {literal(v)}" for k, v in value.items()) + "}"
    if isinstance(value, list | tuple):
        items = ", ".join(literal(item) for item in value)
        return f"[{items}]" if isinstance(value, list) else f"({items},)"
    return repr(value)


def sdk_call(case: Any) -> str:
    """The SDK call of a case: ``tracker.issues.get("DE-7")``."""
    domain = case.operation.split(".")[0]
    arguments = [
        f"{domain}.{arg.resource}" if isinstance(arg, Sibling) else literal(arg)
        for arg in case.args
    ]
    arguments += [f"{name}={literal(value)}" for name, value in case.kwargs.items()]
    return f"{case.operation}({', '.join(arguments)})"


def snippet(case: Any) -> str:
    """The tabs for one case; a surface the case does not reach has no tab."""
    tabs: list[tuple[str, str, str]] = []
    if case.cli:
        tabs.append(("CLI", "bash", shlex.join(["ycli", *case.cli])))
    if case.mcp:
        name, arguments = case.mcp
        call = json.dumps(
            {"name": name, "arguments": dict(arguments)}, ensure_ascii=False, indent=2
        )
        tabs.append(("MCP", "json", call))
    tabs.append(("SDK", "python", sdk_call(case)))
    blocks = []
    for title, language, code in tabs:
        body = "\n".join(f"    {line}" for line in code.splitlines())
        blocks.append(f'=== "{title}"\n\n    ```{language}\n{body}\n    ```\n')
    return "\n".join(blocks)


def first_call(language: str) -> str:
    """The animated terminal of the home page: install, sign in, and a real `issues get`.

    The issue is the demo fixture printed by ``docs/demo/render.py``, the same offline renderer
    the README recording uses, so the output is what ycli prints and holds no real data.
    """
    render = subprocess.run(
        [sys.executable, str(DOCS / "demo" / "render.py"), "tracker", "issues", "get", "DEMO-42"],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "COLUMNS": "100"},
    )
    output = "\n".join(line.rstrip() for line in ANSI.sub("", render.stdout).splitlines())
    return (
        '<div class="termy" markdown>\n\n```console\n'
        "$ uv tool install 'yandex-cli[mcp]'\n---> 100%\n"
        f"$ ycli auth login\n// {SIGN_IN[language]}\n"
        f"$ ycli tracker issues get DEMO-42\n{output.strip()}\n"
        "```\n\n</div>\n"
    )


def included() -> set[str]:
    """Every operation some documentation page includes."""
    return {
        operation
        for page in DOCS.rglob("*.md")
        if SNIPPETS not in page.parents
        for operation in INCLUDE.findall(page.read_text(encoding="utf-8"))
    }


def build() -> dict[Path, str]:
    """Every snippet to write, keyed by its path."""
    cases = _cases()
    unknown = sorted(included() - cases.keys())
    if unknown:
        raise SystemExit(f"gen_examples: no contract case for {', '.join(unknown)}")
    terminals = {
        TERMINALS / f"first-call.{language}.md": first_call(language) for language in SIGN_IN
    }
    operations = {
        SNIPPETS / f"{operation}.md": snippet(cases[operation]) for operation in included()
    }
    return {**operations, **terminals}


def main(argv: list[str] | None = None) -> int:
    """Write the snippets, or with ``--check`` report the stale and unused ones and exit 1."""
    parser = argparse.ArgumentParser(description="Generate the documentation's example tabs.")
    parser.add_argument("--check", action="store_true", help="exit 1 if a snippet is stale")
    args = parser.parse_args(argv)
    snippets = build()
    orphans = [
        path
        for directory in (SNIPPETS, TERMINALS)
        for path in directory.glob("*.md")
        if path not in snippets
    ]
    if args.check:
        stale = [
            path
            for path, text in snippets.items()
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        for path in [*stale, *orphans]:
            print(f"stale: {path.relative_to(ROOT)}", file=sys.stderr)
        if stale or orphans:
            print("run: uv run scripts/gen_examples.py", file=sys.stderr)
            return 1
        return 0
    for path in orphans:
        path.unlink()
    for path, text in snippets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
