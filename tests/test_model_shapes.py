"""One definition per shape: two models of a service with the same schema need a stated reason.

The same model used to be written many times under different names (#203). A model's shape
is its JSON schema without prose (titles, descriptions, examples); classes of one service that
share a shape must be one class, or a group in ``SAME_SHAPE`` with the reason they are not.
"""

from __future__ import annotations

import ast
import doctest
import importlib
import json
import pkgutil
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from ycli.yandex.registry import SERVICES

ROOT = Path(__file__).resolve().parent.parent
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
    (
        "wiki",
        frozenset({"pages.BacklinksResponse", "pages.DescendantsResponse"}),
    ): "cursor envelopes, to become one generic page (#203)",
}

# Names moved into a service's shared module, by the module that used to define them. They stay
# importable from there until 0.38; nothing in this repository may import them from there.
DEPRECATED: dict[tuple[str, str], str] = {
    (
        "ycli.yandex.forms.answers.models",
        "EXPORT_TERMINAL_STATUSES",
    ): "ycli.yandex.forms.models.TERMINAL_STATUSES",
    (
        "ycli.yandex.forms.operations.models",
        "TERMINAL_STATUSES",
    ): "ycli.yandex.forms.models.TERMINAL_STATUSES",
    (
        "ycli.yandex.forms.answers.models",
        "ExportResult",
    ): "ycli.yandex.forms.models.OperationResult",
    (
        "ycli.yandex.forms.operations.models",
        "OperationResult",
    ): "ycli.yandex.forms.models.OperationResult",
    (
        "ycli.yandex.tracker.autoactions.models",
        "AutoactionAction",
    ): "ycli.yandex.tracker.models.AutomationAction",
    (
        "ycli.yandex.tracker.checklists.models",
        "ChecklistDeadline",
    ): "ycli.yandex.tracker.models.Deadline",
    (
        "ycli.yandex.tracker.checklists.models",
        "ChecklistDeadlineInput",
    ): "ycli.yandex.tracker.models.DeadlineInput",
    ("ycli.yandex.tracker.entities.models", "Deadline"): "ycli.yandex.tracker.models.Deadline",
    (
        "ycli.yandex.tracker.entities.models",
        "DeadlineInput",
    ): "ycli.yandex.tracker.models.DeadlineInput",
    ("ycli.yandex.tracker.fields.models", "FieldCreate"): "ycli.yandex.tracker.models.FieldCreate",
    ("ycli.yandex.tracker.fields.models", "FieldSchema"): "ycli.yandex.tracker.models.FieldSchema",
    ("ycli.yandex.tracker.linktypes.models", "LinkType"): "ycli.yandex.tracker.models.LinkType",
    (
        "ycli.yandex.tracker.localfields.models",
        "LocalFieldCreate",
    ): "ycli.yandex.tracker.models.FieldCreate",
    (
        "ycli.yandex.tracker.localfields.models",
        "LocalFieldSchema",
    ): "ycli.yandex.tracker.models.FieldSchema",
    (
        "ycli.yandex.tracker.remotelinks.models",
        "RemoteLinkType",
    ): "ycli.yandex.tracker.models.LinkType",
    (
        "ycli.yandex.tracker.triggers.models",
        "TriggerAction",
    ): "ycli.yandex.tracker.models.AutomationAction",
    ("ycli.yandex.wiki.access.models", "AccessUser"): "ycli.yandex.wiki.models.User",
    ("ycli.yandex.wiki.uploadsessions.models", "UploadSessionUser"): "ycli.yandex.wiki.models.User",
    (
        "ycli.yandex.wiki.operations.models",
        "OperationType",
    ): "ycli.yandex.wiki.models.OperationType",
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


def deprecated_uses(source: str, module: str = "") -> list[str]:
    """The names ``DEPRECATED`` lists that ``source`` (the module ``module``) takes by old path.

    It sees ``from <module> import <name>``, absolute or relative, ``<alias>.<name>`` where the
    alias is the old module, and the same inside docstring examples, which users copy. A module
    reached some other way (``importlib``, a longer attribute chain) is not seen.

    Example:
        >>> deprecated_uses("from ycli.yandex.tracker.users.models import Group, User")
        ['ycli.yandex.tracker.users.models.Group']
        >>> deprecated_uses("from .models import Group", "ycli.yandex.tracker.users.client")
        ['ycli.yandex.tracker.users.models.Group']
    """
    tree = ast.parse(source)
    found: list[str] = []
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            package = module.split(".")[: -node.level] if node.level else []
            origin = ".".join([*package, *([node.module] if node.module else [])])
            for alias in node.names:
                if (origin, alias.name) in DEPRECATED:
                    found.append(f"{origin}.{alias.name}")
                aliases[alias.asname or alias.name] = f"{origin}.{alias.name}"
        elif isinstance(node, ast.Import):
            aliases.update({alias.asname: alias.name for alias in node.names if alias.asname})
        elif isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            examples = doctest.DocTestParser().get_examples(ast.get_docstring(node) or "")
            if examples:
                code = "".join(example.source for example in examples)
                found += deprecated_uses(code, module)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            origin = aliases.get(node.value.id, "")
            if (origin, node.attr) in DEPRECATED:
                found.append(f"{origin}.{node.attr}")
    return found


def test_nothing_here_takes_a_merged_model_by_its_old_path():
    found = {}
    for folder in ("src", "tests", "scripts", "e2e"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            relative = path.relative_to(ROOT / "src" if folder == "src" else ROOT)
            module = ".".join(relative.with_suffix("").parts)
            if names := deprecated_uses(path.read_text(encoding="utf-8"), module):
                found[str(path.relative_to(ROOT))] = names
    assert not found, f"use the shared class instead: {found}"


OLD_MODULE = "ycli.yandex.tracker.boards.models"


@pytest.mark.parametrize(
    "source",
    [
        "from ycli.yandex.tracker.boards.models import BoardColumn",
        "from .models import BoardColumn",
        "from . import models\nmodels.BoardColumn",
        "import ycli.yandex.tracker.boards.models as m\nm.BoardColumn",
        "from ycli.yandex.tracker.boards import models as m\nm.BoardColumn",
        f'def f():\n    """Doc.\n\n    >>> from {OLD_MODULE} import BoardColumn\n    """',
        "from ycli.yandex.wiki.operations.models import OperationType",
    ],
)
def test_the_old_path_check_sees_each_way_of_taking_a_name(source):
    assert deprecated_uses(source, "ycli.yandex.tracker.boards.client")


def test_the_old_path_check_leaves_the_shared_class_alone():
    assert not deprecated_uses("from ycli.yandex.tracker.models import Reference\nReference")
    # The defining module assigns the old name; that is the alias itself, not a use of it.
    assert not deprecated_uses("BoardColumn = Reference", "ycli.yandex.tracker.boards.models")


def test_every_deprecated_name_is_still_importable_and_is_the_shared_class():
    for (module, name), shared in DEPRECATED.items():
        shared_module, shared_name = shared.rsplit(".", 1)
        expected = getattr(importlib.import_module(shared_module), shared_name)
        assert getattr(importlib.import_module(module), name) is expected, (module, name)
