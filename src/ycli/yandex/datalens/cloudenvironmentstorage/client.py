"""DataLens cloud environment storage client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.cloudenvironmentstorage import endpoints

if TYPE_CHECKING:
    from ycli.yandex.core.listing import Listing
    from ycli.yandex.datalens.cloudenvironmentstorage.models import (
        BucketDownloadUrl,
        BucketObjectMetadata,
        BucketUploadUrl,
    )


class CloudEnvironmentStorageClient(Resource):
    """The storage bucket of a cloud environment: its objects, and links to read and write one.

    Experimental in the DataLens API and written from its document: the owner's instance has no
    cloud environment, so no reply was measured. An environment nothing knows answers
    ``403 Permission denied``.
    """

    def bucket_objects_list(
        self,
        cloud_environment_id: str,
        *,
        prefix: str | None = None,
        limit: int | None = None,
        next: str | None = None,
    ) -> Listing[str]:
        """``listBucketObjects`` → the paths of the objects in the bucket (not measured).

        Capped at ``limit`` (``None`` = every path).

        Args:
            cloud_environment_id: The environment the bucket belongs to.
            prefix: Only the paths that start with this.
            limit: The most paths to return; ``None`` returns every path.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.

        Returns:
            The paths of the objects.

        Examples:
            >>> datalens.cloudenvironmentstorage.bucket_objects_list(
            ...     "env0000000001", prefix="raw/"
            ... ).collect().items
            ['raw/orders.parquet', 'raw/users.parquet']
        """
        paged = endpoints.bucket_objects_list(cloud_environment_id, prefix=prefix)
        return self._session.iterate(paged, limit=limit, next=next)

    def bucket_object_metadata_get(
        self, cloud_environment_id: str, *, path: str
    ) -> BucketObjectMetadata:
        """``getBucketObjectMetadata`` → the size of an object and when it changed (not measured).

        Args:
            cloud_environment_id: The environment the bucket belongs to.
            path: The path of the object in the bucket.

        Returns:
            The size in bytes, as a string, and the time of the last change.

        Examples:
            >>> datalens.cloudenvironmentstorage.bucket_object_metadata_get(
            ...     "env0000000001", path="raw/orders.parquet"
            ... ).size
            '1048576'
        """
        return self._session.send(
            endpoints.bucket_object_metadata_get(cloud_environment_id, path=path)
        )

    def bucket_download_url_create(
        self, cloud_environment_id: str, *, path: str
    ) -> BucketDownloadUrl:
        """``createBucketDownloadUrl`` → a signed link to read one object (not measured).

        The link works for whoever holds it, for a time: treat it as a secret.

        Args:
            cloud_environment_id: The environment the bucket belongs to.
            path: The path of the object in the bucket.

        Returns:
            The link.

        Examples:
            >>> datalens.cloudenvironmentstorage.bucket_download_url_create(
            ...     "env0000000001", path="raw/orders.parquet"
            ... ).url
            'https://storage.example.net/raw/orders.parquet?signature=example'
        """
        return self._session.send(
            endpoints.bucket_download_url_create(cloud_environment_id, path=path)
        )

    def bucket_upload_url_create(
        self, cloud_environment_id: str, *, path: str, size: str, content_md5: str
    ) -> BucketUploadUrl:
        """``createBucketUploadUrl`` → a signed link to put one object (not measured).

        The link works for whoever holds it, for a time: treat it as a secret.

        Args:
            cloud_environment_id: The environment the bucket belongs to.
            path: The path the object is to have in the bucket.
            size: The size of the object in bytes, as a string.
            content_md5: The MD5 digest of the content: 16 bytes, base64-encoded.

        Returns:
            The link.

        Examples:
            >>> datalens.cloudenvironmentstorage.bucket_upload_url_create(
            ...     "env0000000001",
            ...     path="raw/new.parquet",
            ...     size="2048",
            ...     content_md5="1B2M2Y8AsgTpgAmY7PhCfg==",
            ... ).url
            'https://storage.example.net/raw/new.parquet?signature=example'
        """
        return self._session.send(
            endpoints.bucket_upload_url_create(
                cloud_environment_id, path=path, size=size, content_md5=content_md5
            )
        )
