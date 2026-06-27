"""Packaging guarantees that aren't covered by behavior tests.

The PEP 561 marker is easy to drop by accident (it's an empty file, invisible
in diffs) yet load-bearing: without it, every downstream mypy/pyright treats
``ycli`` as untyped and the typed pydantic models are invisible. Lock it in.
"""

from __future__ import annotations

from importlib import resources


def test_py_typed_marker_is_packaged():
    """``ycli`` ships a PEP 561 ``py.typed`` marker next to the package."""
    marker = resources.files("ycli").joinpath("py.typed")
    assert marker.is_file(), "PEP 561 py.typed marker missing from the ycli package"
