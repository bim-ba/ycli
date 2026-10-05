"""Contract cases for Tracker global ``/fields`` and their categories (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.fields.models import FieldCategoryCreate, FieldCategoryUpdate, FieldUpdate
from ycli.yandex.tracker.models import FieldCreate, LocalizedName, OptionsProviderInput

STRING_TYPE = "ru.yandex.startrek.core.fields.StringFieldType"

CASES = [
    Case(
        "tracker.fields.list",
        cli=["tracker", "fields", "list"],
        mcp=("tracker_fields_list", {}),
        exchanges=[
            (
                Sent("GET", "fields"),
                Reply(json=[{"id": "ruName", "key": "ruName", "schema": {"type": "string"}}]),
            )
        ],
    ),
    Case(
        "tracker.fields.get",
        args=("enName",),
        cli=["tracker", "fields", "get", "enName"],
        mcp=("tracker_fields_get", {"field_id": "enName"}),
        exchanges=[(Sent("GET", "fields/enName"), Reply(json={"id": "enName", "name": "Field"}))],
    ),
    Case(
        "tracker.fields.create",
        args=(
            FieldCreate(
                name=LocalizedName(ru="Поле", en="Field"),
                id="myField",
                category="cat-1",
                type=STRING_TYPE,
                options_provider=OptionsProviderInput(
                    type="CustomListProvider", values=["alpha", "beta"]
                ),
                order=7,
                description="A custom field",
                readonly=True,
            ),
        ),
        cli=[
            "tracker",
            "fields",
            "create",
            "--id",
            "myField",
            "--type",
            STRING_TYPE,
            "--category",
            "cat-1",
            "--name-ru",
            "Поле",
            "--name-en",
            "Field",
            "--description",
            "A custom field",
            "--order",
            "7",
            "--readonly",
            "--option",
            "alpha",
            "--option",
            "beta",
            "--options-type",
            "CustomListProvider",
        ],
        mcp=(
            "tracker_fields_create",
            {
                "body": {
                    "name": {"ru": "Поле", "en": "Field"},
                    "id": "myField",
                    "category": "cat-1",
                    "type": STRING_TYPE,
                    "options_provider": {"type": "CustomListProvider", "values": ["alpha", "beta"]},
                    "order": 7,
                    "description": "A custom field",
                    "readonly": True,
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "fields",
                    json={
                        "name": {"ru": "Поле", "en": "Field"},
                        "id": "myField",
                        "category": "cat-1",
                        "type": STRING_TYPE,
                        "optionsProvider": {
                            "type": "CustomListProvider",
                            "values": ["alpha", "beta"],
                        },
                        "order": 7,
                        "description": "A custom field",
                        "readonly": True,
                    },
                ),
                Reply(json={"id": "myField"}, status=201),
            )
        ],
    ),
    # `--option` alone uses the fixed-list provider; `--no-readonly` sends false, not nothing.
    Case(
        "tracker.fields.create",
        args=(
            FieldCreate(
                name=LocalizedName(ru="Список"),
                id="listField",
                category="cat-2",
                type="ListType",
                options_provider=OptionsProviderInput(
                    type="FixedListOptionsProvider", values=["a", "b"]
                ),
                readonly=False,
            ),
        ),
        cli=[
            "tracker",
            "fields",
            "create",
            "--id",
            "listField",
            "--type",
            "ListType",
            "--category",
            "cat-2",
            "--name-ru",
            "Список",
            "--option",
            "a",
            "--option",
            "b",
            "--options-type",
            "FixedListOptionsProvider",
            "--no-readonly",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "fields",
                    json={
                        "name": {"ru": "Список"},
                        "id": "listField",
                        "category": "cat-2",
                        "type": "ListType",
                        "optionsProvider": {
                            "type": "FixedListOptionsProvider",
                            "values": ["a", "b"],
                        },
                        "readonly": False,
                    },
                ),
                Reply(json={"id": "listField"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.fields.update",
        args=(
            "ruName",
            FieldUpdate(
                name=LocalizedName(ru="Имя", en="Name"),
                options_provider=OptionsProviderInput(type="CustomListProvider", values=["x"]),
            ),
        ),
        kwargs={"version": 3},
        cli=[
            "tracker",
            "fields",
            "update",
            "ruName",
            "--name-ru",
            "Имя",
            "--name-en",
            "Name",
            "--option",
            "x",
            "--options-type",
            "CustomListProvider",
            "--version",
            "3",
        ],
        mcp=(
            "tracker_fields_update",
            {
                "field_id": "ruName",
                "body": {
                    "name": {"ru": "Имя", "en": "Name"},
                    "options_provider": {"type": "CustomListProvider", "values": ["x"]},
                },
                "version": 3,
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "fields/ruName",
                    {"version": "3"},
                    {
                        "name": {"ru": "Имя", "en": "Name"},
                        "optionsProvider": {"type": "CustomListProvider", "values": ["x"]},
                    },
                ),
                Reply(json={"id": "ruName"}),
            )
        ],
    ),
    # Without --version no ?version= is sent; without a name no name key.
    Case(
        "tracker.fields.update",
        args=(
            "tags",
            FieldUpdate(
                options_provider=OptionsProviderInput(type="FixedListOptionsProvider", values=["y"])
            ),
        ),
        cli=[
            "tracker",
            "fields",
            "update",
            "tags",
            "--option",
            "y",
            "--options-type",
            "FixedListOptionsProvider",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "fields/tags",
                    json={"optionsProvider": {"type": "FixedListOptionsProvider", "values": ["y"]}},
                ),
                Reply(json={"id": "tags"}),
            )
        ],
    ),
    # A rename alone sends no optionsProvider.
    Case(
        "tracker.fields.update",
        args=("summary", FieldUpdate(name=LocalizedName(ru="Заголовок"))),
        kwargs={"version": 9},
        cli=["tracker", "fields", "update", "summary", "--name-ru", "Заголовок", "--version", "9"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "fields/summary", {"version": "9"}, {"name": {"ru": "Заголовок"}}),
                Reply(json={"id": "summary"}),
            )
        ],
    ),
    Case(
        "tracker.fields.categories_create",
        args=(
            FieldCategoryCreate(
                name=LocalizedName(ru="Своя", en="Own"), order=400, description="Custom category"
            ),
        ),
        cli=[
            "tracker",
            "fields",
            "categories-create",
            "--name-ru",
            "Своя",
            "--name-en",
            "Own",
            "--order",
            "400",
            "--description",
            "Custom category",
        ],
        mcp=(
            "tracker_fields_categories_create",
            {
                "body": {
                    "name": {"ru": "Своя", "en": "Own"},
                    "order": 400,
                    "description": "Custom category",
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "fields/categories",
                    json={
                        "name": {"ru": "Своя", "en": "Own"},
                        "order": 400,
                        "description": "Custom category",
                    },
                ),
                Reply(json={"id": "604f99", "version": 1}, status=201),
            )
        ],
    ),
    Case(
        "tracker.fields.categories_update",
        args=(
            "604f99",
            FieldCategoryUpdate(
                name=LocalizedName(en="Renamed"), order=500, description="New description"
            ),
        ),
        kwargs={"version": 1},
        cli=[
            "tracker",
            "fields",
            "categories-update",
            "604f99",
            "--name-en",
            "Renamed",
            "--order",
            "500",
            "--description",
            "New description",
            "--version",
            "1",
        ],
        mcp=(
            "tracker_fields_categories_update",
            {
                "category_id": "604f99",
                "body": {
                    "name": {"en": "Renamed"},
                    "order": 500,
                    "description": "New description",
                },
                "version": 1,
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "fields/categories/604f99",
                    {"version": "1"},
                    {"name": {"en": "Renamed"}, "order": 500, "description": "New description"},
                ),
                Reply(json={"id": "604f99", "version": 2}),
            )
        ],
    ),
    Case(
        "tracker.fields.categories_update",
        args=("cat-9", FieldCategoryUpdate(order=600)),
        cli=["tracker", "fields", "categories-update", "cat-9", "--order", "600"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "fields/categories/cat-9", json={"order": 600}),
                Reply(json={"id": "cat-9", "version": 3}),
            )
        ],
    ),
]
