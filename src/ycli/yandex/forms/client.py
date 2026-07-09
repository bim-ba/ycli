"""FormsClient — composition root over the forms resource clients (one shared session)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests

from ycli.yandex.forms.answers.client import AnswersClient
from ycli.yandex.forms.keysets.client import KeysetsClient
from ycli.yandex.forms.me.client import MeClient
from ycli.yandex.forms.questions.client import QuestionsClient
from ycli.yandex.forms.surveys.client import SurveysClient
from ycli.yandex.transport import Transport


class FormsClient:
    """Holds the per-resource forms clients, all sharing one authed ``requests.Session``.

    Example:
        >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
    """

    def __init__(
        self,
        *,
        oauth_token: str,
        organization_id: str,
        timeout_seconds: int = 30,
        retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        transport = Transport.session(
            oauth_token=oauth_token,
            organization_id=organization_id,
            timeout_seconds=timeout_seconds,
            retries=retries,
            base=session,
        )
        self.me = MeClient(session=transport)
        self.surveys = SurveysClient(session=transport)
        self.questions = QuestionsClient(session=transport)
        self.answers = AnswersClient(session=transport)
        self.keysets = KeysetsClient(session=transport)
