"""`forms conditions` commands: reads and writes of display conditions.

The conditions belong to a question, a page, the submit button or an integration group (hook).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.typedefs import values_option
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionUpdate
from ycli.yandex.forms.models import Condition, ConditionOperatorType, ConditionsResponse
from ycli.yandex.forms.typedefs import FormPageIDArg, HookIDArg, QuestionIDArg, SurveyIDArg
from ycli.yandex.models import Ack

app = typer.Typer(name="conditions", help="Forms display (show) conditions.", no_args_is_help=True)
question_app = typer.Typer(name="question", help="Question show conditions.", no_args_is_help=True)
page_app = typer.Typer(name="page", help="Page show conditions.", no_args_is_help=True)
submit_app = typer.Typer(name="submit", help="Submit-button show conditions.", no_args_is_help=True)
hook_app = typer.Typer(
    name="hook", help="Conditions that gate an integration group.", no_args_is_help=True
)
app.add_typer(question_app)
app.add_typer(page_app)
app.add_typer(submit_app)
app.add_typer(hook_app)

ConditionIDArg = Annotated[
    int, typer.Argument(metavar="CONDITION_ID", help="Condition group id (integer).")
]
OperatorOpt = Annotated[
    str | None, values_option(ConditionOperatorType, "--operator", help="Boolean operator.")
]
JoinOperatorOpt = Annotated[
    str, values_option(ConditionOperatorType, "--operator", help="Boolean operator.")
]
ItemOpt = Annotated[
    list[str] | None,
    typer.Option(
        "--item",
        help='Condition clause as JSON: {"type", "condition", "question"?, "value"?} (repeatable).',
    ),
]
ConditionFileOpt = Annotated[
    Path | None,
    typer.Option(
        "--body-file",
        exists=True,
        dir_okay=False,
        readable=True,
        help="JSON file with the full {operator, items} group body.",
    ),
]


def _resolve_body[M: ConditionCreate](
    model_cls: type[M], operator: str | None, item: list[str] | None, body_file: Path | None
) -> M:
    """The typed group body from ``--body-file`` JSON, or from ``--operator`` + ``--item``."""
    if body_file is not None:
        return model_cls.model_validate_json(body_file.read_bytes())
    given = {"operator": operator, "items": [json.loads(c) for c in item] if item else None}
    return model_cls.model_validate({k: v for k, v in given.items() if v is not None})


# --- question ---


@question_app.command("list")
def question_list(
    survey_id: SurveyIDArg, question_id: QuestionIDArg, *, forms: FormsClient
) -> ConditionsResponse:
    """List show conditions of question QUESTION_ID (GET …/questions/{id}/conditions)."""
    return forms.conditions.question_list(survey_id, question_id)


@question_app.command("get")
def question_get(
    survey_id: SurveyIDArg,
    question_id: QuestionIDArg,
    condition_id: ConditionIDArg,
    *,
    forms: FormsClient,
) -> Condition:
    """Print one condition group (SURVEY_ID QUESTION_ID CONDITION_ID)."""
    return forms.conditions.question_get(survey_id, question_id, condition_id)


@question_app.command("create")
def question_create(
    survey_id: SurveyIDArg,
    question_id: QuestionIDArg,
    operator: OperatorOpt = None,
    item: ItemOpt = None,
    body_file: ConditionFileOpt = None,
    *,
    forms: FormsClient,
) -> Condition:
    """Create a condition group on the question (POST …/conditions)."""
    body = _resolve_body(ConditionCreate, operator, item, body_file)
    return forms.conditions.question_create(survey_id, question_id, body)


@question_app.command("update")
def question_update(
    survey_id: SurveyIDArg,
    question_id: QuestionIDArg,
    condition_id: ConditionIDArg,
    operator: OperatorOpt = None,
    item: ItemOpt = None,
    body_file: ConditionFileOpt = None,
    *,
    forms: FormsClient,
) -> Condition:
    """Replace condition group CONDITION_ID (PATCH — the API takes the FULL group, no partial)."""
    body = _resolve_body(ConditionUpdate, operator, item, body_file)
    return forms.conditions.question_update(survey_id, question_id, condition_id, body)


@question_app.command("delete")
def question_delete(
    survey_id: SurveyIDArg,
    question_id: QuestionIDArg,
    condition_id: ConditionIDArg,
    *,
    forms: FormsClient,
) -> Ack:
    """Delete condition group CONDITION_ID (DELETE — the API answers 200, no body)."""
    forms.conditions.question_delete(survey_id, question_id, condition_id)
    return Ack.deleted("condition", condition_id, from_=f"question {question_id}")


@question_app.command("set-operator")
def question_set_operator(
    survey_id: SurveyIDArg,
    question_id: QuestionIDArg,
    operator: JoinOperatorOpt,
    *,
    forms: FormsClient,
) -> ConditionsResponse:
    """Set the operator BETWEEN the question's condition groups (collection PATCH)."""
    return forms.conditions.question_set_operator(survey_id, question_id, operator)


