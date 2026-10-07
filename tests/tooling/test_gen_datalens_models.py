"""The generated models of DataLens: what the script does to the specification, and its checks.

The specification is not committed, so nothing here reads it: the pipeline's own steps are
tested on a small document, and the committed files are held to be what the script last wrote.
"""

import difflib
import importlib
import json
import re
import shutil
from pathlib import Path

import pytest
from scripts import gen_datalens_models as gen

from tests.architecture.scanners import GENERATED, SRC

REF = "#/components/schemas/"


def _json(schema: dict) -> dict:
    return {"content": {"application/json": {"schema": schema}}}


SPEC = {
    "paths": {
        "/rpc/getChart": {
            "post": {
                "tags": ["Charts"],
                "requestBody": _json(
                    {
                        "type": "object",
                        "properties": {"chartId": {"type": "string"}},
                        "additionalProperties": False,
                    }
                ),
                "responses": {"200": _json({"$ref": REF + "Chart"})},
            }
        },
        "/rpc/updateChart": {
            "post": {
                "tags": ["Charts"],
                "requestBody": _json({"$ref": REF + "UpdateChartArgs"}),
                "responses": {"200": _json({"$ref": REF + "Chart"})},
            }
        },
        "/rpc/deleteDashboard": {
            "post": {
                "tags": ["Dashboards"],
                "requestBody": _json({"$ref": REF + "DeleteArgs"}),
                "responses": {"200": _json({})},
            }
        },
    },
    "components": {
        "schemas": {
            "Chart": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "mode": {"type": "string", "enum": ["save", "publish"], "default": "save"},
                    "managedBy": {"enum": ["user", "system", None]},
                    "kind": {"type": "string", "enum": ["wizard"]},
                    "config": {
                        "discriminator": {
                            "propertyName": "type",
                            "mapping": {"line": REF + "Line", "pie": REF + "Pie"},
                        },
                        "oneOf": [{"$ref": REF + "Line"}, {"$ref": REF + "Pie"}],
                    },
                    "owner": {"$ref": REF + "User", "x-python-type": "subprocess.Popen"},
                    "meta": {
                        "type": "object",
                        "customBasePath": "subprocess.Popen",
                        "properties": {
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"default": {"type": "string"}},
                                },
                            }
                        },
                    },
                },
            },
            "ChartMeta": {"type": "object", "properties": {"taken": {"type": "boolean"}}},
            "Line": {
                "type": "object",
                "properties": {"type": {"type": "string", "enum": ["line", "area"]}},
            },
            "Pie": {"type": "object", "properties": {"type": {"type": "string", "const": "pie"}}},
            "UpdateChartArgs": {
                "type": "object",
                "description": "Only the fields given are changed.",
                "properties": {
                    "chartId": {"type": "string", "minLength": 1, "maxLength": 36, "pattern": "^c"},
                    "meta": {"$ref": REF + "ChartMeta"},
                    "tags": {
                        "type": "array",
                        "maxItems": 5,
                        "items": {"type": "integer", "minimum": 0},
                    },
                },
                "additionalProperties": False,
            },
            "DeleteArgs": {
                "type": "object",
                "properties": {"dashboardId": {"type": "string"}, "by": {"$ref": REF + "User"}},
                "additionalProperties": {},
            },
            "User": {"type": "object", "properties": {"login": {"type": "string"}}},
            "Orphan": {"type": "object", "properties": {"left": {"$ref": REF + "User"}}},
        }
    },
}


def test_the_specification_is_prepared_for_ycli_rules():
    before = json.dumps(SPEC)
    prepared = gen.prepare(SPEC)
    assert json.dumps(SPEC) == before, "the document given is left as it was"
    schemas = prepared["components"]["schemas"]
    # A module per section; what two sections reach is shared; what none reaches is gone.
    assert sorted(schemas) == [
        "charts.Chart",
        "charts.ChartMeta",
        "charts.ChartMeta2",
        "charts.ChartMeta2TagsItem",
        "charts.GetChartRequest",
        "charts.Line",
        "charts.OtherKind",
        "charts.Pie",
        "charts.UpdateChartArgs",
        "dashboards.DeleteArgs",
        "shared.User",
    ]
    chart = schemas["charts.Chart"]["properties"]
    # A reply is read as it comes; only the envelope of a request is closed, unless the
    # document itself leaves that envelope open.
    assert "additionalProperties" not in schemas["charts.Chart"]
    # Closed is said as the base class, by the code generator's own key (``gen._BASE``).
    assert schemas["charts.GetChartRequest"][gen._BASE] == gen._CLOSED
    assert schemas["charts.UpdateChartArgs"][gen._BASE] == gen._CLOSED
    assert "additionalProperties" not in schemas["charts.GetChartRequest"]
    assert schemas["dashboards.DeleteArgs"]["additionalProperties"] == {}
    assert gen._BASE not in schemas["dashboards.DeleteArgs"]
    # A set of values is open, with or without `null`; a single value is a tag and stays.
    assert chart["mode"] == {
        "anyOf": [{"enum": ["save", "publish"], "type": "string"}, {"type": "string"}]
    }
    assert chart["managedBy"] == {"anyOf": [{"enum": ["user", "system", None]}, {"type": "string"}]}
    assert chart["kind"] == {"type": "string", "enum": ["wizard"]}
    # A union a reply reaches is read softly: the tag the discriminator mapped to a member
    # is written into it and required, the discriminator goes, a spare open member is added.
    assert schemas["charts.Line"] == {
        "type": "object",
        "properties": {"type": {"type": "string", "enum": ["line"]}},
        "required": ["type"],
    }
    assert schemas["charts.Pie"]["required"] == ["type"]
    assert chart["config"] == {
        "anyOf": [
            {"$ref": REF + "charts.Line"},
            {"$ref": REF + "charts.Pie"},
            {"$ref": REF + "charts.OtherKind"},
        ]
    }
    assert schemas["charts.OtherKind"] == {
        "type": "object",
        "description": "A kind the specification does not describe: kept as it came.",
    }
    # An object written in place is named from its place; a name already taken is not reused.
    assert chart["meta"] == {"$ref": REF + "charts.ChartMeta2"}
    assert schemas["charts.ChartMeta2"]["properties"]["tags"]["items"] == {
        "$ref": REF + "charts.ChartMeta2TagsItem"
    }
    assert schemas["charts.ChartMeta"]["properties"] == {"taken": {"type": "boolean"}}
    # A property may be called `default`; the keyword of that name is gone, and so is every
    # directive to the generator.
    assert schemas["charts.ChartMeta2TagsItem"]["properties"] == {"default": {"type": "string"}}
    # A limit on a value is the API's to enforce: none is copied.
    assert schemas["charts.UpdateChartArgs"]["properties"]["chartId"] == {"type": "string"}
    assert schemas["charts.UpdateChartArgs"]["properties"]["tags"] == {
        "type": "array",
        "items": {"type": "integer"},
    }
    text = json.dumps(prepared)
    assert '"default": "save"' not in text and "subprocess" not in text
    assert chart["owner"] == {"$ref": REF + "shared.User"}
    # The inline request got a name; the untyped reply stays untyped.
    operations = prepared["paths"]
    request = operations["/rpc/getChart"]["post"]["requestBody"]["content"]["application/json"]
    assert request["schema"] == {"$ref": REF + "charts.GetChartRequest"}
    reply = operations["/rpc/deleteDashboard"]["post"]["responses"]["200"]["content"]
    assert reply["application/json"]["schema"] == {}


