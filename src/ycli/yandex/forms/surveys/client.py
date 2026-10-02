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

        Args:
            limit: The most forms to return; ``None`` returns every form.

        Returns:
            The forms.

        Examples:
            >>> forms.surveys.list(limit=500).root[0].name
            'Onboarding'
        """
        return SurveyList(list(self._session.iterate(endpoints.list_surveys(), limit=limit)))

    def get(self, survey_id: str) -> Survey:
        """``GET /surveys/{id}`` → a single ``Survey`` (settings).

        Args:
            survey_id: The form's id.

        Returns:
            The form's settings.

        Examples:
            >>> forms.surveys.get("686d0a1b2c3d4e5f00000001").name
            'Onboarding'
        """
        return self._session.send(endpoints.get_survey(survey_id))

    def create(self, body: dict[str, Any]) -> Survey:
        """``POST /surveys`` — create a form from a ready body (a dumped ``SurveyCreate``).

        Args:
            body: The dumped ``SurveyCreate``.

        Returns:
            The created form, with its ``id``.

        Examples:
            >>> forms.surveys.create({"name": "Onboarding", "language": "en"}).id
            '686d0a1b2c3d4e5f00000001'
        """
        return self._session.send(endpoints.create_survey(body))

    def modify(self, survey_id: str, body: dict[str, Any]) -> Survey:
        """``PATCH /surveys/{id}`` — only the keys present in ``body`` change (a ``SurveyUpdate``).

        Args:
            survey_id: The form's id.
            body: The keys to change.

        Returns:
            The updated form.

        Examples:
            >>> forms.surveys.modify("686d0a1b2c3d4e5f00000002", {"name": "Onboarding"}).name
            'Onboarding'
        """
        return self._session.send(endpoints.modify_survey(survey_id, body))

    def delete(self, survey_id: str) -> Ack:
        """``DELETE /surveys/{id}`` (``204 No Content``) → an :class:`Ack`.

        Args:
            survey_id: The form's id.

        Returns:
            An acknowledgement naming the deleted form.

        Examples:
            >>> forms.surveys.delete("686d0a1b2c3d4e5f00000003").ok
            True
        """
        self._session.send(endpoints.delete_survey(survey_id))
        return Ack.deleted("survey", survey_id)

    def publish(self, survey_id: str) -> Ack:
        """``POST /surveys/{id}/publish`` → an :class:`Ack`.

        Fails (typed ``YandexError``) if the form is blocked, has hit its response cap, or is
        inside an unexpired response-period window.

        Args:
            survey_id: The form's id.

        Returns:
            An acknowledgement naming the published form.

        Examples:
            >>> forms.surveys.publish("686d0a1b2c3d4e5f00000004").detail
            'published survey 686d0a1b2c3d4e5f00000004'
        """
        self._session.send(endpoints.publish_survey(survey_id))
        return Ack.published("survey", survey_id)

    def unpublish(self, survey_id: str) -> Ack:
        """``POST /surveys/{id}/unpublish`` → an :class:`Ack` (auto-publication forms included).

        Args:
            survey_id: The form's id.

        Returns:
            An acknowledgement naming the unpublished form.

        Examples:
            >>> forms.surveys.unpublish("686d0a1b2c3d4e5f00000005").detail
            'unpublished survey 686d0a1b2c3d4e5f00000005'
        """
        self._session.send(endpoints.unpublish_survey(survey_id))
        return Ack.unpublished("survey", survey_id)
