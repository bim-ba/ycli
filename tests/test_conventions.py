"""The rules of ``docs/conventions/resources.md`` that the ARCH checks do not cover."""

from __future__ import annotations

import ast
import asyncio
import importlib
import pkgutil
from pathlib import Path
from typing import Any, get_origin

from pydantic import BaseModel, Field, RootModel
from scripts import api_drift

import ycli.yandex
from tests.full_server import tools_with_output_schemas
from ycli.yandex.models import (
    IGNORED_BY_API,
    APIModel,
    ItemList,
    RequestBody,
    WarnsOnIgnored,
    ignored_fields,
)

SRC = Path(__file__).resolve().parent.parent / "src"

# A pydantic model in ``ycli.yandex`` that is not an ``APIModel``, and why.
MODEL_BASE_EXCEPTIONS = {
    "ycli.yandex.core.auth._IAMToken": "the core knows no service model; parses the IAM answer",
}


def _models() -> list[type[BaseModel]]:
    """Every pydantic model class defined under ``ycli.yandex``."""
    for module in pkgutil.walk_packages(ycli.yandex.__path__, "ycli.yandex."):
        importlib.import_module(module.name)

    def subclasses(cls: type[BaseModel]) -> list[type[BaseModel]]:
        return [found for sub in cls.__subclasses__() for found in (sub, *subclasses(sub))]

    return [
        cls
        for cls in subclasses(BaseModel)
        if cls.__module__.startswith("ycli.yandex.")
        and not cls.__pydantic_generic_metadata__["origin"]  # ItemList[X] is ItemList
    ]


def _name(cls: type) -> str:
    return f"{cls.__module__}.{cls.__qualname__}"


def _wrong_base(models: list[type[BaseModel]]) -> list[str]:
    """Models that are neither an ``APIModel`` nor a bare-mapping ``RootModel``."""
    return sorted(
        _name(cls)
        for cls in models
        if not issubclass(cls, APIModel | RootModel) and _name(cls) not in MODEL_BASE_EXCEPTIONS
    )


def _own_list_classes(models: list[type[BaseModel]]) -> list[str]:
    """``RootModel`` list classes other than the one generic ``ItemList``."""
    return sorted(
        _name(cls)
        for cls in models
        if issubclass(cls, RootModel)
        and cls is not ItemList
        and get_origin(cls.model_fields["root"].annotation) is list
    )


def test_every_model_inherits_apimodel():
    """Section 1: a bare ``BaseModel`` would drop the lenient parse and the API's field names."""
    models = _models()
    assert _wrong_base(models) == []
    stale = set(MODEL_BASE_EXCEPTIONS) - {_name(cls) for cls in models}
    assert not stale, f"an exception names a class that no longer exists: {stale}"


def _marked_without_warning(models: list[type[BaseModel]]) -> list[str]:
    """Models with a field marked ``IGNORED_BY_API`` that would not warn when it is set."""
    return [
        f"{model.__module__}.{model.__name__}"
        for model in models
        if ignored_fields(model) and not issubclass(model, WarnsOnIgnored)
    ]


def test_a_model_with_an_ignored_field_warns_when_it_is_set():
    """A field the API ignores: only a ``WarnsOnIgnored`` body logs the warning."""
    assert _marked_without_warning(_models()) == []

    class Silent(APIModel):
        draft: bool | None = Field(default=None, description=IGNORED_BY_API + "no effect.")

    class Loud(WarnsOnIgnored):
        draft: bool | None = Field(default=None, description=IGNORED_BY_API + "no effect.")

    assert [name.rsplit(".", 1)[-1] for name in _marked_without_warning([Silent, Loud])] == [
        "Silent"
    ]


def test_no_resource_defines_a_list_class_of_its_own():
    """Section 2: a flat list is ``ItemList[X]``."""
    assert _own_list_classes(_models()) == []


def test_the_model_checks_bite():
    class Bare(BaseModel):
        value: int = 0

    class Names(RootModel[list[str]]): ...

    class Mapping(RootModel[dict[str, str]]): ...

    class Fine(APIModel):
        value: int = 0

    probes: list[type[BaseModel]] = [Bare, Names, Mapping, Fine]
    assert [name.rsplit(".", 1)[-1] for name in _wrong_base(probes)] == ["Bare"]
    assert [name.rsplit(".", 1)[-1] for name in _own_list_classes(probes)] == ["Names"]


