"""Forms display-conditions client on the httpx2 core (question / page / submit / hook targets).

A "condition" is a GROUP of clauses with its own ``operator``; a target's groups are joined by
the target-level operator that ``*_set_operator`` changes. Individual clauses have no ids: a
clause is edited by replacing its whole group with ``*_update``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.conditions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionUpdate
    from ycli.yandex.forms.models import Condition, ConditionOperatorType, ConditionsResponse


class ConditionsClient(Resource):
    """List, get, create, update, delete and re-join the display-condition groups of a target."""

    # --- question family: when a question is shown ---

    def question_list(self, survey_id: str, question_id: str) -> ConditionsResponse:
        """``GET /surveys/{id}/questions/{question_id}/conditions`` → ``{operator, items}``.

        Args:
            survey_id: The form's id.
            question_id: The question's id.

        Returns:
            The target's operator and condition groups.

        Examples:
            >>> forms.conditions.question_list("686d0a1b2c3d4e5f00000090", "17").operator
            'or'
        """
        return self._session.send(endpoints.question_list(survey_id, question_id))

    def question_get(self, survey_id: str, question_id: str, condition_id: int) -> Condition:
        """``GET …/questions/{question_id}/conditions/{condition_id}`` → one group.

        Args:
            survey_id: The form's id.
            question_id: The question's id.
            condition_id: The condition group's id.

        Returns:
            The condition group.

        Examples:
            >>> forms.conditions.question_get("686d0a1b2c3d4e5f00000090", "17", 102).id
            102
        """
        return self._session.send(endpoints.question_get(survey_id, question_id, condition_id))

    def question_create(self, survey_id: str, question_id: str, body: ConditionCreate) -> Condition:
        """``POST …/questions/{question_id}/conditions`` — add a group → it, with its ``id``.

        Args:
            survey_id: The form's id.
            question_id: The question's id.
            body: The new group: its operator and clauses.

        Returns:
            The created group, with its ``id``.

        Examples:
            >>> from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionItemWrite
            >>> body = ConditionCreate(
            ...     operator="and",
            ...     items=[
            ...         ConditionItemWrite(
            ...             type="question", condition="gt", question="age100", value="18"
            ...         )
            ...     ],
            ... )
            >>> forms.conditions.question_create("686d0a1b2c3d4e5f00000090", "17", body).id
            103
        """
        return self._session.send(endpoints.question_create(survey_id, question_id, body))

    def question_update(
        self, survey_id: str, question_id: str, condition_id: int, body: ConditionUpdate
    ) -> Condition:
        """``PATCH …/questions/{question_id}/conditions/{condition_id}`` — replace the group.

        Args:
            survey_id: The form's id.
            question_id: The question's id.
            condition_id: The condition group's id.
            body: The full replacement group: its operator and clauses.

        Returns:
            The replaced group.

        Examples:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite, ConditionUpdate
            >>> body = ConditionUpdate(
            ...     operator="or",
            ...     items=[ConditionItemWrite(type="language", condition="eq", value="ru")],
            ... )
            >>> forms.conditions.question_update("686d0a1b2c3d4e5f00000090", "17", 104, body).id
            104
        """
        return self._session.send(
            endpoints.question_update(survey_id, question_id, condition_id, body)
        )

    def question_delete(self, survey_id: str, question_id: str, condition_id: int) -> None:
        """``DELETE …/questions/{question_id}/conditions/{condition_id}`` (200, no body).

        Args:
            survey_id: The form's id.
            question_id: The question's id.
            condition_id: The condition group's id.

        Examples:
            >>> forms.conditions.question_delete("686d0a1b2c3d4e5f00000090", "17", 106)
        """
        self._session.send(endpoints.question_delete(survey_id, question_id, condition_id))

    def question_update_operator(
        self, survey_id: str, question_id: str, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH …/questions/{question_id}/conditions`` — the operator BETWEEN groups.

        Args:
            survey_id: The form's id.
            question_id: The question's id.
            operator: The operator joining the groups: ``and`` or ``or``.

        Returns:
            The target's operator and condition groups.

        Examples:
            >>> forms.conditions.question_update_operator(
            ...     "686d0a1b2c3d4e5f00000090", "17", "or"
            ... ).operator
            'or'
        """
        return self._session.send(
            endpoints.question_update_operator(survey_id, question_id, operator)
        )

    # --- page family: when a page is shown ---

    def page_list(self, survey_id: str, page_id: int) -> ConditionsResponse:
        """``GET /surveys/{id}/pages/{page_id}/conditions`` → ``{operator, items}``.

        Args:
            survey_id: The form's id.
            page_id: The page's id.

        Returns:
            The target's operator and condition groups.

        Examples:
            >>> forms.conditions.page_list("686d0a1b2c3d4e5f00000090", 3).operator
            'or'
        """
        return self._session.send(endpoints.page_list(survey_id, page_id))

    def page_get(self, survey_id: str, page_id: int, condition_id: int) -> Condition:
        """``GET …/pages/{page_id}/conditions/{condition_id}`` → one group.

        Args:
            survey_id: The form's id.
            page_id: The page's id.
            condition_id: The condition group's id.

        Returns:
            The condition group.

        Examples:
            >>> forms.conditions.page_get("686d0a1b2c3d4e5f00000090", 3, 202).id
            202
        """
        return self._session.send(endpoints.page_get(survey_id, page_id, condition_id))

    def page_create(self, survey_id: str, page_id: int, body: ConditionCreate) -> Condition:
        """``POST …/pages/{page_id}/conditions`` — add a group → it, with its ``id``.

        Args:
            survey_id: The form's id.
            page_id: The page's id.
            body: The new group: its operator and clauses.

        Returns:
            The created group, with its ``id``.

        Examples:
            >>> from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionItemWrite
            >>> body = ConditionCreate(
            ...     operator="and",
            ...     items=[
            ...         ConditionItemWrite(
            ...             type="question", condition="gt", question="age200", value="18"
            ...         )
            ...     ],
            ... )
            >>> forms.conditions.page_create("686d0a1b2c3d4e5f00000090", 3, body).id
            203
        """
        return self._session.send(endpoints.page_create(survey_id, page_id, body))

    def page_update(
        self, survey_id: str, page_id: int, condition_id: int, body: ConditionUpdate
    ) -> Condition:
        """``PATCH …/pages/{page_id}/conditions/{condition_id}`` — replace the group.

        Args:
            survey_id: The form's id.
            page_id: The page's id.
            condition_id: The condition group's id.
            body: The full replacement group: its operator and clauses.

        Returns:
            The replaced group.

        Examples:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite, ConditionUpdate
            >>> body = ConditionUpdate(
            ...     operator="or",
            ...     items=[ConditionItemWrite(type="language", condition="eq", value="ru")],
            ... )
            >>> forms.conditions.page_update("686d0a1b2c3d4e5f00000090", 3, 204, body).id
            204
        """
        return self._session.send(endpoints.page_update(survey_id, page_id, condition_id, body))

    def page_delete(self, survey_id: str, page_id: int, condition_id: int) -> None:
        """``DELETE …/pages/{page_id}/conditions/{condition_id}`` (200, no body).

        Args:
            survey_id: The form's id.
            page_id: The page's id.
            condition_id: The condition group's id.

        Examples:
            >>> forms.conditions.page_delete("686d0a1b2c3d4e5f00000090", 3, 206)
        """
        self._session.send(endpoints.page_delete(survey_id, page_id, condition_id))

    def page_update_operator(
        self, survey_id: str, page_id: int, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH …/pages/{page_id}/conditions`` — the operator BETWEEN groups.

        Args:
            survey_id: The form's id.
            page_id: The page's id.
            operator: The operator joining the groups: ``and`` or ``or``.

        Returns:
            The target's operator and condition groups.

        Examples:
            >>> forms.conditions.page_update_operator("686d0a1b2c3d4e5f00000090", 3, "or").operator
            'or'
        """
        return self._session.send(endpoints.page_update_operator(survey_id, page_id, operator))

    # --- submit family: when the form's Submit button is shown (right on the survey) ---

    def submit_list(self, survey_id: str) -> ConditionsResponse:
        """``GET /surveys/{id}/conditions`` → ``{operator, items}``.

        Args:
            survey_id: The form's id.

        Returns:
            The target's operator and condition groups.

        Examples:
            >>> forms.conditions.submit_list("686d0a1b2c3d4e5f00000090").operator
            'or'
        """
        return self._session.send(endpoints.submit_list(survey_id))

    def submit_get(self, survey_id: str, condition_id: int) -> Condition:
        """``GET /surveys/{id}/conditions/{condition_id}`` → one group.

        Args:
            survey_id: The form's id.
            condition_id: The condition group's id.

        Returns:
            The condition group.

        Examples:
            >>> forms.conditions.submit_get("686d0a1b2c3d4e5f00000090", 302).id
            302
        """
        return self._session.send(endpoints.submit_get(survey_id, condition_id))

    def submit_create(self, survey_id: str, body: ConditionCreate) -> Condition:
        """``POST /surveys/{id}/conditions`` — add a group → it, with its ``id``.

        Args:
            survey_id: The form's id.
            body: The new group: its operator and clauses.

        Returns:
            The created group, with its ``id``.

        Examples:
            >>> from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionItemWrite
            >>> body = ConditionCreate(
            ...     operator="and",
            ...     items=[
            ...         ConditionItemWrite(
            ...             type="question", condition="gt", question="age300", value="18"
            ...         )
            ...     ],
            ... )
            >>> forms.conditions.submit_create("686d0a1b2c3d4e5f00000090", body).id
            303
        """
        return self._session.send(endpoints.submit_create(survey_id, body))

    def submit_update(self, survey_id: str, condition_id: int, body: ConditionUpdate) -> Condition:
        """``PATCH /surveys/{id}/conditions/{condition_id}`` — replace the group.

        Args:
            survey_id: The form's id.
            condition_id: The condition group's id.
            body: The full replacement group: its operator and clauses.

        Returns:
            The replaced group.

        Examples:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite, ConditionUpdate
            >>> body = ConditionUpdate(
            ...     operator="or",
            ...     items=[ConditionItemWrite(type="language", condition="eq", value="ru")],
            ... )
            >>> forms.conditions.submit_update("686d0a1b2c3d4e5f00000090", 304, body).id
            304
        """
        return self._session.send(endpoints.submit_update(survey_id, condition_id, body))

    def submit_delete(self, survey_id: str, condition_id: int) -> None:
        """``DELETE /surveys/{id}/conditions/{condition_id}`` (200, no body).

        Args:
            survey_id: The form's id.
            condition_id: The condition group's id.

        Examples:
            >>> forms.conditions.submit_delete("686d0a1b2c3d4e5f00000090", 306)
        """
        self._session.send(endpoints.submit_delete(survey_id, condition_id))

    def submit_update_operator(
        self, survey_id: str, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH /surveys/{id}/conditions`` — the operator BETWEEN groups.

        Args:
            survey_id: The form's id.
            operator: The operator joining the groups: ``and`` or ``or``.

        Returns:
            The target's operator and condition groups.

        Examples:
            >>> forms.conditions.submit_update_operator("686d0a1b2c3d4e5f00000090", "or").operator
            'or'
        """
        return self._session.send(endpoints.submit_update_operator(survey_id, operator))

    # --- hook family: when an integration group (hook) fires ---

    def hook_list(self, survey_id: str, hook_id: int) -> ConditionsResponse:
        """``GET /surveys/{id}/hooks/{hook_id}/conditions`` → ``{operator, items}``.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.

        Returns:
            The target's operator and condition groups.

        Examples:
            >>> forms.conditions.hook_list("686d0a1b2c3d4e5f00000090", 11).operator
            'or'
        """
        return self._session.send(endpoints.hook_list(survey_id, hook_id))

    def hook_get(self, survey_id: str, hook_id: int, condition_id: int) -> Condition:
        """``GET …/hooks/{hook_id}/conditions/{condition_id}`` → one group.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            condition_id: The condition group's id.

        Returns:
            The condition group.

        Examples:
            >>> forms.conditions.hook_get("686d0a1b2c3d4e5f00000090", 11, 402).id
            402
        """
        return self._session.send(endpoints.hook_get(survey_id, hook_id, condition_id))

    def hook_create(self, survey_id: str, hook_id: int, body: ConditionCreate) -> Condition:
        """``POST …/hooks/{hook_id}/conditions`` — add a group → it, with its ``id``.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            body: The new group: its operator and clauses.

        Returns:
            The created group, with its ``id``.

        Examples:
            >>> from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionItemWrite
            >>> body = ConditionCreate(
            ...     operator="and",
            ...     items=[
            ...         ConditionItemWrite(
            ...             type="question", condition="gt", question="age400", value="18"
            ...         )
            ...     ],
            ... )
            >>> forms.conditions.hook_create("686d0a1b2c3d4e5f00000090", 11, body).id
            403
        """
        return self._session.send(endpoints.hook_create(survey_id, hook_id, body))

    def hook_update(
        self, survey_id: str, hook_id: int, condition_id: int, body: ConditionUpdate
    ) -> Condition:
        """``PATCH …/hooks/{hook_id}/conditions/{condition_id}`` — replace the group.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            condition_id: The condition group's id.
            body: The full replacement group: its operator and clauses.

        Returns:
            The replaced group.

        Examples:
            >>> from ycli.yandex.forms.conditions.models import ConditionItemWrite, ConditionUpdate
            >>> body = ConditionUpdate(
            ...     operator="or",
            ...     items=[ConditionItemWrite(type="language", condition="eq", value="ru")],
            ... )
            >>> forms.conditions.hook_update("686d0a1b2c3d4e5f00000090", 11, 404, body).id
            404
        """
        return self._session.send(endpoints.hook_update(survey_id, hook_id, condition_id, body))

    def hook_delete(self, survey_id: str, hook_id: int, condition_id: int) -> None:
        """``DELETE …/hooks/{hook_id}/conditions/{condition_id}`` (200, no body).

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            condition_id: The condition group's id.

        Examples:
            >>> forms.conditions.hook_delete("686d0a1b2c3d4e5f00000090", 11, 406)
        """
        self._session.send(endpoints.hook_delete(survey_id, hook_id, condition_id))

    def hook_update_operator(
        self, survey_id: str, hook_id: int, operator: ConditionOperatorType
    ) -> ConditionsResponse:
        """``PATCH …/hooks/{hook_id}/conditions`` — the operator BETWEEN groups.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            operator: The operator joining the groups: ``and`` or ``or``.

        Returns:
            The target's operator and condition groups.

        Examples:
            >>> forms.conditions.hook_update_operator("686d0a1b2c3d4e5f00000090", 11, "or").operator
            'or'
        """
        return self._session.send(endpoints.hook_update_operator(survey_id, hook_id, operator))
