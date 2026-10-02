"""Forms ``/surveys`` client on the httpx2 core."""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.surveys import endpoints
from ycli.yandex.forms.surveys.models import Survey, SurveyList
from ycli.yandex.models import Ack


class SurveysClient(Resource):
    """List, get, create, modify, delete, publish and unpublish forms."""

    def list(self, *, limit: int | None = None) -> SurveyList:
        """``GET /surveys`` → every form, page by page, at most ``limit`` (``None`` = all).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.list(limit=50).root[0].name  # doctest: +SKIP
            'Новая задача'
        """
        return SurveyList(list(self._session.iterate(endpoints.list_surveys(), limit=limit)))

    def get(self, survey_id: str) -> Survey:
        """``GET /surveys/{id}`` → a single ``Survey`` (settings).

        Example:
            >>> client.surveys.get("686d0a1b2c3d4e5f").is_published  # doctest: +SKIP
            True
        """
        return self._session.send(endpoints.get_survey(survey_id))

    def create(self, body: dict[str, Any]) -> Survey:
        """``POST /surveys`` — create a form from a ready body (a dumped ``SurveyCreate``).

        Example:
            >>> client.surveys.create({"name": "Onboarding"}).id  # doctest: +SKIP
            '686d0a1b2c3d4e5f00000001'
        """
        return self._session.send(endpoints.create_survey(body))

    def modify(self, survey_id: str, body: dict[str, Any]) -> Survey:
        """``PATCH /surveys/{id}`` — only the keys present in ``body`` change (a ``SurveyUpdate``).

        Example:
            >>> client.surveys.modify(
            ...     "686d0a1b2c3d4e5f", {"name": "Renamed"}
            ... ).name  # doctest: +SKIP
            'Renamed'
        """
        return self._session.send(endpoints.modify_survey(survey_id, body))

    def delete(self, survey_id: str) -> Ack:
        """``DELETE /surveys/{id}`` (``204 No Content``) → an :class:`Ack`.

        Example:
            >>> client.surveys.delete("686d0a1b2c3d4e5f").ok  # doctest: +SKIP
            True
        """
        self._session.send(endpoints.delete_survey(survey_id))
        return Ack.deleted("survey", survey_id)

    def publish(self, survey_id: str) -> Ack:
        """``POST /surveys/{id}/publish`` → an :class:`Ack`.

        Fails (typed ``YandexError``) if the form is blocked, has hit its response cap, or is
        inside an unexpired response-period window.

        Example:
            >>> client.surveys.publish("686d0a1b2c3d4e5f").detail  # doctest: +SKIP
            'published survey 686d0a1b2c3d4e5f'
        """
        self._session.send(endpoints.publish_survey(survey_id))
        return Ack.published("survey", survey_id)

    def unpublish(self, survey_id: str) -> Ack:
        """``POST /surveys/{id}/unpublish`` → an :class:`Ack` (auto-publication forms included).

        Example:
            >>> client.surveys.unpublish("686d0a1b2c3d4e5f").detail  # doctest: +SKIP
            'unpublished survey 686d0a1b2c3d4e5f'
        """
        self._session.send(endpoints.unpublish_survey(survey_id))
        return Ack.unpublished("survey", survey_id)
