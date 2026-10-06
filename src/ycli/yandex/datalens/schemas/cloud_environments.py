# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class ListCloudEnvironmentsArgs(RequestBody):
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of cloud environments to return.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of cloud environments.",
    )
    filter: list[str] | None = Field(
        default=None,
        description='Filter conditions applied to the cloud environment list, combined with AND. Each condition has the form `field="value"`, where field is one of `name`, `cloud_id`, `status` or `created_by_id`.',
    )
    include_permissions: bool | None = Field(
        default=None,
        alias="includePermissions",
        description="Whether to return permissions of the current user.",
    )


class GetCloudEnvironmentArgs(RequestBody):
    id: str = Field(..., description="ID of the cloud environment to return.")
    include_permissions: bool | None = Field(
        default=None,
        alias="includePermissions",
        description="Whether to return permissions of the current user.",
    )


class DeleteCloudEnvironmentArgs(RequestBody):
    id: str = Field(..., description="ID of the cloud environment to delete.")


class CloudEnvironmentCreatedAt(APIModel):
    """Time when the cloud environment was created."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: int | float | None = Field(
        default=None, description="Fractional seconds in nanoseconds."
    )


class CloudEnvironmentUpdatedAt(APIModel):
    """Time when the cloud environment was last updated."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: int | float | None = Field(
        default=None, description="Fractional seconds in nanoseconds."
    )


class CloudEnvironmentStorage(APIModel):
    """Storage settings of the cloud environment."""

    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum size of the storage bucket in bytes. Zero means unlimited.",
    )


class CreateCloudEnvironmentArgsStorage(APIModel):
    """Storage settings of the cloud environment."""

    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum size of the storage bucket in bytes. Zero means unlimited.",
    )


class UpdateCloudEnvironmentArgsStorage(APIModel):
    """New storage settings of the cloud environment. Fails for an environment created without storage."""

    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum size of the storage bucket in bytes. Zero means unlimited.",
    )


class CloudEnvironment(APIModel):
    id: str | None = Field(default=None, description="ID of the cloud environment.")
    name: str | None = Field(default=None, description="Name of the cloud environment.")
    description: str | None = Field(
        default=None, description="Description of the cloud environment."
    )
    created_at: CloudEnvironmentCreatedAt | None = Field(default=None, alias="createdAt")
    created_by_id: str | None = Field(
        default=None,
        alias="createdById",
        description="ID of the cloud environment creator.",
    )
    updated_at: CloudEnvironmentUpdatedAt | None = Field(default=None, alias="updatedAt")
    updated_by_id: str | None = Field(
        default=None,
        alias="updatedById",
        description="ID of the user who last updated the cloud environment.",
    )
    status: (
        Literal[
            "STATUS_UNSPECIFIED",
            "CREATING",
            "READY",
            "ERROR",
            "DELETING",
            "BROKEN",
        ]
        | str
        | None
    ) = Field(default=None, description="Current status of the cloud environment.")
    status_details: str | None = Field(
        default=None,
        alias="statusDetails",
        description="Details of the current status.",
    )
    cloud_id: str | None = Field(
        default=None,
        alias="cloudId",
        description="ID of the cloud that hosts the cloud environment.",
    )
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="ID of the DataLens tenant."
    )
    subnet_id: str | None = Field(
        default=None,
        alias="subnetId",
        description="ID of the subnet used by the cloud environment.",
    )
    security_group_ids: list[str] | None = Field(
        default=None,
        alias="securityGroupIds",
        description="IDs of the security groups used by the cloud environment.",
    )
    permissions: dict[str, bool] | None = Field(
        default=None,
        description="Permissions of the current user for the cloud environment.",
    )
    storage: CloudEnvironmentStorage | None = None


class ListCloudEnvironmentsResult(APIModel):
    cloud_environments: list[CloudEnvironment] | None = Field(
        default=None,
        alias="cloudEnvironments",
        description="Cloud environments matching the request.",
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of cloud environments.",
    )


class CreateCloudEnvironmentArgs(RequestBody):
    name: str = Field(..., description="Name of the cloud environment.")
    description: str | None = Field(
        default=None, description="Description of the cloud environment."
    )
    cloud_id: str = Field(
        ...,
        alias="cloudId",
        description="ID of the cloud in which to create the cloud environment.",
    )
    subnet_id: str = Field(
        ...,
        alias="subnetId",
        description="ID of the subnet used by the cloud environment.",
    )
    security_group_ids: list[str] | None = Field(
        default=None,
        alias="securityGroupIds",
        description="IDs of the security groups used by the cloud environment.",
    )
    storage: CreateCloudEnvironmentArgsStorage | None = None


class UpdateCloudEnvironmentArgs(RequestBody):
    """Only the fields passed in the request are updated; at least one of them is required. The network and the cloud cannot be changed."""

    id: str = Field(..., description="ID of the cloud environment to update.")
    name: str | None = Field(default=None, description="New name of the cloud environment.")
    description: str | None = Field(
        default=None,
        description="New description of the cloud environment. An empty string clears it.",
    )
    security_group_ids: list[str] | None = Field(
        default=None,
        alias="securityGroupIds",
        description="New IDs of the security groups used by the cloud environment.",
    )
    storage: UpdateCloudEnvironmentArgsStorage | None = None
