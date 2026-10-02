"""Forms form-filling client on the httpx2 core: fillable-form settings, submit and suggest."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.filling import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.filling.models import (
        FillableForm,
        SubmitBody,
        SubmitResult,
        SuggestionList,
    )


class FillingClient(Resource):
    """Fill a form the way a respondent does."""

    def get(self, survey: str, key: str | None = None) -> FillableForm:
        """``GET /surveys/{survey}/form`` → the :class:`FillableForm` settings for filling.

        ``survey`` is the form id, its slug, or an id+verification-key combination; ``key`` is
        the personal-link fill key. The call also checks that the form is published and fillable.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filling.get("686d0a1b2c3d4e5f").name  # doctest: +SKIP
            'Feedback'
        """
        return self._session.send(endpoints.get_form(survey, key=key))

    def submit(
        self, survey: str, body: SubmitBody, *, dry_run: bool = False, key: str | None = None
    ) -> SubmitResult:
        """``POST /surveys/{survey}/form`` — submit a response → :class:`SubmitResult`.

        ``body`` maps each question ``slug`` to its answer. ``dry_run=True`` validates
        everything but saves nothing and fires no integrations.

        Example:
            >>> client.filling.submit(
            ...     "686d", SubmitBody({"name": "Ann"})
            ... ).answer_id  # doctest: +SKIP
            99
        """
        endpoint = endpoints.submit_form(
            survey, body.model_dump(), dry_run=dry_run, key=key or None
        )
        return self._session.send(endpoint)

    def suggest(
        self,
        survey: str,
        *,
        question: str | None = None,
        text: str | None = None,
        suggest_id: str | None = None,
        parent_id: str | None = None,
    ) -> SuggestionList:
        """``GET /surveys/{survey}/suggest`` → prompts for a fill field (read-only).

        ``question`` is the question slug, ``text`` the search text, ``suggest_id`` (the API's
        ``id``) a comma-separated list of suggestion ids to resolve, and ``parent_id`` scopes a
        Master/Detail lookup.

        Example:
            >>> client.filling.suggest("686d", question="city", text="Ber").root[
            ...     0
            ... ].text  # doctest: +SKIP
            'Berlin'
        """
        params = {
            "question": question or None,
            "text": text or None,
            "id": suggest_id or None,
            "parent_id": parent_id or None,
        }
        return self._session.send(endpoints.suggest(survey, params))
