"""The rules of ``docs/conventions/resources.md`` that the ARCH checks do not cover."""

from __future__ import annotations

import ast
import asyncio
import importlib
import inspect
import pkgutil
import re
from pathlib import Path
from typing import Any, get_origin

from pydantic import BaseModel, Field, RootModel
from scripts import api_drift

import ycli.yandex
from tests.architecture.scanners import GENERATED, is_generated, unexplained
from tests.full_server import tools_with_output_schemas
from ycli.yandex.core.pagination import BodyCursorPagination
from ycli.yandex.models import (
    IGNORED_BY_API,
    APIModel,
    ItemList,
    RequestBody,
    WarnsOnIgnored,
    ignored_fields,
)
from ycli.yandex.registry import SERVICES

SRC = Path(__file__).resolve().parents[2] / "src"

# A pydantic model in ``ycli.yandex`` that is not an ``APIModel``, and why.
MODEL_BASE_EXCEPTIONS = {
    "ycli.yandex.core.auth._IAMToken": "the core knows no service model; parses the IAM answer",
}


def _models() -> list[type[BaseModel]]:
    """Every pydantic model class written by hand under ``ycli.yandex`` (``GENERATED`` apart)."""
    for module in pkgutil.walk_packages(ycli.yandex.__path__, "ycli.yandex."):
        importlib.import_module(module.name)

    def subclasses(cls: type[BaseModel]) -> list[type[BaseModel]]:
        return [found for sub in cls.__subclasses__() for found in (sub, *subclasses(sub))]

    generated = tuple(".".join(("ycli", *home.parts, "")) for home in GENERATED)
    return [
        cls
        for cls in subclasses(BaseModel)
        if cls.__module__.startswith("ycli.yandex.")
        and not cls.__module__.startswith(generated)
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


def _undescribed_fields(models: list[type[BaseModel]]) -> list[str]:
    """``module.Class.field`` for each field a model declares without a description."""
    return sorted(
        f"{_name(cls)}.{name}"
        for cls in models
        if not issubclass(cls, RootModel)
        for name, field in cls.model_fields.items()
        if name in cls.__annotations__ and not (field.description or "").strip()
    )


def test_every_model_field_has_a_description():
    """Section 6, ``models.py``: the description is the text of the MCP schema and the docs."""
    assert _undescribed_fields(_models()) == []


def test_the_field_description_check_bites():
    class Parent(APIModel):
        described: int = Field(default=0, description="Fine.")

    class Child(Parent):
        bare: int = 0
        blank: int = Field(default=0, description=" ")

    assert [name.rsplit(".", 1)[-1] for name in _undescribed_fields([Parent, Child])] == [
        "bare",
        "blank",
    ]


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


def _generated_classes() -> frozenset[str]:
    """The names of the classes of the generated layer (``GENERATED``)."""
    return frozenset(
        name
        for home in GENERATED
        for module in sorted((SRC / "ycli" / home).glob("*.py"))
        for name in re.findall(r"^class (\w+)", module.read_text(encoding="utf-8"), re.MULTILINE)
    )


def _undiscriminated_unions(
    schema: Any, path: str = "$", *, generated: frozenset[str] = frozenset()
) -> list[str]:
    """Paths of ``anyOf`` / ``oneOf`` with two or more object branches and no discriminator.

    A union whose every object branch is a class named in ``generated`` is not one of them:
    the generated layer reads a union softly, with a spare open member and no discriminator
    (docs/conventions/resources.md, "Generated models").
    """
    found: list[str] = []
    if isinstance(schema, dict):
        for key in ("anyOf", "oneOf"):
            objects = [
                branch
                for branch in schema.get(key, [])
                if "$ref" in branch or branch.get("type") == "object"
            ]
            layer = all(
                branch.get("$ref", "").rsplit("/", 1)[-1] in generated for branch in objects
            )
            if len(objects) >= 2 and "discriminator" not in schema and not layer:
                found.append(path)
        for key, value in schema.items():
            found += _undiscriminated_unions(value, f"{path}.{key}", generated=generated)
    elif isinstance(schema, list):
        for index, value in enumerate(schema):
            found += _undiscriminated_unions(value, f"{path}[{index}]", generated=generated)
    return found


def test_every_union_a_tool_returns_is_discriminated():
    """Section 5: fastmcp rebuilds an undiscriminated union as its first matching member."""
    generated = _generated_classes()
    offenders = {
        tool.name: paths
        for tool in asyncio.run(tools_with_output_schemas())
        if (paths := _undiscriminated_unions(tool.output_schema, generated=generated))
    }
    assert offenders == {}


def test_the_union_check_bites():
    members = [{"$ref": "#/$defs/A"}, {"$ref": "#/$defs/B"}]
    assert _undiscriminated_unions({"properties": {"item": {"anyOf": members}}}) == [
        "$.properties.item"
    ]
    assert _undiscriminated_unions({"oneOf": members, "discriminator": {"propertyName": "t"}}) == []
    assert _undiscriminated_unions({"anyOf": [{"$ref": "#/$defs/A"}, {"type": "null"}]}) == []
    # Both sides of the generated layer: a union of its classes alone is left to it, and one
    # hand-written member brings the union back under the rule.
    layer = frozenset({"A", "B"})
    assert _undiscriminated_unions({"anyOf": members}, generated=layer) == []
    assert _undiscriminated_unions({"anyOf": members}, generated=frozenset({"A"})) == ["$"]
    assert {"ContentPage", "OtherKindByEntity"} & _generated_classes() == {"OtherKindByEntity"}


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
    "ycli.yandex.forms.subscriptions.models.HTTPSubscription",
    "ycli.yandex.forms.subscriptions.models.JSONRPCSubscription",
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


def _is_generated(model: type[BaseModel]) -> bool:
    """Whether ``model`` is a class of a generated module (``GENERATED``)."""
    homes = tuple("ycli." + ".".join(home.parts) + "." for home in GENERATED)
    return model.__module__.startswith(homes)


def _model_roles() -> tuple[set[type[BaseModel]], set[type[BaseModel]]]:
    """The models that request bodies are built from, and the ones replies are read into.

    Of a generated model only the one a body or a reply is itself counts: inside it the
    generated layer keeps its own rule (the envelope of a request is closed, the rest is
    read as it comes; docs/conventions/resources.md, "Generated models").
    """

    def collect(annotation: Any, found: set[type[BaseModel]], *, inside: bool = False) -> None:
        for model in api_drift._models(annotation):
            if inside and _is_generated(model):
                continue
            if model not in found:
                found.add(model)
                model.model_rebuild()  # a forward reference is a name until the model is built
                for field in model.model_fields.values():
                    collect(field.annotation, found, inside=True)

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
    """Body-only models that would send a key they do not declare.

    A generated model is not counted: of the generated layer only the envelope of a request
    is closed, and the generator's own tests hold that.
    """
    return sorted(
        _name(model)
        for model in bodies - replies
        if not issubclass(model, RequestBody) and not _is_generated(model)
    )


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


def _literal_values(node: ast.AST) -> frozenset[str] | None:
    """The values of a ``Literal[...]`` with two or more of them, else ``None``."""
    if not (isinstance(node, ast.Subscript) and ast.unparse(node.value) == "Literal"):
        return None
    items = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
    values = frozenset(str(item.value) for item in items if isinstance(item, ast.Constant))
    return values if len(values) > 1 else None


def _value_sets(sources: dict[str, str]) -> dict[frozenset[str], list[str]]:
    """Every closed value set in ``sources`` (path -> text) with the places that define it."""
    found: dict[frozenset[str], list[str]] = {}
    for path, source in sources.items():
        for node in ast.walk(ast.parse(source)):
            values = _literal_values(node)
            if isinstance(node, ast.ClassDef) and any(
                ast.unparse(base).endswith("StrEnum") for base in node.bases
            ):
                members = [item for item in node.body if isinstance(item, ast.Assign)]
                values = frozenset(
                    str(member.value.value)
                    for member in members
                    if isinstance(member.value, ast.Constant)
                )
            if values:
                found.setdefault(values, []).append(f"{path}:{getattr(node, 'lineno', 0)}")
    return found


def _sources() -> dict[str, str]:
    """Every hand-written module by its path under ``src/ycli``: ``{"cli/app.py": "..."}``."""
    root = Path(ycli.__file__).parent
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in root.rglob("*.py")
        if not is_generated(path.relative_to(root))
    }


