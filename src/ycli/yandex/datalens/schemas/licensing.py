# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class LicenseWithLastLogin(APIModel):
    license_id: str | None = Field(
        default=None, alias="licenseId", description="Unique identifier of the license."
    )
    meta: dict[str, Any] | None = Field(default=None, description="Additional license metadata.")
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="ID of the tenant that owns the license.",
    )
    user_id: str | None = Field(
        default=None, alias="userId", description="ID of the user assigned the license."
    )
    license_type: Literal["creator", "viewer"] | str | None = Field(
        default=None, alias="licenseType", description="Type of the license."
    )
    is_active: bool | None = Field(
        default=None, alias="isActive", description="Whether the license is active."
    )
    expires_at: str | None = Field(
        default=None,
        alias="expiresAt",
        description="Date and time when the license expires.",
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the license.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the license was created.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the license.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the license was last updated.",
    )
    last_login_at: str | None = Field(
        default=None,
        alias="lastLoginAt",
        description="Date and time when the licensed user last logged in.",
    )


class GetLicensesResult(APIModel):
    licenses: list[LicenseWithLastLogin] | None = Field(
        default=None, description="Licenses matching the request."
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of licenses.",
    )


class GetLicensesArgs(RequestBody):
    user_ids: list[str] | None = Field(
        default=None,
        alias="userIds",
        description="IDs of users whose licenses should be returned.",
    )
    status: Literal["active", "expired", "expiring"] | str | None = Field(
        default=None, description="License status to filter by."
    )
    sort_by: Literal["createdAt", "updatedAt"] | str | None = Field(
        default=None, alias="sortBy", description="License field to sort by."
    )
    order: Literal["asc", "desc"] | str | None = Field(
        default=None, description="License sort order."
    )
    limit: int | float | None = Field(
        default=None, description="Maximum number of licenses to return."
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of licenses.",
    )


class SetLicenseLimitArgs(RequestBody):
    value: int | float = Field(
        ..., description="Maximum number of licenses allowed for the tenant."
    )


class License(APIModel):
    license_id: str | None = Field(
        default=None, alias="licenseId", description="Unique identifier of the license."
    )
    meta: dict[str, Any] | None = Field(default=None, description="Additional license metadata.")
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="ID of the tenant that owns the license.",
    )
    user_id: str | None = Field(
        default=None, alias="userId", description="ID of the user assigned the license."
    )
    license_type: Literal["creator", "viewer"] | str | None = Field(
        default=None, alias="licenseType", description="Type of the license."
    )
    is_active: bool | None = Field(
        default=None, alias="isActive", description="Whether the license is active."
    )
    expires_at: str | None = Field(
        default=None,
        alias="expiresAt",
        description="Date and time when the license expires.",
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the license.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the license was created.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the license.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the license was last updated.",
    )


class AssignLicensesArgs(RequestBody):
    user_ids: list[str] = Field(
        ..., alias="userIds", description="IDs of users to assign licenses to."
    )


class AssignLicensesResponse(RootModel[list[License]]):
    """Licenses assigned to the users."""

    root: list[License] = Field(..., description="Licenses assigned to the users.")


class LicenseLimitsCurrent(APIModel):
    """Current license limit."""

    type: Literal["regular", "forced"] | str | None = Field(
        default=None, description="Type of the license limit."
    )
    value: int | float | None = Field(
        default=None, description="Maximum number of active licenses."
    )
    started_at: str | None = Field(
        default=None,
        alias="startedAt",
        description="Date and time when the license limit takes effect.",
    )
    active_licenses_count: int | float | None = Field(
        default=None,
        alias="activeLicensesCount",
        description="Number of active licenses counted against the limit.",
    )


class LicenseLimitsNext(APIModel):
    """Upcoming license limit."""

    type: Literal["regular", "forced"] | str | None = Field(
        default=None, description="Type of the license limit."
    )
    value: int | float | None = Field(
        default=None, description="Maximum number of active licenses."
    )
    started_at: str | None = Field(
        default=None,
        alias="startedAt",
        description="Date and time when the license limit takes effect.",
    )
    active_licenses_count: int | float | None = Field(
        default=None,
        alias="activeLicensesCount",
        description="Number of active licenses counted against the limit.",
    )


class LicenseLimits(APIModel):
    current: LicenseLimitsCurrent | None = None
    next: LicenseLimitsNext | None = None
