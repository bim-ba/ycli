"""DataLens member models: the public names of the generated classes this resource uses."""

from typing import Literal

from ycli.yandex.datalens.models import Language as MemberLanguage
from ycli.yandex.datalens.schemas.access import AccessExtBatchListMembersResult as MembersPage
from ycli.yandex.datalens.schemas.access import AccessExtSubjectClaims as Member

#: Which kind of subject a listing of members keeps.
MemberKind = (
    Literal[
        "SUBJECT_TYPE_UNSPECIFIED",
        "USER_ACCOUNT",
        "GROUP",
        "INVITEE",
        "SERVICE_ACCOUNT",
        "_system",
    ]
    | str
)

__all__ = ["Member", "MemberKind", "MemberLanguage", "MembersPage"]
