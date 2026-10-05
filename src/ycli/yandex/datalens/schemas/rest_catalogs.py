# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class CreatedAt(APIModel):
    """Time when the REST catalog was created."""

    seconds: str = Field(..., description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class UpdatedAt(APIModel):
    """Time when the REST catalog was last updated."""

    seconds: str = Field(..., description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class Settings(APIModel):
    """Settings of the REST catalog bucket."""

    storage_class: str = Field(
        ...,
        alias="storageClass",
        description="Storage class of the REST catalog bucket.",
    )
    max_size: str = Field(
        ...,
        alias="maxSize",
        description="Maximum size of the REST catalog bucket in bytes.",
    )
    alias: str = Field(..., description="Human-readable alias of the REST catalog bucket.")
    description: str | None = Field(
        default=None, description="Description of the REST catalog bucket."
    )


class UpdatedAtModel(APIModel):
    """Time when the bucket details were updated."""

    seconds: str = Field(..., description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class Details(APIModel):
    """Current details of the REST catalog bucket."""

    used_size: str | None = Field(
        default=None,
        alias="usedSize",
        description="Current size of the bucket in bytes.",
    )
    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum size of the bucket in bytes.",
    )
    updated_at: UpdatedAtModel | None = Field(
        default=None,
        alias="updatedAt",
        description="Time when the bucket details were updated.",
    )


class Bucket(APIModel):
    """Bucket associated with the REST catalog."""

    settings: Settings = Field(..., description="Settings of the REST catalog bucket.")
    details: Details | None = Field(
        default=None, description="Current details of the REST catalog bucket."
    )


class RestCatalog(APIModel):
    id: str = Field(..., description="ID of the REST catalog.")
    organization_id: str = Field(
        ...,
        alias="organizationId",
        description="ID of the organization that owns the REST catalog.",
    )
    tenant_id: str = Field(
        ...,
        alias="tenantId",
        description="ID of the tenant that owns the REST catalog.",
    )
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the associated cloud environment.",
    )
    name: str = Field(..., description="Name of the REST catalog.")
    description: str = Field(..., description="Description of the REST catalog.")
    labels: dict[str, str] | None = Field(default=None, description="REST catalog labels.")
    created_at: CreatedAt | None = Field(
        default=None,
        alias="createdAt",
        description="Time when the REST catalog was created.",
    )
    created_by_id: str = Field(
        ...,
        alias="createdById",
        description="ID of the user who created the REST catalog.",
    )
    updated_at: UpdatedAt | None = Field(
        default=None,
        alias="updatedAt",
        description="Time when the REST catalog was last updated.",
    )
    bucket: Bucket = Field(..., description="Bucket associated with the REST catalog.")
    permissions: dict[str, bool] | None = Field(
        default=None, description="Permissions for the REST catalog."
    )


class ListCatalogsResult(APIModel):
    rest_catalogs: list[RestCatalog] = Field(
        ..., alias="restCatalogs", description="REST catalogs matching the request."
    )
    next_page_token: str = Field(
        ...,
        alias="nextPageToken",
        description="Token for the next page of REST catalogs.",
    )


class ListCatalogsArgs(RequestBody):
    cloud_environment_id: str | None = Field(
        default=None,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment to list REST catalogs in. Lists the whole tenant when omitted.",
    )
    filter: list[str] | None = Field(
        default=None,
        description='Filter expressions such as name="…"; only matching REST catalogs are returned.',
    )
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of REST catalogs to return. The default is 100.",
        ge=0,
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of REST catalogs.",
    )
    sort_by: Literal["name", "createdAt", "updatedAt"] | str | None = Field(
        default=None, alias="sortBy", description="Field used to sort REST catalogs."
    )
    reverse_order: bool | None = Field(
        default=None,
        alias="reverseOrder",
        description="Whether to sort REST catalogs in descending order.",
    )
    include_permissions: bool | None = Field(
        default=None,
        alias="includePermissions",
        description="Include permission information in the response.",
    )


class Labels(RootModel[str]):
    root: str = Field(..., max_length=63, pattern="^[-_0-9a-z]*$")


class BucketSettings(APIModel):
    """Settings of the REST catalog bucket."""

    storage_class: (
        Literal["STANDARD", "COLD", "STANDARD_IA", "NEARLINE", "ICE", "GLACIER"] | str
    ) = Field(..., alias="storageClass", description="Storage class of the REST catalog bucket.")
    max_size: str = Field(
        ...,
        alias="maxSize",
        description="Maximum size of the REST catalog bucket in bytes.",
        pattern="^\\d+$",
    )
    alias: str = Field(
        ...,
        description="Human-readable alias of the REST catalog bucket.",
        max_length=50,
        min_length=1,
    )
    description: str | None = Field(
        default=None,
        description="Description of the REST catalog bucket.",
        max_length=1024,
    )


class CreateRestCatalogArgs(RequestBody):
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment in which to create the REST catalog.",
        max_length=50,
        min_length=1,
    )
    name: str = Field(
        ...,
        description="Name of the REST catalog.",
        max_length=63,
        pattern="^[a-z](?:[a-z0-9_-]*[a-z0-9])?$",
    )
    description: str | None = Field(
        default=None, description="Description of the REST catalog.", max_length=200
    )
    labels: dict[str, Labels] | None = Field(default=None, description="REST catalog labels.")
    bucket_settings: BucketSettings = Field(
        ..., alias="bucketSettings", description="Settings of the REST catalog bucket."
    )