def test_a_closed_value_set_is_defined_once():
    """Section 1, "A field with a set of values" (#161): one definition per set, used by name."""
    sources = _sources()
    twice = {
        ", ".join(sorted(values)): places
        for values, places in _value_sets(sources).items()
        if len(places) > 1
    }
    assert twice == {}


def test_the_value_set_check_bites():
    sources = {
        "a/models.py": (
            'Order = Literal["asc", "desc"]\nclass Kind(StrEnum):\n    A = "a"\n    B = "b"\n'
        ),
        "a/mcp.py": 'def list_(order: Literal["desc", "asc"] | None, one: Literal["x"]): ...\n',
    }
    sets = _value_sets(sources)
    assert sets[frozenset({"asc", "desc"})] == ["a/models.py:1", "a/mcp.py:1"]
    assert sets[frozenset({"a", "b"})] == ["a/models.py:2"]
    assert frozenset({"x"}) not in sets


def _options_naming_a_set_by_hand(
    sources: dict[str, str], sets: dict[frozenset[str], list[str]]
) -> list[str]:
    """Plain ``str`` options and tool parameters whose text lists every value of a defined set.

    One that does so on purpose has ``# violation(value-set): <reason>`` on the line above the
    parameter; such a marker above anything else is reported too.
    """
    offenders = []
    for path, source in sources.items():
        found = []
        if not path.endswith(("cli.py", "mcp.py")) and "/cli/" not in path:
            continue
        for function in ast.walk(ast.parse(source)):
            if not isinstance(function, ast.FunctionDef):
                continue
            for argument in [*function.args.args, *function.args.kwonlyargs]:
                if argument.annotation is None:
                    continue
                declared = ast.unparse(argument.annotation)
                # A parameter typed with the set, or built from it, may explain its values.
                plain = declared.removeprefix("Annotated[").split(",")[0].strip() in {
                    "str",
                    "str | None",
                    "list[str]",
                    "list[str] | None",
                }
                if not plain or "values_option(" in declared:
                    continue
                texts = [
                    item.value
                    for item in ast.walk(argument.annotation)
                    if isinstance(item, ast.Constant) and isinstance(item.value, str)
                ]
                words = set(re.findall(r"[\w%]+", " ".join(texts)))
                if any(values <= words for values in sets):
                    found.append((argument.lineno, f"{path}:{function.name}.{argument.arg}"))
        offenders += unexplained(found, source, "value-set", path)
    return offenders


