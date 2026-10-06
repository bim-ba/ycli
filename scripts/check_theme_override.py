"""Fail when the theme partial we override has changed upstream.

`docs/overrides/partials/actions.html` is a copy of Zensical's partial with one more condition.
An upgrade that changes the original would leave the copy silently behind, so the docs workflow
runs this next to the build: compare the two files, update the copy, then the hash below.

Usage::

    uv run --only-group docs scripts/check_theme_override.py
"""

import hashlib
from importlib.resources import files

ORIGINAL = "templates/partials/actions.html"
SHA256 = "d76435e7c0e7cc581eaaffb83c7576ce1553d83f89247e4bab2cb766347b0fdb"


def main() -> int:
    """Exit 1 when the installed original no longer has the recorded hash."""
    actual = hashlib.sha256(files("zensical").joinpath(ORIGINAL).read_bytes()).hexdigest()
    if actual != SHA256:
        print(
            f"zensical/{ORIGINAL} changed (sha256 {actual}): compare it with "
            "docs/overrides/partials/actions.html, then update SHA256 in this script."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
