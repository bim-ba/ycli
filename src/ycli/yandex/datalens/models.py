"""DataLens models several resources share: the public names of the generated classes."""

from typing import Literal

from ycli.yandex.datalens.schemas.shared import DatalensOperation as Operation
from ycli.yandex.datalens.schemas.shared import ListAccessBindingsResult as AccessBindingsPage
from ycli.yandex.datalens.schemas.shared import SubjectWithBindings
from ycli.yandex.datalens.schemas.shared import USAccessBindingDelta as AccessBindingDelta

#: What a listing of collections or workbooks is sorted by.
OrderField = Literal["title", "createdAt", "updatedAt"] | str

__all__ = [
    "AccessBindingDelta",
    "AccessBindingsPage",
    "Operation",
    "OrderField",
    "SubjectWithBindings",
]
