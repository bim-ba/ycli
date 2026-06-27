# Architecture Guardrails (Track A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `ycli`'s load-bearing architecture invariants impossible to break silently, by encoding them as import-linter contracts, pytest checks, public-surface snapshots, a scaffolding generator, a review rubric, and local+CI enforcement.

**Architecture:** Six numbered invariants live in `ARCHITECTURE.md` (source of truth). Each is enforced by an executable artifact: import-linter (`pyproject.toml`) for import-confinement, `tests/test_architecture.py` for structural/semantic checks, and `tests/snapshots/` for public-surface stability. A `/new-endpoint` generator makes the compliant shape the path of least resistance. Pre-commit + a Claude `Stop` hook + CI run the checks so drift fails in the authoring session, not after several PRs.

**Tech Stack:** Python ≥3.12, uv, pytest (existing 100%-cov gate), import-linter (new dev dep), pre-commit (new dev dep), Typer→Click introspection, FastMCP in-memory `Client`.

## Global Constraints

- Keep the 100%-coverage gate green (`--cov-fail-under=100`); every new module needs coverage.
- Conventional Commits only. NEVER put `[skip ci]`/`[ci skip]` in any commit or squash-merge message (GitHub scans the whole message → silently cancels the release).
- Branch → PR → green CI → explicit confirm before merge. Dependencies via `uv add --dev` only — never hand-edit `pyproject.toml` dependency lists.
- Guardrails stay few and load-bearing (YAGNI): exactly the six invariants below, no more.
- Verified facts (hold today): 16 resource dirs under `src/ycli/yandex/{tracker,wiki,forms}/<resource>/` each with `__init__.py`/`client.py`/`cli.py`/`mcp.py`/`models.py`; `requests`/`uplink` only in `*/client.py`,`base.py`,`transport.py`; `fastmcp` only in `mcp.py` modules; `model_dump_json` only in `src/ycli/output.py`; version via `importlib.metadata`; 23 MCP tools all carry `readOnlyHint=True`; CLI command tree = 49 nodes.

## The six invariants (authored in Task 1, enforced thereafter)

- **ARCH-1** Every `yandex/<domain>/<resource>/` has `__init__.py`,`client.py`,`cli.py`,`mcp.py`,`models.py`. — *test_architecture*
- **ARCH-2** `cli.py`/`mcp.py`/`models.py` never import `requests`/`uplink`. — *import-linter*
- **ARCH-3** `fastmcp` imported only in `mcp.py`; every MCP tool is read-only (read verb + `readOnlyHint=True`). — *import-linter + test_architecture*
- **ARCH-4** `model_dump_json` appears only in `src/ycli/output.py`. — *test_architecture*
- **ARCH-5** No hardcoded version literal / `YANDEX_ID_*` token / org-header string in `src/` outside `transport.py`/`__init__.py`. — *test_architecture*
- **ARCH-6** The CLI command tree and MCP tool list change only via an intentional snapshot update. — *snapshot tests*

## File Structure

- Create `ARCHITECTURE.md` — the six invariants + how to change one.
- Modify `pyproject.toml` — add `import-linter`/`pre-commit` dev deps + `[tool.importlinter]` contracts.
- Create `tests/test_architecture.py` — ARCH-1/3/4/5 checks.
- Create `tests/snapshots/__init__.py`, `tests/snapshots/_surface.py` (shared enumerators), `tests/snapshots/__main__.py` (`--update`), `tests/test_snapshots.py`, and the golden files `tests/snapshots/cli_tree.txt` + `tests/snapshots/mcp_tools.txt` — ARCH-6.
- Create `scripts/new_endpoint.py` + `.claude/commands/new-endpoint.md` — Layer 2 generator.
- Create `.claude/commands/arch-review.md` — Layer 3 rubric; modify `CLAUDE.md` — invariant-change rule + pointer.
- Create `.pre-commit-config.yaml`; modify `.claude/settings.json` (Stop hook) + `.github/workflows/ci.yml` (lint-imports step) — Layer 4.

---

