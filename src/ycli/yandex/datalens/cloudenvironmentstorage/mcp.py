"""DataLens cloud environment storage FastMCP tools (read + write) — Depends DI."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.cloudenvironmentstorage.models import (
    BucketDownloadUrl,
    BucketObjectMetadata,
    BucketUploadUrl,
)
from ycli.yandex.datalens.dependencies import LIMIT_CAP, RO, WRITE, app_config, datalens_client
from ycli.yandex.models import ItemList

mcp = FastMCP("datalens-cloudenvironmentstorage")

StorageEnvironment = Annotated[
    str, Field(description="Id of the cloud environment the bucket belongs to.")
]
ObjectPath = Annotated[str, Field(description="The path of the object in the bucket.")]


@mcp.tool(
    name="cloudenvironmentstorage_bucket_objects_list",
    annotations={**RO, "title": "List the objects of a DataLens storage bucket"},
)
def bucket_objects_list(
    cloud_environment_id: StorageEnvironment,
    prefix: Annotated[str | None, Field(description="Only the paths that start with this.")] = None,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max paths to return; {LIMIT_CAP}")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[str]:
    """The paths of the objects in a cloud environment's storage bucket, auto-paginated.

    Experimental in the DataLens API and written from its document: not measured.
    """
    return client.cloudenvironmentstorage.bucket_objects_list(
        cloud_environment_id, prefix=prefix, limit=config.http.cap(limit)
    )


@mcp.tool(
    name="cloudenvironmentstorage_bucket_object_metadata_get",
    annotations={**RO, "title": "Get the metadata of a DataLens bucket object"},
)
def bucket_object_metadata_get(
    cloud_environment_id: StorageEnvironment,
    path: ObjectPath,
    client: DataLensClient = Depends(datalens_client),
) -> BucketObjectMetadata:
    """The size of an object, in bytes as a string, and when it last changed.

    Experimental in the DataLens API and written from its document: not measured.
    """
    return client.cloudenvironmentstorage.bucket_object_metadata_get(
        cloud_environment_id, path=path
    )


@mcp.tool(
    name="cloudenvironmentstorage_bucket_download_url_create",
    annotations={**RO, "title": "Create a download link for a DataLens bucket object"},
)
def bucket_download_url_create(
    cloud_environment_id: StorageEnvironment,
    path: ObjectPath,
    client: DataLensClient = Depends(datalens_client),
) -> BucketDownloadUrl:
    """A signed link to read one object of the bucket.

    The link works for whoever holds it, for a time, and it comes in this tool's result: hand
    it to the person and do not repeat it. Experimental in the DataLens API and written from
    its document: not measured.
    """
    return client.cloudenvironmentstorage.bucket_download_url_create(
        cloud_environment_id, path=path
    )


@mcp.tool(
    name="cloudenvironmentstorage_bucket_upload_url_create",
    annotations={**WRITE, "title": "Create an upload link for a DataLens bucket object"},
)
def bucket_upload_url_create(
    cloud_environment_id: StorageEnvironment,
    path: ObjectPath,
    size: Annotated[str, Field(description="The size of the object in bytes, as a string.")],
    content_md5: Annotated[
        str, Field(description="The MD5 digest of the content: 16 bytes, base64-encoded.")
    ],
    client: DataLensClient = Depends(datalens_client),
) -> BucketUploadUrl:
    """A signed link to put one object into the bucket.

    The link works for whoever holds it, for a time, and it comes in this tool's result: hand
    it to the person and do not repeat it. Experimental in the DataLens API and written from
    its document: not measured.
    """
    return client.cloudenvironmentstorage.bucket_upload_url_create(
        cloud_environment_id, path=path, size=size, content_md5=content_md5
    )