# --- page ---


@page_app.command("list")
def page_list(
    survey_id: SurveyIDArg, page_id: FormPageIDArg, *, forms: FormsClient
) -> ConditionsResponse:
    """List show conditions of page PAGE_ID (GET …/pages/{id}/conditions)."""
    return forms.conditions.page_list(survey_id, page_id)


@page_app.command("get")
def page_get(
    survey_id: SurveyIDArg,
    page_id: FormPageIDArg,
    condition_id: ConditionIDArg,
    *,
    forms: FormsClient,
) -> Condition:
    """Print one condition group (SURVEY_ID PAGE_ID CONDITION_ID)."""
    return forms.conditions.page_get(survey_id, page_id, condition_id)


@page_app.command("create")
def page_create(
    survey_id: SurveyIDArg,
    page_id: FormPageIDArg,
    operator: OperatorOpt = None,
    item: ItemOpt = None,
    body_file: ConditionFileOpt = None,
    *,
    forms: FormsClient,
) -> Condition:
    """Create a condition group on the page (POST …/conditions)."""
    body = _resolve_body(ConditionCreate, operator, item, body_file)
    return forms.conditions.page_create(survey_id, page_id, body)


@page_app.command("update")
def page_update(
    survey_id: SurveyIDArg,
    page_id: FormPageIDArg,
    condition_id: ConditionIDArg,
    operator: OperatorOpt = None,
    item: ItemOpt = None,
    body_file: ConditionFileOpt = None,
    *,
    forms: FormsClient,
) -> Condition:
    """Replace condition group CONDITION_ID (PATCH — the API takes the FULL group, no partial)."""
    body = _resolve_body(ConditionUpdate, operator, item, body_file)
    return forms.conditions.page_update(survey_id, page_id, condition_id, body)


@page_app.command("delete")
def page_delete(
    survey_id: SurveyIDArg,
    page_id: FormPageIDArg,
    condition_id: ConditionIDArg,
    *,
    forms: FormsClient,
) -> Ack:
    """Delete condition group CONDITION_ID (DELETE — the API answers 200, no body)."""
    forms.conditions.page_delete(survey_id, page_id, condition_id)
    return Ack.deleted("condition", condition_id, from_=f"page {page_id}")


@page_app.command("set-operator")
def page_set_operator(
    survey_id: SurveyIDArg, page_id: FormPageIDArg, operator: JoinOperatorOpt, *, forms: FormsClient
) -> ConditionsResponse:
    """Set the operator BETWEEN the page's condition groups (collection PATCH)."""
    return forms.conditions.page_set_operator(survey_id, page_id, operator)


# --- submit ---


@submit_app.command("list")
def submit_list(survey_id: SurveyIDArg, *, forms: FormsClient) -> ConditionsResponse:
    """List show conditions of the submit button (GET /surveys/{id}/conditions)."""
    return forms.conditions.submit_list(survey_id)


@submit_app.command("get")
def submit_get(
    survey_id: SurveyIDArg, condition_id: ConditionIDArg, *, forms: FormsClient
) -> Condition:
    """Print one condition group (SURVEY_ID CONDITION_ID)."""
    return forms.conditions.submit_get(survey_id, condition_id)


