"""Forms ``/surveys/{id}/keysets`` operations, declared once (sans-IO).

Examples:
    >>> download_keyset("686d", 3).response_type
    <class 'bytes'>
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.keysets.models import Keyset, KeysetList


def _keysets(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/keysets"


def list_keysets(survey_id: str) -> Endpoint[KeysetList]:
    return Endpoint("GET", _keysets(survey_id), KeysetList)


def get_keyset(survey_id: str, keyset_id: int) -> Endpoint[Keyset]:
    return Endpoint("GET", f"{_keysets(survey_id)}/{segment(keyset_id)}", Keyset)


def create_keyset(survey_id: str, body: dict[str, Any]) -> Endpoint[Keyset]:
    return Endpoint("POST", _keysets(survey_id), Keyset, json=body)


def modify_keyset(survey_id: str, keyset_id: int, body: dict[str, Any]) -> Endpoint[Keyset]:
    return Endpoint("PATCH", f"{_keysets(survey_id)}/{segment(keyset_id)}", Keyset, json=body)


def delete_keyset(survey_id: str, keyset_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"{_keysets(survey_id)}/{segment(keyset_id)}")


def download_keyset(survey_id: str, keyset_id: int) -> Endpoint[bytes]:
    return Endpoint("GET", f"{_keysets(survey_id)}/{segment(keyset_id)}/download", bytes)
