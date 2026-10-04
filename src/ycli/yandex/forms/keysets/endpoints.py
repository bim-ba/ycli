"""Forms ``/surveys/{id}/keysets`` operations, declared once (sans-IO).

Examples:
    >>> download("686d", 3).response_type
    <class 'bytes'>
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.keysets.models import Keyset, KeysetCreate, KeysetUpdate
from ycli.yandex.models import ItemList


def _keysets(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/keysets"


def list_(survey_id: str) -> Endpoint[ItemList[Keyset]]:
    return Endpoint("GET", _keysets(survey_id), ItemList[Keyset])


def get(survey_id: str, keyset_id: int) -> Endpoint[Keyset]:
    return Endpoint("GET", f"{_keysets(survey_id)}/{segment(keyset_id)}", Keyset)


def create(survey_id: str, body: KeysetCreate) -> Endpoint[Keyset]:
    return Endpoint("POST", _keysets(survey_id), Keyset, json=body)


def update(survey_id: str, keyset_id: int, body: KeysetUpdate) -> Endpoint[Keyset]:
    return Endpoint("PATCH", f"{_keysets(survey_id)}/{segment(keyset_id)}", Keyset, json=body)


def delete(survey_id: str, keyset_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"{_keysets(survey_id)}/{segment(keyset_id)}")


def download(survey_id: str, keyset_id: int) -> Endpoint[bytes]:
    return Endpoint("GET", f"{_keysets(survey_id)}/{segment(keyset_id)}/download", bytes)
