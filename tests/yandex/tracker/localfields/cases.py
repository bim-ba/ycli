"""Contract cases for Tracker ``/queues/{id}/localFields`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.localfields.models import LocalFieldUpdate
from ycli.yandex.tracker.models import FieldCreate, LocalizedName, OptionsProviderInput

STRING_TYPE = "ru.yandex.startrek.core.fields.StringFieldType"

CASES = [
    Case(
        "tracker.localfields.list",
        args=("ORG",),
        cli=["tracker", "localfields", "list", "ORG"],
        mcp=("tracker_localfields_list", {"queue_id": "ORG"}),
        exchanges=[
            (
                Sent("GET", "queues/ORG/localFields"),
                Reply(json=[{"id": "loc--1", "key": "loc_field_key", "name": "Local"}]),
            )
        ],
    ),
    Case(
        "tracker.localfields.get",
        args=("OPS", "deadline_note"),
        cli=["tracker", "localfields", "get", "OPS", "deadline_note"],
        mcp=("tracker_localfields_get", {"queue_id": "OPS", "field_key": "deadline_note"}),
        exchanges=[
            (
                Sent("GET", "queues/OPS/localFields/deadline_note"),
                Reply(json={"id": "loc--2", "key": "deadline_note", "name": "Deadline note"}),
            )
        ],
    ),
    Case(
        "tracker.localfields.create",
        args=(
            "DEV",
            FieldCreate(
                name=LocalizedName(ru="Поле", en="Field"),
                id="loc_new",
                category="cat-3",
                type=STRING_TYPE,
                options_provider=OptionsProviderInput(type="CustomListProvider", values=["p", "q"]),
                order=12,
                description="Queue-scoped",
                readonly=True,
            ),
        ),
        cli=[
            "tracker",
            "localfields",
            "create",
            "DEV",
            "--id",
            "loc_new",
            "--type",
            STRING_TYPE,
            "--category",
            "cat-3",
            "--name-ru",
            "Поле",
            "--name-en",
            "Field",
            "--description",
            "Queue-scoped",
            "--order",
            "12",
            "--readonly",
            "--option",
            "p",
            "--option",
            "q",
            "--options-type",
            "CustomListProvider",
        ],
        mcp=(
            "tracker_localfields_create",
            {
                "queue_id": "DEV",
                "body": {
                    "name": {"ru": "Поле", "en": "Field"},
                    "id": "loc_new",
                    "category": "cat-3",
                    "type": STRING_TYPE,
                    "options_provider": {"type": "CustomListProvider", "values": ["p", "q"]},
                    "order": 12,
                    "description": "Queue-scoped",
                    "readonly": True,
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "queues/DEV/localFields",
                    json={
                        "name": {"ru": "Поле", "en": "Field"},
                        "id": "loc_new",
                        "category": "cat-3",
                        "type": STRING_TYPE,
                        "optionsProvider": {"type": "CustomListProvider", "values": ["p", "q"]},
                        "order": 12,
                        "description": "Queue-scoped",
                        "readonly": True,
                    },
                ),
                Reply(json={"key": "loc_new"}, status=201),
            )
        ],
    ),
    # Without --option no optionsProvider; `--no-readonly` sends false, not nothing.
    Case(
        "tracker.localfields.create",
        args=(
            "QA",
            FieldCreate(
                name=LocalizedName(en="Plain"),
                id="loc_plain",
                category="cat-4",
                type="TextType",
                readonly=False,
            ),
        ),
        cli=[
            "tracker",
            "localfields",
            "create",
            "QA",
            "--id",
            "loc_plain",
            "--type",
            "TextType",
            "--category",
            "cat-4",
            "--name-en",
            "Plain",
            "--no-readonly",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "queues/QA/localFields",
                    json={
                        "name": {"en": "Plain"},
                        "id": "loc_plain",
                        "category": "cat-4",
                        "type": "TextType",
                        "readonly": False,
                    },
                ),
                Reply(json={"key": "loc_plain"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.localfields.update",
        args=(
            "SUP",
            "loc_edit",
            LocalFieldUpdate(
                name=LocalizedName(ru="Новое", en="New"),
                category="cat-5",
                options_provider=OptionsProviderInput(type="CustomListProvider", values=["r"]),
                order=102,
                description="Edited",
                readonly=True,
                visible=False,
                hidden=True,
            ),
        ),
        cli=[
            "tracker",
            "localfields",
            "update",
            "SUP",
            "loc_edit",
            "--name-ru",
            "Новое",
            "--name-en",
            "New",
            "--category",
            "cat-5",
            "--description",
            "Edited",
            "--order",
            "102",
            "--readonly",
            "--no-visible",
            "--hidden",
            "--option",
            "r",
            "--options-type",
            "CustomListProvider",
        ],
        mcp=(
            "tracker_localfields_update",
            {
                "queue_id": "SUP",
                "field_key": "loc_edit",
                "body": {
                    "name": {"ru": "Новое", "en": "New"},
                    "category": "cat-5",
                    "options_provider": {"type": "CustomListProvider", "values": ["r"]},
                    "order": 102,
                    "description": "Edited",
                    "readonly": True,
                    "visible": False,
                    "hidden": True,
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "queues/SUP/localFields/loc_edit",
                    json={
                        "name": {"ru": "Новое", "en": "New"},
                        "category": "cat-5",
                        "optionsProvider": {"type": "CustomListProvider", "values": ["r"]},
                        "order": 102,
                        "description": "Edited",
                        "readonly": True,
                        "visible": False,
                        "hidden": True,
                    },
                ),
                Reply(json={"key": "loc_edit", "order": 102}),
            )
        ],
    ),
    # Only the options passed are sent; there is no ?version= lock.
    Case(
        "tracker.localfields.update",
        args=("HR", "loc_order", LocalFieldUpdate(order=5, visible=True)),
        cli=["tracker", "localfields", "update", "HR", "loc_order", "--order", "5", "--visible"],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "PATCH", "queues/HR/localFields/loc_order", json={"order": 5, "visible": True}
                ),
                Reply(json={"key": "loc_order", "order": 5}),
            )
        ],
    ),
]