@pytest.mark.parametrize("name", ["Chart.V2", "Chart-V2"])
def test_a_name_that_is_no_class_name_stops_the_run(name):
    """A dot would turn a section into a package, and the run would lose a module in silence."""
    odd = json.loads(json.dumps(SPEC))
    odd["components"]["schemas"][name] = {"type": "object", "properties": {}}
    odd["components"]["schemas"]["Chart"]["properties"]["next"] = {"$ref": REF + name}
    with pytest.raises(SystemExit, match="names a schema or a section"):
        gen.prepare(odd)


def test_the_small_specification_becomes_modules_that_follow_the_rules():
    """The whole pipeline on the small document: prepare, generate, finish, format."""
    modules = gen.generate(SPEC)
    assert sorted(modules) == ["__init__.py", "charts.py", "dashboards.py", "shared.py"]
    charts = modules["charts.py"]
    assert charts.startswith(gen.HEADER)
    assert "class GetChartRequest(RequestBody):" in charts
    # An envelope with a description of its own is a request body all the same.
    assert 'class UpdateChartArgs(RequestBody):\n    """Only the fields given are changed."""' in (
        charts
    )
    assert "class Chart(APIModel):" in charts and 'extra="forbid"' not in charts
    assert 'mode: Literal["save", "publish"] | str | None = None' in charts
    assert 'managed_by: Literal["user", "system"] | str | None = Field(' in charts
    assert 'kind: Literal["wizard"] | None = None' in charts
    # A union member's tag is the one its mapping gave it; it is never widened.
    assert 'type: Literal["line"]\n' in charts and 'type: Literal["pie"]\n' in charts
    assert "meta: ChartMeta2 | None = None" in charts and "class ChartMeta2TagsItem" in charts
    # The envelope the document leaves open is not closed by ycli.
    assert "class DeleteArgs(APIModel):" in modules["dashboards.py"]
    assert 'extra="allow"' in modules["dashboards.py"]
    # No default of the document, no directive to the generator, nothing but plain models.
    assert '"save"\n' not in charts and "subprocess" not in "".join(modules.values())
    assert [gen.foreign(text) for text in modules.values()] == [[], [], [], []]
    # The base class is the code generator's doing: the last step rewrites no class, so one
    # written the old way (open, with a config that forbids) is left exactly as it came.
    old_way = (
        'class GetArgs(APIModel):\n    model_config = ConfigDict(\n        extra="forbid",\n    )\n'
    )
    assert old_way in gen.finish(gen.HEADER + old_way)
    assert gen._BASE not in charts and "customBasePath" not in "".join(modules.values())
    # What was written is what the last step leaves: finishing it again changes nothing.
    assert gen._ruff(gen.finish(charts), "charts.py") == charts


@pytest.mark.parametrize(
    ("module", "found"),
    [
        ("import os\n", ["line 1: a statement that is no import and no class"]),
        ("from os import system\n", ["line 1: imports os"]),
        ("from .. import cli\n", ["line 1: imports .."]),
        ("class A(dict):\n    pass\n", ["line 1: A inherits from dict"]),
        ("class A(os.PathLike):\n    pass\n", ["line 1: A inherits from os.PathLike"]),
        (
            "class A(APIModel):\n    def run(self):\n        pass\n",
            ["line 2: A holds FunctionDef"],
        ),
        (
            "class A(APIModel):\n    x: int = __import__('os').system('true')\n",
            ["line 2: A calls __import__('os').system", "line 2: A calls __import__"],
        ),
        ("print('hello')\n", ["line 1: a statement that is no import and no class"]),
        (
            "from . import shared\nfrom .shared import User\n"
            "class A(shared.Base, User, RootModel[int]):\n    x: int = Field(1)\n",
            [],
        ),
    ],
)
def test_a_generated_module_is_nothing_but_models(module, found):
    """The modules come from a downloaded document and every test run imports them."""
    assert gen.foreign(module) == found


def test_a_generated_model_refuses_nothing_the_api_could_take():
    """ARCH-9 on the generated layer: no length, range or pattern limit, and no validator."""
    from tests.architecture.test_arch9 import _refusals

    found = [
        text
        for home in GENERATED
        for path in sorted((SRC / home).glob("*.py"))
        for _, text in _refusals(str(path.relative_to(SRC)), path.read_text(encoding="utf-8"))
    ]
    assert found == []


def test_no_generated_file_differs_from_what_the_script_wrote():
    assert gen.edited_by_hand() == []


