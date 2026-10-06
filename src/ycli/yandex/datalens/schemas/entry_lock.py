# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class CreateEntryLockResult(APIModel):
    lock_token: str | None = Field(
        default=None,
        alias="lockToken",
        description="Token identifying the created lock.",
    )


class EntryLock(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="ID of the locked entry."
    )
    lock_id: str | None = Field(
        default=None, alias="lockId", description="Unique identifier of the lock."
    )
    lock_token: str | None = Field(
        default=None, alias="lockToken", description="Token identifying the lock."
    )
    expiry_date: str | None = Field(
        default=None,
        alias="expiryDate",
        description="Expiration date and time of the lock.",
    )
    login: str | None = Field(default=None, description="Login of the user who owns the lock.")


class CreateEntryLockArgsData(APIModel):
    duration: int | float | None = Field(default=None, description="Lock duration in milliseconds.")
    force: bool | None = Field(
        default=None, description="Whether to replace an existing active lock."
    )


class ExtendEntryLockArgsData(APIModel):
    lock_token: str | None = Field(
        default=None,
        alias="lockToken",
        description="Token identifying the lock to extend.",
    )
    duration: int | float | None = Field(
        default=None, description="New lock duration in milliseconds."
    )
    force: bool | None = Field(default=None, description="Whether to force lock extension.")


class DeleteEntryLockArgsParams(APIModel):
    lock_token: str | None = Field(
        default=None,
        alias="lockToken",
        description="Token identifying the lock to delete.",
    )
    force: bool | None = Field(default=None, description="Whether to force lock deletion.")


class CreateEntryLockArgs(RequestBody):
    entry_id: str = Field(..., alias="entryId", description="ID of the entry to lock.")
    data: CreateEntryLockArgsData


class ExtendEntryLockArgs(RequestBody):
    entry_id: str = Field(
        ...,
        alias="entryId",
        description="ID of the entry whose lock should be extended.",
    )
    data: ExtendEntryLockArgsData


class DeleteEntryLockArgs(RequestBody):
    entry_id: str = Field(
        ...,
        alias="entryId",
        description="ID of the entry whose lock should be deleted.",
    )
    params: DeleteEntryLockArgsParams
