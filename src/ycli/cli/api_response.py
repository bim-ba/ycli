"""``APIResponse`` — a JSON answer of ``ycli api``, whatever shape the endpoint gave it."""

from __future__ import annotations

from typing import Any

from pydantic import RootModel


class APIResponse(RootModel[Any]):
    """The decoded JSON body of a raw call: an object, an array or a scalar.

    A model, so ``--format`` treats it like every other result.

    Examples:
        >>> APIResponse({"key": "DE-1"}).model_dump()
        {'key': 'DE-1'}
    """