### Task 1: ARCHITECTURE.md + CLAUDE.md pointer (Layer 0)

**Files:**
- Create: `ARCHITECTURE.md`
- Modify: `CLAUDE.md` (append a section)

**Interfaces:**
- Produces: the canonical invariant IDs `ARCH-1..ARCH-6` and the "to change an invariant, edit this doc + its enforcing test in the same PR" rule that later tasks and the review rubric reference.

- [ ] **Step 1: Write `ARCHITECTURE.md`**

````markdown
# Architecture

`ycli` exposes one SDK four ways (CLI, MCP server, Python SDK, Claude Code plugin).
Its strength is a regular, symmetric layout — and that regularity is enforced, not hoped for.
These invariants are checked by `tests/test_architecture.py`, import-linter (`pyproject.toml`),
and `tests/test_snapshots.py`. A failing build names the violated invariant.

## Layout

```
src/ycli/
├── cli.py · mcp.py · output.py · log.py     # roots
└── yandex/
    ├── base.py · transport.py               # shared HTTP/session
    └── <domain>/                            # tracker · wiki · forms
        ├── _base.py · _deps.py · _clideps.py · client.py · cli.py · mcp.py
        └── <resource>/                      # issues · pages · surveys · …
            ├── client.py   # uplink SDK — the ONLY place HTTP happens
            ├── cli.py      # Typer — output via ycli.output.render
            ├── mcp.py      # FastMCP read-only tools
            ├── models.py   # pydantic
            └── __init__.py
```

## Invariants

- **ARCH-1 — Four-surface symmetry.** Every `yandex/<domain>/<resource>/` directory contains
  `__init__.py`, `client.py`, `cli.py`, `mcp.py`, `models.py`. Use `/new-endpoint` to scaffold.
- **ARCH-2 — HTTP confinement.** `cli.py`, `mcp.py`, and `models.py` never import `requests` or
  `uplink`. All HTTP lives in `client.py` / `base.py` / `transport.py`.
- **ARCH-3 — MCP is read-only.** `fastmcp` is imported only in modules named `mcp.py`. Every MCP
  tool wraps a read (no `create/update/add/execute/delete/set/remove`) and carries
  `readOnlyHint=True` (via the `RO` annotation).
- **ARCH-4 — Output discipline.** CLI results render through `ycli.output.render`;
  `model_dump_json` may appear only in `src/ycli/output.py`. (Raw passthroughs like
  `json.dumps(raw)`, `print(count)`, `.content` are intentional and allowed.)
- **ARCH-5 — Single sources of truth.** No hardcoded version literal, `YANDEX_ID_*` token, or
  org-header string in `src/` outside `transport.py` (headers) and `__init__.py` (version, read
  from `importlib.metadata`).
- **ARCH-6 — Public-surface stability.** The CLI command tree and MCP tool list change only by
  regenerating the snapshots in `tests/snapshots/` on purpose.

## Changing an invariant

These are deliberate, not incidental. To change one: edit this file **and** its enforcing check
(in `tests/test_architecture.py`, `pyproject.toml`, or the snapshots) **in the same PR**, and say
so in the PR body. A reviewer (human or `/arch-review`) should reject a surface/structure change
that isn't reflected here.
````

- [ ] **Step 2: Append the pointer + rule to `CLAUDE.md`**

Append this section to `CLAUDE.md`:

```markdown
## Architecture invariants (enforced)

The repo's structure is enforced by executable checks — see [`ARCHITECTURE.md`](ARCHITECTURE.md)
for the six invariants (ARCH-1..6). They are verified by `tests/test_architecture.py`,
import-linter (`uv run lint-imports`), and `tests/test_snapshots.py`. Do **not** route around
them: HTTP only in `client.py`; CLI output only via `ycli.output.render`; MCP tools read-only;
new resources via `/new-endpoint`. To change an invariant, edit `ARCHITECTURE.md` **and** its
enforcing check in the **same** PR and flag it.
```

- [ ] **Step 3: Verify links resolve**

