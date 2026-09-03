"""`forms conditions` commands (question / page / submit show conditions, reads + writes)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms.conditions.models import (
    ConditionCreate,
    ConditionOperatorType,
    ConditionUpdate,
)
from ycli.yandex.forms.typedefs import (
    QuestionIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="conditions", help="Forms display (show) conditions.", no_args_is_help=True)
question_app = typer.Typer(name="question", help="Question show conditions.", no_args_is_help=True)
page_app = typer.Typer(name="page", help="Page show conditions.", no_args_is_help=True)
submit_app = typer.Typer(name="submit", help="Submit-button show conditions.", no_args_is_help=True)
app.add_typer(question_app)
app.add_typer(page_app)
app.add_typer(submit_app)

PageIdArg = Annotated[int, typer.Argument(metavar="PAGE_ID", help="Page id (integer).")]
ConditionIdArg = Annotated[
    int, typer.Argument(metavar="CONDITION_ID", help="Condition group id (integer).")
]
OperatorOpt = Annotated[str, typer.Option("--operator", help="Boolean operator: and | or.")]
ItemOpt = Annotated[
    list[str] | None,
    typer.Option(
        "--item",
        help='Condition clause as JSON: {"type", "condition", "question"?, "value"?} (repeatable).',
    ),
]
BodyFileOpt = Annotated[
    Path | None,
    typer.Option("--body-file", help="JSON file with the full {operator, items} group body."),
]


def _validated_operator(operator: str) -> ConditionOperatorType:
    """Reject anything but the two API operators with a clean usage error."""
    if operator == "and":
        return "and"
    if operator == "or":
        return "or"
    raise typer.BadParameter("--operator must be 'and' or 'or'")


def _resolve_body[M: ConditionCreate](
    model_cls: type[M], operator: str, item: list[str] | None, body_file: Path | None
) -> M:
    """Build the typed group body from --body-file JSON, or --operator + --item clauses."""
    if body_file is not None:
        return model_cls.model_validate(json.loads(body_file.read_text(encoding="utf-8")))
    if not operator or not item:
        raise typer.BadParameter("pass --operator and at least one --item, or --body-file")
    return model_cls.model_validate(
        {"operator": _validated_operator(operator), "items": [json.loads(c) for c in item]}
    )


# --------------------------------------------------------------------------------------------
# question sub-app
# --------------------------------------------------------------------------------------------


@question_app.command("list")
def question_list(ctx: typer.Context, survey_id: SurveyIdArg, question_id: QuestionIdArg) -> None:
    """List show conditions of question QUESTION_ID (GET …/questions/{id}/conditions)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.question_list(survey_id, question_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@question_app.command("get")
def question_get(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    condition_id: ConditionIdArg,
) -> None:
    """Print one condition group (SURVEY_ID QUESTION_ID CONDITION_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.question_get(survey_id, question_id, condition_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@question_app.command("create")
def question_create(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    operator: OperatorOpt = "",
    item: ItemOpt = None,
    body_file: BodyFileOpt = None,
) -> None:
    """Create a condition group on the question (POST …/conditions)."""
    body = _resolve_body(ConditionCreate, operator, item, body_file)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.question_create(survey_id, question_id, body),
        app_ctx.strategy,
        app_ctx.console,
    )


@question_app.command("modify")
def question_modify(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    condition_id: ConditionIdArg,
    operator: OperatorOpt = "",
    item: ItemOpt = None,
    body_file: BodyFileOpt = None,
) -> None:
    """Replace condition group CONDITION_ID (PATCH — the API takes the FULL group, no partial)."""
    body = _resolve_body(ConditionUpdate, operator, item, body_file)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.question_modify(survey_id, question_id, condition_id, body),
        app_ctx.strategy,
        app_ctx.console,
    )


@question_app.command("delete")
def question_delete(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    condition_id: ConditionIdArg,
) -> None:
    """Delete condition group CONDITION_ID (DELETE — the API answers 200, no body)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.question_delete(survey_id, question_id, condition_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@question_app.command("set-operator")
def question_set_operator(
    ctx: typer.Context, survey_id: SurveyIdArg, question_id: QuestionIdArg, operator: OperatorOpt
) -> None:
    """Set the operator BETWEEN the question's condition groups (collection PATCH)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.question_set_operator(
            survey_id, question_id, _validated_operator(operator)
        ),
        app_ctx.strategy,
        app_ctx.console,
    )


# --------------------------------------------------------------------------------------------
# page sub-app
# --------------------------------------------------------------------------------------------


@page_app.command("list")
def page_list(ctx: typer.Context, survey_id: SurveyIdArg, page_id: PageIdArg) -> None:
    """List show conditions of page PAGE_ID (GET …/pages/{id}/conditions)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.page_list(survey_id, page_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@page_app.command("get")
def page_get(
    ctx: typer.Context, survey_id: SurveyIdArg, page_id: PageIdArg, condition_id: ConditionIdArg
) -> None:
    """Print one condition group (SURVEY_ID PAGE_ID CONDITION_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.page_get(survey_id, page_id, condition_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@page_app.command("create")
def page_create(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    page_id: PageIdArg,
    operator: OperatorOpt = "",
    item: ItemOpt = None,
    body_file: BodyFileOpt = None,
) -> None:
    """Create a condition group on the page (POST …/conditions)."""
    body = _resolve_body(ConditionCreate, operator, item, body_file)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.page_create(survey_id, page_id, body),
        app_ctx.strategy,
        app_ctx.console,
    )


@page_app.command("modify")
def page_modify(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    page_id: PageIdArg,
    condition_id: ConditionIdArg,
    operator: OperatorOpt = "",
    item: ItemOpt = None,
    body_file: BodyFileOpt = None,
) -> None:
    """Replace condition group CONDITION_ID (PATCH — the API takes the FULL group, no partial)."""
    body = _resolve_body(ConditionUpdate, operator, item, body_file)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.page_modify(survey_id, page_id, condition_id, body),
        app_ctx.strategy,
        app_ctx.console,
    )


@page_app.command("delete")
def page_delete(
    ctx: typer.Context, survey_id: SurveyIdArg, page_id: PageIdArg, condition_id: ConditionIdArg
) -> None:
    """Delete condition group CONDITION_ID (DELETE — the API answers 200, no body)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.page_delete(survey_id, page_id, condition_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@page_app.command("set-operator")
def page_set_operator(
    ctx: typer.Context, survey_id: SurveyIdArg, page_id: PageIdArg, operator: OperatorOpt
) -> None:
    """Set the operator BETWEEN the page's condition groups (collection PATCH)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.page_set_operator(
            survey_id, page_id, _validated_operator(operator)
        ),
        app_ctx.strategy,
        app_ctx.console,
    )


# --------------------------------------------------------------------------------------------
# submit sub-app
# --------------------------------------------------------------------------------------------


@submit_app.command("list")
def submit_list(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """List show conditions of the submit button (GET /surveys/{id}/conditions)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.submit_list(survey_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@submit_app.command("get")
def submit_get(ctx: typer.Context, survey_id: SurveyIdArg, condition_id: ConditionIdArg) -> None:
    """Print one condition group (SURVEY_ID CONDITION_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.submit_get(survey_id, condition_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@submit_app.command("create")
def submit_create(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    operator: OperatorOpt = "",
    item: ItemOpt = None,
    body_file: BodyFileOpt = None,
) -> None:
    """Create a condition group on the submit button (POST …/conditions)."""
    body = _resolve_body(ConditionCreate, operator, item, body_file)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.submit_create(survey_id, body),
        app_ctx.strategy,
        app_ctx.console,
    )


@submit_app.command("modify")
def submit_modify(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    condition_id: ConditionIdArg,
    operator: OperatorOpt = "",
    item: ItemOpt = None,
    body_file: BodyFileOpt = None,
) -> None:
    """Replace condition group CONDITION_ID (PATCH — the API takes the FULL group, no partial)."""
    body = _resolve_body(ConditionUpdate, operator, item, body_file)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.submit_modify(survey_id, condition_id, body),
        app_ctx.strategy,
        app_ctx.console,
    )


@submit_app.command("delete")
def submit_delete(ctx: typer.Context, survey_id: SurveyIdArg, condition_id: ConditionIdArg) -> None:
    """Delete condition group CONDITION_ID (DELETE — the API answers 200, no body)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.submit_delete(survey_id, condition_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@submit_app.command("set-operator")
def submit_set_operator(ctx: typer.Context, survey_id: SurveyIdArg, operator: OperatorOpt) -> None:
    """Set the operator BETWEEN the submit button's condition groups (collection PATCH)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.conditions.submit_set_operator(survey_id, _validated_operator(operator)),
        app_ctx.strategy,
        app_ctx.console,
    )
