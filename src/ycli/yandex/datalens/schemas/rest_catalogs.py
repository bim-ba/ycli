# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


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


class ListCatalogsResultRestCatalogsItemCreatedAt(APIModel):
    """Time when the REST catalog was created."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class ListCatalogsResultRestCatalogsItemUpdatedAt(APIModel):
    """Time when the REST catalog was last updated."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class ListCatalogsResultRestCatalogsItemBucketSettings(APIModel):
    """Settings of the REST catalog bucket."""

    storage_class: str | None = Field(
        default=None,
        alias="storageClass",
        description="Storage class of the REST catalog bucket.",
    )
    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum size of the REST catalog bucket in bytes.",
    )
    alias: str | None = Field(
        default=None, description="Human-readable alias of the REST catalog bucket."
    )
    description: str | None = Field(
        default=None, description="Description of the REST catalog bucket."
    )


class ListCatalogsResultRestCatalogsItemBucketDetailsUpdatedAt(APIModel):
    """Time when the bucket details were updated."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class CreateRestCatalogArgsBucketSettings(APIModel):
    """Settings of the REST catalog bucket."""

    storage_class: (
        Literal["STANDARD", "COLD", "STANDARD_IA", "NEARLINE", "ICE", "GLACIER"] | str | None
    ) = Field(
        default=None, alias="storageClass", description="Storage class of the REST catalog bucket."
    )
    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum size of the REST catalog bucket in bytes.",
    )
    alias: str | None = Field(
        default=None, description="Human-readable alias of the REST catalog bucket."
    )
    description: str | None = Field(
        default=None, description="Description of the REST catalog bucket."
    )


class CreateRestCatalogArgs(RequestBody):
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment in which to create the REST catalog.",
    )
    name: str = Field(..., description="Name of the REST catalog.")
    description: str | None = Field(default=None, description="Description of the REST catalog.")
    labels: dict[str, str] | None = Field(default=None, description="REST catalog labels.")
    bucket_settings: CreateRestCatalogArgsBucketSettings = Field(..., alias="bucketSettings")


class ListCatalogsResultRestCatalogsItemBucketDetails(APIModel):
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
    updated_at: ListCatalogsResultRestCatalogsItemBucketDetailsUpdatedAt | None = Field(
        default=None, alias="updatedAt"
    )


class ListCatalogsResultRestCatalogsItemBucket(APIModel):
    """Bucket associated with the REST catalog."""

    settings: ListCatalogsResultRestCatalogsItemBucketSettings | None = None
    details: ListCatalogsResultRestCatalogsItemBucketDetails | None = None


class ListCatalogsResultRestCatalogsItem(APIModel):
    id: str | None = Field(default=None, description="ID of the REST catalog.")
    organization_id: str | None = Field(
        default=None,
        alias="organizationId",
        description="ID of the organization that owns the REST catalog.",
    )
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="ID of the tenant that owns the REST catalog.",
    )
    cloud_environment_id: str | None = Field(
        default=None,
        alias="cloudEnvironmentId",
        description="ID of the associated cloud environment.",
    )
    name: str | None = Field(default=None, description="Name of the REST catalog.")
    description: str | None = Field(default=None, description="Description of the REST catalog.")
    labels: dict[str, str] | None = Field(default=None, description="REST catalog labels.")
    created_at: ListCatalogsResultRestCatalogsItemCreatedAt | None = Field(
        default=None, alias="createdAt"
    )
    created_by_id: str | None = Field(
        default=None,
        alias="createdById",
        description="ID of the user who created the REST catalog.",
    )
    updated_at: ListCatalogsResultRestCatalogsItemUpdatedAt | None = Field(
        default=None, alias="updatedAt"
    )
    bucket: ListCatalogsResultRestCatalogsItemBucket | None = None
    permissions: dict[str, bool] | None = Field(
        default=None, description="Permissions for the REST catalog."
    )


class ListCatalogsResult(APIModel):
    rest_catalogs: list[ListCatalogsResultRestCatalogsItem] | None = Field(
        default=None,
        alias="restCatalogs",
        description="REST catalogs matching the request.",
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of REST catalogs.",
    )