Run: `ls ARCHITECTURE.md && grep -c 'ARCH-1' ARCHITECTURE.md CLAUDE.md`
Expected: file listed; `ARCHITECTURE.md` count ≥1, `CLAUDE.md` count ≥1.

- [ ] **Step 4: Commit**

```bash
git add ARCHITECTURE.md CLAUDE.md
git commit -m "docs: add ARCHITECTURE.md with enforced invariants (ARCH-1..6)"
```

---

### Task 2: import-linter contracts (Layer 1 — ARCH-2, ARCH-3 import side)

**Files:**
- Modify: `pyproject.toml` (dev deps + `[tool.importlinter]`)

**Interfaces:**
- Produces: a passing `uv run lint-imports`; CI (Task 7) calls the same command.

- [ ] **Step 1: Add the dev dependency**

Run: `uv add --dev import-linter`
Expected: `import-linter` appears in `[dependency-groups].dev` and `uv.lock` updates.

- [ ] **Step 2: Add contracts to `pyproject.toml`**

Append to `pyproject.toml`:

```toml
[tool.importlinter]
root_package = "ycli"
include_external_packages = true

[[tool.importlinter.contracts]]
name = "ARCH-2: cli/mcp/models never import HTTP libraries directly"
type = "forbidden"
source_modules = [
    "ycli.yandex.**.cli",
    "ycli.yandex.**.mcp",
    "ycli.yandex.**.models",
]
forbidden_modules = ["requests", "uplink"]

[[tool.importlinter.contracts]]
name = "ARCH-3: fastmcp is imported only in mcp modules"
type = "forbidden"
source_modules = [
    "ycli.cli",
    "ycli.output",
    "ycli.yandex.**.cli",
    "ycli.yandex.**.client",
    "ycli.yandex.**.models",
]
forbidden_modules = ["fastmcp"]
```

- [ ] **Step 3: Verify it PASSES on the current (clean) code**

Run: `uv run lint-imports`
Expected: `Contracts: 2 kept, 0 broken.`

- [ ] **Step 4: Verify it CATCHES a violation (red-bar proof)**

Temporarily add `import requests` to `src/ycli/yandex/tracker/issues/cli.py`, then run `uv run lint-imports`.
Expected: `ARCH-2 ... BROKEN` and a non-zero exit. Then revert the edit:
```bash
git checkout src/ycli/yandex/tracker/issues/cli.py
uv run lint-imports   # back to: 2 kept, 0 broken
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "ci: enforce ARCH-2/ARCH-3 import boundaries with import-linter"
```

---

### Task 3: tests/test_architecture.py (Layer 1 — ARCH-1, ARCH-3 semantic, ARCH-4, ARCH-5)

**Files:**
- Create: `tests/test_architecture.py`

**Interfaces:**
- Consumes: package layout under `src/ycli`; the root MCP server `ycli.mcp.mcp`.
- Produces: nothing imported elsewhere; runs inside the existing pytest/coverage suite.

- [ ] **Step 1: Write the tests**

