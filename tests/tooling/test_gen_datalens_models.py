"""The generated models of DataLens: what the script does to the specification, and its checks.

The specification is not committed, so nothing here reads it: the pipeline's own two steps are
tested on a small document, and the committed files are held to be what the last step leaves.
"""

import importlib
import json
import shutil

import pytest
from scripts import gen_datalens_models as gen

from tests.architecture.scanners import GENERATED, SRC

REF = "#/components/schemas/"
SPEC = {
    "paths": {
        "/rpc/getChart": {
            "post": {
                "tags": ["Charts"],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"chartId": {"type": "string"}},
                                "additionalProperties": False,
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"content": {"application/json": {"schema": {"$ref": REF + "Chart"}}}}
                },
            }
        },
        "/rpc/deleteDashboard": {
            "post": {
                "tags": ["Dashboards"],
                "requestBody": {
                    "content": {"application/json": {"schema": {"$ref": REF + "DeleteArgs"}}}
                },
                "responses": {"200": {"content": {"application/json": {"schema": {}}}}},
            }
        },
    },
    "components": {
        "schemas": {
            "Chart": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "mode": {"type": "string", "enum": ["save", "publish"]},
                    "kind": {"type": "string", "enum": ["wizard"]},
                    "config": {
                        "discriminator": {
                            "propertyName": "type",
                            "mapping": {"line": REF + "Line", "pie": REF + "Pie"},
                        },
                        "oneOf": [{"$ref": REF + "Line"}, {"$ref": REF + "Pie"}],
                    },
                    "owner": {"$ref": REF + "User"},
                },
            },
            "Line": {
                "type": "object",
                "properties": {"type": {"type": "string", "enum": ["line", "area"]}},
            },
            "Pie": {"type": "object", "properties": {"type": {"type": "string", "const": "pie"}}},
            "DeleteArgs": {
                "type": "object",
                "properties": {"dashboardId": {"type": "string"}, "by": {"$ref": REF + "User"}},
            },
            "User": {"type": "object", "properties": {"login": {"type": "string"}}},
            "Orphan": {"type": "object"},
        }
    },
}


def test_the_specification_is_prepared_for_ycli_rules():
    before = json.dumps(SPEC)
    prepared = gen.prepare(SPEC)
    assert json.dumps(SPEC) == before, "the document given is left as it was"
    schemas = prepared["components"]["schemas"]
    # A module per section; a schema two sections reach, or none, is shared.
    assert sorted(schemas) == [
        "charts.Chart",
        "charts.GetChartRequest",
        "charts.Line",
        "charts.Pie",
        "dashboards.DeleteArgs",
        "shared.Orphan",
        "shared.User",
    ]
    chart = schemas["charts.Chart"]
    # A reply is read as it comes; only the envelope of a request is closed.
    assert "additionalProperties" not in chart
    assert schemas["charts.GetChartRequest"]["additionalProperties"] is False
    assert schemas["dashboards.DeleteArgs"]["additionalProperties"] is False
    # A set of values is open, a single value is a tag and stays.
    assert chart["properties"]["mode"] == {
        "anyOf": [{"enum": ["save", "publish"], "type": "string"}, {"type": "string"}]
    }
    assert chart["properties"]["kind"] == {"type": "string", "enum": ["wizard"]}
    # A union's tag stays closed even with several values, and its members always carry it.
    assert schemas["charts.Line"] == {
        "type": "object",
        "properties": {"type": {"type": "string", "enum": ["line", "area"]}},
        "required": ["type"],
    }
    assert schemas["charts.Pie"]["required"] == ["type"]
    assert chart["properties"]["config"]["discriminator"]["mapping"] == {
        "line": REF + "charts.Line",
        "pie": REF + "charts.Pie",
    }
    assert chart["properties"]["owner"] == {"$ref": REF + "shared.User"}
    # The inline request got a name; the untyped reply stays untyped.
    operations = prepared["paths"]
    request = operations["/rpc/getChart"]["post"]["requestBody"]["content"]["application/json"]
    assert request["schema"] == {"$ref": REF + "charts.GetChartRequest"}
    reply = operations["/rpc/deleteDashboard"]["post"]["responses"]["200"]["content"]
    assert reply["application/json"]["schema"] == {}


