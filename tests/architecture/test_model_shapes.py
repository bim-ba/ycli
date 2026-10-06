"""One definition per shape: two models of a service with the same schema need a stated reason.

The same model used to be written many times under different names (#203). A model's shape
is its JSON schema without prose (titles, descriptions, examples); classes of one service that
share a shape must be one class, or a group in ``SAME_SHAPE`` with the reason they are not.
"""

import importlib
import json
import pkgutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ycli.yandex.registry import SERVICES

PROSE = frozenset({"title", "description", "examples"})
REPOSITORY = Path(__file__).parents[2]

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
        frozenset({"issuetypes.IssueTypeCreate", "resolutions.ResolutionCreate"}),
    ): UNRELATED_BODIES,
    (
        "tracker",
        frozenset({"issuetypes.IssueTypeUpdate", "priorities.PriorityUpdate"}),
    ): UNRELATED_BODIES,
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


INCOMPLETE = """
import importlib, pkgutil
from pydantic import BaseModel
import ycli.yandex

found = set()
for info in pkgutil.walk_packages(ycli.yandex.__path__, "ycli.yandex."):
    for name, value in vars(importlib.import_module(info.name)).items():
        defined_here = isinstance(value, type) and value.__module__ == info.name
        if defined_here and issubclass(value, BaseModel) and not value.__pydantic_complete__:
            found.add(f"{info.name}.{name}")
print(*sorted(found))
"""


def test_every_model_is_complete_once_its_module_is_imported():
    """A model left waiting for a name defined below it cannot be serialized by an MCP tool.

    Asked in an interpreter of its own: pydantic finishes such a model the first time it
    validates with it, so any test that ran before would hide the answer.
    """
    proc = subprocess.run(
        [sys.executable, "-c", INCOMPLETE], capture_output=True, text=True, cwd=REPOSITORY
    )
    assert proc.returncode == 0, proc.stderr
    assert not proc.stdout.split(), f"not complete after import: {proc.stdout.split()}"
