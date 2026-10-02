"""FormsClient — composition root over the forms resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.yandex.core.session import SyncSession

from ycli.yandex.base import DomainClient
from ycli.yandex.forms import SERVICE
from ycli.yandex.forms.access.client import AccessClient
from ycli.yandex.forms.answers.client import AnswersClient
from ycli.yandex.forms.conditions.client import ConditionsClient
from ycli.yandex.forms.files.client import FilesClient
from ycli.yandex.forms.filling.client import FillingClient
from ycli.yandex.forms.history.client import HistoryClient
from ycli.yandex.forms.hooks.client import HooksClient
from ycli.yandex.forms.images.client import ImagesClient
from ycli.yandex.forms.keysets.client import KeysetsClient
from ycli.yandex.forms.me.client import MeClient
from ycli.yandex.forms.notifications.client import NotificationsClient
from ycli.yandex.forms.operations.client import OperationsClient
from ycli.yandex.forms.questions.client import QuestionsClient
from ycli.yandex.forms.subscriptions.client import SubscriptionsClient
from ycli.yandex.forms.surveys.client import SurveysClient
from ycli.yandex.forms.variables.client import VariablesClient


class FormsClient(DomainClient):
    """Holds the per-resource forms clients, all sharing one httpx2 core session.

    Examples:
        >>> forms.me.get().email
        'ann@example.com'
    """

    profile = SERVICE.profile

    def probe(self) -> None:
        """One cheap authenticated read: the current user."""
        self.me.get()

    def _wire(self, session: SyncSession) -> None:
        self.me = MeClient(session=session)
        self.surveys = SurveysClient(session=session)
        self.questions = QuestionsClient(session=session)
        self.conditions = ConditionsClient(session=session)
        self.access = AccessClient(session=session)
        self.history = HistoryClient(session=session)
        self.answers = AnswersClient(session=session)
        self.keysets = KeysetsClient(session=session)
        self.operations = OperationsClient(session=session)
        self.notifications = NotificationsClient(session=session)
        self.files = FilesClient(session=session)
        self.images = ImagesClient(session=session)
        self.filling = FillingClient(session=session)
        self.hooks = HooksClient(session=session)
        self.subscriptions = SubscriptionsClient(session=session)
        self.variables = VariablesClient(session=session)
