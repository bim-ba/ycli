"""`forms subscriptions` commands: the integrations of an integration group (hook).

``attach`` uploads a local file (a binary payload), so it is CLI/SDK only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.models import FileOut
from ycli.yandex.forms.subscriptions.models import Subscription, SubscriptionAdapter
from ycli.yandex.forms.typedefs import HookIdArg, SurveyIdArg
from ycli.yandex.models import Ack, ItemList

app = typer.Typer(
    name="subscriptions", help="Forms integrations of an integration group.", no_args_is_help=True
)

SubscriptionIdArg = Annotated[
    int, typer.Argument(metavar="SUBSCRIPTION_ID", help="Integration id (integer).")
]
BodyFileArg = Annotated[
    Path,
    typer.Option(
        "--body-file",
        exists=True,
        dir_okay=False,
        readable=True,
        help='JSON file with the integration body; "type" selects it: email, tracker, '
        "tracker_comment, wiki, jsonrpc, http or function.",
    ),
]
FilePathArg = Annotated[
    Path,
    typer.Argument(
        exists=True,
        dir_okay=False,
        readable=True,
        metavar="FILE_PATH",
        help="Local file to attach to every run.",
    ),
]


def _body(body_file: Path) -> Subscription:
    return SubscriptionAdapter.validate_json(body_file.read_bytes())


@app.command("list")
def list_(
    survey_id: SurveyIdArg, hook_id: HookIdArg, *, forms: FormsClient
) -> ItemList[Subscription]:
    """List the integrations of hook HOOK_ID (GET …/hooks/{id}/subscriptions)."""
    return forms.subscriptions.list(survey_id, hook_id)


@app.command()
def get(
    survey_id: SurveyIdArg,
    hook_id: HookIdArg,
    subscription_id: SubscriptionIdArg,
    *,
    forms: FormsClient,
) -> Subscription:
    """Print one integration (SURVEY_ID HOOK_ID SUBSCRIPTION_ID)."""
    return forms.subscriptions.get(survey_id, hook_id, subscription_id)


@app.command()
def create(
    survey_id: SurveyIdArg, hook_id: HookIdArg, body_file: BodyFileArg, *, forms: FormsClient
) -> Subscription:
    """Add an integration to hook HOOK_ID from a JSON body (POST …/subscriptions)."""
    return forms.subscriptions.create(survey_id, hook_id, _body(body_file))


@app.command()
def update(
    survey_id: SurveyIdArg,
    hook_id: HookIdArg,
    subscription_id: SubscriptionIdArg,
    body_file: BodyFileArg,
    *,
    forms: FormsClient,
) -> Subscription:
    """Change integration SUBSCRIPTION_ID: only the fields in the JSON body change (PATCH)."""
    return forms.subscriptions.update(survey_id, hook_id, subscription_id, _body(body_file))


@app.command()
def delete(
    survey_id: SurveyIdArg,
    hook_id: HookIdArg,
    subscription_id: SubscriptionIdArg,
    *,
    forms: FormsClient,
) -> Ack:
    """Delete integration SUBSCRIPTION_ID from hook HOOK_ID."""
    forms.subscriptions.delete(survey_id, hook_id, subscription_id)
    return Ack.deleted("subscription", subscription_id, from_=f"hook {hook_id}")


@app.command()
def attach(
    survey_id: SurveyIdArg,
    hook_id: HookIdArg,
    subscription_id: SubscriptionIdArg,
    file_path: FilePathArg,
    *,
    forms: FormsClient,
) -> FileOut:
    """Upload a file for the integration's fixed attachments; returns its path."""
    return forms.subscriptions.attach(
        survey_id,
        hook_id,
        subscription_id,
        filename=file_path.name,
        data=file_path.read_bytes(),
    )
