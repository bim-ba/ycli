"""What git knows of the files of a repository: the one protection of a local edit."""

import subprocess
from collections.abc import Sequence
from pathlib import Path, PurePosixPath


def uncommitted(root: Path, paths: Sequence[PurePosixPath]) -> set[PurePosixPath]:
    """The ones of ``paths`` that hold work git has not committed.

    Outside a git repository, or with no ``git`` at all, nothing is known and nothing is named.

    Args:
        root: The root of the repository.
        paths: Files, from that root.

    Returns:
        The paths that are modified, staged or not tracked.
    """
    if not paths:
        return set()
    command = ["git", "status", "--porcelain", "--no-renames", "-z", "--", *map(str, paths)]
    try:
        told = subprocess.check_output(command, cwd=root, text=True, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {PurePosixPath(entry[3:]) for entry in told.split("\0") if entry}