def test_the_hand_edit_check_bites(tmp_path, monkeypatch):
    """Prove-it: a changed type, a closed reply, an added file and a removed one are reported."""
    copy = tmp_path / "schemas"
    shutil.copytree(gen.SCHEMAS, copy, ignore=shutil.ignore_patterns("__pycache__"))
    record = tmp_path / "record.sha256"
    shutil.copy(gen.MANIFEST, record)
    monkeypatch.setattr(gen, "SCHEMAS", copy)
    monkeypatch.setattr(gen, "MANIFEST", record)
    assert gen.edited_by_hand() == []
    tenants = copy / "tenants.py"
    text = tenants.read_text(encoding="utf-8")
    assert ": bool" in text and "(APIModel):\n" in text
    for edited in (
        text.replace(": bool", ": int", 1),  # a field of another type
        text.replace("(APIModel):\n", '(APIModel):\n    model_config = {"extra": "forbid"}\n', 1),
        text + "\n",  # nothing but layout
    ):
        tenants.write_text(edited, encoding="utf-8")
        assert gen.edited_by_hand() == ["tenants.py: differs from what the script wrote"]
    tenants.unlink()
    assert gen.edited_by_hand() == ["tenants.py: recorded, not in the directory"]
    tenants.write_text(text, encoding="utf-8")
    (copy / "handmade.py").write_text(gen.HEADER + "import os\n", encoding="utf-8")
    assert gen.edited_by_hand() == [
        "handmade.py: not written by the script",
        "handmade.py: line 2: a statement that is no import and no class",
    ]
    (copy / "handmade.py").unlink()
    (copy / "charts").mkdir()
    assert gen.edited_by_hand() == ["charts: a directory"]
    (copy / "charts").rmdir()
    assert gen.edited_by_hand() == []


@pytest.mark.parametrize(
    "module",
    sorted(
        ".".join(("ycli", *path.relative_to(SRC).with_suffix("").parts))
        for home in GENERATED
        for path in (SRC / home).glob("*.py")
        if path.stem != "__init__"
    ),
)
def test_every_generated_module_imports(module):
    """Pydantic builds every class at import: a union it cannot build fails here."""
    assert importlib.import_module(module)


def test_what_is_not_given_is_not_sent():
    """A generated body carries no default of the document's: only what the caller set leaves."""
    from pydantic_core import to_jsonable_python

    from ycli.yandex.datalens.schemas.workbook import CreateWorkbookArgs
    from ycli.yandex.models import WIRE

    body = CreateWorkbookArgs.model_validate({"title": "Sales", "collectionId": None})
    assert to_jsonable_python(body, context=WIRE) == {"title": "Sales"}
    with pytest.raises(ValueError, match="nmae"):
        CreateWorkbookArgs.model_validate({"title": "Sales", "nmae": "typo"})


def test_main_writes_records_and_checks(tmp_path, monkeypatch, capsys):
    """A run from a saved document writes the package and its record; both checks read them."""
    saved = tmp_path / "spec.json"
    saved.write_text(json.dumps(SPEC), encoding="utf-8")
    monkeypatch.setattr(gen, "SCHEMAS", tmp_path / "schemas")
    monkeypatch.setattr(gen, "MANIFEST", tmp_path / "record.sha256")
    assert gen.main(["--spec", str(saved)]) == 0
    assert "4 modules" in capsys.readouterr().out
    recorded = (tmp_path / "record.sha256").read_text(encoding="utf-8").splitlines()
    assert [line.split("  ")[1] for line in recorded] == [
        "__init__.py",
        "charts.py",
        "dashboards.py",
        "shared.py",
    ]
    assert gen.main(["--check"]) == 0
    assert gen.main(["--check", "--live", "--spec", str(saved)]) == 0
    charts = tmp_path / "schemas" / "charts.py"
    charts.write_text(charts.read_text(encoding="utf-8") + "X = 1\n", encoding="utf-8")
    (tmp_path / "schemas" / "gone.py").write_text(gen.HEADER, encoding="utf-8")
    assert gen.main(["--check"]) == 1
    assert "not what the script wrote: charts.py" in capsys.readouterr().err
    assert gen.main(["--check", "--live", "--spec", str(saved)]) == 1
    assert capsys.readouterr().out.splitlines() == [
        "differs from the published specification: charts.py",
        "differs from the published specification: gone.py",
    ]
    assert gen.main(["--spec", str(saved)]) == 0
    assert not (tmp_path / "schemas" / "gone.py").exists()
    assert gen.main(["--check"]) == 0


def test_a_package_from_the_generator_stops_the_run(monkeypatch):
    """A module the generator turned into a package would vanish from a flat listing."""
    real = gen.subprocess.run

    def with_a_package(command, **options):
        if "datamodel_code_generator" not in command:
            return real(command, **options)
        done = real(command, **options)
        output = command[command.index("--output") + 1]
        (gen.Path(output) / "charts").mkdir()
        return done

    monkeypatch.setattr(gen.subprocess, "run", with_a_package)
    with pytest.raises(SystemExit, match="wrote packages, not modules"):
        gen.generate(SPEC)


def test_generated_code_that_is_not_plain_models_stops_the_run(monkeypatch):
    monkeypatch.setattr(gen, "finish", lambda text: text + "import os\n")
    with pytest.raises(SystemExit, match="not plain models"):
        gen.generate(SPEC)


def _operation(request: dict, reply: dict) -> dict:
    return {
        "post": {
            "tags": ["Things"],
            "requestBody": _json(request),
            "responses": {"200": _json(reply)},
        }
    }


def test_nothing_is_required_but_a_kind_and_the_arguments_of_an_operation():
    """Both sides: an object loses what it requires, whoever reaches it; two things keep it."""
    thing = {
        "type": "object",
        "properties": {"id": {"type": "string"}, "kind": {"enum": ["thing"]}},
        "required": ["id", "kind"],
    }
    shared = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
    arguments = {
        "type": "object",
        "properties": {"id": {"type": "string"}, "owner": {"$ref": REF + "Owner"}},
        "required": ["id"],
    }
    reply = {
        "type": "object",
        "properties": {"thing": {"$ref": REF + "Thing"}, "owner": {"$ref": REF + "Owner"}},
        "required": ["thing", "owner"],
    }
    spec = {
        "paths": {"/rpc/getThing": _operation(arguments, reply)},
        "components": {"schemas": {"Thing": thing, "Owner": shared}},
    }
    schemas = gen.prepare(spec)["components"]["schemas"]
    assert schemas["things.GetThingResponse"]["required"] == []
    # One value, but no union to tell apart: as optional as the rest of a reply.
    assert schemas["things.Thing"]["required"] == []
    assert schemas["things.Owner"]["required"] == []  # read and sent back: one class
    assert schemas["things.GetThingRequest"]["required"] == ["id"]  # an argument