def test_an_option_takes_the_values_it_names_from_the_definition_of_the_set():
    """Section 1 (#161, #278): ``values_option`` and the tool schema show a set's values.

    A help text that lists them by hand goes stale when the set changes.
    """
    sources = _sources()
    found = _options_naming_a_set_by_hand(sources, _value_sets(sources))
    assert found == []


def test_the_hand_written_values_check_bites():
    sources = {
        "a/models.py": 'Order = Literal["asc", "desc"] | str\n',
        "a/cli.py": (
            "def list_(\n"
            '    by_hand: Annotated[str | None, typer.Option(help="asc or desc.")] = None,\n'
            '    taken: Annotated[str | None, values_option(Order, help="Order.")] = None,\n'
            '    other: Annotated[str | None, typer.Option(help="Ascending names.")] = None,\n'
            "): ...\n"
        ),
    }
    found = _options_naming_a_set_by_hand(sources, _value_sets(sources))
    assert found == ["a/cli.py:list_.by_hand"]
    # Both sides: a marked option passes; the marker above an option that names no set does not.
    marker = "    # violation(value-set): a JSON value; its help shows the shape\n"
    marked = dict(sources)
    marked["a/cli.py"] = sources["a/cli.py"].replace("    by_hand:", marker + "    by_hand:")
    assert _options_naming_a_set_by_hand(marked, _value_sets(marked)) == []
    stale = dict(sources)
    stale["a/cli.py"] = sources["a/cli.py"].replace("    other:", marker + "    other:")
    assert _options_naming_a_set_by_hand(stale, _value_sets(stale)) == [
        "a/cli.py:list_.by_hand",
        "a/cli.py:4: violation(value-set) marks nothing the check finds",
    ]