```python
"""Architecture invariants as tests — see ARCHITECTURE.md (ARCH-1/3/4/5).

A failure means a change drifted from the architecture. Fix the code, or — if the
change is intentional — update ARCHITECTURE.md and this check together in one PR.
"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path

from fastmcp import Client

from ycli.mcp import mcp as root_mcp

SRC = Path(__file__).resolve().parent.parent / "src" / "ycli"
YANDEX = SRC / "yandex"
DOMAINS = ("tracker", "wiki", "forms")
CANONICAL = {"__init__.py", "client.py", "cli.py", "mcp.py", "models.py"}
WRITE_VERBS = {"create", "update", "add", "execute", "delete", "set", "remove"}


def _resource_dirs():
    for domain in DOMAINS:
        for child in sorted((YANDEX / domain).iterdir()):
            if child.is_dir() and not child.name.startswith(("_", "__")):
                yield child


def test_arch1_four_surface_symmetry():
    checked = 0
    for d in _resource_dirs():
        files = {p.name for p in d.iterdir() if p.is_file()}
        missing = CANONICAL - files
        assert not missing, f"{d.relative_to(SRC)} missing canonical files: {sorted(missing)}"
        checked += 1
    assert checked >= 16, f"expected >=16 resource dirs, found {checked}"


def _mcp_tools():
    async def go():
        async with Client(root_mcp) as c:
            return await c.list_tools()
    return asyncio.run(go())


def test_arch3_mcp_tools_are_read_only():
    tools = _mcp_tools()
    assert tools, "no MCP tools discovered"
    for t in tools:
        verb = t.name.rsplit("_", 1)[-1]
        assert verb not in WRITE_VERBS, f"MCP tool {t.name!r} has a write verb"
        ann = getattr(t, "annotations", None)
        assert ann is not None and ann.readOnlyHint is True, f"{t.name!r} lacks readOnlyHint"


def test_arch4_model_dump_json_only_in_output():
    offenders = [
        str(p.relative_to(SRC))
        for p in SRC.rglob("*.py")
        if p.name != "output.py" and "model_dump_json" in p.read_text(encoding="utf-8")
    ]
    assert not offenders, f"model_dump_json must live only in output.py; found in {offenders}"


_TOKEN_RE = re.compile(r"YANDEX_ID_\w+\s*=\s*['\"]")
_VERSION_RE = re.compile(r"__version__\s*=\s*['\"]\d")
_ORG_HEADER_RE = re.compile(r"X-Org-I[dD]")


def test_arch5_single_sources_of_truth():
    offenders = []
    for p in SRC.rglob("*.py"):
        rel = p.relative_to(SRC)
        text = p.read_text(encoding="utf-8")
        if _TOKEN_RE.search(text):
            offenders.append(f"{rel}: hardcoded YANDEX_ID token literal")
        if p.name != "__init__.py" and _VERSION_RE.search(text):
            offenders.append(f"{rel}: hardcoded __version__ literal")
        if p.name != "transport.py" and _ORG_HEADER_RE.search(text):
            offenders.append(f"{rel}: org header string outside transport.py")
    assert not offenders, offenders
```

- [ ] **Step 2: Run — expect PASS on current code**

Run: `uv run pytest tests/test_architecture.py -v`
Expected: 4 passed.

- [ ] **Step 3: Red-bar proof for each check**

Verify each catches drift, reverting after each:
- ARCH-1: `rm src/ycli/yandex/tracker/worklog/models.py` → `test_arch1` FAILS → `git checkout src/ycli/yandex/tracker/worklog/models.py`.
- ARCH-4: add `x = obj.model_dump_json()` to `src/ycli/yandex/wiki/pages/cli.py` → `test_arch4` FAILS → revert.
- ARCH-5: add `__version__ = "9.9.9"` to `src/ycli/log.py` → `test_arch5` FAILS → revert.

Run after reverts: `uv run pytest tests/test_architecture.py -q` → 4 passed.

- [ ] **Step 4: Confirm coverage gate still green**

Run: `uv run pytest -q`
Expected: all pass, `Total coverage: 100.00%`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_architecture.py
git commit -m "test: enforce ARCH-1/3/4/5 architecture invariants"
```

---

### Task 4: Public-surface snapshot tests (Layer 1 — ARCH-6)

**Files:**
- Create: `tests/snapshots/__init__.py`, `tests/snapshots/_surface.py`, `tests/snapshots/__main__.py`, `tests/snapshots/cli_tree.txt`, `tests/snapshots/mcp_tools.txt`, `tests/test_snapshots.py`

**Interfaces:**
- Consumes: `ycli.cli.app`, `ycli.mcp.mcp`.
- Produces: `cli_tree() -> list[str]` and `mcp_tool_names() -> list[str]` in `_surface.py`; an `--update` entry point; two golden files.

- [ ] **Step 1: Write the shared enumerators `tests/snapshots/_surface.py`**

```python
"""Deterministic enumerators of ycli's public surface (CLI tree + MCP tool names)."""
from __future__ import annotations

import asyncio

import typer.main
from fastmcp import Client