def test_a_reply_without_a_field_the_document_requires_is_read():
    """Measured: ``getWorkbook`` answers without ``permissions`` unless the request asks."""
    from ycli.yandex.datalens.schemas.workbook import GetWorkbookResult

    workbook = GetWorkbookResult.model_validate({"workbookId": "w1", "title": "Q1"})
    assert (workbook.workbook_id, workbook.permissions) == ("w1", None)


def test_fields_and_one_of_becomes_one_of_each_with_the_fields():
    """The members are written out and named by place, of a mapped union too.

    A part that is no object leaves the schema as it is, named by its place.
    """
    named = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
    text = {"type": "object", "properties": {"text": {"type": "string"}}}
    number = {"type": "object", "properties": {"number": {"type": "integer"}}}
    item = {"allOf": [named, {"anyOf": [text, number]}]}
    arguments = {"type": "object", "properties": {"params": {"type": "array", "items": item}}}
    mapped = {
        "allOf": [
            named,
            {
                "oneOf": [{"$ref": REF + "Kind"}],
                "discriminator": {"propertyName": "kind", "mapping": {"a": REF + "Kind"}},
            },
        ]
    }
    kind = {"type": "object", "properties": {"kind": {"enum": ["a"]}}}
    left = {"allOf": [{"type": "string"}, {"anyOf": [text, number]}]}
    reply = {"type": "object", "properties": {"mapped": mapped, "left": left}}
    spec = {
        "paths": {"/rpc/getThing": _operation(arguments, reply)},
        "components": {"schemas": {"Kind": kind}},
    }
    schemas = gen.prepare(spec)["components"]["schemas"]
    members = schemas["things.GetThingRequest"]["properties"]["params"]["items"]["anyOf"]
    assert [member["$ref"].removeprefix(REF) for member in members] == [
        "things.GetThingRequestParamsItemVariant1",
        "things.GetThingRequestParamsItemVariant2",
    ]
    assert sorted(schemas["things.GetThingRequestParamsItemVariant2"]["properties"]) == [
        "name",
        "number",
    ]
    # A union with a mapping is spread too: its member is a new object that carries the
    # tag, named by its place and not ``MappedModel`` by the generator.
    read = schemas["things.GetThingResponse"]["properties"]
    assert read["mapped"] == {
        "discriminator": {"propertyName": "kind"},
        "oneOf": [{"$ref": REF + "things.GetThingResponseMappedVariant1"}],
    }
    assert sorted(schemas["things.GetThingResponseMappedVariant1"]["properties"]) == [
        "kind",
        "name",
    ]
    assert "allOf" in schemas[read["left"]["$ref"].removeprefix(REF)]


def test_a_number_is_read_as_the_whole_number_or_the_fraction_it_is():
    """Both sides on a small document: ``number`` takes an integer too; ``integer`` is left."""
    arguments = {
        "type": "object",
        "properties": {
            "duration": {"type": "number"},
            "ratio": {"type": ["number", "null"]},
            "count": {"type": "integer"},
        },
    }
    spec = {
        "paths": {"/rpc/getThing": _operation(arguments, {"type": "object"})},
        "components": {"schemas": {}},
    }
    properties = gen.prepare(spec)["components"]["schemas"]["things.GetThingRequest"]["properties"]
    assert properties["duration"]["type"] == ["integer", "number"]
    assert properties["ratio"]["type"] == ["integer", "number", "null"]
    assert properties["count"]["type"] == "integer"


def test_a_generated_model_sends_a_number_as_it_was_given():
    """Measured: a lock of 60000 ms went out as ``60000.0``."""
    from ycli.yandex.datalens.schemas.entry_lock import CreateEntryLockArgsData
    from ycli.yandex.models import WIRE

    def sent(duration: object) -> str:
        terms = CreateEntryLockArgsData.model_validate({"duration": duration})
        return json.dumps(terms.model_dump(context=WIRE))

    assert sent(60000) == '{"duration": 60000}'
    assert sent(1.5) == '{"duration": 1.5}'


def _mapping_reply(members: list[dict]) -> dict:
    """A document whose ``getThing`` reply is a union of ``members`` with no discriminator."""
    reply = {"post": {"tags": ["Things"], "responses": {"200": _json({"anyOf": members})}}}
    return {"paths": {"/rpc/getThing": reply}, "components": {"schemas": {}}}


def _text(description: str = "") -> dict:
    return {"type": "string", **({"description": description} if description else {})}


def test_a_reply_union_nothing_tells_apart_is_read_as_one_object():
    """Three sides: agreeing members merge; a name of two types keeps the union; tags open."""
    granted = {"type": "object", "properties": {"permissions": {"type": "object"}}}
    missing = {"type": "object", "properties": {"error": {"enum": ["NOT_FOUND"]}}}
    merged = gen.prepare(_mapping_reply([granted, missing]))["components"]["schemas"]
    assert set(merged["things.GetThingResponse"]["properties"]) == {"permissions", "error"}
    assert "anyOf" not in merged["things.GetThingResponse"]

    locked = {
        "type": "object",
        "properties": {"isLocked": {"const": True}, "id": _text("Of the locked entry.")},
    }
    plain = {
        "type": "object",
        "properties": {"isLocked": {"type": "boolean"}, "id": _text("Of the entry.")},
    }
    one = gen.prepare(_mapping_reply([locked, plain]))["components"]["schemas"]
    fields = one["things.GetThingResponse"]["properties"]
    # A one-value field is of its type, descriptions are not compared, the first one is kept.
    assert fields["isLocked"] == {"type": "boolean"}
    assert fields["id"] == _text("Of the locked entry.")

    auto = {"type": "object", "properties": {"scale": {"enum": ["auto"]}}}
    fixed = {"type": "object", "properties": {"scale": {"enum": ["fixed"]}}}
    tagged = gen.prepare(_mapping_reply([auto, fixed]))["components"]["schemas"]
    # The values the members were told apart by: a set of them, open like any other.
    assert tagged["things.GetThingResponse"]["properties"]["scale"] == {
        "anyOf": [{"enum": ["auto", "fixed"], "type": "string"}, {"type": "string"}]
    }

    texts = {"type": "object", "properties": {"value": {"type": "string"}}}
    numbers = {"type": "object", "properties": {"value": {"type": "object", "properties": {}}}}
    kept = gen.prepare(_mapping_reply([texts, numbers]))["components"]["schemas"]
    assert "anyOf" in kept["things.GetThingResponse"]  # one name, two types: still a union