def _annotated_aliases(sources: dict[str, str]) -> dict[str, list[str]]:
    """Each module-level ``X = Annotated[...]`` by its text: ``{text: ["a/cli.py:X", ...]}``."""
    found: dict[str, list[str]] = {}
    for path, source in sources.items():
        for node in ast.parse(source).body:
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Subscript)
                and ast.unparse(node.value.value) == "Annotated"
            ):
                found.setdefault(ast.unparse(node.value), []).append(f"{path}:{node.targets[0].id}")
    return found


def test_an_annotated_alias_is_defined_once():
    """Section 7, "Names" (#160): the same alias text lives in one module and is imported."""
    twice = {
        text: places for text, places in _annotated_aliases(_sources()).items() if len(places) > 1
    }
    assert twice == {}


def test_the_alias_check_bites():
    sources = {
        "a/cli.py": 'IDArg = Annotated[int, typer.Argument(help="Id.")]\n',
        "b/cli.py": (
            "IDArg = Annotated[\n    int,\n    typer.Argument(help='Id.'),\n]\n"
            'KeyArg = Annotated[str, typer.Argument(help="Key.")]\n'
        ),
    }
    aliases = _annotated_aliases(sources)
    assert [places for places in aliases.values() if len(places) > 1] == [
        ["a/cli.py:IDArg", "b/cli.py:IDArg"]
    ]


# Written in capitals inside a CapWords name: `QueueID`, never `QueueId` (PEP 8).
ACRONYMS = frozenset(
    {
        *("ID", "UID", "URL", "API", "HTTP", "JSON", "RPC", "YAML", "ACL", "HTML"),
        *("CSV", "XLSX", "XML", "TQL", "MCP", "CLI", "SDK", "IAM", "JWT", "YFM"),
    }
)
# A name with a spelling of its own, and where that spelling comes from.
OWN_SPELLINGS = {"OAuth": "the protocol's own name (RFC 6749)"}
_NAME_WORD = re.compile(r"[A-Z][a-z0-9]+|[A-Z]+(?![a-z])")


def _misspelled_acronyms(sources: dict[str, str]) -> list[str]:
    """CapWords names that lower an acronym (``PageId``) or respell ``OWN_SPELLINGS``."""
    offenders = []
    for path, source in sources.items():
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ClassDef):
                names = [node.name]
            elif isinstance(node, ast.Assign):
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            elif isinstance(node, ast.AnnAssign | ast.TypeAlias):
                target = node.target if isinstance(node, ast.AnnAssign) else node.name
                names = [target.id] if isinstance(target, ast.Name) else []
            else:
                continue
            for name in names:
                if not re.fullmatch(r"_?[A-Z][A-Za-z0-9]*", name) or name.isupper():
                    continue
                lowered = any(
                    word != word.upper() and word.upper().removesuffix("S") in ACRONYMS
                    for word in _NAME_WORD.findall(name)
                )
                respelled = any(
                    spelling.lower() in name.lower() and spelling not in name
                    for spelling in OWN_SPELLINGS
                )
                if lowered or respelled:
                    offenders.append(f"{path}:{name}")
    return offenders


def test_an_acronym_keeps_its_capitals_in_a_name():
    """Section 7, "Names" (#160): `QueueID`, `HTTPSubscription`, `OAuth`."""
    assert _misspelled_acronyms(_sources()) == []


def test_the_acronym_check_bites():
    sources = {
        "a/models.py": (
            "class PageId: ...\nclass JsonRpcCall: ...\nclass OauthClient: ...\n"
            "class PageID: ...\nclass UserIDs: ...\nclass OAuthClient: ...\nclass Idea: ...\n"
            "UserIds = Annotated[str, Field()]\nMAX_ID = 1\nitem_id: int = 1\ntype ApiKey = str\n"
        )
    }
    assert _misspelled_acronyms(sources) == [
        "a/models.py:PageId",
        "a/models.py:JsonRpcCall",
        "a/models.py:OauthClient",
        "a/models.py:UserIds",
        "a/models.py:ApiKey",
    ]


