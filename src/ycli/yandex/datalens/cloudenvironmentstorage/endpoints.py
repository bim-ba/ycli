"""DataLens cloud environment storage operations, declared once (sans-IO).

Every one of them is marked experimental in the document DataLens publishes.

Examples:
    >>> bucket_object_metadata_get("env1", path="a/b.csv").body
    {'cloudEnvironmentId': 'env1', 'path': 'a/b.csv'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cloudenvironmentstorage.models import (
    BucketDownloadUrl,
    BucketObjectMetadata,
    BucketObjectsPage,
    BucketUploadUrl,
)
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.schemas.cloud_environment_storage import (
    CreateBucketDownloadUrlArgs,
    CreateBucketUploadUrlArgs,
    GetBucketObjectMetadataArgs,
    ListBucketObjectsArgs,
)


def bucket_objects_list(
    cloud_environment_id: str, *, prefix: str | None
) -> Paged[BucketObjectsPage, str]:
    body = ListBucketObjectsArgs(cloudEnvironmentId=cloud_environment_id, prefix=prefix)
    return Paged(
        RPC("listBucketObjects", BucketObjectsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.keys or [],
    )


def bucket_object_metadata_get(
    cloud_environment_id: str, *, path: str
) -> Endpoint[BucketObjectMetadata]:
    body = GetBucketObjectMetadataArgs(cloudEnvironmentId=cloud_environment_id, path=path)
    return RPC("getBucketObjectMetadata", BucketObjectMetadata, json=body, effect=Effect.READ)


def bucket_download_url_create(
    cloud_environment_id: str, *, path: str
) -> Endpoint[BucketDownloadUrl]:
    # A read: the link lets its holder read one object, and nothing is changed by making it.
    body = CreateBucketDownloadUrlArgs(cloudEnvironmentId=cloud_environment_id, path=path)
    return RPC("createBucketDownloadUrl", BucketDownloadUrl, json=body, effect=Effect.READ)


def bucket_upload_url_create(
    cloud_environment_id: str, *, path: str, size: str, content_md5: str
) -> Endpoint[BucketUploadUrl]:
    # A write: the link is the right to put an object into the bucket.
    body = CreateBucketUploadUrlArgs(
        cloudEnvironmentId=cloud_environment_id, path=path, size=size, contentMd5=content_md5
    )
    return RPC("createBucketUploadUrl", BucketUploadUrl, json=body, effect=Effect.WRITE)
