"""DataLens models several resources share: the public names of the generated classes."""

from typing import Annotated, Literal

from pydantic import Field, RootModel

from ycli.yandex.datalens.schemas.shared import DatalensOperation as Operation
from ycli.yandex.datalens.schemas.shared import LakehouseOperation, SubjectWithBindings
from ycli.yandex.datalens.schemas.shared import ListAccessBindingsResult as AccessBindingsPage
from ycli.yandex.datalens.schemas.shared import USAccessBindingDelta as AccessBindingDelta
from ycli.yandex.models import KindByOwnField, RequestBody

#: What kind an entry is.
EntryScope = (
    Literal[
        "dash",
        "report",
        "widget",
        "dataset",
        "folder",
        "connection",
        "compute",
        "artifact",
        "sql_query",
    ]
    | str
)
#: A language DataLens answers in: of the names of members, of a preview.
Language = Literal["en", "ru"] | str
#: Which revision of an entry is meant: the one saved last, or the one everyone sees.
RevisionBranch = Literal["saved", "published"] | str
#: How a chart or a dashboard is saved: as a draft, or as the version everyone sees.
SaveMode = Literal["save", "publish"] | str
#: What a listing of collections or workbooks is sorted by.
OrderField = Literal["title", "createdAt", "updatedAt"] | str


class _ByBranch(RequestBody):
    branch: RevisionBranch = Field(description="The saved version, or the published one.")


class _ByRevision(RequestBody):
    rev_id: str = Field(description="One revision, by its id.")


class OneRevision(RootModel, hide_input_in_errors=True):
    """What a read of an entry asks for: a branch, or one revision by its id, never both.

    DataLens answers a named revision whatever the branch says (measured on a chart of the
    editor and on a dashboard), and the published one when neither is given. A read therefore
    names exactly one of the two, so that it says which version it means.

    Examples:
        >>> one_revision(branch="saved", rev_id=None)
        >>> one_revision(branch=None, rev_id=None)
        Traceback (most recent call last):
            ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for OneRevision
          give exactly one of: branch, rev_id [type=one_kind]
    """

    root: Annotated[_ByBranch | _ByRevision, KindByOwnField()]


def one_revision(*, branch: RevisionBranch | None, rev_id: str | None) -> None:
    """Refuse a read that names both a branch and a revision, or neither.

    The refusal is the ``ValidationError`` of :class:`OneRevision`.

    Args:
        branch: The branch asked for, if any.
        rev_id: The revision asked for, if any.
    """
    given = {"branch": branch, "rev_id": rev_id}
    OneRevision.model_validate({name: value for name, value in given.items() if value is not None})


__all__ = [
    "AccessBindingDelta",
    "AccessBindingsPage",
    "EntryScope",
    "LakehouseOperation",
    "Language",
    "OneRevision",
    "Operation",
    "OrderField",
    "RevisionBranch",
    "SaveMode",
    "SubjectWithBindings",
    "one_revision",
]
