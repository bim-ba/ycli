"""Contract cases for the storage of a DataLens cloud environment (see tests/contract/).

Written from the document: the owner's instance has no cloud environment, so nothing here
was measured.
"""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

ENV = "env0000000001"
DOWNLOAD = "https://storage.example.net/raw/orders.parquet?signature=example"
UPLOAD = "https://storage.example.net/raw/new.parquet?signature=example"
MD5 = "1B2M2Y8AsgTpgAmY7PhCfg=="

CASES = [
    Case(
        "datalens.cloudenvironmentstorage.bucket_objects_list",
        args=(ENV,),
        kwargs={"prefix": "raw/"},
        cli=["datalens", "cloudenvironmentstorage", "bucket-objects-list", ENV, "--prefix", "raw/"],
        mcp=(
            "datalens_cloudenvironmentstorage_bucket_objects_list",
            {"cloud_environment_id": ENV, "prefix": "raw/"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listBucketObjects",
                    json={"cloudEnvironmentId": ENV, "prefix": "raw/"},
                ),
                Reply(json={"keys": ["raw/orders.parquet"], "nextPageToken": "p2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/listBucketObjects",
                    json={"cloudEnvironmentId": ENV, "prefix": "raw/", "pageToken": "p2"},
                ),
                Reply(json={"keys": ["raw/users.parquet"], "nextPageToken": ""}),
            ),
        ],
    ),
    Case(
        "datalens.cloudenvironmentstorage.bucket_object_metadata_get",
        args=(ENV,),
        kwargs={"path": "raw/orders.parquet"},
        cli=[
            *("datalens", "cloudenvironmentstorage", "bucket-object-metadata-get", ENV),
            *("--path", "raw/orders.parquet"),
        ],
        mcp=(
            "datalens_cloudenvironmentstorage_bucket_object_metadata_get",
            {"cloud_environment_id": ENV, "path": "raw/orders.parquet"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getBucketObjectMetadata",
                    json={"cloudEnvironmentId": ENV, "path": "raw/orders.parquet"},
                ),
                Reply(
                    json={"size": "1048576", "lastModified": {"seconds": "1790000000", "nanos": 0}}
                ),
            )
        ],
    ),
    Case(
        "datalens.cloudenvironmentstorage.bucket_download_url_create",
        args=(ENV,),
        kwargs={"path": "raw/orders.parquet"},
        cli=[
            *("datalens", "cloudenvironmentstorage", "bucket-download-url-create", ENV),
            *("--path", "raw/orders.parquet"),
        ],
        mcp=(
            "datalens_cloudenvironmentstorage_bucket_download_url_create",
            {"cloud_environment_id": ENV, "path": "raw/orders.parquet"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createBucketDownloadUrl",
                    json={"cloudEnvironmentId": ENV, "path": "raw/orders.parquet"},
                ),
                Reply(json={"url": DOWNLOAD}),
            )
        ],
    ),
    Case(
        "datalens.cloudenvironmentstorage.bucket_upload_url_create",
        args=(ENV,),
        kwargs={"path": "raw/new.parquet", "size": "2048", "content_md5": MD5},
        cli=[
            *("datalens", "cloudenvironmentstorage", "bucket-upload-url-create", ENV),
            *("--path", "raw/new.parquet", "--size", "2048", "--content-md5", MD5),
        ],
        mcp=(
            "datalens_cloudenvironmentstorage_bucket_upload_url_create",
            {
                "cloud_environment_id": ENV,
                "path": "raw/new.parquet",
                "size": "2048",
                "content_md5": MD5,
            },
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createBucketUploadUrl",
                    json={
                        "cloudEnvironmentId": ENV,
                        "path": "raw/new.parquet",
                        "size": "2048",
                        "contentMd5": MD5,
                    },
                ),
                Reply(json={"url": UPLOAD}),
            )
        ],
    ),
]
