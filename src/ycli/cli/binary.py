"""Binary CLI output — write raw ``bytes`` to a file or stdout (the ARCH-4 carve-out).

Model→text rendering goes through :class:`ycli.cli.output.Serializer`; a *binary* download
(an exported form, an attachment blob) is not model output and must never be JSON/YAML
serialized. This helper is that deliberate carve-out — the byte analogue of ``print(int)`` for
a scalar ``count``: it writes the bytes verbatim, to the file at ``output`` or, when ``output``
is ``None`` / ``"-"``, to ``sys.stdout.buffer`` so a shell can redirect it (``ycli … > file``).
"""

from __future__ import annotations

import sys
from pathlib import Path


def write_output(data: bytes, output: str | None) -> None:
    """Write ``data`` to the file at ``output``, or to ``sys.stdout.buffer`` for ``None`` / ``"-"``.

    Args:
        data: The raw bytes to emit (an exported form, a downloaded attachment, …).
        output: A filesystem path to write to, or ``None`` / ``"-"`` for standard output.

    Example:
        >>> write_output(b"%PDF-1.7 …", "report.pdf")  # doctest: +SKIP
        >>> write_output(b"%PDF-1.7 …", None)  # streams to stdout  # doctest: +SKIP
    """
    if output is None or output == "-":
        sys.stdout.buffer.write(data)
    else:
        Path(output).write_bytes(data)
