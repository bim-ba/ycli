"""Forms ``/surveys`` client on the httpx2 core."""

from __future__ import annotations

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.surveys import endpoints
from ycli.yandex.forms.surveys.models import Survey, SurveyCreate, SurveyUpdate
from ycli.yandex.models import Ack, ItemList


class SurveysClient(Resource):
    """List, get, create, update, delete, publish and unpublish forms."""

    def list(
        self,
        *,
        limit: int | None = None,
        name: str | None = None,
        published: bool | None = None,
        ownership: str | None = None,
        group: str | None = None,
        favourite: bool | None = None,
        show_all: bool = False,
        orderby: str | None = None,
    ) -> ItemList[Survey]:
        """``GET /surveys`` → every form, page by page, at most ``limit`` (``None`` = all).

        Args:
            limit: The most forms to return; ``None`` returns every form.
            name: Keep the forms whose name matches.
            published: Keep only published (``True``) or only unpublished (``False``) forms.
            ownership: ``mine`` (created by the caller) or ``shared`` (open to the caller).
            group: Keep the forms of this group.
            favourite: Keep only favourite (``True``) or only other (``False``) forms.
            show_all: For an administrator, list every form of the organization.
            orderby: The sort, a comma list such as ``name,-modified,-count``.

        Returns:
            The forms.

        Examples:
            >>> forms.surveys.list(limit=500).root[0].name
            'Onboarding'
        """
        paged = endpoints.list_(
            name=name,
            published=published,
            ownership=ownership,
            group=group,
            favourite=favourite,
            show_all=show_all,
            orderby=orderby,
        )
        return ItemList[Survey](list(self._session.iterate(paged, limit=limit)))

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
        return self._session.send(endpoints.get(survey_id))

    def create(self, body: SurveyCreate) -> Survey:
        """``POST /surveys`` — create a form from a ``SurveyCreate``.

        Args:
            body: The ``SurveyCreate``.

        Returns:
            The created form, with its ``id``.

        Examples:
            >>> from ycli.yandex.forms.surveys.models import SurveyCreate
            >>> forms.surveys.create(
            ...     SurveyCreate.model_validate({"name": "Onboarding", "language": "en"})
            ... ).id
            '686d0a1b2c3d4e5f00000001'
        """
        return self._session.send(endpoints.create(body))

    def update(self, survey_id: str, body: SurveyUpdate) -> Survey:
        """``PATCH /surveys/{id}`` — only the keys present in ``body`` change (a ``SurveyUpdate``).

        Args:
            survey_id: The form's id.
            body: The keys to change.

        Returns:
            The updated form.

        Examples:
            >>> from ycli.yandex.forms.surveys.models import SurveyUpdate
            >>> forms.surveys.update(
            ...     "686d0a1b2c3d4e5f00000002", SurveyUpdate.model_validate({"name": "Onboarding"})
            ... ).name
            'Onboarding'
        """
        return self._session.send(endpoints.update(survey_id, body))

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
        self._session.send(endpoints.delete(survey_id))
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
        self._session.send(endpoints.publish(survey_id))
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
        self._session.send(endpoints.unpublish(survey_id))
        return Ack.unpublished("survey", survey_id)
