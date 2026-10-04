"""Regenerate the committed surface snapshots: ``python -m tests.snapshots --update``."""

from __future__ import annotations

import sys
from pathlib import Path

from tests.snapshots._surface import (
    cli_signatures,
    mcp_output_schemas,
    mcp_prompts_and_resources,
    mcp_signatures,
)

HERE = Path(__file__).resolve().parent
FILES = {
    HERE / "cli_signatures.txt": cli_signatures,
    HERE / "mcp_signatures.txt": mcp_signatures,
    HERE / "mcp_prompts_and_resources.txt": mcp_prompts_and_resources,
    HERE / "mcp_output_schemas.txt": mcp_output_schemas,
}


def main() -> None:
    if "--update" not in sys.argv:  # pragma: no cover
        print("usage: python -m tests.snapshots --update")
        raise SystemExit(2)
    for path, fn in FILES.items():
        path.write_text("\n".join(fn()) + "\n", encoding="utf-8")
        print(f"wrote {path.name}")


if __name__ == "__main__":  # pragma: no cover
    main()
