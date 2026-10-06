"""The generated models of DataLens: what the script does to the specification, and its checks.

The specification is not committed, so nothing here reads it: the pipeline's own steps are
tested on a small document, and the committed files are held to be what the script last wrote.
"""

import importlib
import json
import shutil

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
        "charts.Pie",
        "charts.UpdateChartArgs",
        "dashboards.DeleteArgs",
        "shared.User",
    ]
    chart = schemas["charts.Chart"]["properties"]
    # A reply is read as it comes; only the envelope of a request is closed, unless the
    # document itself leaves that envelope open.
    assert "additionalProperties" not in schemas["charts.Chart"]
    assert schemas["charts.GetChartRequest"]["additionalProperties"] is False
    assert schemas["charts.UpdateChartArgs"]["additionalProperties"] is False
    assert schemas["dashboards.DeleteArgs"]["additionalProperties"] == {}
    # A set of values is open, with or without `null`; a single value is a tag and stays.
    assert chart["mode"] == {
        "anyOf": [{"enum": ["save", "publish"], "type": "string"}, {"type": "string"}]
    }
    assert chart["managedBy"] == {"anyOf": [{"enum": ["user", "system", None]}, {"type": "string"}]}
    assert chart["kind"] == {"type": "string", "enum": ["wizard"]}
    # A union's tag stays closed even with several values, and its members always carry it.
    assert schemas["charts.Line"] == {
        "type": "object",
        "properties": {"type": {"type": "string", "enum": ["line", "area"]}},
        "required": ["type"],
    }
    assert schemas["charts.Pie"]["required"] == ["type"]
    assert chart["config"]["discriminator"]["mapping"] == {
        "line": REF + "charts.Line",
        "pie": REF + "charts.Pie",
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
    # The generator writes a union member's tag from the mapping; it is never widened.
    assert 'type: Literal["line"]\n' in charts and 'type: Literal["pie"]\n' in charts
    assert "meta: ChartMeta2 | None = None" in charts and "class ChartMeta2TagsItem" in charts
    # The envelope the document leaves open is not closed by ycli.
    assert "class DeleteArgs(APIModel):" in modules["dashboards.py"]
    assert 'extra="allow"' in modules["dashboards.py"]
    # No default of the document, no directive to the generator, nothing but plain models.
    assert '"save"\n' not in charts and "subprocess" not in "".join(modules.values())
    assert [gen.foreign(text) for text in modules.values()] == [[], [], [], []]
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
    assert schemas["things.Thing"]["required"] == ["kind"]  # one value: it tells the kind
    assert schemas["things.Owner"]["required"] == []  # read and sent back: one class
    assert schemas["things.GetThingRequest"]["required"] == ["id"]  # an argument


def test_a_reply_without_a_field_the_document_requires_is_read():
    """Measured: ``getWorkbook`` answers without ``permissions`` unless the request asks."""
    from ycli.yandex.datalens.schemas.workbook import GetWorkbookResult

    workbook = GetWorkbookResult.model_validate({"workbookId": "w1", "title": "Q1"})
    assert (workbook.workbook_id, workbook.permissions) == ("w1", None)


def test_fields_and_one_of_becomes_one_of_each_with_the_fields():
    """Both sides: the members are written out and named by place; a mapped union is left."""
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
    reply = {"type": "object", "properties": {"mapped": mapped}}
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
    assert "allOf" in schemas["things.GetThingResponse"]["properties"]["mapped"]


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