def _undiscriminated_unions(schema: Any, path: str = "$") -> list[str]:
    """Paths of ``anyOf`` / ``oneOf`` with two or more object branches and no discriminator."""
    found: list[str] = []
    if isinstance(schema, dict):
        for key in ("anyOf", "oneOf"):
            objects = [
                branch
                for branch in schema.get(key, [])
                if "$ref" in branch or branch.get("type") == "object"
            ]
            if len(objects) >= 2 and "discriminator" not in schema:
                found.append(path)
        for key, value in schema.items():
            found += _undiscriminated_unions(value, f"{path}.{key}")
    elif isinstance(schema, list):
        for index, value in enumerate(schema):
            found += _undiscriminated_unions(value, f"{path}[{index}]")
    return found


def test_every_union_a_tool_returns_is_discriminated():
    """Section 5: fastmcp rebuilds an undiscriminated union as its first matching member."""
    offenders = {
        tool.name: paths
        for tool in asyncio.run(tools_with_output_schemas())
        if (paths := _undiscriminated_unions(tool.output_schema))
    }
    assert offenders == {}


def test_the_union_check_bites():
    members = [{"$ref": "#/$defs/A"}, {"$ref": "#/$defs/B"}]
    assert _undiscriminated_unions({"properties": {"item": {"anyOf": members}}}) == [
        "$.properties.item"
    ]
    assert _undiscriminated_unions({"oneOf": members, "discriminator": {"propertyName": "t"}}) == []
    assert _undiscriminated_unions({"anyOf": [{"$ref": "#/$defs/A"}, {"type": "null"}]}) == []


# Models that both build a request body and read a reply. A reply keeps what Yandex adds, so
# they stay open; a key they do not declare, nested in a body, reaches the API.
BODY_AND_REPLY = {
    "ycli.yandex.forms.access.models.GroupIdentity",
    "ycli.yandex.forms.images.models.Image",
    "ycli.yandex.forms.models.UserIdentity",
    "ycli.yandex.forms.questions.models.DataSourceParam",
    "ycli.yandex.forms.questions.models.QuestionDataSource",
    "ycli.yandex.forms.questions.models.QuestionHintSource",
    "ycli.yandex.forms.questions.models.QuestionMatrixRow",
    "ycli.yandex.forms.questions.models.QuestionQuizComment",
    "ycli.yandex.forms.questions.models.QuestionQuizItem",
    "ycli.yandex.forms.questions.models.QuestionValidator",
    "ycli.yandex.forms.subscriptions.models.AttachmentQuestions",
    "ycli.yandex.forms.subscriptions.models.EmailSubscription",
    "ycli.yandex.forms.subscriptions.models.FunctionSubscription",
    "ycli.yandex.forms.subscriptions.models.HttpSubscription",
    "ycli.yandex.forms.subscriptions.models.JsonRpcSubscription",
    "ycli.yandex.forms.subscriptions.models.StaticAttachment",
    "ycli.yandex.forms.subscriptions.models.SubscriptionAttachments",
    "ycli.yandex.forms.subscriptions.models.SubscriptionHeader",
    "ycli.yandex.forms.subscriptions.models.SubscriptionVariable",
    "ycli.yandex.forms.subscriptions.models.TrackerCommentSubscription",
    "ycli.yandex.forms.subscriptions.models.TrackerField",
    "ycli.yandex.forms.subscriptions.models.TrackerFieldKey",
    "ycli.yandex.forms.subscriptions.models.TrackerSubscription",
    "ycli.yandex.forms.subscriptions.models.VariableQuestions",
    "ycli.yandex.forms.subscriptions.models.WikiField",
    "ycli.yandex.forms.subscriptions.models.WikiFieldKey",
    "ycli.yandex.forms.subscriptions.models.WikiGrid",
    "ycli.yandex.forms.subscriptions.models.WikiSubscription",
    "ycli.yandex.forms.surveys.models.SurveyAutoPublication",
    "ycli.yandex.forms.surveys.models.SurveyQuiz",
    "ycli.yandex.forms.surveys.models.SurveyQuizItem",
    "ycli.yandex.forms.surveys.models.SurveyStyleImages",
    "ycli.yandex.forms.surveys.models.SurveyStyles",
    "ycli.yandex.forms.surveys.models.SurveyTexts",
    "ycli.yandex.tracker.autoactions.models.AutoactionCalendar",
    "ycli.yandex.tracker.models.AutomationAction",
    "ycli.yandex.tracker.models.LocalizedName",
    "ycli.yandex.tracker.triggers.models.TriggerCondition",
    "ycli.yandex.wiki.access.models.GroupIdentity",
    "ycli.yandex.wiki.models.PageIdentity",
    "ycli.yandex.wiki.models.UserIdentity",
}


