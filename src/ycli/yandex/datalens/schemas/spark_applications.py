# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class CreatedAt(APIModel):
    """Time when the Spark application was created."""

    seconds: str = Field(..., description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class StartedAt(APIModel):
    """Time when the Spark application was started."""

    seconds: str = Field(..., description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class FinishedAt(APIModel):
    """Time when the Spark application was finished."""

    seconds: str = Field(..., description="Number of seconds since the Unix epoch.")
    nanos: float | None = Field(default=None, description="Fractional seconds in nanoseconds.")


class Catalog(APIModel):
    catalog_id: str = Field(
        ...,
        alias="catalogId",
        description="ID of the REST catalog.",
        max_length=50,
        min_length=1,
    )


class Arg(RootModel[str]):
    root: str = Field(..., max_length=2047)


class JarFileUri(RootModel[str]):
    root: str = Field(..., max_length=2047)


class FileUri(RootModel[str]):
    root: str = Field(..., max_length=2047)


class ArchiveUri(RootModel[str]):
    root: str = Field(..., max_length=2047)


class Properties(RootModel[str]):
    root: str = Field(..., max_length=256)


class Package(RootModel[str]):
    root: str = Field(..., max_length=255)


class Repository(RootModel[str]):
    root: str = Field(..., max_length=2047)


class ExcludePackage(RootModel[str]):
    root: str = Field(..., max_length=255)


class SparkApplication(APIModel):
    args: list[Arg] = Field(
        ..., description="Arguments passed to the Spark driver.", max_length=100
    )
    jar_file_uris: list[JarFileUri] = Field(
        ...,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
        max_length=100,
    )
    file_uris: list[FileUri] = Field(
        ...,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
        max_length=100,
    )
    archive_uris: list[ArchiveUri] = Field(
        ...,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
        max_length=100,
    )
    properties: dict[str, Properties] = Field(..., description="Spark configuration properties.")
    main_jar_file_uri: str = Field(
        ...,
        alias="mainJarFileUri",
        description="URI of the JAR file that contains the main class.",
        max_length=2047,
        min_length=1,
    )
    main_class: str = Field(
        ...,
        alias="mainClass",
        description="Name of the driver main class.",
        max_length=255,
    )
    packages: list[Package] = Field(
        ..., description="Maven packages added to the Spark classpaths.", max_length=100
    )
    repositories: list[Repository] = Field(
        ..., description="Additional Maven repositories.", max_length=10
    )
    exclude_packages: list[ExcludePackage] = Field(
        ...,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
        max_length=100,
    )


class SparkApplicationModel(APIModel):
    id: str = Field(..., description="ID of the Spark application.", max_length=50, min_length=1)
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    created_at: CreatedAt = Field(
        ...,
        alias="createdAt",
        description="Time when the Spark application was created.",
    )
    started_at: StartedAt | None = Field(
        ...,
        alias="startedAt",
        description="Time when the Spark application was started.",
    )
    finished_at: FinishedAt | None = Field(
        ...,
        alias="finishedAt",
        description="Time when the Spark application was finished.",
    )
    name: str = Field(..., description="Name of the Spark application.")
    created_by: str = Field(
        ...,
        alias="createdBy",
        description="ID of the user who created the Spark application.",
        min_length=1,
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
    ) = Field(..., description="Current status of the Spark application.")
    connect_url: str = Field(..., alias="connectUrl", description="Spark Connect URL.")
    catalogs: list[Catalog] = Field(
        ..., description="REST catalogs attached to the Spark application."
    )
    spark_application: SparkApplication = Field(..., alias="sparkApplication")
    application_spec: Literal["sparkApplication"] = Field(..., alias="applicationSpec")


class PythonFileUri(RootModel[str]):
    root: str = Field(..., max_length=2047)


class PysparkApplication(APIModel):
    args: list[Arg] = Field(
        ..., description="Arguments passed to the PySpark driver.", max_length=100
    )
    jar_file_uris: list[JarFileUri] = Field(
        ...,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
        max_length=100,
    )
    file_uris: list[FileUri] = Field(
        ...,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
        max_length=100,
    )
    archive_uris: list[ArchiveUri] = Field(
        ...,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
        max_length=100,
    )
    properties: dict[str, Properties] = Field(..., description="Spark configuration properties.")
    main_python_file_uri: str = Field(
        ...,
        alias="mainPythonFileUri",
        description="URI of the main Python file.",
        max_length=2047,
        min_length=1,
    )
    python_file_uris: list[PythonFileUri] = Field(
        ...,
        alias="pythonFileUris",
        description="Additional Python files passed to PySpark.",
        max_length=100,
    )
    packages: list[Package] = Field(
        ..., description="Maven packages added to the Spark classpaths.", max_length=100
    )
    repositories: list[Repository] = Field(
        ..., description="Additional Maven repositories.", max_length=10
    )
    exclude_packages: list[ExcludePackage] = Field(
        ...,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
        max_length=100,
    )


class SparkApplicationModel1(APIModel):
    id: str = Field(..., description="ID of the Spark application.", max_length=50, min_length=1)
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    created_at: CreatedAt = Field(
        ...,
        alias="createdAt",
        description="Time when the Spark application was created.",
    )
    started_at: StartedAt | None = Field(
        ...,
        alias="startedAt",
        description="Time when the Spark application was started.",
    )
    finished_at: FinishedAt | None = Field(
        ...,
        alias="finishedAt",
        description="Time when the Spark application was finished.",
    )
    name: str = Field(..., description="Name of the Spark application.")
    created_by: str = Field(
        ...,
        alias="createdBy",
        description="ID of the user who created the Spark application.",
        min_length=1,
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
    ) = Field(..., description="Current status of the Spark application.")
    connect_url: str = Field(..., alias="connectUrl", description="Spark Connect URL.")
    catalogs: list[Catalog] = Field(
        ..., description="REST catalogs attached to the Spark application."
    )
    pyspark_application: PysparkApplication = Field(..., alias="pysparkApplication")
    application_spec: Literal["pysparkApplication"] = Field(..., alias="applicationSpec")


class SparkConnectApplication(APIModel):
    jar_file_uris: list[JarFileUri] = Field(
        ...,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
        max_length=100,
    )
    file_uris: list[FileUri] = Field(
        ...,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
        max_length=100,
    )
    archive_uris: list[ArchiveUri] = Field(
        ...,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
        max_length=100,
    )
    properties: dict[str, Properties] = Field(..., description="Spark configuration properties.")
    packages: list[Package] = Field(
        ..., description="Maven packages added to the Spark classpaths.", max_length=100
    )
    repositories: list[Repository] = Field(
        ..., description="Additional Maven repositories.", max_length=10
    )
    exclude_packages: list[ExcludePackage] = Field(
        ...,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
        max_length=100,
    )


class SparkApplicationModel2(APIModel):
    id: str = Field(..., description="ID of the Spark application.", max_length=50, min_length=1)
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    created_at: CreatedAt = Field(
        ...,
        alias="createdAt",
        description="Time when the Spark application was created.",
    )
    started_at: StartedAt | None = Field(
        ...,
        alias="startedAt",
        description="Time when the Spark application was started.",
    )
    finished_at: FinishedAt | None = Field(
        ...,
        alias="finishedAt",
        description="Time when the Spark application was finished.",
    )
    name: str = Field(..., description="Name of the Spark application.")
    created_by: str = Field(
        ...,
        alias="createdBy",
        description="ID of the user who created the Spark application.",
        min_length=1,
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
    ) = Field(..., description="Current status of the Spark application.")
    connect_url: str = Field(..., alias="connectUrl", description="Spark Connect URL.")
    catalogs: list[Catalog] = Field(
        ..., description="REST catalogs attached to the Spark application."
    )
    spark_connect_application: SparkConnectApplication = Field(..., alias="sparkConnectApplication")
    application_spec: Literal["sparkConnectApplication"] = Field(..., alias="applicationSpec")


class SparkApplicationModel3(APIModel):
    id: str = Field(..., description="ID of the Spark application.", max_length=50, min_length=1)
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    created_at: CreatedAt = Field(
        ...,
        alias="createdAt",
        description="Time when the Spark application was created.",
    )
    started_at: StartedAt | None = Field(
        ...,
        alias="startedAt",
        description="Time when the Spark application was started.",
    )
    finished_at: FinishedAt | None = Field(
        ...,
        alias="finishedAt",
        description="Time when the Spark application was finished.",
    )
    name: str = Field(..., description="Name of the Spark application.")
    created_by: str = Field(
        ...,
        alias="createdBy",
        description="ID of the user who created the Spark application.",
        min_length=1,
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
    ) = Field(..., description="Current status of the Spark application.")
    connect_url: str = Field(..., alias="connectUrl", description="Spark Connect URL.")
    catalogs: list[Catalog] = Field(
        ..., description="REST catalogs attached to the Spark application."
    )


class SparkApplicationModel4(
    RootModel[
        SparkApplicationModel
        | SparkApplicationModel1
        | SparkApplicationModel2
        | SparkApplicationModel3
    ]
):
    root: (
        SparkApplicationModel
        | SparkApplicationModel1
        | SparkApplicationModel2
        | SparkApplicationModel3
    )


class ListSparkApplicationsResult(APIModel):
    applications: list[SparkApplicationModel4] = Field(
        ..., description="Spark applications matching the request."
    )
    next_page_token: str = Field(
        ...,
        alias="nextPageToken",
        description="Token for the next page of Spark applications.",
        max_length=200,
    )


class FilterItem(RootModel[str]):
    root: str = Field(
        ...,
        max_length=200,
        pattern='^(?:name|created_by|application_type|catalog_id)="[^"]*"$',
    )


class ListSparkApplicationsArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of Spark applications to return. The default is 100.",
        ge=0,
        le=1000,
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of Spark applications.",
        max_length=200,
    )
    filter: list[FilterItem] | None = Field(
        default=None,
        description='Filter conditions applied to the Spark application list, combined with AND. Each condition has the form `field="value"`, where field is one of `name`, `created_by`, `application_type` or `catalog_id`.',
        max_length=100,
    )


class GetSparkApplicationArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    application_id: str = Field(
        ...,
        alias="applicationId",
        description="ID of the Spark application to return.",
        max_length=50,
        min_length=1,
    )


class SparkApplicationModel5(APIModel):
    args: list[Arg] | None = Field(
        default=None,
        description="Arguments passed to the Spark driver.",
        max_length=100,
    )
    jar_file_uris: list[JarFileUri] | None = Field(
        default=None,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
        max_length=100,
    )
    file_uris: list[FileUri] | None = Field(
        default=None,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
        max_length=100,
    )
    archive_uris: list[ArchiveUri] | None = Field(
        default=None,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
        max_length=100,
    )
    properties: dict[str, Properties] | None = Field(
        default=None, description="Spark configuration properties."
    )
    main_jar_file_uri: str = Field(
        ...,
        alias="mainJarFileUri",
        description="URI of the JAR file that contains the main class.",
        max_length=2047,
        min_length=1,
    )
    main_class: str | None = Field(
        default=None,
        alias="mainClass",
        description="Name of the driver main class.",
        max_length=255,
    )
    packages: list[Package] | None = Field(
        default=None,
        description="Maven packages added to the Spark classpaths.",
        max_length=100,
    )
    repositories: list[Repository] | None = Field(
        default=None, description="Additional Maven repositories.", max_length=10
    )
    exclude_packages: list[ExcludePackage] | None = Field(
        default=None,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
        max_length=100,
    )


class CreateSparkApplicationArgs(APIModel):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    name: str | None = Field(
        default=None,
        description="Name of the Spark application.",
        max_length=255,
        pattern="^(?:|[a-z][-a-z0-9]{1,61}[a-z0-9])$",
    )
    catalogs: list[Catalog] | None = Field(
        default=None, description="REST catalogs to attach to the Spark application."
    )
    spark_application: SparkApplicationModel5 = Field(..., alias="sparkApplication")


class PysparkApplicationModel(APIModel):
    args: list[Arg] | None = Field(
        default=None,
        description="Arguments passed to the PySpark driver.",
        max_length=100,
    )
    jar_file_uris: list[JarFileUri] | None = Field(
        default=None,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
        max_length=100,
    )
    file_uris: list[FileUri] | None = Field(
        default=None,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
        max_length=100,
    )
    archive_uris: list[ArchiveUri] | None = Field(
        default=None,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
        max_length=100,
    )
    properties: dict[str, Properties] | None = Field(
        default=None, description="Spark configuration properties."
    )
    main_python_file_uri: str = Field(
        ...,
        alias="mainPythonFileUri",
        description="URI of the main Python file.",
        max_length=2047,
        min_length=1,
    )
    python_file_uris: list[PythonFileUri] | None = Field(
        default=None,
        alias="pythonFileUris",
        description="Additional Python files passed to PySpark.",
        max_length=100,
    )
    packages: list[Package] | None = Field(
        default=None,
        description="Maven packages added to the Spark classpaths.",
        max_length=100,
    )
    repositories: list[Repository] | None = Field(
        default=None, description="Additional Maven repositories.", max_length=10
    )
    exclude_packages: list[ExcludePackage] | None = Field(
        default=None,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
        max_length=100,
    )


class CreateSparkApplicationArgsModel(APIModel):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    name: str | None = Field(
        default=None,
        description="Name of the Spark application.",
        max_length=255,
        pattern="^(?:|[a-z][-a-z0-9]{1,61}[a-z0-9])$",
    )
    catalogs: list[Catalog] | None = Field(
        default=None, description="REST catalogs to attach to the Spark application."
    )
    pyspark_application: PysparkApplicationModel = Field(..., alias="pysparkApplication")


class SparkConnectApplicationModel(APIModel):
    jar_file_uris: list[JarFileUri] | None = Field(
        default=None,
        alias="jarFileUris",
        description="JAR files added to the Spark classpaths.",
        max_length=100,
    )
    file_uris: list[FileUri] | None = Field(
        default=None,
        alias="fileUris",
        description="Files copied to the Spark working directory.",
        max_length=100,
    )
    archive_uris: list[ArchiveUri] | None = Field(
        default=None,
        alias="archiveUris",
        description="Archives extracted in the Spark working directory.",
        max_length=100,
    )
    properties: dict[str, Properties] | None = Field(
        default=None, description="Spark configuration properties."
    )
    packages: list[Package] | None = Field(
        default=None,
        description="Maven packages added to the Spark classpaths.",
        max_length=100,
    )
    repositories: list[Repository] | None = Field(
        default=None, description="Additional Maven repositories.", max_length=10
    )
    exclude_packages: list[ExcludePackage] | None = Field(
        default=None,
        alias="excludePackages",
        description="Maven packages excluded during dependency resolution.",
        max_length=100,
    )


class CreateSparkApplicationArgsModel1(APIModel):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    name: str | None = Field(
        default=None,
        description="Name of the Spark application.",
        max_length=255,
        pattern="^(?:|[a-z][-a-z0-9]{1,61}[a-z0-9])$",
    )
    catalogs: list[Catalog] | None = Field(
        default=None, description="REST catalogs to attach to the Spark application."
    )
    spark_connect_application: SparkConnectApplicationModel = Field(
        ..., alias="sparkConnectApplication"
    )


class CreateSparkApplicationArgsModel2(
    RootModel[
        CreateSparkApplicationArgs
        | CreateSparkApplicationArgsModel
        | CreateSparkApplicationArgsModel1
    ]
):
    root: (
        CreateSparkApplicationArgs
        | CreateSparkApplicationArgsModel
        | CreateSparkApplicationArgsModel1
    )


class CancelSparkApplicationArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    application_id: str = Field(
        ...,
        alias="applicationId",
        description="ID of the Spark application to cancel.",
        max_length=50,
        min_length=1,
    )


class ListSparkApplicationLogResult(APIModel):
    content: str = Field(..., description="Requested fragment of the Spark application log.")
    next_page_token: str = Field(
        ...,
        alias="nextPageToken",
        description="Token for the next fragment of the Spark application log.",
        max_length=200,
    )


class ListSparkApplicationLogArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster.",
        max_length=50,
        min_length=1,
    )
    application_id: str = Field(
        ...,
        alias="applicationId",
        description="ID of the Spark application.",
        max_length=50,
        min_length=1,
    )
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum length of the returned log fragment.",
        ge=0,
        le=1048576,
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next fragment of the Spark application log.",
        max_length=200,
    )