def test_a_union_a_request_reaches_is_not_merged():
    """The other side of the rule: merged, a request could carry the fields of two members."""
    either = {
        "anyOf": [
            {"type": "object", "properties": {"auto": {"type": "boolean"}}},
            {"type": "object", "properties": {"fixed": {"type": "boolean"}}},
        ]
    }
    arguments = {"type": "object", "properties": {"scale": either}}
    spec = {
        "paths": {"/rpc/setThing": _operation(arguments, {"type": "object"})},
        "components": {"schemas": {}},
    }
    schemas = gen.prepare(spec)["components"]["schemas"]
    assert "anyOf" in schemas["things.SetThingRequest"]["properties"]["scale"]


def test_the_measured_permission_replies_are_read():
    """Measured: a found id answers its permissions, a missing one ``{"error": "NOT_FOUND"}``."""
    from ycli.yandex.datalens.schemas.entries import GetEntriesPermissionsResult
    from ycli.yandex.datalens.schemas.permissions import GetPermissionsBulkResult

    rights = {"execute": True, "read": True, "edit": False, "admin": False}
    mixed = {"ent1": {"permissions": rights}, "ent2": {"error": "NOT_FOUND"}}
    entries = GetEntriesPermissionsResult.model_validate(mixed)
    assert entries.model_dump(exclude_none=True)["ent1"] == {"permissions": rights}
    assert entries.root["ent2"].error == "NOT_FOUND"
    bulk = GetPermissionsBulkResult.model_validate(
        {"entries": {"e": {"error": "NOT_FOUND"}}, "workbooks": {"w": {"permissions": {}}}}
    )
    assert bulk.model_dump(exclude_none=True)["entries"] == {"e": {"error": "NOT_FOUND"}}
    assert bulk.model_dump(exclude_none=True)["workbooks"] == {"w": {"permissions": {}}}


def _kind(value: str, tag: str = "kind") -> dict:
    """An object of the kind ``value``: its tag has that one value, its ``size`` a type of its own.

    Members that agreed on every field would be one object (``_merge_agreeing_replies``).
    """
    size = {"type": "integer"} if value == "a" else {"type": "string"}
    return {"type": "object", "properties": {tag: {"const": value}, "size": size}}


def _kinds_document(reply: dict, request: dict | None = None, shared: dict | None = None) -> dict:
    """A document whose ``getThing`` answers ``reply`` and takes ``request``."""
    taken = {"type": "object", "properties": {"filter": request or {"type": "string"}}}
    given = {"type": "object", "properties": {"item": reply}}
    return {
        "paths": {"/rpc/getThing": _operation(taken, given)},
        "components": {"schemas": shared or {}},
    }


def test_a_union_of_kinds_gets_a_spare_member_in_a_reply_and_in_a_request():
    """A kind the document does not know is read (#391) and is sent (#444)."""
    reply = {"oneOf": [_kind("a"), _kind("b")]}
    request = {"oneOf": [_kind("a"), _kind("b")]}
    schemas = gen.prepare(_kinds_document(reply, request))["components"]["schemas"]
    read = schemas["things.GetThingResponse"]["properties"]["item"]["anyOf"]
    assert len(read) == 3 and read[-1] == {"$ref": REF + "things.OtherKind"}
    # The spare class is empty: it declares no field, not even the tag, and keeps every key.
    assert schemas["things.OtherKind"] == {
        "type": "object",
        "description": "A kind the specification does not describe: kept as it came.",
    }
    sent = schemas["things.GetThingRequest"]["properties"]["filter"]["anyOf"]
    assert len(sent) == 3 and sent[-1] == {"$ref": REF + "things.OtherKind"}


def test_a_request_union_that_nothing_tells_apart_is_left_as_it_is():
    """Both sides: with no kind to be unknown, a spare member would let every object fit."""
    plain = {"type": "object", "properties": {"size": {"type": "boolean"}}}
    other = {"type": "object", "properties": {"size": {"type": "string"}}}
    untold = {"anyOf": [plain, other]}
    schemas = gen.prepare(_kinds_document({"type": "string"}, untold))["components"]["schemas"]
    sent = schemas["things.GetThingRequest"]["properties"]["filter"]["anyOf"]
    assert len(sent) == 2 and not [name for name in schemas if "OtherKind" in name]
    # The same union in a reply is read softly, as before.
    read = gen.prepare(_kinds_document(untold))["components"]["schemas"]
    assert "things.OtherKind" in read


def test_a_union_a_request_and_a_reply_share_is_read_softly_both_ways():
    """An object read, changed and sent back holds the kind it came with."""
    shared = {"Item": {"oneOf": [_kind("a"), _kind("b")]}}
    document = _kinds_document({"$ref": REF + "Item"}, {"$ref": REF + "Item"}, shared)
    schemas = gen.prepare(document)["components"]["schemas"]
    assert schemas["things.Item"]["anyOf"][-1] == {"$ref": REF + "things.OtherKind"}


def test_every_union_of_kinds_falls_back_to_the_one_spare_class():
    """Whatever tells the members apart, or nothing at all: one empty class for all."""
    plain = {"type": "object", "properties": {"size": {"type": "boolean"}}}
    snake = {"oneOf": [_kind("a", "source_type"), _kind("b", "source_type")]}
    for reply in ({"anyOf": [plain, _kind("a")]}, snake):
        schemas = gen.prepare(_kinds_document(reply))["components"]["schemas"]
        assert [name for name in schemas if "OtherKind" in name] == ["things.OtherKind"]
    # A value that is no object, or one object alone, is no union of kinds: left as it is.
    alone = gen.prepare(_kinds_document({"anyOf": [_kind("a"), {"type": "string"}]}))
    assert not [name for name in alone["components"]["schemas"] if "OtherKind" in name]


