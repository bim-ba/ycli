"""Pydantic models for the variables Forms offers a form's integrations.

This is a catalogue of variable *types* (answer url, a question's answer, the respondent's
e-mail, a quiz score, …) with the renderers and arguments each accepts, not the variables
configured on a subscription (those are ``SubscriptionVariable``).
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel


class VariableCategory(APIModel):
    """The group a variable type belongs to.

    Examples:
        >>> VariableCategory(type="form", name="Форма").type
        'form'
    """

    type: str | None = Field(
        default=None, description="Category: tracker, form, user, quiz, request, browser, …."
    )
    name: str | None = Field(default=None, description="Category display name.")


class VariableRenderer(APIModel):
    """One way a variable's value can render.

    Examples:
        >>> VariableRenderer(type="json", name="JSON").type
        'json'
    """

    type: str | None = Field(
        default=None, description="Renderer: txt, formatted, yfm, json, dir_staff.*."
    )
    name: str | None = Field(default=None, description="Renderer display name.")


class VariableInfo(APIModel):
    """A variable type an integration of this form can reference.

    Examples:
        >>> VariableInfo.model_validate(
        ...     {"type": "form.question_answer", "arguments": ["question"]}
        ... ).arguments
        ['question']
    """

    type: str | None = Field(
        default=None, description="Variable type, e.g. form.answer_url or user.email."
    )
    name: str | None = Field(default=None, description="Variable display name.")
    category: VariableCategory | None = Field(
        default=None, description="The group the variable belongs to."
    )
    filters: dict[str, Any] | None = Field(
        default=None, description="Which questions the variable accepts, as filter criteria."
    )
    arguments: list[Any] | None = Field(
        default=None, description="Arguments the variable takes, e.g. question, show_filenames."
    )
    renderers: list[VariableRenderer] | None = Field(
        default=None, description="Ways the variable's value can render."
    )
