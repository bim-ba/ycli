"""Contract cases for Tracker ``/queues`` and ``/versions`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.queues.models import (
    IssueTypeConfigInput,
    QueueCreate,
    QueuePermissionScope,
    QueuePermissionSubjects,
    QueuePermissionsUpdate,
    QueueTagRemove,
    QueueVersionCreate,
    QueueVersionUpdate,
)

# A full first page (Tracker's 50) forces a second request; the short second page ends the walk.
FULL_PAGE = [{"id": str(index), "key": f"Q{index}"} for index in range(50)]
USER_ACCESS = {
    "user": {
        "self": "https://api.tracker.yandex.net/v3/users/11",
        "id": "11",
        "display": "Carol",
        "cloudUid": "ajeppa7dgp53",
        "passportUid": 1100,
    },
    "permissions": {
        "GRANT": {
            "roles": [
                {
                    "self": "https://api.tracker.yandex.net/v3/roles/queue-lead",
                    "id": "queue-lead",
                    "display": "Queue owner",
                }
            ]
        },
        "CREATE": {
            "users": [
                {
                    "self": "https://api.tracker.yandex.net/v3/users/11",
                    "id": "11",
                    "display": "Carol",
                    "passportUid": 1100,
                }
            ],
            "groups": [
                {
                    "self": "https://api.tracker.yandex.net/v3/groups/5",
                    "id": "5",
                    "display": "All users",
                }
            ],
        },
        "DENY": {"users": [{"id": "12", "display": "Dan"}]},
    },
    "components": [
        {
            "self": "https://api.tracker.yandex.net/v3/components/1",
            "id": "1",
            "display": "Component 1",
        }
    ],
}
QUEUE = {"id": "3", "key": "DESIGN", "name": "Design"}


def _listed(key: str) -> dict:
    """A queue as listed with only its key, every other field at its default."""
    unset = (
        "self", "id", "version", "name", "description", "lead", "assignAuto", "defaultType",
        "defaultPriority", "denyVoting",
    )  # fmt: skip
    empty = {"teamUsers": [], "issueTypes": [], "versions": [], "workflows": {}}
    return {"key": key, **dict.fromkeys(unset), **empty, "issueTypesConfig": []}


CASES = [
    Case(
        "tracker.queues.list",
        kwargs={"limit": 500},
        cli=["tracker", "queues", "list"],
        mcp=("tracker_queues_list", {}),
        exchanges=[
            (Sent("GET", "queues/", {"page": "1", "perPage": "50"}), Reply(json=FULL_PAGE)),
            (
                Sent("GET", "queues/", {"page": "2", "perPage": "50"}),
                Reply(json=[{"id": "50", "key": "TAIL"}]),
            ),
        ],
    ),
    Case(
        "tracker.queues.list",
        kwargs={"limit": 2},
        cli=["tracker", "queues", "list", "--limit", "2"],
        mcp=("tracker_queues_list", {"limit": 2}),
        exchanges=[
            (
                Sent("GET", "queues/", {"page": "1", "perPage": "50"}),
                Reply(json=[{"key": "A"}, {"key": "B"}, {"key": "C"}]),
            )
        ],
        output=[_listed("A"), _listed("B")],
    ),
    Case(
        "tracker.queues.list",
        kwargs={"limit": None},
        cli=["tracker", "queues", "list", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "queues/", {"page": "1", "perPage": "50"}),
                Reply(json=[{"key": "ALL1"}, {"key": "ALL2"}]),
            )
        ],
    ),
    Case(
        "tracker.queues.get",
        args=("TEST",),
        kwargs={"expand": "all"},
        cli=["tracker", "queues", "get", "TEST", "--expand", "all"],
        mcp=("tracker_queues_get", {"queue_id": "TEST", "expand": "all"}),
        exchanges=[
            (
                Sent("GET", "queues/TEST", {"expand": "all"}),
                Reply(json={"id": "4", "key": "TEST", "issueTypes": [{"key": "bug"}]}),
            )
        ],
    ),
    Case(
        "tracker.queues.get",
        args=("PLAIN",),
        cli=["tracker", "queues", "get", "PLAIN"],
        mcp=("tracker_queues_get", {"queue_id": "PLAIN"}),
        exchanges=[(Sent("GET", "queues/PLAIN"), Reply(json={"id": "5", "key": "PLAIN"}))],
    ),
    Case(
        "tracker.queues.tags",
        args=("TAGQ",),
        cli=["tracker", "queues", "tags", "TAGQ"],
        mcp=("tracker_queues_tags_list", {"queue_id": "TAGQ"}),
        exchanges=[(Sent("GET", "queues/TAGQ/tags"), Reply(json=["tag1", "tag2"]))],
    ),
    Case(
        "tracker.queues.versions",
        args=("VERQ",),
        cli=["tracker", "queues", "versions", "VERQ"],
        mcp=("tracker_queues_versions_list", {"queue_id": "VERQ"}),
        exchanges=[
            (
                Sent("GET", "queues/VERQ/versions"),
                Reply(json=[{"id": 1, "name": "v0.1", "queue": {"key": "VERQ"}}]),
            )
        ],
    ),
    Case(
        "tracker.queues.fields",
        args=("FLDQ",),
        cli=["tracker", "queues", "fields", "FLDQ"],
        mcp=("tracker_queues_fields_list", {"queue_id": "FLDQ"}),
        exchanges=[
            (
                Sent("GET", "queues/FLDQ/fields"),
                Reply(json=[{"id": "myfield", "schema": {"type": "string"}, "order": 222}]),
            )
        ],
    ),
    Case(
        "tracker.queues.create",
        args=(
            QueueCreate(
                key="DESIGN",
                name="Design",
                lead="lead-login",
                default_type="task",
                default_priority="normal",
                issue_types_config=[
                    IssueTypeConfigInput(
                        issueType="bug", workflow="oicn", resolutions=["wontFix", "fixed"]
                    )
                ],
            ),
        ),
        cli=[
            "tracker",
            "queues",
            "create",
            "--key",
            "DESIGN",
            "--name",
            "Design",
            "--lead",
            "lead-login",
            "--default-type",
            "task",
            "--default-priority",
            "normal",
            "--issue-type-config",
            '{"issueType": "bug", "workflow": "oicn", "resolutions": ["wontFix", "fixed"]}',
        ],
        mcp=(
            "tracker_queues_create",
            {
                "body": {
                    "key": "DESIGN",
                    "name": "Design",
                    "lead": "lead-login",
                    "default_type": "task",
                    "default_priority": "normal",
                    "issue_types_config": [
                        {
                            "issueType": "bug",
                            "workflow": "oicn",
                            "resolutions": ["wontFix", "fixed"],
                        }
                    ],
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "queues/",
                    json={
                        "key": "DESIGN",
                        "name": "Design",
                        "lead": "lead-login",
                        "defaultType": "task",
                        "defaultPriority": "normal",
                        "issueTypesConfig": [
                            {
                                "issueType": "bug",
                                "workflow": "oicn",
                                "resolutions": ["wontFix", "fixed"],
                            }
                        ],
                    },
                ),
                Reply(json=QUEUE, status=201),
            )
        ],
    ),
    # Without --issue-type-config no issueTypesConfig key is sent.
    Case(
        "tracker.queues.create",
        args=(
            QueueCreate(
                key="MIN", name="Minimal", lead="owner", default_type="bug", default_priority="low"
            ),
        ),
        cli=[
            "tracker",
            "queues",
            "create",
            "--key",
            "MIN",
            "--name",
            "Minimal",
            "--lead",
            "owner",
            "--default-type",
            "bug",
            "--default-priority",
            "low",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "queues/",
                    json={
                        "key": "MIN",
                        "name": "Minimal",
                        "lead": "owner",
                        "defaultType": "bug",
                        "defaultPriority": "low",
                    },
                ),
                Reply(json={"key": "MIN"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.queues.delete",
        args=("GONE",),
        cli=["tracker", "queues", "delete", "GONE"],
        mcp=("tracker_queues_delete", {"queue_id": "GONE"}),
        exchanges=[(Sent("DELETE", "queues/GONE"), Reply(status=204))],
    ),
    Case(
        "tracker.queues.restore",
        args=("BACK",),
        cli=["tracker", "queues", "restore", "BACK"],
        mcp=("tracker_queues_restore", {"queue_id": "BACK"}),
        exchanges=[(Sent("POST", "queues/BACK/_restore"), Reply(json={"id": "8", "key": "BACK"}))],
    ),
    Case(
        "tracker.queues.set_permissions",
        args=(
            "PERM",
            QueuePermissionsUpdate(
                create=QueuePermissionScope(roles=["author"]),
                write=QueuePermissionScope(users=QueuePermissionSubjects(add=["alice"])),
                read=QueuePermissionScope(groups=[17]),
                grant=QueuePermissionScope(roles=QueuePermissionSubjects(remove=["follower"])),
            ),
        ),
        cli=[
            "tracker",
            "queues",
            "permissions",
            "PERM",
            "--create",
            '{"roles": ["author"]}',
            "--write",
            '{"users": {"add": ["alice"]}}',
            "--read",
            '{"groups": [17]}',
            "--grant",
            '{"roles": {"remove": ["follower"]}}',
        ],
        mcp=(
            "tracker_queues_set_permissions",
            {
                "queue_id": "PERM",
                "body": {
                    "create": {"roles": ["author"]},
                    "write": {"users": {"add": ["alice"]}},
                    "read": {"groups": [17]},
                    "grant": {"roles": {"remove": ["follower"]}},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "queues/PERM/permissions",
                    json={
                        "create": {"roles": ["author"]},
                        "write": {"users": {"add": ["alice"]}},
                        "read": {"groups": [17]},
                        "grant": {"roles": {"remove": ["follower"]}},
                    },
                ),
                Reply(json={"version": 11}),
            )
        ],
    ),
    # Only the scopes passed are sent.
    Case(
        "tracker.queues.set_permissions",
        args=(
            "ONE",
            QueuePermissionsUpdate(
                grant=QueuePermissionScope(roles=QueuePermissionSubjects(add=["author"]))
            ),
        ),
        cli=[
            "tracker",
            "queues",
            "permissions",
            "ONE",
            "--grant",
            '{"roles": {"add": ["author"]}}',
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "queues/ONE/permissions",
                    json={"grant": {"roles": {"add": ["author"]}}},
                ),
                Reply(json={"version": 12}),
            )
        ],
    ),
    Case(
        "tracker.queues.tag_remove",
        args=("TAGGED", QueueTagRemove(tag="obsolete")),
        cli=["tracker", "queues", "tag-remove", "TAGGED", "obsolete"],
        mcp=("tracker_queues_tag_remove", {"queue_id": "TAGGED", "body": {"tag": "obsolete"}}),
        exchanges=[
            (
                Sent("POST", "queues/TAGGED/tags/_remove", json={"tag": "obsolete"}),
                Reply(status=204),
            )
        ],
        effect="destructive",
    ),
    Case(
        "tracker.queues.version_create",
        args=(
            QueueVersionCreate(
                queue="RELQ",
                name="v2.0",
                description="Second release",
                start_date="2023-10-03",
                due_date="2023-12-31",
            ),
        ),
        cli=[
            "tracker",
            "queues",
            "version-create",
            "--queue",
            "RELQ",
            "--name",
            "v2.0",
            "--description",
            "Second release",
            "--start-date",
            "2023-10-03",
            "--due-date",
            "2023-12-31",
        ],
        mcp=(
            "tracker_queues_version_create",
            {
                "body": {
                    "queue": "RELQ",
                    "name": "v2.0",
                    "description": "Second release",
                    "start_date": "2023-10-03",
                    "due_date": "2023-12-31",
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "versions/",
                    json={
                        "queue": "RELQ",
                        "name": "v2.0",
                        "description": "Second release",
                        "startDate": "2023-10-03",
                        "dueDate": "2023-12-31",
                    },
                ),
                Reply(json={"id": 5, "name": "v2.0"}, status=201),
            )
        ],
    ),
    # Empty optional options are left out of the body.
    Case(
        "tracker.queues.version_create",
        args=(QueueVersionCreate(queue="BARE", name="v0.1"),),
        cli=["tracker", "queues", "version-create", "--queue", "BARE", "--name", "v0.1"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "versions/", json={"queue": "BARE", "name": "v0.1"}),
                Reply(json={"id": 6, "name": "v0.1"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.queues.version_get",
        args=(901,),
        kwargs={"fields": "name,dueDate,released"},
        cli=["tracker", "queues", "version-get", "901", "--fields", "name,dueDate,released"],
        mcp=(
            "tracker_queues_version_get",
            {"version_id": 901, "fields": "name,dueDate,released"},
        ),
        exchanges=[
            (
                Sent("GET", "versions/901", {"fields": "name,dueDate,released"}),
                Reply(
                    json={
                        "self": "https://api.tracker.yandex.net/v3/versions/901",
                        "id": 901,
                        "version": 1,
                        "queue": {"id": "1", "key": "TEST", "display": "Test queue"},
                        "name": "Release 1.0",
                        "description": "First release",
                        "startDate": "2026-08-26",
                        "dueDate": "2026-08-27",
                        "released": False,
                        "archived": False,
                    }
                ),
            )
        ],
    ),
    Case(
        "tracker.queues.version_get",
        args=(902,),
        cli=["tracker", "queues", "version-get", "902"],
        mcp=None,
        exchanges=[(Sent("GET", "versions/902"), Reply(json={"id": 902, "name": "Plain"}))],
    ),
    Case(
        "tracker.queues.version_edit",
        args=(
            903,
            QueueVersionUpdate(
                name="Release 1.1",
                description="Renamed",
                start_date="2026-09-01",
                due_date="2026-09-30",
            ),
        ),
        kwargs={"fields": "name,description"},
        cli=[
            "tracker",
            "queues",
            "version-edit",
            "903",
            "--name",
            "Release 1.1",
            "--description",
            "Renamed",
            "--start-date",
            "2026-09-01",
            "--due-date",
            "2026-09-30",
            "--fields",
            "name,description",
        ],
        mcp=(
            "tracker_queues_version_edit",
            {
                "version_id": 903,
                "body": {
                    "name": "Release 1.1",
                    "description": "Renamed",
                    "start_date": "2026-09-01",
                    "due_date": "2026-09-30",
                },
                "fields": "name,description",
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "versions/903",
                    {"fields": "name,description"},
                    {
                        "name": "Release 1.1",
                        "description": "Renamed",
                        "startDate": "2026-09-01",
                        "dueDate": "2026-09-30",
                    },
                ),
                Reply(json={"id": 903, "version": 2, "name": "Release 1.1"}),
            )
        ],
    ),
    # Only the supplied fields are sent, and no ?version= lock goes with a version edit.
    Case(
        "tracker.queues.version_edit",
        args=(904, QueueVersionUpdate(due_date="2027-01-31")),
        cli=["tracker", "queues", "version-edit", "904", "--due-date", "2027-01-31"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "versions/904", json={"dueDate": "2027-01-31"}),
                Reply(json={"id": 904, "dueDate": "2027-01-31"}),
            )
        ],
    ),
    Case(
        "tracker.queues.version_delete",
        args=(905,),
        cli=["tracker", "queues", "version-delete", "905"],
        mcp=("tracker_queues_version_delete", {"version_id": 905}),
        exchanges=[(Sent("DELETE", "versions/905"), Reply(status=204))],
    ),
    Case(
        "tracker.queues.user_permissions",
        args=("PERMQ", "carol"),
        cli=["tracker", "queues", "user-permissions", "PERMQ", "carol"],
        mcp=("tracker_queues_user_permissions_get", {"queue_id": "PERMQ", "user_id": "carol"}),
        exchanges=[(Sent("GET", "queues/PERMQ/permissions/users/carol"), Reply(json=USER_ACCESS))],
    ),
    Case(
        "tracker.queues.group_permissions",
        args=("PERMG", 77),
        cli=["tracker", "queues", "group-permissions", "PERMG", "77"],
        mcp=("tracker_queues_group_permissions_get", {"queue_id": "PERMG", "group_id": 77}),
        exchanges=[
            (
                Sent("GET", "queues/PERMG/permissions/groups/77"),
                Reply(
                    json={
                        "group": {
                            "self": "https://api.tracker.yandex.net/v3/groups/77",
                            "id": "77",
                            "display": "Editors",
                        },
                        "permissions": {
                            "CREATE": {"groups": [{"id": "77", "display": "Editors"}]},
                            "READ": {"groups": [{"id": "77", "display": "Editors"}]},
                        },
                        "components": [{"id": "9", "display": "Component 9"}],
                    }
                ),
            )
        ],
    ),
]