def test_a_name_of_the_document_that_the_spare_member_needs_stops_the_run():
    taken = {"OtherKind": {"type": "object", "properties": {"x": {"type": "string"}}}}
    reply = {"oneOf": [_kind("a"), _kind("b")]}
    with pytest.raises(SystemExit, match="'OtherKind' already"):
        gen.prepare(_kinds_document(reply, shared=taken))


def test_the_measured_kinds_the_document_does_not_know_are_read():
    """Measured: a dataset's source of the kind ``CH_FROZEN_SOURCE``, which no list names."""
    from ycli.yandex.datalens.schemas.collection import GetStructureItemsResult
    from ycli.yandex.datalens.schemas.dataset import DataSourceStrict

    frozen = {"id": "s1", "source_type": "CH_FROZEN_SOURCE", "parameters": {"db": "x"}}
    read = DataSourceStrict.model_validate(frozen).root
    assert type(read).__name__ == "OtherKind"
    assert read.model_dump()["source_type"] == "CH_FROZEN_SOURCE"
    assert read.model_dump(exclude_none=True) == frozen  # sent back as it came
    # A kind the document knows is read as its own class...
    known = DataSourceStrict.model_validate({**frozen, "source_type": "CH_TABLE"}).root
    assert type(known).__name__ == "CHTABLE"
    # ...unless a field of it comes of another type than the document says: read all the same.
    odd = DataSourceStrict.model_validate({"source_type": "CH_TABLE", "valid": {"no": 1}}).root
    assert type(odd).__name__ == "OtherKind"
    # The items of a collection: a kind added tomorrow does not fail the page.
    page = GetStructureItemsResult.model_validate(
        {"items": [{"entity": "workbook", "workbookId": "w1"}, {"entity": "folder", "id": "f1"}]}
    )
    assert [type(item).__name__ for item in page.items or []] == [
        "GetStructureItemsResultItemsItemVariant2",
        "OtherKind",
    ]


def _connection_document(fields: dict) -> dict:
    """A document whose ``createThing`` takes an object with ``fields``."""
    taken = {"type": "object", "properties": fields}
    return {
        "paths": {"/rpc/createThing": _operation(taken, {"type": "object"})},
        "components": {"schemas": {}},
    }


def test_a_secret_of_the_document_gets_the_type_of_a_secret():
    """#388: ``writeOnly`` strings and two maps are secrets; a path and a certificate are not."""
    fields = {
        "password": {"type": ["string", "null"], "writeOnly": True},
        "dir_path": {"type": "string", "writeOnly": True},
        "ssl_ca": {"type": ["string", "null"], "writeOnly": True},
        "secret_headers": {
            "type": ["object", "null"],
            "additionalProperties": {"type": ["string", "null"]},
        },
        "host": {"type": "string"},
    }
    document = _connection_document(fields)
    typed = gen.prepare(document)["components"]["schemas"]["things.CreateThingRequest"]
    assert typed["properties"] == {
        "password": {"type": ["string", "null"], "format": "password"},
        "dir_path": {"type": "string"},
        "ssl_ca": {"type": ["string", "null"]},
        "secret_headers": {
            "type": "object",
            "additionalProperties": {"type": "string", "format": "password"},
        },
        "host": {"type": "string"},
    }
    module = gen.generate(document)["things.py"]
    assert "password: SecretStr | None = None" in module
    assert "secret_headers: dict[str, SecretStr] | None = None" in module
    assert "dir_path: str | None = None" in module and "writeOnly" not in module


def test_a_secret_that_is_no_string_stops_the_run():
    """The rule types strings; a new shape of a secret is looked at by a person."""
    document = _connection_document({"key": {"type": "object", "writeOnly": True}})
    with pytest.raises(SystemExit, match="the secret 'key' is no string"):
        gen.prepare(document)


def test_a_generated_root_model_does_not_quote_its_input_in_an_error():
    """Both sides: every ``RootModel`` of the layer has the setting, and it bites."""
    from pydantic import ValidationError

    from ycli.yandex.datalens.schemas.connection import ConnectionCreate

    roots = [
        line
        for home in GENERATED
        for module in sorted((SRC / home).glob("*.py"))
        for line in module.read_text(encoding="utf-8").split("\n\n\n")
        if line.startswith("class ") and "RootModel[" in line.split("):")[0]
    ]
    assert roots and all("hide_input_in_errors=True" in root for root in roots)
    with pytest.raises(ValidationError) as refused:
        # No union of kinds refuses an object any more (#444): a value that is no object does.
        ConnectionCreate.model_validate(["S3cret-value"])
    assert "S3cret-value" not in str(refused.value)


def test_a_set_of_values_is_written_in_one_order_everywhere():
    """Measured: the output schema of `connections get` differed between Python 3.13 and 3.14.

    Up to 3.13 ``Literal["on", "off"] | str`` and ``Literal["off", "on"] | str`` are one object,
    the first evaluated; 3.14 keeps two. Both sides: the step turns the rarer order, and no
    set of values of the committed layer stands in two orders.
    """
    often, once = {"enum": ["on", "off"]}, {"enum": ["off", "on"]}
    fields = {"a": often, "b": once, "c": dict(often), "d": {"enum": ["x", "y"]}}
    prepared = gen.prepare(_connection_document(fields))["components"]["schemas"]
    listed = [
        field["anyOf"][0]["enum"]
        for field in prepared["things.CreateThingRequest"]["properties"].values()
    ]
    assert listed == [["on", "off"], ["on", "off"], ["on", "off"], ["x", "y"]]
    orders: dict[frozenset[str], set[str]] = {}
    for home in GENERATED:
        for module in sorted((SRC / home).glob("*.py")):
            for written in re.findall(r"Literal\[([^\]]+)\]", module.read_text(encoding="utf-8")):
                values = " ".join(written.split())
                orders.setdefault(frozenset(values.rstrip(",").split(", ")), set()).add(values)
    assert not [sorted(found) for found in orders.values() if len(found) > 1]


