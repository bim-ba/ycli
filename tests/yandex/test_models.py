"""TDD for shared ``ycli.yandex.models`` helpers — ``require_found`` (the not-found guard)."""

import pytest
from pydantic import BaseModel

from ycli.yandex.models import require_found


class _LenientResult(BaseModel):
    """Stand-in for a lenient Forms/Tracker model that parses an empty 404 to all-``None``."""

    id: str | None = None


def test_require_found_raises_with_message_when_sentinel_is_true():
    empty = _LenientResult()
    with pytest.raises(ValueError, match="thing 'x' not found"):
        require_found(empty, sentinel=lambda r: r.id is None, message="thing 'x' not found")


def test_require_found_returns_result_when_sentinel_is_false():
    present = _LenientResult(id="17")
    out = require_found(present, sentinel=lambda r: r.id is None, message="unreachable")
    assert out is present