from ycli.cli import app
from ycli.mcp import mcp


def cli_tree() -> list[str]:
    """Every CLI command path (space-joined), sorted, e.g. 'tracker issues get'."""
    root = typer.main.get_command(app)

    def walk(command, prefix: str) -> list[str]:
        out: list[str] = []
        for name in sorted(getattr(command, "commands", {})):
            path = f"{prefix} {name}".strip()
            out.append(path)
            out += walk(command.commands[name], path)
        return out

    return walk(root, "")


def mcp_tool_names() -> list[str]:
    """Every MCP tool name, sorted (protocol-level, via the in-memory client)."""
    async def go() -> list[str]:
        async with Client(mcp) as client:
            return sorted(t.name for t in await client.list_tools())

    return asyncio.run(go())
```

- [ ] **Step 2: Write `tests/snapshots/__init__.py`**

```python
"""Committed snapshots of ycli's public surface (see ARCHITECTURE.md ARCH-6)."""
```

- [ ] **Step 3: Write the updater `tests/snapshots/__main__.py`**

```python
"""Regenerate the committed surface snapshots: ``python -m tests.snapshots --update``."""
from __future__ import annotations

import sys
from pathlib import Path

from tests.snapshots._surface import cli_tree, mcp_tool_names

HERE = Path(__file__).resolve().parent
FILES = {HERE / "cli_tree.txt": cli_tree, HERE / "mcp_tools.txt": mcp_tool_names}


