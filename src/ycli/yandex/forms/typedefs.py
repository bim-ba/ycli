"""Shared forms CLI argument type aliases."""

from __future__ import annotations

from typing import Annotated

import typer

SurveyIdArg = Annotated[
    str, typer.Argument(metavar="SURVEY_ID", help="Form id, e.g. 6818ceffe010db4f59d11329.")
]

QuestionIdArg = Annotated[
    str, typer.Argument(metavar="QUESTION_ID", help="Question id (integer), e.g. 17.")
]

PageIdArg = Annotated[
    int, typer.Argument(metavar="PAGE_ID", help="Page id (integer), from `questions list`.")
]

HookIdArg = Annotated[
    int, typer.Argument(metavar="HOOK_ID", help="Integration group (hook) id (integer).")
]

NotificationIdArg = Annotated[
    int,
    typer.Argument(
        metavar="NOTIFICATION_ID", help="Notification id (integer), from `notifications list`."
    ),
]

AnswerIdArg = Annotated[
    int, typer.Argument(metavar="ANSWER_ID", help="Answer id (integer), from `answers get`.")
]
