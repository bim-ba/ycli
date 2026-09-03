"""FormsClient — composition root over the forms resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

from ycli.yandex.base import DomainClient
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
    """Holds the per-resource forms clients, all sharing one authed ``requests.Session``.

    Example:
        >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
    """

    def _wire(self, transport: requests.Session) -> None:
        self.me = MeClient(session=transport)
        self.surveys = SurveysClient(session=transport)
        self.questions = QuestionsClient(session=transport)
        self.conditions = ConditionsClient(session=transport)
        self.answers = AnswersClient(session=transport)
        self.keysets = KeysetsClient(session=transport)
        self.operations = OperationsClient(session=transport)
        self.files = FilesClient(session=transport)
        self.images = ImagesClient(session=transport)
        self.filling = FillingClient(session=transport)
