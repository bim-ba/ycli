"""`forms hooks` commands: a form's integration groups (reads + writes)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.hooks.models import Hook, HookCreate, HookList, HookUpdate
from ycli.yandex.forms.typedefs import HookIdArg, SurveyIdArg
from ycli.yandex.models import Ack

app = typer.Typer(name="hooks", help="Forms integration groups (hooks).", no_args_is_help=True)

NameOpt = Annotated[str, typer.Option(help="Integration group name (max 100 characters).")]
ActiveOpt = Annotated[
    bool | None,
    typer.Option("--active/--inactive", help="Run the group's integrations, or pause them."),
]


@app.command("list")
def list_(survey_id: SurveyIdArg, *, forms: FormsClient) -> HookList:
    """List the integration groups of form SURVEY_ID with their integrations."""
    return forms.hooks.list(survey_id)


@app.command()
def get(survey_id: SurveyIdArg, hook_id: HookIdArg, *, forms: FormsClient) -> Hook:
    """Print one integration group (SURVEY_ID HOOK_ID)."""
    return forms.hooks.get(survey_id, hook_id)


@app.command()
def create(
    survey_id: SurveyIdArg, name: NameOpt = "", active: ActiveOpt = None, *, forms: FormsClient
) -> Hook:
    """Create an integration group on form SURVEY_ID (POST /surveys/{id}/hooks)."""
    body = HookCreate(name=name or None, active=active).model_dump(exclude_none=True)
    return forms.hooks.create(survey_id, body)


@app.command()
def modify(
    survey_id: SurveyIdArg,
    hook_id: HookIdArg,
    name: NameOpt = "",
    active: ActiveOpt = None,
    *,
    forms: FormsClient,
) -> Hook:
    """Change integration group HOOK_ID: only the options given change (PATCH)."""
    body = HookUpdate(name=name or None, active=active).model_dump(exclude_none=True)
    return forms.hooks.modify(survey_id, hook_id, body)


@app.command()
def delete(survey_id: SurveyIdArg, hook_id: HookIdArg, *, forms: FormsClient) -> Ack:
    """Delete integration group HOOK_ID with all its integrations and conditions."""
    forms.hooks.delete(survey_id, hook_id)
    return Ack.deleted("hook", hook_id, from_=f"survey {survey_id}")
