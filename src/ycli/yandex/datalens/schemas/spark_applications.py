# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class ListSparkApplicationsArgs(RequestBody):
    cluster_id: str = Field(..., alias="clusterId", description="ID of the Spark cluster.")
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of Spark applications to return. The default is 100.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of Spark applications.",
    )
    filter: list[str] | None = Field(
        default=None,
        description='Filter conditions applied to the Spark application list, combined with AND. Each condition has the form `field="value"`, where field is one of `name`, `created_by`, `application_type` or `catalog_id`.',
    )


class GetSparkApplicationArgs(RequestBody):
    cluster_id: str = Field(..., alias="clusterId", description="ID of the Spark cluster.")
    application_id: str = Field(
        ..., alias="applicationId", description="ID of the Spark application to return."
    )


class CancelSparkApplicationArgs(RequestBody):
    cluster_id: str = Field(..., alias="clusterId", description="ID of the Spark cluster.")
    application_id: str = Field(
        ..., alias="applicationId", description="ID of the Spark application to cancel."
    )


class ListSparkApplicationLogResult(APIModel):
    content: str | None = Field(
        default=None, description="Requested fragment of the Spark application log."
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next fragment of the Spark application log.",
    )


class ListSparkApplicationLogArgs(RequestBody):
    cluster_id: str = Field(..., alias="clusterId", description="ID of the Spark cluster.")
    application_id: str = Field(
        ..., alias="applicationId", description="ID of the Spark application."
    )
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum length of the returned log fragment.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next fragment of the Spark application log.",
    )


class SparkApplicationCreatedAt(APIModel):
    """Time when the Spark application was created."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: int | float | None = Field(
        default=None, description="Fractional seconds in nanoseconds."
    )


class SparkApplicationStartedAt(APIModel):
    """Time when the Spark application was started."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: int | float | None = Field(
        default=None, description="Fractional seconds in nanoseconds."
    )


class SparkApplicationFinishedAt(APIModel):
    """Time when the Spark application was finished."""

    seconds: str | None = Field(default=None, description="Number of seconds since the Unix epoch.")
    nanos: int | float | None = Field(
        default=None, description="Fractional seconds in nanoseconds."
    )


class SparkApplicationCatalogsItem(APIModel):
    catalog_id: str | None = Field(
        default=None, alias="catalogId", description="ID of the REST catalog."
    )


class SparkApplicationSparkApplication(APIModel):
    args: list[str] | None = Field(
        default=None, description="Arguments passed to the Spark driver."
    )
    jar_file_uris: list[str] | None = Field(
        default=None,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
    )
    file_uris: list[str] | None = Field(
        default=None,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
    )
    archive_uris: list[str] | None = Field(
        default=None,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
    )
    properties: dict[str, str] | None = Field(
        default=None, description="Spark configuration properties."
    )
    main_jar_file_uri: str | None = Field(
        default=None,
        alias="mainJarFileUri",
        description="URI of the JAR file that contains the main class.",
    )
    main_class: str | None = Field(
        default=None, alias="mainClass", description="Name of the driver main class."
    )
    packages: list[str] | None = Field(
        default=None, description="Maven packages added to the Spark classpaths."
    )
    repositories: list[str] | None = Field(
        default=None, description="Additional Maven repositories."
    )
    exclude_packages: list[str] | None = Field(
        default=None,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
    )


class SparkApplicationPysparkApplication(APIModel):
    args: list[str] | None = Field(
        default=None, description="Arguments passed to the PySpark driver."
    )
    jar_file_uris: list[str] | None = Field(
        default=None,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
    )
    file_uris: list[str] | None = Field(
        default=None,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
    )
    archive_uris: list[str] | None = Field(
        default=None,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
    )
    properties: dict[str, str] | None = Field(
        default=None, description="Spark configuration properties."
    )
    main_python_file_uri: str | None = Field(
        default=None,
        alias="mainPythonFileUri",
        description="URI of the main Python file.",
    )
    python_file_uris: list[str] | None = Field(
        default=None,
        alias="pythonFileUris",
        description="Additional Python files passed to PySpark.",
    )
    packages: list[str] | None = Field(
        default=None, description="Maven packages added to the Spark classpaths."
    )
    repositories: list[str] | None = Field(
        default=None, description="Additional Maven repositories."
    )
    exclude_packages: list[str] | None = Field(
        default=None,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
    )