def test_a_request_envelope_given_in_parts_is_one_closed_object():
    """Both sides (#371): parts that are plain objects are joined; a union among them is not.

    Seen on the defect: before the step ``createWizardChart`` came out as an open class that
    inherits one part, so the arguments check had no envelope to read.
    """
    place = {"type": "object", "properties": {"name": {"type": "string"}}}
    own = {"type": "object", "properties": {"data": {"type": "object"}}, "required": ["data"]}
    spec = {
        "paths": {"/rpc/createThing": _operation({"allOf": [own, {"$ref": REF + "Place"}]}, {})},
        "components": {"schemas": {"Place": place}},
    }
    envelope = gen.prepare(spec)["components"]["schemas"]["things.CreateThingRequest"]
    assert sorted(envelope["properties"]) == ["data", "name"]
    assert envelope["required"] == ["data"] and envelope[gen._BASE] == gen._CLOSED
    module = gen.generate(spec)["things.py"]
    assert "class CreateThingRequest(RequestBody):" in module
    kinds = {"oneOf": [_kind("a"), _kind("b")]}
    spec["paths"]["/rpc/createThing"] = _operation({"allOf": [own, kinds]}, {})
    assert "class CreateThingRequest(RequestBody):" not in gen.generate(spec)["things.py"]
    # The layer as committed: the four envelopes the document gives in parts are closed.
    from ycli.yandex.datalens.schemas import html_pages, ql, reports, wizard
    from ycli.yandex.models import RequestBody

    for envelope_class in (
        wizard.CreateWizardChartV1Args,
        ql.CreateQLChartArgs,
        reports.CreateReportV2Args,
        html_pages.CreateHtmlPageArgs,
    ):
        assert issubclass(envelope_class, RequestBody), envelope_class.__name__


def test_no_class_of_the_layer_is_named_by_the_code_generator():
    """A class is named by the document or by its place, never ``EntryModel3`` in order met.

    Seven names stay: the document itself has ``AddField`` and ``add_field``, two names that
    are one in Python, and the generator tells the second apart with ``Model``.
    """
    made_up = sorted(
        name
        for home in GENERATED
        for module in sorted((SRC / home).glob("*.py"))
        for name in re.findall(r"^class (\w+)", module.read_text(encoding="utf-8"), re.MULTILINE)
        if re.search(r"Model\d*$", name)
    )
    assert made_up == [
        "AddFieldModel",
        "CloneFieldModel",
        "DeleteFieldModel",
        "DeleteObligatoryFilterModel",
        "RefreshSourceModel",
        "ReplaceConnectionModel",
        "UpdateFieldModel",
    ]


def test_a_kind_the_document_does_not_know_is_sent_as_it_was_given():
    """Measured (#444): DataLens takes a source of the kind ``GSHEETS_V2``; ycli refused it."""
    from ycli.yandex.datalens.schemas.dataset import DatasetValidate
    from ycli.yandex.models import WIRE

    source = {"source_type": "GSHEETS_V2", "id": "s1", "parameters": {"sheet": "Sales"}}
    tried = {"updates": [{"action": "add_source", "source": source}]}
    built = DatasetValidate.model_validate(tried)
    assert built.model_dump(mode="json", context=WIRE) == tried  # nothing lost on the way
    # The other side: a kind the document knows is still built as its own class, with its
    # fields checked by their types; the spare one is taken only when its own does not fit.
    known = {"updates": [{"action": "add_source", "source": {"source_type": "CH_TABLE"}}]}
    update = DatasetValidate.model_validate(known).updates
    assert update is not None
    added = update[0].root
    assert type(added).__name__ == "AddSource"
    assert type(getattr(added, "source").root).__name__.startswith("CHTABLE")  # noqa: B009


def test_a_connection_of_a_kind_nobody_knows_is_sent_and_its_secret_is_not_typed():
    """What #444 costs, written down: the spare class is empty, so a password in it is text.

    A connection of a kind the document lacks, or of a known kind with a field of another
    type, goes to DataLens as given. ``repr`` and a dump of it print the password; a dry run
    and the text of an error still do not (``tests/unit/yandex/datalens/connections``).
    """
    from ycli.yandex.datalens.schemas.connection import ConnectionCreate
    from ycli.yandex.models import WIRE, secret_keys

    secret = "S3cret-value"
    for body in (
        {"type": "gsheets_v9", "name": "x", "password": secret},  # a kind not in the document
        {"type": "clickhouse", "port": "not a number", "password": secret},  # a field mistyped
    ):
        built = ConnectionCreate.model_validate(body)
        assert type(built.root).__name__ == "OtherKind"
        assert built.model_dump(mode="json", context=WIRE) == body
        assert secret in repr(built) and secret in built.model_dump_json()
    # A body that fits its kind keeps the guarantee of #388.
    fits = ConnectionCreate.model_validate({"type": "clickhouse", "password": secret})
    assert secret not in repr(fits) and secret not in fits.model_dump_json()
    assert "password" in secret_keys(ConnectionCreate)  # what a dry run masks by


def test_a_field_required_and_nullable_is_marked_to_go_out_as_null():
    """Both sides of the rule on a small document; the mark reaches the generated class."""
    nested = {
        "type": "object",
        "required": ["interval", "title"],
        "properties": {
            "interval": {"type": ["number", "null"]},  # required and may be null: marked
            "title": {"type": "string"},  # required, never null: no mark
            "hint": {"type": ["string", "null"]},  # may be null, not required: no mark
            "limit": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
        },
    }
    nested["required"].append("limit")  # a union with null counts as nullable too
    document = _connection_document({"settings": nested})
    schemas = gen.prepare(document)["components"]["schemas"]
    settings = schemas["things.CreateThingRequestSettings"]["properties"]
    assert {name for name, field in settings.items() if field.get(gen._KEEPS_NULL)} == {
        "interval",
        "limit",
    }
    # The field stays optional to give and to read: only the mark says what to send.
    assert (
        "required" not in schemas["things.CreateThingRequestSettings"]
        or not (schemas["things.CreateThingRequestSettings"]["required"])
    )
    module = gen.generate(document)["things.py"]
    # The class carries a typed mark; the key of the prepared document does not reach it.
    assert "interval: Annotated[int | float | None, NoDropNull()] = None" in module
    assert "limit: Annotated[int | None, NoDropNull()] = None" in module
    assert "x-ycli" not in module and "json_schema_extra" not in module
    assert "title: str | None = None" in module