def main() -> None:
    if "--update" not in sys.argv:
        print("usage: python -m tests.snapshots --update")
        raise SystemExit(2)
    for path, fn in FILES.items():
        path.write_text("\n".join(fn()) + "\n", encoding="utf-8")
        print(f"wrote {path.name}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Generate the golden files**

Run: `uv run python -m tests.snapshots --update`
Expected: `wrote cli_tree.txt` and `wrote mcp_tools.txt`. Then sanity-check:
`wc -l tests/snapshots/cli_tree.txt tests/snapshots/mcp_tools.txt`
Expected: ~49 and ~23 lines respectively.

- [ ] **Step 5: Write `tests/test_snapshots.py`**

```python
"""ARCH-6: the public surface changes only via an intentional snapshot update."""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.snapshots._surface import cli_tree, mcp_tool_names

HERE = Path(__file__).resolve().parent / "snapshots"
HINT = "run `uv run python -m tests.snapshots --update` to accept the new surface"


@pytest.mark.parametrize(
    ("filename", "current"),
    [("cli_tree.txt", cli_tree), ("mcp_tools.txt", mcp_tool_names)],
)
def test_public_surface_matches_snapshot(filename, current):
    expected = (HERE / filename).read_text(encoding="utf-8").splitlines()
    assert current() == expected, f"public surface drifted ({filename}); {HINT}"
```

- [ ] **Step 6: Run — expect PASS, then red-bar proof**

Run: `uv run pytest tests/test_snapshots.py -v` → 2 passed.
Proof: add a throwaway `@app.command()` named `zzz` in `src/ycli/cli.py` → `cli_tree` test FAILS with the hint → revert. Re-run → 2 passed.

- [ ] **Step 7: Confirm full suite + coverage**

Run: `uv run pytest -q`
Expected: all pass, 100% coverage. (If `tests/snapshots/_surface.py` or `__main__.py` dips coverage, the snapshot test exercises `_surface.py`; add `# pragma: no cover` only to `__main__.py:main`'s `usage` branch if needed.)

- [ ] **Step 8: Commit**

```bash
git add tests/snapshots tests/test_snapshots.py
git commit -m "test: snapshot CLI tree + MCP tool list to lock the public surface (ARCH-6)"
```

---

### Task 5: `/new-endpoint` scaffolding generator (Layer 2)

**Files:**
- Create: `scripts/new_endpoint.py`, `.claude/commands/new-endpoint.md`

**Interfaces:**
- Produces: a CLI `python scripts/new_endpoint.py <domain> <resource>` that creates
  `src/ycli/yandex/<domain>/<resource>/{__init__,client,cli,mcp,models}.py` pre-wired to pass
  ARCH-1/2/3/4 and import-linter. Generated stubs contain one clearly-marked spot to wire the
  real API path.

- [ ] **Step 1: Write `scripts/new_endpoint.py`**

```python
"""Scaffold a new Yandex resource that satisfies the architecture by construction.

    python scripts/new_endpoint.py tracker macros

Creates src/ycli/yandex/tracker/macros/{__init__,client,cli,mcp,models}.py wired to the
domain deps, the render output path, and read-only MCP annotations. Fill the marked spots
with the real endpoint; the structure already satisfies ARCH-1..4 and import-linter.
"""
from __future__ import annotations

import argparse
from pathlib import Path

DOMAINS = ("tracker", "wiki", "forms")
ROOT = Path(__file__).resolve().parent.parent / "src" / "ycli" / "yandex"

INIT = '"""Yandex {domain} /{resource} resource (client · cli · mcp · models)."""\n'

MODELS = '''"""Pydantic models for {domain} /{resource}."""
from __future__ import annotations

from pydantic import BaseModel


class {cls}(BaseModel):
    """One {resource} record. FILL: add the real fields."""

    id: str = ""
'''

CLIENT = '''"""{domain} /{resource} SDK calls (uplink). The only place HTTP happens for this resource."""
from __future__ import annotations

from uplink import Consumer, get, returns

from ycli.yandex.{domain}.{resource}.models import {cls}


class {cls}Client(Consumer):
    """Read calls for /{resource}."""

    @returns.json
    @get("FILL/{resource}/{{item_id}}")  # FILL: real path
    def get(self, item_id: str) -> {cls}:  # type: ignore[empty-body]
        """Fetch one {resource} by id."""
'''

CLI = '''"""{domain} /{resource} Typer commands. Output via ycli.output.render."""
from __future__ import annotations

import typer

from ycli.output import render
from ycli.yandex.{domain}._clideps import {domain}_client

app = typer.Typer(name="{resource}", help="{domain} /{resource}.", no_args_is_help=True)


@app.command()
def get(ctx: typer.Context, item_id: str) -> None:
    """Fetch one {resource} by id."""
    render({domain}_client(ctx).{resource}.get(item_id))
'''

MCP = '''"""{domain} /{resource} FastMCP tools (read-only)."""
from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.{domain}._deps import RO, TAGS, {domain}_client
from ycli.yandex.{domain}.client import {domain_cls}Client
from ycli.yandex.{domain}.{resource}.models import {cls}

mcp = FastMCP("{domain}-{resource}")


@mcp.tool(name="{resource}_get", annotations=RO, tags=TAGS)
def get(item_id: str, client: {domain_cls}Client = Depends({domain}_client)) -> {cls}:
    """Fetch one {resource} by id."""
    return client.{resource}.get(item_id)
'''


def _cls(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new Yandex resource.")
    parser.add_argument("domain", choices=DOMAINS)
    parser.add_argument("resource", help="resource name, e.g. macros")
    args = parser.parse_args()

    resource = args.resource.replace("-", "_")
    target = ROOT / args.domain / resource
    if target.exists():
        raise SystemExit(f"{target} already exists")
    target.mkdir(parents=True)

    ctx = {
        "domain": args.domain,
        "resource": resource,
        "cls": _cls(resource),
        "domain_cls": _cls(args.domain),
    }
    for filename, template in (
        ("__init__.py", INIT),
        ("models.py", MODELS),
        ("client.py", CLIENT),
        ("cli.py", CLI),
        ("mcp.py", MCP),
    ):
        (target / filename).write_text(template.format(**ctx), encoding="utf-8")

    print(f"scaffolded {target.relative_to(ROOT.parent.parent.parent)}")
    print("next: replace the FILL markers, wire the sub-app/subserver into the domain "
          "cli.py + mcp.py, and add tests under tests/yandex/.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the generator produces an ARCH-compliant skeleton**

```bash
uv run python scripts/new_endpoint.py tracker _scratch
uv run pytest tests/test_architecture.py::test_arch1_four_surface_symmetry -q   # still passes (>=16; new dir compliant)
uv run lint-imports                                                             # 2 kept, 0 broken
rg -c FILL src/ycli/yandex/tracker/_scratch/client.py                           # marked spots present
rm -rf src/ycli/yandex/tracker/_scratch                                         # clean up scratch
```
Expected: arch test passes, import-linter clean, FILL markers present, scratch removed.

- [ ] **Step 3: Write `.claude/commands/new-endpoint.md`**

```markdown
---
description: Scaffold a new Yandex resource (client/cli/mcp/models) that satisfies the architecture by construction.
argument-hint: <domain> <resource>
---

Run the generator, then finish wiring:

1. `uv run python scripts/new_endpoint.py $ARGUMENTS`
2. Replace every `FILL` marker in the generated `client.py`/`models.py` with the real
   endpoint path and fields (see `docs/references/yandex/` for the API).
3. Mount the new sub-app into the domain `cli.py` (`app.add_typer(...)`) and the new subserver
   into the domain `mcp.py` (`mcp.mount(...)`), mirroring a sibling resource.
4. Add tests under `tests/yandex/<domain>/<resource>/` (client + cli + mcp) — reads ship across
   SDK+CLI+MCP; keep 100% coverage.
5. Run `uv run pytest`, `uv run lint-imports`, and `uv run python -m tests.snapshots --update`
   (the new commands/tools change the public surface — accept it intentionally).

Architecture rules: see ARCHITECTURE.md. HTTP only in `client.py`; CLI output via
`ycli.output.render`; MCP tools read-only.
```

- [ ] **Step 4: Commit**

```bash
git add scripts/new_endpoint.py .claude/commands/new-endpoint.md
git commit -m "feat: add /new-endpoint generator scaffolding ARCH-compliant resources"
```

---

### Task 6: Architecture review rubric (Layer 3)

**Files:**
- Create: `.claude/commands/arch-review.md`

**Interfaces:**
- Consumes: `ARCHITECTURE.md` invariants (Task 1).

- [ ] **Step 1: Write `.claude/commands/arch-review.md`**

```markdown
---
description: Review the current diff against the ARCHITECTURE.md invariants before merge.
---

Review the working diff (`git diff main...HEAD`) strictly against `ARCHITECTURE.md`. For each
invariant, state PASS/FAIL with file:line evidence:

- ARCH-1 every new resource dir has all five canonical files.
- ARCH-2 no `requests`/`uplink` import in `cli.py`/`mcp.py`/`models.py`.
- ARCH-3 `fastmcp` only in `mcp.py`; new MCP tools are read-only + `readOnlyHint`.
- ARCH-4 no `model_dump_json` outside `output.py`; CLI output via `render`.
- ARCH-5 no hardcoded version/token/org-header outside the sanctioned files.
- ARCH-6 if the CLI tree or MCP tool list changed, `tests/snapshots/` was regenerated AND the
  change is intentional.

Also flag SEMANTIC drift the linters can't see: business logic in `cli.py` that belongs in
`client.py`; a client method bypassing `transport`; a new ad-hoc output path; an asymmetric
resource. If any invariant changed, confirm `ARCHITECTURE.md` was edited in the SAME diff —
if not, that is a FAIL (silent invariant change). End with: APPROVE or REQUEST CHANGES + the
specific fixes.
```

- [ ] **Step 2: Verify front-matter parses**

Run: `head -3 .claude/commands/arch-review.md`
Expected: a `---` fenced `description:` block.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/arch-review.md
git commit -m "docs: add /arch-review rubric for invariant compliance"
```

---

### Task 7: Local + CI enforcement (Layer 4)

**Files:**
- Create: `.pre-commit-config.yaml`
- Modify: `.claude/settings.json` (add a `Stop` hook), `.github/workflows/ci.yml` (lint-imports step), `CONTRIBUTING.md` (pre-commit note)

**Interfaces:**
- Consumes: `uv run lint-imports` (Task 2), `tests/test_architecture.py` (Task 3).

- [ ] **Step 1: Add pre-commit dev dep**

Run: `uv add --dev pre-commit`

- [ ] **Step 2: Write `.pre-commit-config.yaml`**

```yaml
# Fast local guardrails — run: uv run pre-commit install
repos:
  - repo: local
    hooks:
      - id: lint-imports
        name: import-linter (ARCH-2/3 boundaries)
        entry: uv run lint-imports
        language: system
        pass_filenames: false
        files: ^src/ycli/.*\.py$
      - id: architecture-tests
        name: architecture invariants (ARCH-1/3/4/5)
        entry: uv run pytest tests/test_architecture.py tests/test_snapshots.py -q
        language: system
        pass_filenames: false
        files: ^(src/ycli/|tests/).*\.py$
      - id: no-skip-ci
        name: block skip-ci tokens in tracked files
        entry: bash -c '! git diff --cached -U0 | grep -nE "\[(skip ci|ci skip)\]"'
        language: system
        pass_filenames: false
```

- [ ] **Step 3: Verify pre-commit runs green**

Run: `uv run pre-commit run --all-files`
Expected: `lint-imports`, `architecture-tests`, `no-skip-ci` all Passed.

- [ ] **Step 4: Add a Claude `Stop` hook to `.claude/settings.json`**

Add a top-level `"hooks"` key (sibling to `"permissions"`) so the agent self-checks before handing back:

```json
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "cd \"$CLAUDE_PROJECT_DIR\" && uv run lint-imports >/dev/null 2>&1 && uv run pytest tests/test_architecture.py tests/test_snapshots.py -q >/dev/null 2>&1 || echo '⚠️ architecture guardrails failing — run: uv run pytest tests/test_architecture.py tests/test_snapshots.py && uv run lint-imports'"
        }
      ]
    }
  ]
}
```

- [ ] **Step 5: Validate the settings JSON**

Run: `python3 -c "import json; json.load(open('.claude/settings.json')); print('ok')"`
Expected: `ok`.

- [ ] **Step 6: Add the CI step to `.github/workflows/ci.yml`**

In the `test` job, after `Install dependencies` and before `Run tests`, insert:

```yaml
      - name: Check architecture boundaries
        run: uv run lint-imports
```
(The architecture + snapshot pytest files already run inside `uv run pytest`.)

- [ ] **Step 7: Add a CONTRIBUTING note**

Append under the setup section of `CONTRIBUTING.md`:

```markdown
### Architecture guardrails

The structure in [`ARCHITECTURE.md`](ARCHITECTURE.md) is enforced. Install the local hooks once:

```bash
uv run pre-commit install
```

They run import-linter + the architecture/snapshot tests on commit. CI runs the same. If you
change the public surface on purpose, regenerate snapshots: `uv run python -m tests.snapshots --update`.
```

- [ ] **Step 8: Full verification**

Run:
```bash
uv run pytest -q            # all pass, 100% coverage
uv run lint-imports         # 2 kept, 0 broken
uv run pre-commit run --all-files
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('ci ok')"
```
Expected: all green.

- [ ] **Step 9: Commit**

```bash
git add .pre-commit-config.yaml .claude/settings.json .github/workflows/ci.yml CONTRIBUTING.md pyproject.toml uv.lock
git commit -m "ci: run guardrails via pre-commit, a Stop hook, and CI"
```

---

## Notes for the executor

- This whole plan is **Track A**. Do it on one branch `feat/architecture-guardrails`, open a PR, let CI go green, and confirm before merge. The squash-merge title should be `feat:` (the `/new-endpoint` generator is user-facing) **unless** you want to avoid a release, in which case `chore:` — decide with the user. NEVER put a skip-ci token in the message.
- Snapshot regeneration is intentional: if Task 5's generator or any task changes the public surface, run `uv run python -m tests.snapshots --update` and review the diff.
- Keep coverage at 100%; the architecture/snapshot tests themselves count.
```
