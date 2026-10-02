"""FormsClient — composition root over the forms resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.yandex.core.session import SyncSession

from ycli.yandex.base import DomainClient
from ycli.yandex.forms import SERVICE
from ycli.yandex.forms.answers.client import AnswersClient
from ycli.yandex.forms.conditions.client import ConditionsClient
from ycli.yandex.forms.files.client import FilesClient
from ycli.yandex.forms.filling.client import FillingClient
from ycli.yandex.forms.images.client import ImagesClient
from ycli.yandex.forms.keysets.client import KeysetsClient
from ycli.yandex.forms.me.client import MeClient
from ycli.yandex.forms.operations.client import OperationsClient
from ycli.yandex.forms.questions.client import QuestionsClient
from ycli.yandex.forms.surveys.client import SurveysClient


class FormsClient(DomainClient):
    """Holds the per-resource forms clients, all sharing one httpx2 core session.

    Example:
        >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
    """

    profile = SERVICE.profile

    def _wire(self, session: SyncSession) -> None:
        self.me = MeClient(session=session)
        self.surveys = SurveysClient(session=session)
        self.questions = QuestionsClient(session=session)
        self.conditions = ConditionsClient(session=session)
        self.answers = AnswersClient(session=session)
        self.keysets = KeysetsClient(session=session)
        self.operations = OperationsClient(session=session)
        self.files = FilesClient(session=session)
        self.images = ImagesClient(session=session)
        self.filling = FillingClient(session=session)