def _model_roles() -> tuple[set[type[BaseModel]], set[type[BaseModel]]]:
    """The models that request bodies are built from, and the ones replies are read into."""

    def collect(annotation: Any, found: set[type[BaseModel]]) -> None:
        for model in api_drift._models(annotation):
            if model not in found:
                found.add(model)
                model.model_rebuild()  # a forward reference is a name until the model is built
                for field in model.model_fields.values():
                    collect(field.annotation, found)

    bodies: set[type[BaseModel]] = set()
    replies: set[type[BaseModel]] = set()
    for recorded in api_drift.recorded():
        collect(recorded.endpoint.response_type, replies)
        collect(api_drift.typed_body(recorded), bodies)
        collect(recorded.hints.get("filters"), bodies)
        if isinstance(recorded.endpoint.json, BaseModel):
            collect(type(recorded.endpoint.json), bodies)
    return bodies, replies


def _open_bodies(bodies: set[type[BaseModel]], replies: set[type[BaseModel]]) -> list[str]:
    """Body-only models that would send a key they do not declare."""
    return sorted(_name(model) for model in bodies - replies if not issubclass(model, RequestBody))


def test_a_request_body_is_closed_or_listed_with_its_reason():
    """Section 4: a body refuses an unknown key; a reply keeps it (#197).

    A model only bodies are built from inherits ``RequestBody``, or is in ``OPEN_BODIES``; a
    model that is also read from a reply is in ``BODY_AND_REPLY``. A listed model that no
    longer fits its list fails too.
    """
    bodies, replies = _model_roles()
    assert _open_bodies(bodies, replies) == sorted(api_drift.OPEN_BODIES)
    assert sorted(_name(model) for model in bodies & replies) == sorted(BODY_AND_REPLY)
    closed_replies = sorted(_name(model) for model in replies if issubclass(model, RequestBody))
    assert closed_replies == [], "a reply model that refuses unknown fields"

    class Loose(APIModel):
        name: str

    class Tight(RequestBody):
        name: str

    assert [name.rsplit(".", 1)[-1] for name in _open_bodies({Loose, Tight}, set())] == ["Loose"]


# What ``core.endpoint.dump_body`` does not run: it walks the fields itself.
SERIALIZER_HOOKS = (
    "field_serializer",
    "model_serializer",
    "computed_field",
    "PlainSerializer",
    "WrapSerializer",
    "SerializeAsAny",
)


def _serializer_hooks(source: str) -> list[str]:
    """The pydantic serializer hooks a module names."""
    names = {node.id for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Name)}
    names |= {node.attr for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Attribute)}
    return sorted(names & set(SERIALIZER_HOOKS))


def test_no_model_has_a_serializer_the_body_dump_would_skip():
    """``dump_body`` reads field values directly, so a custom serializer would be ignored."""
    offenders = {
        str(path.relative_to(SRC)): hooks
        for path in (SRC / "ycli" / "yandex").rglob("*.py")
        if (hooks := _serializer_hooks(path.read_text(encoding="utf-8")))
    }
    assert offenders == {}
    probe = 'class M(APIModel):\n    @field_serializer("at")\n    def _at(self, v): ...\n'
    assert _serializer_hooks(probe) == ["field_serializer"]
