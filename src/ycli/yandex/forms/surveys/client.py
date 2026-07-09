"""Declarative Forms /surveys client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.surveys.models import (
    Survey,
    SurveyActionResult,
    SurveyList,
    SurveysResponse,
)
from ycli.yandex.pagination import OffsetStrategy

_PAGE_SIZE = 100


class SurveysClient(FormsResource):
    """Declarative HTTP for ``/surveys`` (offset-paged list envelope + single get)."""

    @uplink.returns.json()
    @uplink.get("surveys")
    def _list_page(
        self,
        offset: uplink.Query = 0,  # ty: ignore[invalid-parameter-default]
        limit: uplink.Query = _PAGE_SIZE,  # ty: ignore[invalid-parameter-default]
    ) -> SurveysResponse:  # ty: ignore[empty-body]
        """One raw page of surveys at ``offset`` (page size ``limit``); internal — use ``list``."""

    def list(self, *, limit: int | None = None) -> SurveyList:
        """``GET /surveys`` → flat :class:`SurveyList`, draining offset pages internally.

        Capped at ``limit`` (``None`` = every form). The API pages by ``offset``/``limit``; this
        advances the offset until a short page comes back.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.list(limit=50).root[0].name  # doctest: +SKIP
            'Новая задача'
        """
        strategy = OffsetStrategy(extract=lambda page: page.result, page_size=_PAGE_SIZE)
        surveys = strategy.collect(
            lambda offset: self._list_page(offset=offset, limit=_PAGE_SIZE),
            limit,
        )
        return SurveyList(surveys)

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}")
    def get(self, survey_id: uplink.Path) -> Survey:  # ty: ignore[empty-body]
        """``GET /surveys/{id}`` → a single ``Survey`` (settings).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.get(survey_id="686d0a1b2c3d4e5f").is_published  # doctest: +SKIP
            True
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys")
    def create(self, body: uplink.Body) -> Survey:  # ty: ignore[empty-body]
        """``POST /surveys`` — create a form from a ready body. Returns the created ``Survey``.

        Method/path inferred: the vendored ``03-forms/create.md`` shows only the request Body
        (the request line was truncated); ``03-forms/index.md`` lists it as "Create form", so
        ``POST /surveys`` per REST convention. Build ``body`` from a
        :class:`~ycli.yandex.forms.surveys.models.SurveyCreate`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.create({"name": "Onboarding"}).id  # doctest: +SKIP
            '686d0a1b2c3d4e5f00000001'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("surveys/{survey_id}")
    def modify(self, survey_id: uplink.Path, body: uplink.Body) -> Survey:  # ty: ignore[empty-body]
        """``PATCH /surveys/{id}`` — patch form settings. Returns the updated ``Survey``.

        Method/path inferred: the vendored ``03-forms/modify.md`` shows only the request Body
        (the request line was truncated); ``03-forms/index.md`` lists it as "Modify form", so
        ``PATCH /surveys/{id}`` per REST convention. Only the keys present in ``body`` change —
        build it from a :class:`~ycli.yandex.forms.surveys.models.SurveyUpdate`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.modify(
            ...     "686d0a1b2c3d4e5f", {"name": "Renamed"}
            ... ).name  # doctest: +SKIP
            'Renamed'
        """

    @uplink.delete("surveys/{survey_id}")
    def _delete(self, survey_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """Raw ``DELETE /surveys/{id}`` (204 No Content); internal — callers use ``delete``."""

    def delete(self, survey_id: str) -> SurveyActionResult:
        """``DELETE /surveys/{id}`` → a typed :class:`SurveyActionResult` (``204 No Content``).

        The API returns no body, so the result is synthesized; a non-2xx status raises a
        typed ``YandexError`` before this returns.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.delete("686d0a1b2c3d4e5f").ok  # doctest: +SKIP
            True
        """
        self._delete(survey_id)
        return SurveyActionResult(survey_id=survey_id, action="delete")

    @uplink.post("surveys/{survey_id}/publish")
    def _publish(self, survey_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """Raw bodyless ``POST /surveys/{id}/publish`` (200 OK); internal — use ``publish``."""

    def publish(self, survey_id: str) -> SurveyActionResult:
        """``POST /surveys/{id}/publish`` (no body) → a typed :class:`SurveyActionResult`.

        Publishes the form. The API answers ``200 OK`` with no JSON body, so the result is
        synthesized. Fails (typed ``YandexError``) if the form is blocked, has hit its response
        cap, or is inside an unexpired response-period window.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.publish("686d0a1b2c3d4e5f").action  # doctest: +SKIP
            'publish'
        """
        self._publish(survey_id)
        return SurveyActionResult(survey_id=survey_id, action="publish")

    @uplink.post("surveys/{survey_id}/unpublish")
    def _unpublish(self, survey_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """Raw bodyless ``POST /surveys/{id}/unpublish`` (200 OK); internal — use ``unpublish``."""

    def unpublish(self, survey_id: str) -> SurveyActionResult:
        """``POST /surveys/{id}/unpublish`` (no body) → a typed :class:`SurveyActionResult`.

        Unpublishes the form (any published form, including auto-publication forms before their
        close time). The API answers ``200 OK`` with no JSON body, so the result is synthesized.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.unpublish("686d0a1b2c3d4e5f").action  # doctest: +SKIP
            'unpublish'
        """
        self._unpublish(survey_id)
        return SurveyActionResult(survey_id=survey_id, action="unpublish")
