"""One definition per shape: two models of a service with the same schema need a stated reason.

The same model used to be written many times under different names (#203). A model's shape
is its JSON schema without prose (titles, descriptions, examples); classes of one service that
share a shape must be one class, or a group in ``SAME_SHAPE`` with the reason they are not.
"""

from __future__ import annotations

import ast
import importlib
import json
import pkgutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ycli.yandex.registry import SERVICES

ROOT = Path(__file__).resolve().parent.parent
PROSE = frozenset({"title", "description", "examples"})

# Groups of same-shaped models that stay separate classes, each with its reason. A group is
# named by its members, ``<resource>.<Class>``, and belongs to one service.
AWAITING = "awaiting the owner's decision (#203)"
TWO_OPERATIONS = "two operations of the API, whose bodies may diverge"
FOLLOW_UP = "one concept in two places, merged in the follow-up to this change (#203)"
SAME_SHAPE: dict[tuple[str, frozenset[str]], str] = {
    ("forms", frozenset({"access.AccessGrant", "access.AccessRevoke"})): AWAITING,
    ("forms", frozenset({"answers.ExportResult", "operations.OperationResult"})): AWAITING,
    (
        "forms",
        frozenset({"conditions.ConditionCreate", "conditions.ConditionUpdate"}),
    ): TWO_OPERATIONS,
    ("forms", frozenset({"hooks.HookCreate", "hooks.HookUpdate"})): TWO_OPERATIONS,
    ("forms", frozenset({"keysets.KeysetCreate", "keysets.KeysetUpdate"})): TWO_OPERATIONS,
    (
        "forms",
        frozenset({"questions.QuestionDataSource", "questions.QuestionHintSource"}),
    ): AWAITING,
    (
        "forms",
        frozenset({"subscriptions.AttachmentQuestions", "subscriptions.VariableQuestions"}),
    ): AWAITING,
    ("forms", frozenset({"surveys.SurveyCreate", "surveys.SurveyUpdate"})): TWO_OPERATIONS,
    (
        "forms",
        frozenset({"variables.VariableCategory", "variables.VariableRenderer"}),
    ): "different things that happen to have a name and a type",
    ("tracker", frozenset({"autoactions.AutoactionAction", "triggers.TriggerAction"})): FOLLOW_UP,
    ("tracker", frozenset({"checklists.ChecklistDeadline", "entities.Deadline"})): FOLLOW_UP,
    (
        "tracker",
        frozenset({"checklists.ChecklistDeadlineInput", "entities.DeadlineInput"}),
    ): FOLLOW_UP,
    (
        "tracker",
        frozenset({"dashboards.DashboardOwner", "sprints.SprintBoardInput"}),
    ): "different things that happen to hold only an id",
    (
        "tracker",
        frozenset({"fields.FieldCategoryUpdate", "resolutions.ResolutionUpdate"}),
    ): "bodies of unrelated operations that happen to match",
    ("tracker", frozenset({"fields.FieldCreate", "localfields.LocalFieldCreate"})): FOLLOW_UP,
    ("tracker", frozenset({"fields.FieldSchema", "localfields.LocalFieldSchema"})): FOLLOW_UP,
    (
        "tracker",
        frozenset({"issuetypes.IssueType", "priorities.Priority"}),
    ): "different concepts that share a form",
    (
        "tracker",
        frozenset({"issuetypes.IssueTypeCreate", "resolutions.ResolutionCreate"}),
    ): AWAITING,
    ("tracker", frozenset({"issuetypes.IssueTypeUpdate", "priorities.PriorityUpdate"})): AWAITING,
    (
        "tracker",
        frozenset({"links.LinkObject", "transitions.StatusRef"}),
    ): "different things that happen to have a key and a display name",
    ("tracker", frozenset({"linktypes.LinkType", "remotelinks.RemoteLinkType"})): FOLLOW_UP,
    (
        "tracker",
        frozenset({"workflows.WorkflowActionInput", "workflows.WorkflowActionUpdate"}),
    ): TWO_OPERATIONS,
    ("wiki", frozenset({"access.AccessUser", "uploadsessions.UploadSessionUser"})): AWAITING,
    (
        "wiki",
        frozenset({"pages.BacklinksResponse", "pages.DescendantsResponse"}),
    ): "cursor envelopes, to become one generic page (#203)",
}

