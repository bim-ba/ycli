# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class CreateBucketDownloadUrlResult(APIModel):
    url: str = Field(..., description="Temporary signed URL for accessing the object.")


class CreateBucketDownloadUrlArgs(RequestBody):
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment that owns the storage bucket.",
        max_length=50,
        min_length=1,
    )
    path: str = Field(
        ...,
        description="Path of the object in the storage bucket. Must not exceed 1024 UTF-8 bytes or contain control characters.",
        min_length=1,
    )


class CreateBucketUploadUrlResult(APIModel):
    url: str = Field(..., description="Temporary signed URL for accessing the object.")


class CreateBucketUploadUrlArgs(RequestBody):
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment that owns the storage bucket.",
        max_length=50,
        min_length=1,
    )
    path: str = Field(
        ...,
        description="Path of the object in the storage bucket. Must not exceed 1024 UTF-8 bytes or contain control characters.",
        min_length=1,
    )
    size: str = Field(..., description="Size of the object in bytes.", pattern="^(?:0|[1-9]\\d*)$")
    content_md5: str = Field(
        ...,
        alias="contentMd5",
        description="Base64-encoded 16-byte MD5 digest of the object content.",
        max_length=24,
        min_length=24,
    )


class LastModified(APIModel):
    """Time when the object was last modified."""

    seconds: str = Field(..., description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class GetBucketObjectMetadataResult(APIModel):
    size: str = Field(..., description="Size of the object in bytes.")
    last_modified: LastModified | None = Field(
        default=None,
        alias="lastModified",
        description="Time when the object was last modified.",
    )


class GetBucketObjectMetadataArgs(RequestBody):
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment that owns the storage bucket.",
        max_length=50,
        min_length=1,
    )
    path: str = Field(
        ...,
        description="Path of the object in the storage bucket. Must not exceed 1024 UTF-8 bytes or contain control characters.",
        min_length=1,
    )


class ListBucketObjectsResult(APIModel):
    keys: list[str] = Field(..., description="Paths of objects matching the request.")
    next_page_token: str = Field(
        ..., alias="nextPageToken", description="Token for the next page of objects."
    )


class ListBucketObjectsArgs(RequestBody):
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment that owns the storage bucket.",
        max_length=50,
        min_length=1,
    )
    prefix: str | None = Field(
        default=None,
        description="Prefix used to filter object paths. Must not exceed 1024 UTF-8 bytes or contain control characters. Lists all objects when omitted.",
    )
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of objects to return. The default is 1000.",
        ge=0,
        le=1000,
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of objects.",
    )
