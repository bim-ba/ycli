# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from typing import Annotated, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, NoDropNull, RequestBody


class CheckedFavorite(APIModel):
    entity_id: str | None = Field(default=None, alias="entityId", description="ID of the entity.")
    entity_type: Literal["entry", "workbook", "collection"] | str | None = Field(
        default=None, alias="entityType", description="Type of the entity."
    )
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Whether the current user has marked the entity as a favorite.",
    )
    display_alias: Annotated[str | None, NoDropNull()] = Field(
        default=None,
        alias="displayAlias",
        description="Custom name the user gave to the favorite, or null if there is none.",
    )


class CheckFavoritesResult(RootModel[list[CheckedFavorite]], hide_input_in_errors=True):
    """Checked entities in the order of the request. Duplicates are repeated."""

    root: list[CheckedFavorite] = Field(
        ...,
        description="Checked entities in the order of the request. Duplicates are repeated.",
    )


class FavoriteEntityRef(APIModel):
    entity_id: str | None = Field(default=None, alias="entityId", description="ID of the entity.")
    entity_type: Literal["entry", "workbook", "collection"] | str | None = Field(
        default=None, alias="entityType", description="Type of the entity."
    )


class CheckFavoritesArgs(RequestBody):
    entities: list[FavoriteEntityRef] = Field(..., description="Entities to check.")


class FavoriteMark(APIModel):
    entity_id: str | None = Field(
        default=None,
        alias="entityId",
        description="ID of the entity marked as a favorite.",
    )
    entity_type: Literal["entry", "workbook", "collection"] | str | None = Field(
        default=None,
        alias="entityType",
        description="Type of the entity marked as a favorite.",
    )
    display_alias: Annotated[str | None, NoDropNull()] = Field(
        default=None,
        alias="displayAlias",
        description="Custom name the user gave to the favorite, or null if there is none.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the entity was marked as a favorite.",
    )


class ListFavoritesResult(APIModel):
    entities: list[FavoriteMark] | None = Field(
        default=None, description="Favorite marks of the current user."
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token of the next page. Absent on the last page.",
    )


class ListFavoritesArgs(RequestBody):
    entity_types: list[Literal["entry", "workbook", "collection"] | str] | None = Field(
        default=None,
        alias="entityTypes",
        description="Entity types to return. All types are returned if the field is omitted.",
    )
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of favorites per page. Defaults to 200.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token of the page to return, taken from the previous response.",
    )
