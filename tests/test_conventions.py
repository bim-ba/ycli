"""The rules of ``docs/conventions/resources.md`` that the ARCH checks do not cover."""

from __future__ import annotations

import asyncio
import importlib
import pkgutil
from typing import Any, get_origin

from pydantic import BaseModel, RootModel

import ycli.yandex
from tests.full_server import tools_with_output_schemas
from ycli.yandex.models import APIModel, ItemList

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
