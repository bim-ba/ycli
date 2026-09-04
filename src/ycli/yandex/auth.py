"""Authentication values shared by settings, transport, and SDK clients."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceAccountCredentials:
    """Authorized key used to mint IAM tokens for a Yandex Cloud service account."""

    key_id: str
    service_account_id: str
    private_key: str

    def to_yandexcloud_dict(self) -> dict[str, str]:
        return {
            "id": self.key_id,
            "service_account_id": self.service_account_id,
            "private_key": self.private_key,
        }
