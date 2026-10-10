"""`datalens cloudenvironmentstorage` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, NextOption
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.cloudenvironmentstorage.models import (
    BucketDownloadUrl,
    BucketObjectMetadata,
    BucketUploadUrl,
)

UNMEASURED = (
    "Experimental in the DataLens API and written from its document: not measured. An "
    "environment nothing knows answers 403 Permission denied."
)
app = typer.Typer(
    name="cloudenvironmentstorage",
    help="The storage bucket of a DataLens cloud environment (experimental in the API).",
    no_args_is_help=True,
)

StorageEnvironmentArg = Annotated[
    str,
    typer.Argument(metavar="CLOUD_ENVIRONMENT_ID", help="Id of the cloud environment."),
]
ObjectPathOption = Annotated[
    str, typer.Option("--path", help="The path of the object in the bucket.")
]


@app.command("bucket-objects-list", epilog=UNMEASURED)
def bucket_objects_list(
    cloud_environment_id: StorageEnvironmentArg,
    prefix: Annotated[
        str | None, typer.Option("--prefix", help="Only the paths that start with this.")
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[str]:
    """List the paths of the objects in the bucket (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.cloudenvironmentstorage.bucket_objects_list(
        cloud_environment_id, prefix=prefix, limit=cap, next=next_
    )


@app.command("bucket-object-metadata-get", epilog=UNMEASURED)
def bucket_object_metadata_get(
    cloud_environment_id: StorageEnvironmentArg,
    path: ObjectPathOption,
    *,
    datalens: DataLensClient,
) -> BucketObjectMetadata:
    """Print the size of an object and when it last changed."""
    return datalens.cloudenvironmentstorage.bucket_object_metadata_get(
        cloud_environment_id, path=path
    )


@app.command("bucket-download-url-create", epilog=UNMEASURED)
def bucket_download_url_create(
    cloud_environment_id: StorageEnvironmentArg,
    path: ObjectPathOption,
    *,
    datalens: DataLensClient,
) -> BucketDownloadUrl:
    """Print a signed link to read one object; it works for whoever holds it."""
    return datalens.cloudenvironmentstorage.bucket_download_url_create(
        cloud_environment_id, path=path
    )


@app.command("bucket-upload-url-create", epilog=UNMEASURED)
def bucket_upload_url_create(
    cloud_environment_id: StorageEnvironmentArg,
    path: ObjectPathOption,
    size: Annotated[str, typer.Option("--size", help="The size of the object in bytes.")],
    content_md5: Annotated[
        str,
        typer.Option("--content-md5", help="The MD5 digest of the content, base64-encoded."),
    ],
    *,
    datalens: DataLensClient,
) -> BucketUploadUrl:
    """Print a signed link to put one object; it works for whoever holds it."""
    return datalens.cloudenvironmentstorage.bucket_upload_url_create(
        cloud_environment_id, path=path, size=size, content_md5=content_md5
    )
