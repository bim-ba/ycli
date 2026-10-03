"""One definition per shape: two models of a service with the same schema need a stated reason.

The same model used to be written many times under different names (#203). A model's shape
is its JSON schema without prose (titles, descriptions, examples); classes of one service that
share a shape must be one class, or a group in ``SAME_SHAPE`` with the reason they are not.
"""

from __future__ import annotations

import importlib
import json
import pkgutil
from collections import defaultdict
from typing import Any

from pydantic import BaseModel

from ycli.yandex.registry import SERVICES

PROSE = frozenset({"title", "description", "examples"})

# Groups of same-shaped models that stay separate classes, each with its reason. A group is
# named by its members, ``<resource>.<Class>``, and belongs to one service.
TWO_OPERATIONS = "two operations of the API, whose bodies may diverge"
UNRELATED_BODIES = "bodies of unrelated operations that happen to match"
TWO_ROLES = "two roles in one model that happen to match"
SAME_SHAPE: dict[tuple[str, frozenset[str]], str] = {
    ("forms", frozenset({"access.AccessGrant", "access.AccessRevoke"})): TWO_OPERATIONS,
    (
        "forms",
        frozenset({"conditions.ConditionCreate", "conditions.ConditionUpdate"}),
    ): TWO_OPERATIONS,
    ("forms", frozenset({"hooks.HookCreate", "hooks.HookUpdate"})): TWO_OPERATIONS,
    ("forms", frozenset({"keysets.KeysetCreate", "keysets.KeysetUpdate"})): TWO_OPERATIONS,
    (
        "forms",
        frozenset({"questions.QuestionDataSource", "questions.QuestionHintSource"}),
    ): TWO_ROLES,
    (
        "forms",
        frozenset({"subscriptions.AttachmentQuestions", "subscriptions.VariableQuestions"}),
    ): TWO_ROLES,
    ("forms", frozenset({"surveys.SurveyCreate", "surveys.SurveyUpdate"})): TWO_OPERATIONS,
    (
        "forms",
        frozenset({"variables.VariableCategory", "variables.VariableRenderer"}),
    ): "different things that happen to have a name and a type",
    (
        "tracker",
        frozenset({"dashboards.DashboardOwner", "sprints.SprintBoardInput"}),
    ): "different things that happen to hold only an id",
    (
        "tracker",
        frozenset({"fields.FieldCategoryUpdate", "resolutions.ResolutionUpdate"}),
    ): UNRELATED_BODIES,
    (
        "tracker",
        frozenset({"issuetypes.IssueType", "priorities.Priority"}),
    ): "different concepts that share a form",
    (
        "tracker",
        frozenset({"issuetypes.IssueTypeCreate", "resolutions.ResolutionCreate"}),
    ): UNRELATED_BODIES,
    (
        "tracker",
        frozenset({"issuetypes.IssueTypeUpdate", "priorities.PriorityUpdate"}),
    ): UNRELATED_BODIES,
    (
        "tracker",
        frozenset({"links.LinkObject", "transitions.StatusRef"}),
    ): "different things that happen to have a key and a display name",
    (
        "tracker",
        frozenset({"workflows.WorkflowActionInput", "workflows.WorkflowActionUpdate"}),
    ): TWO_OPERATIONS,
}


def shape(node: Any) -> Any:
    """A schema without its prose, so two models written with different words compare equal.

    Example:
        >>> shape({"title": "A", "properties": {"id": {"type": "string", "description": "x"}}})
        {'properties': {'id': {'type': 'string'}}}
    """
    if isinstance(node, dict):
        return {key: shape(value) for key, value in node.items() if key not in PROSE}
    return [shape(item) for item in node] if isinstance(node, list) else node


def models(service: str) -> dict[str, type[BaseModel]]:
    """Every model class a service defines, by ``<resource>.<Class>`` (``.<Class>`` if shared)."""
    package = importlib.import_module(f"ycli.yandex.{service}")
    found: dict[str, type[BaseModel]] = {}
    for info in pkgutil.walk_packages(package.__path__, f"{package.__name__}."):
        if info.name.rsplit(".", 1)[1] != "models":
            continue
        module = importlib.import_module(info.name)
        resource = info.name.removeprefix(f"{package.__name__}.").removesuffix("models").rstrip(".")
        for name, value in vars(module).items():
            defined_here = isinstance(value, type) and value.__module__ == info.name
            if defined_here and issubclass(value, BaseModel):
                found[f"{resource}.{name}"] = value
    return found


def same_shape_groups(service: str) -> list[frozenset[str]]:
    """The groups of two or more of ``service``'s models whose shapes are identical."""
    by_shape: dict[str, set[str]] = defaultdict(set)
    for name, model in models(service).items():
        schema = shape(model.model_json_schema(by_alias=True))
        by_shape[json.dumps(schema, sort_keys=True)].add(name)
    return sorted((frozenset(names) for names in by_shape.values() if len(names) > 1), key=sorted)


def test_models_of_one_shape_are_one_class_or_explained():
    found = {
        (service.name, group) for service in SERVICES for group in same_shape_groups(service.name)
    }
    unexplained = sorted((service, sorted(group)) for service, group in found - set(SAME_SHAPE))
    assert not unexplained, f"same shape, no reason in SAME_SHAPE: {unexplained}"
    stale = sorted((service, sorted(group)) for service, group in set(SAME_SHAPE) - found)
    assert not stale, f"SAME_SHAPE names groups that no longer share a shape: {stale}"