def _alias_names(sources: dict[str, str]) -> dict[str, list[str]]:
    """Each module-level ``X = Annotated[...]`` by its name: ``{"IDArg": ["a/cli.py", ...]}``."""
    found: dict[str, list[str]] = {}
    for path, source in sources.items():
        for node in ast.parse(source).body:
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Subscript)
                and ast.unparse(node.value.value) == "Annotated"
            ):
                found.setdefault(node.targets[0].id, []).append(path)
    return found


def test_an_alias_name_means_one_thing():
    """Section 7, "Names" (#301): two aliases that differ have different names."""
    twice = {name: places for name, places in _alias_names(_sources()).items() if len(places) > 1}
    assert twice == {}


def test_the_alias_name_check_bites():
    sources = {
        "a/cli.py": 'ActionOpt = Annotated[str, typer.Option(help="Access action.")]\n',
        "b/cli.py": (
            'ActionOpt = Annotated[list[str], typer.Option(help="Trigger action.")]\n'
            'KeyArg = Annotated[str, typer.Argument(help="Key.")]\n'
        ),
    }
    names = _alias_names(sources)
    assert {name: places for name, places in names.items() if len(places) > 1} == {
        "ActionOpt": ["a/cli.py", "b/cli.py"]
    }


def _rpc_arguments_off(method: Any, body: Any, pagination: Any) -> list[str]:
    """The names by which a method's arguments and the fields of its request differ.

    Of an RPC operation every argument lies in one object, so the method takes exactly the
    top-level fields of the request it sends, by their names (#371). The pager's own fields are
    not arguments, and ``limit`` is ycli's cap on a listing, not a field.
    """
    named = vars(pagination) if pagination else {}
    pager = {value for name, value in named.items() if name.endswith("_param")}
    arguments = set(inspect.signature(method).parameters) - ({"limit"} if pagination else set())
    fields = {
        name
        for name, field in (type(body).model_fields if body is not None else {}).items()
        if (field.alias or name) not in pager
    }
    return sorted(arguments ^ fields)


def test_an_rpc_method_takes_the_fields_of_its_request_as_arguments():
    """#371: the top level of an RPC request is the method's arguments, on every surface."""
    clients = {
        service.name: service.client_class()(
            oauth_token="t", organization_id="o", cloud_organization_id="c"
        )
        for service in SERVICES
    }
    offenders = {}
    seen = 0
    for found in api_drift.recorded():
        if not found.endpoint.path.startswith("rpc/"):
            continue
        seen += 1
        domain, resource, operation = found.case.operation.split(".")
        method = getattr(getattr(clients[domain], resource), operation)
        body = found.endpoint.json
        assert body is None or isinstance(body, RequestBody), found.case.operation
        if off := _rpc_arguments_off(method, body, found.pagination):
            offenders[found.case.operation] = off
    assert seen, "no RPC operation was looked at"
    assert offenders == {}


def test_the_rpc_arguments_check_bites():
    class Request(RequestBody):
        thing_id: str = Field(alias="thingId")
        title: str | None = None
        page_token: str | None = Field(default=None, alias="pageToken")

    def exact(thing_id: str, *, limit: int | None = None, title: str | None = None) -> None: ...
    def lacking(thing_id: str) -> None: ...
    def renamed(item_id: str, *, title: str | None = None) -> None: ...

    body = Request(thingId="t")
    paged = BodyCursorPagination(cursor_of=lambda response: None)
    assert _rpc_arguments_off(exact, body, paged) == []
    assert _rpc_arguments_off(lacking, body, paged) == ["title"]
    assert _rpc_arguments_off(renamed, body, paged) == ["item_id", "thing_id"]
    # Without a pager ``limit`` and ``pageToken`` are an argument and a field like any other.
    assert _rpc_arguments_off(exact, body, None) == ["limit", "page_token"]
    assert _rpc_arguments_off(lambda: None, None, None) == []
