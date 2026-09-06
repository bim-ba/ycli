"""Declarative Forms display-conditions client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.conditions.models import (
    Condition,
    ConditionCreate,
    ConditionOperatorType,
    ConditionsResponse,
    ConditionUpdate,
)
from ycli.yandex.models import Ack


class ConditionsClient(FormsResource):
    """Declarative HTTP for the three show-condition families (question / page / submit)."""

    # --- question family ---

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/questions/{question_id}/conditions")
    def question_list(self, survey_id: uplink.Path, question_id: uplink.Path) -> ConditionsResponse:  # ty: ignore[empty-body]
        """``GET …/questions/{id}/conditions`` → the ``{operator, items}`` envelope.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.question_list("686d0a1b", "17").operator  # doctest: +SKIP
            'and'
        """

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/questions/{question_id}/conditions/{condition_id}")
    def question_get(
        self, survey_id: uplink.Path, question_id: uplink.Path, condition_id: uplink.Path
    ) -> Condition:  # ty: ignore[empty-body]
        """``GET …/conditions/{condition_id}`` → one condition group ``{id, operator, items}``.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.question_get("686d0a1b", "17", 5).id  # doctest: +SKIP
            5
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys/{survey_id}/questions/{question_id}/conditions")
    def _question_create(
        self, survey_id: uplink.Path, question_id: uplink.Path, body: uplink.Body
    ) -> Condition:  # ty: ignore[empty-body]
        """Raw POST from a ready dict; internal — callers use ``question_create``."""

    def question_create(self, survey_id: str, question_id: str, body: ConditionCreate) -> Condition:
        """``POST …/conditions`` — create a condition group; returns it with the server ``id``.

        Example:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> body = ConditionCreate(
            ...     operator="and",
            ...     items=[ConditionItemWrite(type="question", condition="eq", question="q1")],
            ... )
            >>> client.conditions.question_create("686d0a1b", "17", body).id  # doctest: +SKIP
            5
        """
        return self._question_create(
            survey_id, question_id, body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("surveys/{survey_id}/questions/{question_id}/conditions/{condition_id}")
    def _question_modify(
        self,
        survey_id: uplink.Path,
        question_id: uplink.Path,
        condition_id: uplink.Path,
        body: uplink.Body,
    ) -> Condition:  # ty: ignore[empty-body]
        """Raw PATCH from a ready dict; internal — callers use ``question_modify``."""

    def question_modify(
        self, survey_id: str, question_id: str, condition_id: int, body: ConditionUpdate
    ) -> Condition:
        """``PATCH …/conditions/{condition_id}`` — REPLACE the group (no partial update).

        Example:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> body = ConditionUpdate(
            ...     operator="or",
            ...     items=[ConditionItemWrite(type="language", condition="eq", value="ru")],
            ... )
            >>> client.conditions.question_modify("686d0a1b", "17", 5, body)  # doctest: +SKIP
        """
        return self._question_modify(
            survey_id,
            question_id,
            condition_id,
            body.model_dump(by_alias=True, exclude_none=True),
        )

    @uplink.delete("surveys/{survey_id}/questions/{question_id}/conditions/{condition_id}")
    def _question_delete(
        self, survey_id: uplink.Path, question_id: uplink.Path, condition_id: uplink.Path
    ) -> requests.Response:  # ty: ignore[empty-body]
        """Raw DELETE (200 OK, no body); internal — callers use ``question_delete``."""

    def question_delete(self, survey_id: str, question_id: str, condition_id: int) -> Ack:
        """``DELETE …/conditions/{condition_id}`` → :class:`Ack` (the API answers 200, no body).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.question_delete("686d0a1b", "17", 5).ok  # doctest: +SKIP
            True
        """
        self._question_delete(survey_id, question_id, condition_id)
        return Ack.deleted("condition", condition_id, from_=f"question {question_id}")

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("surveys/{survey_id}/questions/{question_id}/conditions")
    def _question_set_operator(
        self, survey_id: uplink.Path, question_id: uplink.Path, body: uplink.Body
    ) -> ConditionsResponse:  # ty: ignore[empty-body]
        """Raw collection-PATCH; internal — callers use ``question_set_operator``."""

    def question_set_operator(
        self, survey_id: str, question_id: str, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH …/conditions`` — set the operator BETWEEN groups → the full envelope.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.question_set_operator("686d", "17", "or")  # doctest: +SKIP
        """
        return self._question_set_operator(survey_id, question_id, {"operator": operator})

    # --- page family ---

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/pages/{page_id}/conditions")
    def page_list(self, survey_id: uplink.Path, page_id: uplink.Path) -> ConditionsResponse:  # ty: ignore[empty-body]
        """``GET …/pages/{id}/conditions`` → the ``{operator, items}`` envelope.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.page_list("686d0a1b", 3).operator  # doctest: +SKIP
            'and'
        """

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/pages/{page_id}/conditions/{condition_id}")
    def page_get(
        self, survey_id: uplink.Path, page_id: uplink.Path, condition_id: uplink.Path
    ) -> Condition:  # ty: ignore[empty-body]
        """``GET …/conditions/{condition_id}`` → one condition group ``{id, operator, items}``.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.page_get("686d0a1b", 3, 5).id  # doctest: +SKIP
            5
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys/{survey_id}/pages/{page_id}/conditions")
    def _page_create(
        self, survey_id: uplink.Path, page_id: uplink.Path, body: uplink.Body
    ) -> Condition:  # ty: ignore[empty-body]
        """Raw POST from a ready dict; internal — callers use ``page_create``."""

    def page_create(self, survey_id: str, page_id: int, body: ConditionCreate) -> Condition:
        """``POST …/conditions`` — create a condition group; returns it with the server ``id``.

        Example:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> body = ConditionCreate(
            ...     operator="and",
            ...     items=[ConditionItemWrite(type="question", condition="eq", question="q1")],
            ... )
            >>> client.conditions.page_create("686d0a1b", 3, body).id  # doctest: +SKIP
            5
        """
        return self._page_create(
            survey_id, page_id, body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("surveys/{survey_id}/pages/{page_id}/conditions/{condition_id}")
    def _page_modify(
        self,
        survey_id: uplink.Path,
        page_id: uplink.Path,
        condition_id: uplink.Path,
        body: uplink.Body,
    ) -> Condition:  # ty: ignore[empty-body]
        """Raw PATCH from a ready dict; internal — callers use ``page_modify``."""

    def page_modify(
        self, survey_id: str, page_id: int, condition_id: int, body: ConditionUpdate
    ) -> Condition:
        """``PATCH …/conditions/{condition_id}`` — REPLACE the group (no partial update).

        Example:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> body = ConditionUpdate(
            ...     operator="or",
            ...     items=[ConditionItemWrite(type="language", condition="eq", value="ru")],
            ... )
            >>> client.conditions.page_modify("686d0a1b", 3, 5, body)  # doctest: +SKIP
        """
        return self._page_modify(
            survey_id, page_id, condition_id, body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.delete("surveys/{survey_id}/pages/{page_id}/conditions/{condition_id}")
    def _page_delete(
        self, survey_id: uplink.Path, page_id: uplink.Path, condition_id: uplink.Path
    ) -> requests.Response:  # ty: ignore[empty-body]
        """Raw DELETE (200 OK, no body); internal — callers use ``page_delete``."""

    def page_delete(self, survey_id: str, page_id: int, condition_id: int) -> Ack:
        """``DELETE …/conditions/{condition_id}`` → :class:`Ack` (the API answers 200, no body).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.page_delete("686d0a1b", 3, 5).ok  # doctest: +SKIP
            True
        """
        self._page_delete(survey_id, page_id, condition_id)
        return Ack.deleted("condition", condition_id, from_=f"page {page_id}")

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("surveys/{survey_id}/pages/{page_id}/conditions")
    def _page_set_operator(
        self, survey_id: uplink.Path, page_id: uplink.Path, body: uplink.Body
    ) -> ConditionsResponse:  # ty: ignore[empty-body]
        """Raw collection-PATCH; internal — callers use ``page_set_operator``."""

    def page_set_operator(
        self, survey_id: str, page_id: int, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH …/conditions`` — set the operator BETWEEN groups → the full envelope.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.page_set_operator("686d", 3, "or")  # doctest: +SKIP
        """
        return self._page_set_operator(survey_id, page_id, {"operator": operator})

    # --- submit family (conditions of the form's Submit button, right on the survey) ---

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/conditions")
    def submit_list(self, survey_id: uplink.Path) -> ConditionsResponse:  # ty: ignore[empty-body]
        """``GET /surveys/{id}/conditions`` → the ``{operator, items}`` envelope.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.submit_list("686d0a1b").operator  # doctest: +SKIP
            'and'
        """

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/conditions/{condition_id}")
    def submit_get(self, survey_id: uplink.Path, condition_id: uplink.Path) -> Condition:  # ty: ignore[empty-body]
        """``GET …/conditions/{condition_id}`` → one condition group ``{id, operator, items}``.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.submit_get("686d0a1b", 5).id  # doctest: +SKIP
            5
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys/{survey_id}/conditions")
    def _submit_create(self, survey_id: uplink.Path, body: uplink.Body) -> Condition:  # ty: ignore[empty-body]
        """Raw POST from a ready dict; internal — callers use ``submit_create``."""

    def submit_create(self, survey_id: str, body: ConditionCreate) -> Condition:
        """``POST …/conditions`` — create a condition group; returns it with the server ``id``.

        Example:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> body = ConditionCreate(
            ...     operator="and",
            ...     items=[ConditionItemWrite(type="question", condition="eq", question="q1")],
            ... )
            >>> client.conditions.submit_create("686d0a1b", body).id  # doctest: +SKIP
            5
        """
        return self._submit_create(survey_id, body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("surveys/{survey_id}/conditions/{condition_id}")
    def _submit_modify(
        self, survey_id: uplink.Path, condition_id: uplink.Path, body: uplink.Body
    ) -> Condition:  # ty: ignore[empty-body]
        """Raw PATCH from a ready dict; internal — callers use ``submit_modify``."""

    def submit_modify(self, survey_id: str, condition_id: int, body: ConditionUpdate) -> Condition:
        """``PATCH …/conditions/{condition_id}`` — REPLACE the group (no partial update).

        Example:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> body = ConditionUpdate(
            ...     operator="or",
            ...     items=[ConditionItemWrite(type="language", condition="eq", value="ru")],
            ... )
            >>> client.conditions.submit_modify("686d0a1b", 5, body)  # doctest: +SKIP
        """
        return self._submit_modify(
            survey_id, condition_id, body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.delete("surveys/{survey_id}/conditions/{condition_id}")
    def _submit_delete(
        self, survey_id: uplink.Path, condition_id: uplink.Path
    ) -> requests.Response:  # ty: ignore[empty-body]
        """Raw DELETE (200 OK, no body); internal — callers use ``submit_delete``."""

    def submit_delete(self, survey_id: str, condition_id: int) -> Ack:
        """``DELETE …/conditions/{condition_id}`` → :class:`Ack` (the API answers 200, no body).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.submit_delete("686d0a1b", 5).ok  # doctest: +SKIP
            True
        """
        self._submit_delete(survey_id, condition_id)
        return Ack.deleted("condition", condition_id, from_=f"survey {survey_id}")

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("surveys/{survey_id}/conditions")
    def _submit_set_operator(self, survey_id: uplink.Path, body: uplink.Body) -> ConditionsResponse:  # ty: ignore[empty-body]
        """Raw collection-PATCH; internal — callers use ``submit_set_operator``."""

    def submit_set_operator(
        self, survey_id: str, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH …/conditions`` — set the operator BETWEEN groups → the full envelope.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.submit_set_operator("686d", "or")  # doctest: +SKIP
        """
        return self._submit_set_operator(survey_id, {"operator": operator})