def test_a_name_the_specification_already_uses_stops_the_run():
    clash = json.loads(json.dumps(SPEC))
    clash["components"]["schemas"]["GetChartRequest"] = {"type": "object"}
    with pytest.raises(SystemExit, match="already has a schema GetChartRequest"):
        gen.prepare(clash)


def test_the_small_specification_becomes_modules_that_follow_the_rules():
    """The whole pipeline on the small document: generate, finish, format."""
    modules = {path.name: text for path, text in gen.generate(SPEC).items()}
    assert sorted(modules) == ["__init__.py", "charts.py", "dashboards.py", "shared.py"]
    charts = modules["charts.py"]
    assert charts.startswith(gen.HEADER)
    assert "class GetChartRequest(RequestBody):" in charts
    assert "class Chart(APIModel):" in charts
    assert 'extra="forbid"' not in charts
    assert 'Literal["save", "publish"] | str | None' in charts
    # The generator writes a union member's tag from the mapping; it is never widened.
    assert 'type: Literal["line"]\n' in charts and 'type: Literal["pie"]\n' in charts
    assert 'config: Line | Pie | None = Field(default=None, discriminator="type")' in charts
    assert "class DeleteArgs(RequestBody):" in modules["dashboards.py"]
    # What was written is what the last step leaves: formatting it again changes nothing.
    assert gen._ruff(gen.finish(charts), "charts.py") == charts


def test_no_generated_file_was_edited_by_hand():
    assert gen.edited_by_hand() == []


def test_the_hand_edit_check_bites(tmp_path, monkeypatch):
    """Prove-it: a changed line, a lost header and a closed reply model are each reported."""
    copy = tmp_path / "schemas"
    shutil.copytree(gen.SCHEMAS, copy)
    monkeypatch.setattr(gen, "SCHEMAS", copy)
    assert gen.edited_by_hand() == []
    tenants = copy / "tenants.py"
    text = tenants.read_text(encoding="utf-8")
    tenants.write_text(text + "\n\nNOTE   =   1\n", encoding="utf-8")
    assert gen.edited_by_hand() == [tenants]
    tenants.write_text(text.removeprefix(gen.HEADER), encoding="utf-8")
    assert gen.edited_by_hand() == [tenants]
    tenants.write_text(text, encoding="utf-8")
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


def test_check_reports_and_writes(tmp_path, monkeypatch, capsys):
    """``--check`` exits 1 on an edited file; a run from a saved document writes the package."""
    saved = tmp_path / "spec.json"
    saved.write_text(json.dumps(SPEC), encoding="utf-8")
    monkeypatch.setattr(gen, "SCHEMAS", tmp_path / "schemas")
    assert gen.main(["--spec", str(saved)]) == 0
    assert "4 modules" in capsys.readouterr().out
    assert gen.main(["--check"]) == 0
    assert gen.main(["--check", "--live", "--spec", str(saved)]) == 0
    charts = tmp_path / "schemas" / "charts.py"
    charts.write_text(charts.read_text(encoding="utf-8") + "X = 1\n", encoding="utf-8")
    (tmp_path / "schemas" / "gone.py").write_text(gen.HEADER, encoding="utf-8")
    assert gen.main(["--check"]) == 1
    assert "edited by hand" in capsys.readouterr().err
    assert gen.main(["--check", "--live", "--spec", str(saved)]) == 1
    assert "differs from the published specification" in capsys.readouterr().out
    assert gen.main(["--spec", str(saved)]) == 0
    assert not (tmp_path / "schemas" / "gone.py").exists()
    assert gen.main(["--check"]) == 0