def test_the_model_template_is_the_generators_own_but_for_what_ycli_adds():
    """A copy of a template goes stale: it must stay the generator's, plus the marked lines.

    Both sides: with ycli's lines taken out it is the generator's template word for word, and
    the lines are there.
    """
    import datamodel_code_generator

    name = "pydantic_v2/BaseModel.jinja2"
    upstream = Path(datamodel_code_generator.__file__).parent / "model" / "template" / name
    theirs = upstream.read_text(encoding="utf-8").splitlines()
    ours = (gen.TEMPLATES / name).read_text(encoding="utf-8").splitlines()
    changes = [line for line in difflib.ndiff(theirs, ours) if line[:1] in "+-"]
    assert [line[2:] for line in changes if line[0] == "-"] == ["    {{ description }}"]
    added = [line[2:].strip() for line in changes if line[0] == "+"]
    assert len(added) == 9
    assert sum(line.startswith("{#- ycli:") for line in added) == 2
    assert sum("Annotated[{{ field.type_hint }}, NoDropNull()]" in line for line in added) == 2


def test_a_request_given_as_a_union_of_objects_has_an_envelope_per_member():
    """Both sides: each member is closed and keeps what it requires; a union deeper is not.

    Seen on the defect: before the step both members of ``updateHtmlPage`` were open classes
    that required nothing, so a body with no field and a body with ``content`` and ``revId``
    together both passed.
    """
    new = {
        "type": "object",
        "properties": {"id": {"type": "string"}, "content": {"type": "string"}},
        "required": ["id", "content"],
    }
    old = {
        "type": "object",
        "properties": {"id": {"type": "string"}, "revId": {"type": "string"}},
        "required": ["id", "revId"],
    }
    spec = {
        "paths": {"/rpc/updateThing": _operation({"anyOf": [new, old]}, {})},
        "components": {"schemas": {}},
    }
    schemas = gen.prepare(spec)["components"]["schemas"]
    # Nothing tells the members apart: no spare kind among them.
    assert schemas["things.UpdateThingRequest"]["anyOf"] == [
        {"$ref": REF + "things.UpdateThingRequestVariant1"},
        {"$ref": REF + "things.UpdateThingRequestVariant2"},
    ]
    first, second = (schemas[f"things.UpdateThingRequestVariant{n}"] for n in (1, 2))
    assert (first["required"], second["required"]) == (["id", "content"], ["id", "revId"])
    assert first[gen._BASE] == gen._CLOSED and second[gen._BASE] == gen._CLOSED
    # The other side: the same union one level down belongs to no operation's arguments.
    inner = {"type": "object", "properties": {"change": {"anyOf": [new, old]}}}
    spec["paths"]["/rpc/updateThing"] = _operation(inner, {})
    prepared = gen.prepare(spec)["components"]["schemas"]
    for name in (
        "things.UpdateThingRequestChangeVariant1",
        "things.UpdateThingRequestChangeVariant2",
    ):
        assert prepared[name]["required"] == [] and gen._BASE not in prepared[name]
    # The layer as committed: the model itself refuses both bodies, and names the fields.
    from pydantic import ValidationError

    from ycli.yandex.datalens.schemas import html_pages, spark_applications
    from ycli.yandex.models import WIRE, RequestBody

    for refused, named in (
        ({}, ["content", "entryId", "mode", "revId"]),
        ({"entryId": "p1", "content": "<p>", "revId": "r1", "mode": "save"}, ["content", "revId"]),
    ):
        with pytest.raises(ValidationError) as failure:
            html_pages.UpdateHtmlPageArgs.model_validate(refused)
        assert sorted({error["loc"][-1] for error in failure.value.errors()}) == named
    for body in (
        {"entryId": "p1", "content": "<p>"},
        {"entryId": "p1", "revId": "r1", "mode": "publish"},
    ):
        assert html_pages.UpdateHtmlPageArgs.model_validate(body).model_dump(context=WIRE) == body
    for envelope_class in (
        html_pages.UpdateHtmlPageArgsVariant1,
        html_pages.UpdateHtmlPageArgsVariant2,
        spark_applications.CreateSparkApplicationArgsVariant1,
        spark_applications.CreateSparkApplicationArgsVariant2,
        spark_applications.CreateSparkApplicationArgsVariant3,
    ):
        assert issubclass(envelope_class, RequestBody), envelope_class.__name__


def test_a_field_with_one_value_is_required_only_where_it_tells_kinds_apart():
    """Both sides: required in a member of a union, optional in an object that is none.

    Seen on the defect: ``updateHtmlPage`` answers ``version: null`` (measured, 2026-10-06)
    where the document has the one value ``1``, and the class that required it refused the
    reply.
    """
    spec = {
        "paths": {
            "/rpc/getThing": _operation(
                {"type": "object", "properties": {"id": {"type": "string"}}},
                {
                    "type": "object",
                    "properties": {
                        "alone": {"$ref": REF + "Alone"},
                        "item": {"anyOf": [{"$ref": REF + "A"}, {"$ref": REF + "B"}]},
                    },
                },
            )
        },
        "components": {
            "schemas": {
                name: {**_kind(value), "required": ["kind", "size"]}
                for name, value in (("Alone", "x"), ("A", "a"), ("B", "b"))
            }
        },
    }
    schemas = gen.prepare(spec)["components"]["schemas"]
    assert schemas["things.Alone"]["required"] == []
    assert schemas["things.A"]["required"] == ["kind"] and schemas["things.B"]["required"] == [
        "kind"
    ]
    # The layer as committed: the reply DataLens gives is read, and a known value still is.
    from ycli.yandex.datalens.schemas.html_pages import GetHtmlPageResult, UpdateHtmlPageResult

    saved = {"entry": {"entryId": "p1", "scope": "artifact", "type": "html-page", "version": None}}
    entry = UpdateHtmlPageResult.model_validate(saved).entry
    assert entry is not None and entry.version is None
    assert GetHtmlPageResult.model_validate({"entryId": "p1", "version": 1}).version == 1
