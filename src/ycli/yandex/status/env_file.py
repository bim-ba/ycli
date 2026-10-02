"""Pure ``.env`` upsert helper for `ycli auth login` — no HTTP, no serialization.

Backs up an existing file, then sets the given keys with python-dotenv's ``set_key``, which
replaces a key in place (``export KEY=`` lines included) and preserves every other line
(comments, blanks, unrelated keys). The path is an argument, so it is trivially unit-testable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from dotenv import set_key

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
        if path.exists():
            backup = path.with_name(path.name + ".bak")
            backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            backup.chmod(0o600)  # the backup holds a real token — keep it owner-only
        for key, value in values.items():
            set_key(path, key, value, quote_mode="never")  # the KEY=value form it always wrote
        path.chmod(0o600)  # holds a real OAuth token — keep it owner-only
        return backup