@submit_app.command("create")
def submit_create(
    survey_id: SurveyIDArg,
    operator: OperatorOpt = None,
    item: ItemOpt = None,
    body_file: ConditionFileOpt = None,
    *,
    forms: FormsClient,
) -> Condition:
    """Create a condition group on the submit button (POST …/conditions)."""
    body = _resolve_body(ConditionCreate, operator, item, body_file)
    return forms.conditions.submit_create(survey_id, body)


@submit_app.command("update")
def submit_update(
    survey_id: SurveyIDArg,
    condition_id: ConditionIDArg,
    operator: OperatorOpt = None,
    item: ItemOpt = None,
    body_file: ConditionFileOpt = None,
    *,
    forms: FormsClient,
) -> Condition:
    """Replace condition group CONDITION_ID (PATCH — the API takes the FULL group, no partial)."""
    body = _resolve_body(ConditionUpdate, operator, item, body_file)
    return forms.conditions.submit_update(survey_id, condition_id, body)


@submit_app.command("delete")
def submit_delete(
    survey_id: SurveyIDArg, condition_id: ConditionIDArg, *, forms: FormsClient
) -> Ack:
    """Delete condition group CONDITION_ID (DELETE — the API answers 200, no body)."""
    forms.conditions.submit_delete(survey_id, condition_id)
    return Ack.deleted("condition", condition_id, from_=f"survey {survey_id}")


@submit_app.command("set-operator")
def submit_set_operator(
    survey_id: SurveyIDArg, operator: JoinOperatorOpt, *, forms: FormsClient
) -> ConditionsResponse:
    """Set the operator BETWEEN the submit button's condition groups (collection PATCH)."""
    return forms.conditions.submit_set_operator(survey_id, operator)


# --- hook ---


@hook_app.command("list")
def hook_list(
    survey_id: SurveyIDArg, hook_id: HookIDArg, *, forms: FormsClient
) -> ConditionsResponse:
    """List the conditions of integration group HOOK_ID (GET …/hooks/{id}/conditions)."""
    return forms.conditions.hook_list(survey_id, hook_id)


@hook_app.command("get")
def hook_get(
    survey_id: SurveyIDArg, hook_id: HookIDArg, condition_id: ConditionIDArg, *, forms: FormsClient
) -> Condition:
    """Print one condition group (SURVEY_ID HOOK_ID CONDITION_ID)."""
    return forms.conditions.hook_get(survey_id, hook_id, condition_id)


@hook_app.command("create")
def hook_create(
    survey_id: SurveyIDArg,
    hook_id: HookIDArg,
    operator: OperatorOpt = None,
    item: ItemOpt = None,
    body_file: ConditionFileOpt = None,
    *,
    forms: FormsClient,
) -> Condition:
    """Create a condition group on the integration group (POST …/conditions)."""
    body = _resolve_body(ConditionCreate, operator, item, body_file)
    return forms.conditions.hook_create(survey_id, hook_id, body)


@hook_app.command("update")
def hook_update(
    survey_id: SurveyIDArg,
    hook_id: HookIDArg,
    condition_id: ConditionIDArg,
    operator: OperatorOpt = None,
    item: ItemOpt = None,
    body_file: ConditionFileOpt = None,
    *,
    forms: FormsClient,
) -> Condition:
    """Replace condition group CONDITION_ID (PATCH — the API takes the FULL group, no partial)."""
    body = _resolve_body(ConditionUpdate, operator, item, body_file)
    return forms.conditions.hook_update(survey_id, hook_id, condition_id, body)


@hook_app.command("delete")
def hook_delete(
    survey_id: SurveyIDArg, hook_id: HookIDArg, condition_id: ConditionIDArg, *, forms: FormsClient
) -> Ack:
    """Delete condition group CONDITION_ID (DELETE — the API answers 200, no body)."""
    forms.conditions.hook_delete(survey_id, hook_id, condition_id)
    return Ack.deleted("condition", condition_id, from_=f"hook {hook_id}")


@hook_app.command("set-operator")
def hook_set_operator(
    survey_id: SurveyIDArg, hook_id: HookIDArg, operator: JoinOperatorOpt, *, forms: FormsClient
) -> ConditionsResponse:
    """Set the operator BETWEEN the integration group's condition groups (collection PATCH)."""
    return forms.conditions.hook_set_operator(survey_id, hook_id, operator)