class SparkApplicationSparkConnectApplication(APIModel):
    jar_file_uris: list[str] | None = Field(
        default=None,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
    )
    file_uris: list[str] | None = Field(
        default=None,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
    )
    archive_uris: list[str] | None = Field(
        default=None,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
    )
    properties: dict[str, str] | None = Field(
        default=None, description="Spark configuration properties."
    )
    packages: list[str] | None = Field(
        default=None, description="Maven packages added to the Spark classpaths."
    )
    repositories: list[str] | None = Field(
        default=None, description="Additional Maven repositories."
    )
    exclude_packages: list[str] | None = Field(
        default=None,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
    )


class CreateSparkApplicationArgsVariant1CatalogsItem(APIModel):
    catalog_id: str | None = Field(
        default=None, alias="catalogId", description="ID of the REST catalog."
    )


class CreateSparkApplicationArgsVariant1SparkApplication(APIModel):
    args: list[str] | None = Field(
        default=None, description="Arguments passed to the Spark driver."
    )
    jar_file_uris: list[str] | None = Field(
        default=None,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
    )
    file_uris: list[str] | None = Field(
        default=None,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
    )
    archive_uris: list[str] | None = Field(
        default=None,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
    )
    properties: dict[str, str] | None = Field(
        default=None, description="Spark configuration properties."
    )
    main_jar_file_uri: str | None = Field(
        default=None,
        alias="mainJarFileUri",
        description="URI of the JAR file that contains the main class.",
    )
    main_class: str | None = Field(
        default=None, alias="mainClass", description="Name of the driver main class."
    )
    packages: list[str] | None = Field(
        default=None, description="Maven packages added to the Spark classpaths."
    )
    repositories: list[str] | None = Field(
        default=None, description="Additional Maven repositories."
    )
    exclude_packages: list[str] | None = Field(
        default=None,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
    )


class CreateSparkApplicationArgsVariant2CatalogsItem(APIModel):
    catalog_id: str | None = Field(
        default=None, alias="catalogId", description="ID of the REST catalog."
    )


class CreateSparkApplicationArgsVariant2PysparkApplication(APIModel):
    args: list[str] | None = Field(
        default=None, description="Arguments passed to the PySpark driver."
    )
    jar_file_uris: list[str] | None = Field(
        default=None,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
    )
    file_uris: list[str] | None = Field(
        default=None,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
    )
    archive_uris: list[str] | None = Field(
        default=None,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
    )
    properties: dict[str, str] | None = Field(
        default=None, description="Spark configuration properties."
    )
    main_python_file_uri: str | None = Field(
        default=None,
        alias="mainPythonFileUri",
        description="URI of the main Python file.",
    )
    python_file_uris: list[str] | None = Field(
        default=None,
        alias="pythonFileUris",
        description="Additional Python files passed to PySpark.",
    )
    packages: list[str] | None = Field(
        default=None, description="Maven packages added to the Spark classpaths."
    )
    repositories: list[str] | None = Field(
        default=None, description="Additional Maven repositories."
    )
    exclude_packages: list[str] | None = Field(
        default=None,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
    )


class CreateSparkApplicationArgsVariant3CatalogsItem(APIModel):
    catalog_id: str | None = Field(
        default=None, alias="catalogId", description="ID of the REST catalog."
    )


class CreateSparkApplicationArgsVariant3SparkConnectApplication(APIModel):
    jar_file_uris: list[str] | None = Field(
        default=None,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
    )
    file_uris: list[str] | None = Field(
        default=None,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
    )
    archive_uris: list[str] | None = Field(
        default=None,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
    )
    properties: dict[str, str] | None = Field(
        default=None, description="Spark configuration properties."
    )
    packages: list[str] | None = Field(
        default=None, description="Maven packages added to the Spark classpaths."
    )
    repositories: list[str] | None = Field(
        default=None, description="Additional Maven repositories."
    )
    exclude_packages: list[str] | None = Field(
        default=None,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
    )


