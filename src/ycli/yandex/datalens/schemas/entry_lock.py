# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class CreateEntryLockResult(APIModel):
    lock_token: str = Field(
        ..., alias="lockToken", description="Token identifying the created lock."
    )


class Data(APIModel):
    duration: float = Field(..., description="Lock duration in milliseconds.")
    force: bool | None = Field(
        default=None, description="Whether to replace an existing active lock."
    )


class CreateEntryLockArgs(RequestBody):
    entry_id: str = Field(..., alias="entryId", description="ID of the entry to lock.")
    data: Data


class EntryLock(APIModel):
    entry_id: str = Field(..., alias="entryId", description="ID of the locked entry.")
    lock_id: str = Field(..., alias="lockId", description="Unique identifier of the lock.")
    lock_token: str = Field(..., alias="lockToken", description="Token identifying the lock.")
    expiry_date: str = Field(
        ..., alias="expiryDate", description="Expiration date and time of the lock."
    )
    login: str = Field(..., description="Login of the user who owns the lock.")


class DataModel(APIModel):
    lock_token: str = Field(
        ..., alias="lockToken", description="Token identifying the lock to extend."
    )
    duration: float = Field(..., description="New lock duration in milliseconds.")
    force: bool | None = Field(default=None, description="Whether to force lock extension.")


class ExtendEntryLockArgs(RequestBody):
    entry_id: str = Field(
        ...,
        alias="entryId",
        description="ID of the entry whose lock should be extended.",
    )
    data: DataModel


class Params(APIModel):
    lock_token: str = Field(
        ..., alias="lockToken", description="Token identifying the lock to delete."
    )
    force: bool | None = Field(default=None, description="Whether to force lock deletion.")


class DeleteEntryLockArgs(RequestBody):
    entry_id: str = Field(
        ...,
        alias="entryId",
        description="ID of the entry whose lock should be deleted.",
    )
    params: Params
