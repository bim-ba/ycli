"""Forms display-conditions client on the httpx2 core (question / page / submit / hook targets).

A "condition" is a GROUP of clauses with its own ``operator``; a target's groups are joined by
the target-level operator that ``*_set_operator`` changes. Individual clauses have no ids: a
clause is edited by replacing its whole group with ``*_modify``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.conditions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.conditions.models import (
        ConditionCreate,
        ConditionsResponse,
        ConditionUpdate,
    )
    from ycli.yandex.forms.questions.models import Condition, ConditionOperatorType


def _dumped(body: ConditionCreate) -> dict:
    return body.model_dump(by_alias=True, exclude_none=True)


class ConditionsClient(Resource):
    """List, get, create, modify, delete and re-join the display-condition groups of a target."""

    # --- question family: when a question is shown ---

    def question_list(self, survey_id: str, question_id: str) -> ConditionsResponse:
        """``GET /surveys/{id}/questions/{question_id}/conditions`` → ``{operator, items}``.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.conditions.question_list("686d0a1b", "17").operator  # doctest: +SKIP
            'and'
        """
        return self._session.send(
            endpoints.list_conditions(endpoints.question_target(survey_id, question_id))
        )

    def question_get(self, survey_id: str, question_id: str, condition_id: int) -> Condition:
        """``GET …/questions/{question_id}/conditions/{condition_id}`` → one group.

        Example:
            >>> client.conditions.question_get("686d0a1b", "17", 5).id  # doctest: +SKIP
            5
        """
        target = endpoints.question_target(survey_id, question_id)
        return self._session.send(endpoints.get_condition(target, condition_id))

    def question_create(self, survey_id: str, question_id: str, body: ConditionCreate) -> Condition:
        """``POST …/questions/{question_id}/conditions`` — add a group → it, with its ``id``.

        Example:
            >>> from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionItemWrite
            >>> body = ConditionCreate(
            ...     operator="and",
            ...     items=[ConditionItemWrite(type="question", condition="eq", question="q1")],
            ... )
            >>> client.conditions.question_create("686d0a1b", "17", body).id  # doctest: +SKIP
            5
        """
        target = endpoints.question_target(survey_id, question_id)
        return self._session.send(endpoints.create_condition(target, _dumped(body)))

    def question_modify(
        self, survey_id: str, question_id: str, condition_id: int, body: ConditionUpdate
    ) -> Condition:
        """``PATCH …/questions/{question_id}/conditions/{condition_id}`` — replace the group.

        Example:
            >>> client.conditions.question_modify("686d0a1b", "17", 5, body)  # doctest: +SKIP
        """
        target = endpoints.question_target(survey_id, question_id)
        return self._session.send(endpoints.modify_condition(target, condition_id, _dumped(body)))

    def question_delete(self, survey_id: str, question_id: str, condition_id: int) -> None:
        """``DELETE …/questions/{question_id}/conditions/{condition_id}`` (200, no body).

        Example:
            >>> client.conditions.question_delete("686d0a1b", "17", 5)  # doctest: +SKIP
        """
        target = endpoints.question_target(survey_id, question_id)
        self._session.send(endpoints.delete_condition(target, condition_id))

    def question_set_operator(
        self, survey_id: str, question_id: str, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH …/questions/{question_id}/conditions`` — the operator BETWEEN groups.

        Example:
            >>> client.conditions.question_set_operator("686d", "17", "or")  # doctest: +SKIP
        """
        target = endpoints.question_target(survey_id, question_id)
        return self._session.send(endpoints.set_operator(target, operator))

    # --- page family: when a page is shown ---

    def page_list(self, survey_id: str, page_id: int) -> ConditionsResponse:
        """``GET /surveys/{id}/pages/{page_id}/conditions`` → ``{operator, items}``.

        Example:
            >>> client.conditions.page_list("686d0a1b", 3).operator  # doctest: +SKIP
            'and'
        """
        return self._session.send(
            endpoints.list_conditions(endpoints.page_target(survey_id, page_id))
        )

    def page_get(self, survey_id: str, page_id: int, condition_id: int) -> Condition:
        """``GET …/pages/{page_id}/conditions/{condition_id}`` → one group.

        Example:
            >>> client.conditions.page_get("686d0a1b", 3, 5).id  # doctest: +SKIP
            5
        """
        target = endpoints.page_target(survey_id, page_id)
        return self._session.send(endpoints.get_condition(target, condition_id))

    def page_create(self, survey_id: str, page_id: int, body: ConditionCreate) -> Condition:
        """``POST …/pages/{page_id}/conditions`` — add a group → it, with its ``id``.

        Example:
            >>> client.conditions.page_create("686d0a1b", 3, body).id  # doctest: +SKIP
            5
        """
        target = endpoints.page_target(survey_id, page_id)
        return self._session.send(endpoints.create_condition(target, _dumped(body)))

    def page_modify(
        self, survey_id: str, page_id: int, condition_id: int, body: ConditionUpdate
    ) -> Condition:
        """``PATCH …/pages/{page_id}/conditions/{condition_id}`` — replace the group.

        Example:
            >>> client.conditions.page_modify("686d0a1b", 3, 5, body)  # doctest: +SKIP
        """
        target = endpoints.page_target(survey_id, page_id)
        return self._session.send(endpoints.modify_condition(target, condition_id, _dumped(body)))

    def page_delete(self, survey_id: str, page_id: int, condition_id: int) -> None:
        """``DELETE …/pages/{page_id}/conditions/{condition_id}`` (200, no body).

        Example:
            >>> client.conditions.page_delete("686d0a1b", 3, 5)  # doctest: +SKIP
        """
        target = endpoints.page_target(survey_id, page_id)
        self._session.send(endpoints.delete_condition(target, condition_id))

    def page_set_operator(
        self, survey_id: str, page_id: int, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH …/pages/{page_id}/conditions`` — the operator BETWEEN groups.

        Example:
            >>> client.conditions.page_set_operator("686d", 3, "or")  # doctest: +SKIP
        """
        target = endpoints.page_target(survey_id, page_id)
        return self._session.send(endpoints.set_operator(target, operator))

    # --- submit family: when the form's Submit button is shown (right on the survey) ---

    def submit_list(self, survey_id: str) -> ConditionsResponse:
        """``GET /surveys/{id}/conditions`` → ``{operator, items}``.

        Example:
            >>> client.conditions.submit_list("686d0a1b").operator  # doctest: +SKIP
            'and'
        """
        return self._session.send(endpoints.list_conditions(endpoints.submit_target(survey_id)))

    def submit_get(self, survey_id: str, condition_id: int) -> Condition:
        """``GET /surveys/{id}/conditions/{condition_id}`` → one group.

        Example:
            >>> client.conditions.submit_get("686d0a1b", 5).id  # doctest: +SKIP
            5
        """
        target = endpoints.submit_target(survey_id)
        return self._session.send(endpoints.get_condition(target, condition_id))

    def submit_create(self, survey_id: str, body: ConditionCreate) -> Condition:
        """``POST /surveys/{id}/conditions`` — add a group → it, with its ``id``.

        Example:
            >>> client.conditions.submit_create("686d0a1b", body).id  # doctest: +SKIP
            5
        """
        target = endpoints.submit_target(survey_id)
        return self._session.send(endpoints.create_condition(target, _dumped(body)))

    def submit_modify(self, survey_id: str, condition_id: int, body: ConditionUpdate) -> Condition:
        """``PATCH /surveys/{id}/conditions/{condition_id}`` — replace the group.

        Example:
            >>> client.conditions.submit_modify("686d0a1b", 5, body)  # doctest: +SKIP
        """
        target = endpoints.submit_target(survey_id)
        return self._session.send(endpoints.modify_condition(target, condition_id, _dumped(body)))

    def submit_delete(self, survey_id: str, condition_id: int) -> None:
        """``DELETE /surveys/{id}/conditions/{condition_id}`` (200, no body).

        Example:
            >>> client.conditions.submit_delete("686d0a1b", 5)  # doctest: +SKIP
        """
        self._session.send(
            endpoints.delete_condition(endpoints.submit_target(survey_id), condition_id)
        )

    def submit_set_operator(
        self, survey_id: str, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH /surveys/{id}/conditions`` — the operator BETWEEN groups.

        Example:
            >>> client.conditions.submit_set_operator("686d", "or")  # doctest: +SKIP
        """
        return self._session.send(
            endpoints.set_operator(endpoints.submit_target(survey_id), operator)
        )

    # --- hook family: when an integration group (hook) fires ---

    def hook_list(self, survey_id: str, hook_id: int) -> ConditionsResponse:
        """``GET /surveys/{id}/hooks/{hook_id}/conditions`` → ``{operator, items}``.

        Example:
            >>> client.conditions.hook_list("686d0a1b", 11).operator  # doctest: +SKIP
            'or'
        """
        return self._session.send(
            endpoints.list_conditions(endpoints.hook_target(survey_id, hook_id))
        )

    def hook_get(self, survey_id: str, hook_id: int, condition_id: int) -> Condition:
        """``GET …/hooks/{hook_id}/conditions/{condition_id}`` → one group.

        Example:
            >>> client.conditions.hook_get("686d0a1b", 11, 5).id  # doctest: +SKIP
            5
        """
        target = endpoints.hook_target(survey_id, hook_id)
        return self._session.send(endpoints.get_condition(target, condition_id))

    def hook_create(self, survey_id: str, hook_id: int, body: ConditionCreate) -> Condition:
        """``POST …/hooks/{hook_id}/conditions`` — add a group → it, with its ``id``.

        Example:
            >>> client.conditions.hook_create("686d0a1b", 11, body).id  # doctest: +SKIP
            5
        """
        target = endpoints.hook_target(survey_id, hook_id)
        return self._session.send(endpoints.create_condition(target, _dumped(body)))

    def hook_modify(
        self, survey_id: str, hook_id: int, condition_id: int, body: ConditionUpdate
    ) -> Condition:
        """``PATCH …/hooks/{hook_id}/conditions/{condition_id}`` — replace the group.

        Example:
            >>> client.conditions.hook_modify("686d0a1b", 11, 5, body)  # doctest: +SKIP
        """
        target = endpoints.hook_target(survey_id, hook_id)
        return self._session.send(endpoints.modify_condition(target, condition_id, _dumped(body)))

    def hook_delete(self, survey_id: str, hook_id: int, condition_id: int) -> None:
        """``DELETE …/hooks/{hook_id}/conditions/{condition_id}`` (200, no body).

        Example:
            >>> client.conditions.hook_delete("686d0a1b", 11, 5)  # doctest: +SKIP
        """
        target = endpoints.hook_target(survey_id, hook_id)
        self._session.send(endpoints.delete_condition(target, condition_id))

    def hook_set_operator(
        self, survey_id: str, hook_id: int, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH …/hooks/{hook_id}/conditions`` — the operator BETWEEN groups.

        Example:
            >>> client.conditions.hook_set_operator("686d", 11, "and")  # doctest: +SKIP
        """
        target = endpoints.hook_target(survey_id, hook_id)
        return self._session.send(endpoints.set_operator(target, operator))