class SparkApplication(APIModel):
    id: str | None = Field(default=None, description="ID of the Spark application.")
    cluster_id: str | None = Field(
        default=None, alias="clusterId", description="ID of the Spark cluster."
    )
    created_at: SparkApplicationCreatedAt | None = Field(default=None, alias="createdAt")
    started_at: SparkApplicationStartedAt | None = Field(default=None, alias="startedAt")
    finished_at: SparkApplicationFinishedAt | None = Field(default=None, alias="finishedAt")
    name: str | None = Field(default=None, description="Name of the Spark application.")
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the Spark application.",
    )
    status: (
        Literal[
            "STATUS_UNSPECIFIED",
            "PROVISIONING",
            "PENDING",
            "RUNNING",
            "ERROR",
            "DONE",
            "CANCELLED",
            "CANCELLING",
        ]
        | str
        | None
    ) = Field(default=None, description="Current status of the Spark application.")
    connect_url: str | None = Field(
        default=None, alias="connectUrl", description="Spark Connect URL."
    )
    catalogs: list[SparkApplicationCatalogsItem] | None = Field(
        default=None, description="REST catalogs attached to the Spark application."
    )
    spark_application: SparkApplicationSparkApplication | None = Field(
        default=None, alias="sparkApplication"
    )
    application_spec: (
        Literal["sparkApplication", "pysparkApplication", "sparkConnectApplication"] | str | None
    ) = Field(default=None, alias="applicationSpec")
    pyspark_application: SparkApplicationPysparkApplication | None = Field(
        default=None, alias="pysparkApplication"
    )
    spark_connect_application: SparkApplicationSparkConnectApplication | None = Field(
        default=None, alias="sparkConnectApplication"
    )


class ListSparkApplicationsResult(APIModel):
    applications: list[SparkApplication] | None = Field(
        default=None, description="Spark applications matching the request."
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of Spark applications.",
    )


class CreateSparkApplicationArgsVariant1(APIModel):
    cluster_id: str | None = Field(
        default=None, alias="clusterId", description="ID of the Spark cluster."
    )
    name: str | None = Field(default=None, description="Name of the Spark application.")
    catalogs: list[CreateSparkApplicationArgsVariant1CatalogsItem] | None = Field(
        default=None, description="REST catalogs to attach to the Spark application."
    )
    spark_application: CreateSparkApplicationArgsVariant1SparkApplication | None = Field(
        default=None, alias="sparkApplication"
    )


class CreateSparkApplicationArgsVariant2(APIModel):
    cluster_id: str | None = Field(
        default=None, alias="clusterId", description="ID of the Spark cluster."
    )
    name: str | None = Field(default=None, description="Name of the Spark application.")
    catalogs: list[CreateSparkApplicationArgsVariant2CatalogsItem] | None = Field(
        default=None, description="REST catalogs to attach to the Spark application."
    )
    pyspark_application: CreateSparkApplicationArgsVariant2PysparkApplication | None = Field(
        default=None, alias="pysparkApplication"
    )


class CreateSparkApplicationArgsVariant3(APIModel):
    cluster_id: str | None = Field(
        default=None, alias="clusterId", description="ID of the Spark cluster."
    )
    name: str | None = Field(default=None, description="Name of the Spark application.")
    catalogs: list[CreateSparkApplicationArgsVariant3CatalogsItem] | None = Field(
        default=None, description="REST catalogs to attach to the Spark application."
    )
    spark_connect_application: CreateSparkApplicationArgsVariant3SparkConnectApplication | None = (
        Field(default=None, alias="sparkConnectApplication")
    )


class CreateSparkApplicationArgs(
    RootModel[
        CreateSparkApplicationArgsVariant1
        | CreateSparkApplicationArgsVariant2
        | CreateSparkApplicationArgsVariant3
    ]
):
    root: (
        CreateSparkApplicationArgsVariant1
        | CreateSparkApplicationArgsVariant2
        | CreateSparkApplicationArgsVariant3
    )