# Names merged into a shared class, by the module that used to define them. They stay
# importable from there until 0.38; nothing in this repository may import them from there.
DEPRECATED: dict[tuple[str, str], str] = {
    (
        "ycli.yandex.tracker.attachments.models",
        "AttachmentMetadata",
    ): "ycli.yandex.tracker.models.AttachmentMetadata",
    (
        "ycli.yandex.tracker.autoactions.models",
        "AutoactionQueueRef",
    ): "ycli.yandex.tracker.models.KeyedReference",
    ("ycli.yandex.tracker.boards.models", "BoardColumn"): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.columns.models",
        "ColumnStatus",
    ): "ycli.yandex.tracker.models.KeyedReference",
    (
        "ycli.yandex.tracker.comments.models",
        "CommentAttachment",
    ): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.comments.models",
        "CommentCreate",
    ): "ycli.yandex.tracker.models.CommentCreate",
    (
        "ycli.yandex.tracker.components.models",
        "ComponentLead",
    ): "ycli.yandex.tracker.models.UserReference",
    (
        "ycli.yandex.tracker.components.models",
        "ComponentQueue",
    ): "ycli.yandex.tracker.models.KeyedReference",
    ("ycli.yandex.tracker.entities.models", "AclGroup"): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.entities.models",
        "AttachmentMetadata",
    ): "ycli.yandex.tracker.models.AttachmentMetadata",
    (
        "ycli.yandex.tracker.entities.models",
        "CommentCreate",
    ): "ycli.yandex.tracker.models.CommentCreate",
    ("ycli.yandex.tracker.entities.models", "EntityRef"): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.entities.models",
        "IssueQueueRef",
    ): "ycli.yandex.tracker.models.KeyedReference",
    ("ycli.yandex.tracker.entities.models", "UserRef"): "ycli.yandex.tracker.models.UserReference",
    ("ycli.yandex.tracker.fields.models", "FieldCategory"): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.fields.models",
        "LocalizedName",
    ): "ycli.yandex.tracker.models.LocalizedName",
    (
        "ycli.yandex.tracker.fields.models",
        "OptionsProviderInput",
    ): "ycli.yandex.tracker.models.OptionsProviderInput",
    (
        "ycli.yandex.tracker.filters.models",
        "FilterFieldRef",
    ): "ycli.yandex.tracker.models.Reference",
    ("ycli.yandex.tracker.filters.models", "FilterGroup"): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.filters.models",
        "FilterUser",
    ): "ycli.yandex.tracker.models.UserReference",
    (
        "ycli.yandex.tracker.issuetypes.models",
        "LocalizedName",
    ): "ycli.yandex.tracker.models.LocalizedName",
    (
        "ycli.yandex.tracker.localfields.models",
        "FieldCategory",
    ): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.localfields.models",
        "FieldQueueRef",
    ): "ycli.yandex.tracker.models.KeyedReference",
    (
        "ycli.yandex.tracker.localfields.models",
        "LocalizedName",
    ): "ycli.yandex.tracker.models.LocalizedName",
    (
        "ycli.yandex.tracker.localfields.models",
        "OptionsProviderInput",
    ): "ycli.yandex.tracker.models.OptionsProviderInput",
    ("ycli.yandex.tracker.macros.models", "MacroField"): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.macros.models",
        "MacroQueueRef",
    ): "ycli.yandex.tracker.models.KeyedReference",
    (
        "ycli.yandex.tracker.priorities.models",
        "LocalizedName",
    ): "ycli.yandex.tracker.models.LocalizedName",
    ("ycli.yandex.tracker.queues.models", "AccessRef"): "ycli.yandex.tracker.models.Reference",
    ("ycli.yandex.tracker.queues.models", "QueueRef"): "ycli.yandex.tracker.models.KeyedReference",
    ("ycli.yandex.tracker.queues.models", "QueueUser"): "ycli.yandex.tracker.models.UserReference",
    ("ycli.yandex.tracker.queues.models", "QueueVersion"): "ycli.yandex.tracker.models.Reference",
    ("ycli.yandex.tracker.queues.models", "WorkflowRef"): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.resolutions.models",
        "LocalizedName",
    ): "ycli.yandex.tracker.models.LocalizedName",
    (
        "ycli.yandex.tracker.sprints.models",
        "SprintBoardRef",
    ): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.statuses.models",
        "LocalizedName",
    ): "ycli.yandex.tracker.models.LocalizedName",
    (
        "ycli.yandex.tracker.triggers.models",
        "TriggerQueueRef",
    ): "ycli.yandex.tracker.models.KeyedReference",
    ("ycli.yandex.tracker.users.models", "Group"): "ycli.yandex.tracker.models.Reference",
    (
        "ycli.yandex.tracker.workflows.models",
        "LocalizedText",
    ): "ycli.yandex.tracker.models.LocalizedName",
    ("ycli.yandex.wiki.access.models", "UserIdentity"): "ycli.yandex.wiki.models.UserIdentity",
    (
        "ycli.yandex.wiki.grids.models",
        "GridCloneOperation",
    ): "ycli.yandex.wiki.models.AsyncOperation",
    (
        "ycli.yandex.wiki.grids.models",
        "OperationIdentity",
    ): "ycli.yandex.wiki.models.OperationIdentity",
    ("ycli.yandex.wiki.grids.models", "PageIdentity"): "ycli.yandex.wiki.models.PageIdentity",
    ("ycli.yandex.wiki.me.models", "Identity"): "ycli.yandex.wiki.models.UserIdentity",
    ("ycli.yandex.wiki.operations.models", "PageSchema"): "ycli.yandex.wiki.models.PageIdentity",
    (
        "ycli.yandex.wiki.pages.models",
        "PageCloneOperation",
    ): "ycli.yandex.wiki.models.AsyncOperation",
    (
        "ycli.yandex.wiki.pages.models",
        "PageCloneOperationIdentity",
    ): "ycli.yandex.wiki.models.OperationIdentity",
    (
        "ycli.yandex.wiki.pages.models",
        "PageMoveOperation",
    ): "ycli.yandex.wiki.models.AsyncOperation",
    ("ycli.yandex.wiki.recovery.models", "RecoveredPage"): "ycli.yandex.wiki.models.PageIdentity",
    (
        "ycli.yandex.wiki.uploadsessions.models",
        "UploadSessionUserIdentity",
    ): "ycli.yandex.wiki.models.UserIdentity",
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


def deprecated_imports(source: str) -> list[str]:
    """The ``from <module> import <name>`` statements in ``source`` that ``DEPRECATED`` lists.

    Example:
        >>> deprecated_imports("from ycli.yandex.tracker.users.models import Group, User")
        ['ycli.yandex.tracker.users.models.Group']
    """
    return [
        f"{node.module}.{alias.name}"
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
        if (node.module, alias.name) in DEPRECATED
    ]


def test_nothing_here_imports_a_merged_model_by_its_old_path():
    found = {
        str(path.relative_to(ROOT)): names
        for folder in ("src", "tests", "scripts", "e2e")
        for path in sorted((ROOT / folder).rglob("*.py"))
        if (names := deprecated_imports(path.read_text(encoding="utf-8")))
    }
    assert not found, f"import the shared class instead: {found}"
    assert deprecated_imports("from ycli.yandex.tracker.users.models import Group") != []


def test_every_deprecated_name_is_still_importable_and_is_the_shared_class():
    for (module, name), shared in DEPRECATED.items():
        shared_module, shared_name = shared.rsplit(".", 1)
        expected = getattr(importlib.import_module(shared_module), shared_name)
        assert getattr(importlib.import_module(module), name) is expected, (module, name)
