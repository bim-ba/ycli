"""Pure ``.env`` upsert helper for `ycli auth login` — no HTTP, no serialization.

Backs up an existing file, replaces the given keys in place, and preserves every other
line (comments, blanks, unrelated keys). The path is an argument, so it is trivially
unit-testable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path


class EnvFile:
    """Upsert selected keys into a dotenv file without disturbing the rest."""

    @staticmethod
    def upsert(path: Path, values: Mapping[str, str]) -> Path | None:
        """Write ``values`` into ``path``; return the backup path, or ``None`` when new.

        An existing file is copied to ``<name>.bak`` first; keys already present are
        replaced in place, keys not present are appended, and every other line is kept.
        """
        backup: Path | None = None
        existing_lines: list[str] = []
        if path.exists():
            original = path.read_text(encoding="utf-8")
            backup = path.with_name(path.name + ".bak")
            backup.write_text(original, encoding="utf-8")
            backup.chmod(0o600)  # the backup holds a real token — keep it owner-only
            existing_lines = original.splitlines()
        remaining = dict(values)
        output: list[str] = []
        for line in existing_lines:
            key = EnvFile._key_of(line)
            if key in remaining:
                output.append(f"{key}={remaining.pop(key)}")
            else:
                output.append(line)
        output.extend(f"{key}={value}" for key, value in remaining.items())
        path.write_text("\n".join(output) + "\n", encoding="utf-8")
        path.chmod(0o600)  # holds a real OAuth token — keep it owner-only
        return backup

    @staticmethod
    def _key_of(line: str) -> str | None:
        """The dotenv key a line assigns, or ``None`` for a blank/comment/non-assignment."""
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            return None
        return stripped.split("=", 1)[0].strip()
