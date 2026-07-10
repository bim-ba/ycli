"""Declarative Forms form-filling client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.

Three endpoints hang off ``/surveys/{survey}``: a read **get** (fillable-form settings) that also
reaches MCP, a write **submit** (post a response), and a **suggest** read whose verb is not an MCP
read verb (so it ships SDK + CLI only).
"""

import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.filling.models import FillableForm, SubmitBody, SubmitResult, SuggestionList


class FillingClient(FormsResource):
    """Declarative HTTP for the form-filling endpoints (get-settings / submit / suggest)."""

    @uplink.returns.json()
    @uplink.get("surveys/{survey}/form")
    def get(
        self,
        survey: uplink.Path,
        key: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> FillableForm:  # ty: ignore[empty-body]
        """``GET /surveys/{survey}/form`` → the :class:`FillableForm` settings for filling.

        ``survey`` is the form id, its slug, or an id+verification-key combination; ``key`` is the
        personal-link fill key when the form uses one. The request also checks that the form is
        published and otherwise fillable.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filling.get("686d0a1b2c3d4e5f00000001").name  # doctest: +SKIP
            'Feedback'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys/{survey}/form")
    def _submit(
        self,
        survey: uplink.Path,
        body: uplink.Body,
        dry_run: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        key: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> SubmitResult:  # ty: ignore[empty-body]
        """Raw ``POST …/form`` from a ready answer map; internal — callers use :meth:`submit`."""

    def submit(
        self,
        survey: str,
        body: SubmitBody,
        *,
        dry_run: bool = False,
        key: str | None = None,
    ) -> SubmitResult:
        """``POST /surveys/{survey}/form`` — submit a form response → :class:`SubmitResult`.

        ``body`` is a typed :class:`~ycli.yandex.forms.filling.models.SubmitBody` mapping each
        question ``slug`` to its answer (build the slug list from :meth:`get`). ``dry_run=True``
        runs every validation but saves nothing and fires no integrations; ``key`` is the
        personal-link fill key when the form uses one.

        Example:
            >>> from ycli.yandex.forms.filling.models import SubmitBody
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filling.submit(
            ...     "686d0a1b", SubmitBody.model_validate({"answer_short_text_1": "Ann"})
            ... ).answer_id  # doctest: +SKIP
            99
        """
        return self._submit(
            survey,
            body.model_dump(),
            dry_run="true" if dry_run else None,
            key=key or None,
        )

    @uplink.returns.json()
    @uplink.get("surveys/{survey}/suggest")
    def _suggest(
        self,
        survey: uplink.Path,
        question: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        text: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        suggest_id: uplink.Query("id") = None,  # ty: ignore[invalid-type-form]
        parent_id: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> SuggestionList:  # ty: ignore[empty-body]
        """Raw ``GET …/suggest``; internal — callers use :meth:`suggest`."""

    def suggest(
        self,
        survey: str,
        *,
        question: str | None = None,
        text: str | None = None,
        suggest_id: str | None = None,
        parent_id: str | None = None,
    ) -> SuggestionList:
        """``GET /surveys/{survey}/suggest`` → :class:`SuggestionList` prompts for a fill field.

        ``question`` is the question slug; ``text`` is the search text; ``suggest_id`` (the API's
        ``id``) is a comma-separated list of suggestion-object ids to resolve; ``parent_id`` scopes
        a Master/Detail lookup. This is read-only, but ``suggest`` is not an MCP read verb, so it
        ships SDK + CLI only.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filling.suggest("686d0a1b", question="city_1", text="Ber").root[
            ...     0
            ... ].text  # doctest: +SKIP
            'Berlin'
        """
        return self._suggest(
            survey,
            question=question or None,
            text=text or None,
            suggest_id=suggest_id or None,
            parent_id=parent_id or None,
        )
