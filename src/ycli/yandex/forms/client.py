"""FormsClient — composition root over the forms resource clients (one shared session)."""
from __future__ import annotations

import requests

from ycli.yandex.base import session_from_env
from ycli.yandex.forms.answers.client import AnswersClient
from ycli.yandex.forms.me.client import MeClient
from ycli.yandex.forms.questions.client import QuestionsClient
from ycli.yandex.forms.surveys.client import SurveysClient


class FormsClient:
    """Holds the per-resource forms clients, all sharing one ``requests.Session``.

    Example:
        >>> FormsClient.from_env().me.get()  # doctest: +SKIP
    """

    def __init__(self, *, session: requests.Session) -> None:
        self.me = MeClient(session=session)
        self.surveys = SurveysClient(session=session)
        self.questions = QuestionsClient(session=session)
        self.answers = AnswersClient(session=session)

    @classmethod
    def from_env(cls) -> FormsClient:
        """Build all sub-clients from one env-resolved session."""
        return cls(session=session_from_env())
