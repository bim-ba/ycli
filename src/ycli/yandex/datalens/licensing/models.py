"""DataLens licensing models: the public names of the generated classes this resource uses."""

from typing import Literal

from ycli.yandex.datalens.schemas.licensing import GetLicensesResult as LicensesPage
from ycli.yandex.datalens.schemas.licensing import License, LicenseLimits
from ycli.yandex.datalens.schemas.licensing import LicenseWithLastLogin as LicenseListed

#: Which licences a listing keeps.
LicenseStatus = Literal["active", "expired", "expiring"] | str
#: What a listing of licences is sorted by.
LicenseSortField = Literal["createdAt", "updatedAt"] | str

__all__ = [
    "License",
    "LicenseLimits",
    "LicenseListed",
    "LicenseSortField",
    "LicenseStatus",
    "LicensesPage",
]
