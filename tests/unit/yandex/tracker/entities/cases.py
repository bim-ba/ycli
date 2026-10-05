"""Contract cases for Tracker ``/entities``: projects, portfolios, goals (see tests/contract/)."""

from tests.contract import Case, Reply, Sent, with_query
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.entities.models import (
    ACLInput,
    ACLPrincipalsInput,
    BulkChangeUpdate,
    ChecklistItemInput,
    ChecklistMove,
    CommentUpdate,
    DirectPermissionsUpdate,
    EntityCreate,
    EntityUpdate,
    LinkInput,
    PermissionsUpdate,
    ReportCreate,
)
from ycli.yandex.tracker.models import CommentCreate

ENTITY = {"id": "655f", "entityType": "project", "fields": {"summary": "Q4 launch"}}
COMMENT = {"id": 22, "longId": "lc22", "text": "Готово"}

CASES = [
    # ---- core -------------------------------------------------------------------------------
    Case(
        "tracker.entities.create",
        args=(
            "project",
            EntityCreate.model_validate(
                {
                    "fields": {
                        "summary": "Q4 launch",
                        "description": "Ship the launch",
                        "lead": "lead-1",
                        "author": "author-1",
                        "entityStatus": "in_progress",
                        "start": "2025-01-01T00:00:00.000+0000",
                        "end": "2025-03-31T00:00:00.000+0000",
                        "parentEntity": {"primary": "67f1"},
                        "teamUsers": ["user-2", "user-3"],
                        "tags": ["q4"],
                        "markupType": "md",
                    }
                }
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "create",
            "project",
            "--summary",
            "Q4 launch",
            "--description",
            "Ship the launch",
            "--lead",
            "lead-1",
            "--author",
            "author-1",
            "--status",
            "in_progress",
            "--start",
            "2025-01-01T00:00:00.000+0000",
            "--end",
            "2025-03-31T00:00:00.000+0000",
            "--parent",
            "67f1",
            "--team-user",
            "user-2",
            "--team-user",
            "user-3",
            "--tag",
            "q4",
            "--field",
            "fields[markupType]=md",
        ],
        mcp=(
            "tracker_entities_create",
            {
                "entity_type": "project",
                "body": {
                    "fields": {
                        "summary": "Q4 launch",
                        "description": "Ship the launch",
                        "lead": "lead-1",
                        "author": "author-1",
                        "entityStatus": "in_progress",
                        "start": "2025-01-01T00:00:00.000+0000",
                        "end": "2025-03-31T00:00:00.000+0000",
                        "parentEntity": {"primary": "67f1"},
                        "teamUsers": ["user-2", "user-3"],
                        "tags": ["q4"],
                        "markupType": "md",
                    }
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/project",
                    json={
                        "fields": {
                            "summary": "Q4 launch",
                            "description": "Ship the launch",
                            "lead": "lead-1",
                            "author": "author-1",
                            "entityStatus": "in_progress",
                            "start": "2025-01-01T00:00:00.000+0000",
                            "end": "2025-03-31T00:00:00.000+0000",
                            "parentEntity": {"primary": "67f1"},
                            "teamUsers": ["user-2", "user-3"],
                            "tags": ["q4"],
                            "markupType": "md",
                        }
                    },
                ),
                Reply(json=ENTITY),
            )
        ],
    ),
    # `-F` reaches a field with no option of its own by its path; an option wins over it.
    Case(
        "tracker.entities.create",
        args=(
            "goal",
            EntityCreate.model_validate({"fields": {"summary": "Original", "teamAccess": True}}),
        ),
        cli=[
            "tracker",
            "entities",
            "create",
            "goal",
            "--summary",
            "Original",
            "-F",
            "fields[summary]=Overridden",
            "-F",
            "fields[teamAccess]=true",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/goal",
                    json={"fields": {"summary": "Original", "teamAccess": True}},
                ),
                Reply(json={"id": "g1", "entityType": "goal"}),
            )
        ],
    ),
    Case(
        "tracker.entities.get",
        args=("goal", "g2"),
        kwargs={"expand": "attachments", "fields": "summary,keyResultItems"},
        cli=[
            "tracker",
            "entities",
            "get",
            "goal",
            "g2",
            "--expand",
            "attachments",
            "--fields",
            "summary,keyResultItems",
        ],
        mcp=(
            "tracker_entities_get",
            {
                "entity_type": "goal",
                "entity_id": "g2",
                "expand": "attachments",
                "fields": "summary,keyResultItems",
            },
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    "entities/goal/g2",
                    {"expand": "attachments", "fields": "summary,keyResultItems"},
                ),
                Reply(json={"id": "g2", "entityType": "goal", "fields": {"summary": "Ship"}}),
            )
        ],
    ),
    Case(
        "tracker.entities.get",
        args=("portfolio", "pf3"),
        cli=["tracker", "entities", "get", "portfolio", "pf3"],
        mcp=("tracker_entities_get", {"entity_type": "portfolio", "entity_id": "pf3"}),
        exchanges=[
            (Sent("GET", "entities/portfolio/pf3"), Reply(json={"id": "pf3"})),
        ],
    ),
    Case(
        "tracker.entities.update",
        args=(
            "project",
            "655f04",
            EntityUpdate.model_validate(
                {
                    "fields": {
                        "summary": "Renamed",
                        "description": "New text",
                        "lead": "lead-4",
                        "author": "author-4",
                        "entityStatus": "at_risk",
                        "start": "2025-04-01T00:00:00.000+0000",
                        "end": "2025-06-30T00:00:00.000+0000",
                        "parentEntity": {"primary": "67f4"},
                        "teamUsers": ["user-4"],
                        "tags": ["h1", "h2"],
                        "followers": ["follower-4"],
                    },
                    "comment": "Re-planned",
                }
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "update",
            "project",
            "655f04",
            "--summary",
            "Renamed",
            "--description",
            "New text",
            "--lead",
            "lead-4",
            "--author",
            "author-4",
            "--status",
            "at_risk",
            "--start",
            "2025-04-01T00:00:00.000+0000",
            "--end",
            "2025-06-30T00:00:00.000+0000",
            "--parent",
            "67f4",
            "--team-user",
            "user-4",
            "--tag",
            "h1",
            "--tag",
            "h2",
            "--comment",
            "Re-planned",
            "-F",
            'fields[followers]=["follower-4"]',
        ],
        mcp=(
            "tracker_entities_update",
            {
                "entity_type": "project",
                "entity_id": "655f04",
                "body": {
                    "fields": {
                        "summary": "Renamed",
                        "description": "New text",
                        "lead": "lead-4",
                        "author": "author-4",
                        "entityStatus": "at_risk",
                        "start": "2025-04-01T00:00:00.000+0000",
                        "end": "2025-06-30T00:00:00.000+0000",
                        "parentEntity": {"primary": "67f4"},
                        "teamUsers": ["user-4"],
                        "tags": ["h1", "h2"],
                        "followers": ["follower-4"],
                    },
                    "comment": "Re-planned",
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "entities/project/655f04",
                    json={
                        "fields": {
                            "summary": "Renamed",
                            "description": "New text",
                            "lead": "lead-4",
                            "author": "author-4",
                            "entityStatus": "at_risk",
                            "start": "2025-04-01T00:00:00.000+0000",
                            "end": "2025-06-30T00:00:00.000+0000",
                            "parentEntity": {"primary": "67f4"},
                            "teamUsers": ["user-4"],
                            "tags": ["h1", "h2"],
                            "followers": ["follower-4"],
                        },
                        "comment": "Re-planned",
                    },
                ),
                Reply(json={"id": "655f04"}),
            )
        ],
    ),
    # A comment alone sends no `fields`; fields alone send no `comment`.
    Case(
        "tracker.entities.update",
        args=("goal", "g5", EntityUpdate.model_validate({"comment": "Just a note"})),
        cli=["tracker", "entities", "update", "goal", "g5", "--comment", "Just a note"],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "entities/goal/g5", json={"comment": "Just a note"}),
                Reply(json={"id": "g5"}),
            )
        ],
    ),
    Case(
        "tracker.entities.update",
        args=(
            "portfolio",
            "pf6",
            EntityUpdate.model_validate({"fields": {"summary": "Only a name"}}),
        ),
        cli=["tracker", "entities", "update", "portfolio", "pf6", "--summary", "Only a name"],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "PATCH", "entities/portfolio/pf6", json={"fields": {"summary": "Only a name"}}
                ),
                Reply(json={"id": "pf6"}),
            )
        ],
    ),
    Case(
        "tracker.entities.delete",
        args=("project", "655f07"),
        kwargs={"with_board": True},
        cli=["tracker", "entities", "delete", "project", "655f07", "--with-board"],
        mcp=(
            "tracker_entities_delete",
            {"entity_type": "project", "entity_id": "655f07", "with_board": True},
        ),
        exchanges=[
            (Sent("DELETE", "entities/project/655f07", {"withBoard": "true"}), Reply(status=204)),
        ],
    ),
    Case(
        "tracker.entities.delete",
        args=("goal", "g8"),
        cli=["tracker", "entities", "delete", "goal", "g8"],
        mcp=("tracker_entities_delete", {"entity_type": "goal", "entity_id": "g8"}),
        exchanges=[(Sent("DELETE", "entities/goal/g8"), Reply(status=204))],
    ),
    Case(
        "tracker.entities.search",
        args=(
            "project",
            {
                "input": "Q4",
                "filter": {"entityStatus": "in_progress", "lead": "lead-9"},
                "orderBy": "entityStatus",
                "orderAsc": True,
                "rootOnly": True,
            },
        ),
        kwargs={"fields": "summary,lead"},
        cli=[
            "tracker",
            "entities",
            "search",
            "project",
            "--input-text",
            "Q4",
            "--filter",
            "entityStatus=in_progress",
            "--filter",
            "lead=lead-9",
            "--order-by",
            "entityStatus",
            "--order-asc",
            "--root-only",
            "--fields",
            "summary,lead",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/project/_search",
                    {"fields": "summary,lead"},
                    {
                        "input": "Q4",
                        "filter": {"entityStatus": "in_progress", "lead": "lead-9"},
                        "orderBy": "entityStatus",
                        "orderAsc": True,
                        "rootOnly": True,
                    },
                ),
                Reply(json={"hits": 1, "pages": 1, "values": [ENTITY]}),
            )
        ],
        effect=Effect.READ,
    ),
    Case(
        "tracker.entities.search",
        args=("goal", {"input": "Revenue"}),
        kwargs={"fields": "entityStatus"},
        cli=[
            "tracker",
            "entities",
            "search",
            "goal",
            "--input-text",
            "Revenue",
            "--fields",
            "entityStatus",
        ],
        mcp=(
            "tracker_entities_search",
            {"entity_type": "goal", "body": {"input": "Revenue"}, "fields": "entityStatus"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/goal/_search",
                    {"fields": "entityStatus"},
                    {"input": "Revenue"},
                ),
                Reply(json={"values": [{"id": "g10"}, {"id": "g11"}]}),
            )
        ],
        effect=Effect.READ,
    ),
    # The MCP tool sorts without stating a direction (the CLI's --order-by always sends one).
    Case(
        "tracker.entities.search",
        args=("portfolio", {"input": "Infra", "orderBy": "summary"}),
        cli=None,
        mcp=(
            "tracker_entities_search",
            {"entity_type": "portfolio", "body": {"input": "Infra", "orderBy": "summary"}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/portfolio/_search",
                    json={"input": "Infra", "orderBy": "summary"},
                ),
                Reply(json={"values": []}),
            )
        ],
        effect=Effect.READ,
    ),
    Case(
        "tracker.entities.search",
        args=("project",),
        cli=["tracker", "entities", "search", "project"],
        mcp=("tracker_entities_search", {"entity_type": "project", "body": {}}),
        exchanges=[
            (Sent("POST", "entities/project/_search", json={}), Reply(json={"values": []})),
        ],
        effect=Effect.READ,
    ),
    # Paging the search is SDK-only, and the SDK reads the one page asked for.
    Case(
        "tracker.entities.search",
        args=("goal", {"input": "Paged"}),
        kwargs={"per_page": 25, "page": 3},
        cli=None,
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/goal/_search",
                    {"perPage": "25", "page": "3"},
                    {"input": "Paged"},
                ),
                Reply(json={"hits": 80, "pages": 4, "values": [{"id": "g12"}]}),
            )
        ],
        effect=Effect.READ,
    ),
    # Drained from the last event's id until an empty page; the MCP default cap (500) and the
    # CLI's "all" both ask for full 100-event pages.
    Case(
        "tracker.entities.events_list",
        args=("project", "655f13"),
        cli=["tracker", "entities", "events-list", "project", "655f13"],
        mcp=("tracker_entities_events_list", {"entity_type": "project", "entity_id": "655f13"}),
        exchanges=[
            (
                Sent("GET", "entities/project/655f13/events/_relative", {"perPage": "100"}),
                Reply(json={"events": [{"id": "e1"}, {"id": "e2"}], "hasNext": True}),
            ),
            (
                Sent(
                    "GET",
                    "entities/project/655f13/events/_relative",
                    {"perPage": "100", "from": "e2"},
                ),
                Reply(json={"events": [], "hasNext": False}),
            ),
        ],
    ),
    # A limit narrows the page and stops once it is filled.
    Case(
        "tracker.entities.events_list",
        args=("goal", "g14"),
        kwargs={"limit": 2},
        cli=["tracker", "entities", "events-list", "goal", "g14", "--limit", "2"],
        mcp=(
            "tracker_entities_events_list",
            {"entity_type": "goal", "entity_id": "g14", "limit": 2},
        ),
        exchanges=[
            (
                Sent("GET", "entities/goal/g14/events/_relative", {"perPage": "2"}),
                Reply(json={"events": [{"id": "e3"}, {"id": "e4"}], "hasNext": True}),
            )
        ],
    ),
    Case(
        "tracker.entities.permissions_get",
        args=("project", "655f15"),
        cli=["tracker", "entities", "permissions-get", "project", "655f15"],
        mcp=(
            "tracker_entities_permissions_get",
            {"entity_type": "project", "entity_id": "655f15"},
        ),
        exchanges=[
            (
                Sent("GET", "entities/project/655f15/extendedPermissions"),
                Reply(
                    json={
                        "acl": {"READ": {"roles": ["OWNER"]}},
                        "permissionSources": [{"id": "67f15"}],
                    }
                ),
            )
        ],
    ),
    Case(
        "tracker.entities.permissions_update",
        args=(
            "portfolio",
            "pf16",
            PermissionsUpdate.model_validate(
                {
                    "acl": {
                        "grant": {"READ": {"users": ["8000000000000002"]}},
                        "revoke": {"WRITE": {"groups": ["42"]}},
                    }
                }
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "permissions-update",
            "portfolio",
            "pf16",
            "--acl",
            'grant={"READ":{"users":["8000000000000002"]}}',
            "--acl",
            'revoke={"WRITE":{"groups":["42"]}}',
        ],
        mcp=(
            "tracker_entities_permissions_update",
            {
                "entity_type": "portfolio",
                "entity_id": "pf16",
                "body": {
                    "acl": {
                        "grant": {"READ": {"users": ["8000000000000002"]}},
                        "revoke": {"WRITE": {"groups": ["42"]}},
                    }
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "entities/portfolio/pf16/extendedPermissions",
                    json={
                        "acl": {
                            "grant": {"READ": {"users": ["8000000000000002"]}},
                            "revoke": {"WRITE": {"groups": ["42"]}},
                        }
                    },
                ),
                Reply(json={"acl": {"READ": {"users": [{"id": "8000000000000002"}]}}}),
            )
        ],
    ),
    Case(
        "tracker.entities.update_bulk",
        args=(
            "project",
            BulkChangeUpdate.model_validate(
                {
                    "metaEntities": ["655f17", "655f18"],
                    "values": {"fields": {"lead": "lead-17"}, "comment": "Handed over"},
                }
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "update-bulk",
            "project",
            "--entity",
            "655f17",
            "--entity",
            "655f18",
            "--comment",
            "Handed over",
            "--field",
            "lead=lead-17",
        ],
        mcp=(
            "tracker_entities_update_bulk",
            {
                "entity_type": "project",
                "body": {
                    "metaEntities": ["655f17", "655f18"],
                    "values": {"fields": {"lead": "lead-17"}, "comment": "Handed over"},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/project/bulkchange/_update",
                    json={
                        "metaEntities": ["655f17", "655f18"],
                        "values": {"fields": {"lead": "lead-17"}, "comment": "Handed over"},
                    },
                ),
                Reply(json={"id": "656", "status": "CREATED"}),
            )
        ],
    ),
    Case(
        "tracker.entities.update_bulk",
        args=("goal", BulkChangeUpdate.model_validate({"metaEntities": ["g19"], "values": {}})),
        cli=["tracker", "entities", "update-bulk", "goal", "--entity", "g19"],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/goal/bulkchange/_update",
                    json={"metaEntities": ["g19"], "values": {}},
                ),
                Reply(json={"id": "657", "status": "CREATED"}),
            )
        ],
    ),
    Case(
        "tracker.entities.bulk_get",
        args=("658",),
        cli=["tracker", "entities", "bulk-get", "658"],
        mcp=("tracker_entities_bulk_get", {"bulk_id": "658"}),
        exchanges=[
            (Sent("GET", "bulkchange/658"), Reply(json={"id": "658", "status": "COMPLETE"})),
        ],
    ),
    Case(
        "tracker.entities.reports_create",
        args=(
            ReportCreate.model_validate(
                {
                    "fields": {
                        "summary": "Support export",
                        "parameters": {
                            "type": "issueFilterExport",
                            "format": "csv",
                            "filter": {"query": "Queue: SUPPORT"},
                            "fields": ["key", "summary", "assignee"],
                        },
                    }
                }
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "reports-create",
            "--type",
            "issueFilterExport",
            "--summary",
            "Support export",
            "--query",
            "Queue: SUPPORT",
            "--format",
            "csv",
            "-F",
            "key",
            "-F",
            "summary",
            "-F",
            "assignee",
        ],
        mcp=(
            "tracker_entities_reports_create",
            {
                "body": {
                    "fields": {
                        "summary": "Support export",
                        "parameters": {
                            "type": "issueFilterExport",
                            "format": "csv",
                            "filter": {"query": "Queue: SUPPORT"},
                            "fields": ["key", "summary", "assignee"],
                        },
                    }
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/report/",
                    json={
                        "fields": {
                            "summary": "Support export",
                            "parameters": {
                                "type": "issueFilterExport",
                                "format": "csv",
                                "filter": {"query": "Queue: SUPPORT"},
                                "fields": ["key", "summary", "assignee"],
                            },
                        }
                    },
                ),
                Reply(json={"id": "68f", "entityType": "report", "shortId": 142}),
            )
        ],
    ),
    # Only what the API requires: the type, the query and a column; no format.
    Case(
        "tracker.entities.reports_create",
        args=(
            ReportCreate.model_validate(
                {
                    "fields": {
                        "summary": "Default export",
                        "parameters": {
                            "type": "issueFilterExport",
                            "filter": {"query": "Queue: OPS"},
                            "fields": ["key"],
                        },
                    }
                }
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "reports-create",
            "--type",
            "issueFilterExport",
            "--summary",
            "Default export",
            "--query",
            "Queue: OPS",
            "--field",
            "key",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/report/",
                    json={
                        "fields": {
                            "summary": "Default export",
                            "parameters": {
                                "type": "issueFilterExport",
                                "filter": {"query": "Queue: OPS"},
                                "fields": ["key"],
                            },
                        }
                    },
                ),
                Reply(json={"id": "690", "entityType": "report"}),
            )
        ],
    ),
    # ---- comments ---------------------------------------------------------------------------
    Case(
        "tracker.entities.comments_list",
        args=("project", "655f20"),
        cli=["tracker", "entities", "comments", "list", "project", "655f20"],
        mcp=("tracker_entities_comments_list", {"entity_type": "project", "entity_id": "655f20"}),
        exchanges=[(Sent("GET", "entities/project/655f20/comments"), Reply(json=[COMMENT]))],
    ),
    Case(
        "tracker.entities.comments_list",
        args=("goal", "g21"),
        kwargs={"expand": "html"},
        cli=None,
        mcp=None,
        exchanges=[
            (Sent("GET", "entities/goal/g21/comments", {"expand": "html"}), Reply(json=[])),
        ],
    ),
    Case(
        "tracker.entities.comments_list_relative",
        args=("portfolio", "pf22"),
        kwargs={"limit": 10},
        cli=[
            "tracker",
            "entities",
            "comments",
            "list",
            "portfolio",
            "pf22",
            "--limit",
            "10",
        ],
        mcp=(
            "tracker_entities_comments_list_relative",
            {"entity_type": "portfolio", "entity_id": "pf22", "limit": 10},
        ),
        exchanges=[
            (
                Sent("GET", "entities/portfolio/pf22/comments/_relative", {"perPage": "10"}),
                Reply(
                    json={
                        "comments": [{"id": 31, "longId": "lc31"}, {"id": 32, "longId": "lc32"}],
                        "hasNext": True,
                    }
                ),
            ),
            (
                Sent(
                    "GET",
                    "entities/portfolio/pf22/comments/_relative",
                    {"perPage": "10", "from": "lc32"},
                ),
                Reply(json={"comments": [], "hasNext": False}),
            ),
        ],
    ),
    Case(
        "tracker.entities.comments_get",
        args=("project", "655f23", "23"),
        cli=["tracker", "entities", "comments", "get", "project", "655f23", "23"],
        mcp=(
            "tracker_entities_comments_get",
            {"entity_type": "project", "entity_id": "655f23", "comment_id": "23"},
        ),
        exchanges=[
            (
                Sent("GET", "entities/project/655f23/comments/23"),
                Reply(json={"id": 23, "longId": "lc23", "text": "hi"}),
            )
        ],
    ),
    Case(
        "tracker.entities.comments_get",
        args=("goal", "g24", "24"),
        kwargs={"expand": "reactions"},
        cli=None,
        mcp=None,
        exchanges=[
            (
                Sent("GET", "entities/goal/g24/comments/24", {"expand": "reactions"}),
                Reply(json={"id": 24}),
            )
        ],
    ),
    Case(
        "tracker.entities.comments_create",
        args=(
            "project",
            "655f25",
            CommentCreate.model_validate({"text": "Готово", "summonees": ["user-25", "user-26"]}),
        ),
        cli=[
            "tracker",
            "entities",
            "comments",
            "create",
            "project",
            "655f25",
            "--text",
            "Готово",
            "--summon",
            "user-25",
            "--summon",
            "user-26",
        ],
        mcp=(
            "tracker_entities_comments_create",
            {
                "entity_type": "project",
                "entity_id": "655f25",
                "body": {"text": "Готово", "summonees": ["user-25", "user-26"]},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/project/655f25/comments",
                    json={"text": "Готово", "summonees": ["user-25", "user-26"]},
                ),
                Reply(json=COMMENT, status=201),
            )
        ],
    ),
    # The comment id travels in the path: a PATCH on the collection answers 405.
    Case(
        "tracker.entities.comments_update",
        args=("goal", "g27", "27", CommentUpdate.model_validate({"text": "Fixed typo"})),
        cli=[
            "tracker",
            "entities",
            "comments",
            "update",
            "goal",
            "g27",
            "27",
            "--text",
            "Fixed typo",
        ],
        mcp=(
            "tracker_entities_comments_update",
            {
                "entity_type": "goal",
                "entity_id": "g27",
                "comment_id": "27",
                "body": {"text": "Fixed typo"},
            },
        ),
        exchanges=[
            (
                Sent("PATCH", "entities/goal/g27/comments/27", json={"text": "Fixed typo"}),
                Reply(json={"id": 27, "text": "Fixed typo"}),
            )
        ],
    ),
    Case(
        "tracker.entities.comments_delete",
        args=("portfolio", "pf28", "28"),
        cli=["tracker", "entities", "comments", "delete", "portfolio", "pf28", "28"],
        mcp=(
            "tracker_entities_comments_delete",
            {"entity_type": "portfolio", "entity_id": "pf28", "comment_id": "28"},
        ),
        exchanges=[(Sent("DELETE", "entities/portfolio/pf28/comments/28"), Reply(status=204))],
    ),
    # ---- checklists -------------------------------------------------------------------------
    Case(
        "tracker.entities.checklists_create",
        args=(
            "project",
            "655f29",
            ItemList[ChecklistItemInput].model_validate([{"text": "Draft"}, {"text": "Review"}]),
        ),
        cli=[
            "tracker",
            "entities",
            "checklists",
            "create",
            "project",
            "655f29",
            "--text",
            "Draft",
            "--text",
            "Review",
        ],
        mcp=(
            "tracker_entities_checklists_create",
            {
                "entity_type": "project",
                "entity_id": "655f29",
                "body": [{"text": "Draft"}, {"text": "Review"}],
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/project/655f29/checklistItems",
                    json=[{"text": "Draft"}, {"text": "Review"}],
                ),
                Reply(json={"id": "655f29"}),
            )
        ],
    ),
    Case(
        "tracker.entities.checklists_update",
        args=(
            "goal",
            "g30",
            ItemList[ChecklistItemInput].model_validate(
                [{"id": "5f", "text": "Renamed"}, {"id": "6a", "text": "Second"}]
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "checklists",
            "update",
            "goal",
            "g30",
            "--item",
            "5f=Renamed",
            "--item",
            "6a=Second",
        ],
        mcp=(
            "tracker_entities_checklists_update",
            {
                "entity_type": "goal",
                "entity_id": "g30",
                "body": [{"id": "5f", "text": "Renamed"}, {"id": "6a", "text": "Second"}],
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "entities/goal/g30/checklistItems",
                    json=[{"id": "5f", "text": "Renamed"}, {"id": "6a", "text": "Second"}],
                ),
                Reply(json={"id": "g30"}),
            )
        ],
    ),
    # Item text is never JSON-coerced, and only the first `=` splits.
    Case(
        "tracker.entities.checklists_update",
        args=(
            "project",
            "655f31",
            ItemList[ChecklistItemInput].model_validate(
                [
                    {"id": "7b", "text": "true"},
                    {"id": "8c", "text": "null"},
                    {"id": "9d", "text": "[1, 2]"},
                    {"id": "0e", "text": "a=b"},
                ]
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "checklists",
            "update",
            "project",
            "655f31",
            "--item",
            "7b=true",
            "--item",
            "8c=null",
            "--item",
            "9d=[1, 2]",
            "--item",
            "0e=a=b",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "entities/project/655f31/checklistItems",
                    json=[
                        {"id": "7b", "text": "true"},
                        {"id": "8c", "text": "null"},
                        {"id": "9d", "text": "[1, 2]"},
                        {"id": "0e", "text": "a=b"},
                    ],
                ),
                Reply(json={"id": "655f31"}),
            )
        ],
    ),
    Case(
        "tracker.entities.checklists_items_update",
        args=(
            "portfolio",
            "pf32",
            "1f",
            ChecklistItemInput.model_validate(
                {
                    "text": "Sign off",
                    "checked": True,
                    "assignee": "user-32",
                    "deadline": {"date": "2025-12-01T00:00:00.000+0000", "deadlineType": "date"},
                }
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "checklists",
            "items-update",
            "portfolio",
            "pf32",
            "1f",
            "--text",
            "Sign off",
            "--checked",
            "--assignee",
            "user-32",
            "--deadline",
            "2025-12-01T00:00:00.000+0000",
            "--deadline-type",
            "date",
        ],
        mcp=(
            "tracker_entities_checklists_items_update",
            {
                "entity_type": "portfolio",
                "entity_id": "pf32",
                "item_id": "1f",
                "body": {
                    "text": "Sign off",
                    "checked": True,
                    "assignee": "user-32",
                    "deadline": {"date": "2025-12-01T00:00:00.000+0000", "deadlineType": "date"},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "entities/portfolio/pf32/checklistItems/1f",
                    json={
                        "text": "Sign off",
                        "checked": True,
                        "assignee": "user-32",
                        "deadline": {
                            "date": "2025-12-01T00:00:00.000+0000",
                            "deadlineType": "date",
                        },
                    },
                ),
                Reply(json={"id": "pf32"}),
            )
        ],
    ),
    Case(
        "tracker.entities.checklists_items_update",
        args=("goal", "g33", "2f", ChecklistItemInput.model_validate({"checked": False})),
        cli=[
            "tracker",
            "entities",
            "checklists",
            "items-update",
            "goal",
            "g33",
            "2f",
            "--no-checked",
        ],
        mcp=None,
        exchanges=[
            (
                Sent("PATCH", "entities/goal/g33/checklistItems/2f", json={"checked": False}),
                Reply(json={"id": "g33"}),
            )
        ],
    ),
    Case(
        "tracker.entities.checklists_delete",
        args=("project", "655f34"),
        cli=["tracker", "entities", "checklists", "delete", "project", "655f34"],
        mcp=(
            "tracker_entities_checklists_delete",
            {"entity_type": "project", "entity_id": "655f34"},
        ),
        exchanges=[
            (
                Sent("DELETE", "entities/project/655f34/checklistItems"),
                Reply(json={"id": "655f34", "fields": {"checklistItems": []}}),
            )
        ],
    ),
    Case(
        "tracker.entities.checklists_items_delete",
        args=("goal", "g35", "3f"),
        cli=["tracker", "entities", "checklists", "items-delete", "goal", "g35", "3f"],
        mcp=(
            "tracker_entities_checklists_items_delete",
            {"entity_type": "goal", "entity_id": "g35", "item_id": "3f"},
        ),
        exchanges=[
            (Sent("DELETE", "entities/goal/g35/checklistItems/3f"), Reply(json={"id": "g35"})),
        ],
    ),
    Case(
        "tracker.entities.checklists_move",
        args=("portfolio", "pf36", "4f", ChecklistMove.model_validate({"before": "5a"})),
        cli=[
            "tracker",
            "entities",
            "checklists",
            "move",
            "portfolio",
            "pf36",
            "4f",
            "--before",
            "5a",
        ],
        mcp=(
            "tracker_entities_checklists_move",
            {
                "entity_type": "portfolio",
                "entity_id": "pf36",
                "item_id": "4f",
                "body": {"before": "5a"},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/portfolio/pf36/checklistItems/4f/_move",
                    json={"before": "5a"},
                ),
                Reply(json={"id": "pf36"}),
            )
        ],
    ),
    # Without --before the item moves to the top: an empty body.
    Case(
        "tracker.entities.checklists_move",
        args=("project", "655f37", "6f", ChecklistMove.model_validate({})),
        cli=["tracker", "entities", "checklists", "move", "project", "655f37", "6f"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "entities/project/655f37/checklistItems/6f/_move", json={}),
                Reply(json={"id": "655f37"}),
            )
        ],
    ),
    # ---- links ------------------------------------------------------------------------------
    Case(
        "tracker.entities.links_list",
        args=("project", "655f38"),
        cli=["tracker", "entities", "links", "list", "project", "655f38"],
        mcp=("tracker_entities_links_list", {"entity_type": "project", "entity_id": "655f38"}),
        exchanges=[
            (
                Sent("GET", "entities/project/655f38/links"),
                Reply(
                    json=[{"type": "relates", "linkFieldValues": {"summary": "Other", "id": "658"}}]
                ),
            )
        ],
    ),
    Case(
        "tracker.entities.links_list",
        args=("goal", "g39"),
        kwargs={"fields": "summary"},
        cli=None,
        mcp=None,
        exchanges=[
            (Sent("GET", "entities/goal/g39/links", {"fields": "summary"}), Reply(json=[])),
        ],
    ),
    Case(
        "tracker.entities.links_create",
        args=(
            "portfolio",
            "pf40",
            LinkInput.model_validate({"relationship": "depends on", "entity": "pf41"}),
        ),
        cli=[
            "tracker",
            "entities",
            "links",
            "create",
            "portfolio",
            "pf40",
            "--relationship",
            "depends on",
            "--entity",
            "pf41",
        ],
        mcp=(
            "tracker_entities_links_create",
            {
                "entity_type": "portfolio",
                "entity_id": "pf40",
                "body": {"relationship": "depends on", "entity": "pf41"},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/portfolio/pf40/links",
                    json={"relationship": "depends on", "entity": "pf41"},
                ),
                Reply(),
            )
        ],
    ),
    Case(
        "tracker.entities.links_delete",
        args=("goal", "g42", "g43"),
        cli=["tracker", "entities", "links", "delete", "goal", "g42", "g43"],
        mcp=(
            "tracker_entities_links_delete",
            {"entity_type": "goal", "entity_id": "g42", "right": "g43"},
        ),
        exchanges=[(Sent("DELETE", "entities/goal/g42/links", {"right": "g43"}), Reply())],
    ),
    # ---- attachments ------------------------------------------------------------------------
    Case(
        "tracker.entities.attachments_list",
        args=("project", "655f44"),
        cli=["tracker", "entities", "attachments", "list", "project", "655f44"],
        mcp=(
            "tracker_entities_attachments_list",
            {"entity_type": "project", "entity_id": "655f44"},
        ),
        exchanges=[
            (
                Sent("GET", "entities/project/655f44/attachments"),
                Reply(json=[{"id": "3", "name": "Shops.csv", "size": 559}]),
            )
        ],
    ),
    Case(
        "tracker.entities.attachments_get",
        args=("goal", "g45", "45"),
        cli=["tracker", "entities", "attachments", "get", "goal", "g45", "45"],
        mcp=(
            "tracker_entities_attachments_get",
            {"entity_type": "goal", "entity_id": "g45", "file_id": "45"},
        ),
        exchanges=[
            (
                Sent("GET", "entities/goal/g45/attachments/45"),
                Reply(json={"id": "45", "name": "flowers.jpg", "metadata": {"size": "236x295"}}),
            )
        ],
    ),
    Case(
        "tracker.entities.attachments_download",
        args=("46", "flowers.jpg"),
        cli=["tracker", "entities", "attachments", "download", "46", "flowers.jpg"],
        mcp=None,
        exchanges=[
            (Sent("GET", "attachments/46/flowers.jpg"), Reply(content=b"\xff\xd8\xff\xe0jpg")),
        ],
    ),
    Case(
        "tracker.entities.attachments_attach",
        args=("portfolio", "pf47", "tmp47"),
        cli=["tracker", "entities", "attachments", "attach", "portfolio", "pf47", "tmp47"],
        mcp=(
            "tracker_entities_attachments_attach",
            {"entity_type": "portfolio", "entity_id": "pf47", "temp_file_id": "tmp47"},
        ),
        exchanges=[
            (
                Sent("POST", "entities/portfolio/pf47/attachments/tmp47"),
                Reply(json={"id": "pf47", "entityType": "portfolio"}),
            )
        ],
    ),
    # The API answers the detach with an empty body.
    Case(
        "tracker.entities.attachments_delete",
        args=("project", "655f48", "48"),
        cli=["tracker", "entities", "attachments", "delete", "project", "655f48", "48"],
        mcp=(
            "tracker_entities_attachments_delete",
            {"entity_type": "project", "entity_id": "655f48", "file_id": "48"},
        ),
        exchanges=[(Sent("DELETE", "entities/project/655f48/attachments/48"), Reply())],
    ),
    Case(
        "tracker.entities.search",
        args=(
            "report",
            {"filter": {"author": "report-author"}, "orderBy": "createdAt"},
        ),
        cli=[
            "tracker",
            "entities",
            "search",
            "report",
            "--filter",
            "author=report-author",
            "--order-by",
            "createdAt",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "entities/report/_search",
                    json={
                        "filter": {"author": "report-author"},
                        "orderBy": "createdAt",
                    },
                ),
                Reply(
                    json={
                        "hits": 1,
                        "pages": 1,
                        "values": [
                            {
                                "self": "https://api.tracker.yandex.net/v3/entities/report/6a0d7cfb",
                                "id": "6a0d7cfb",
                                "version": 5,
                                "shortId": 185,
                                "entityType": "report",
                                "createdBy": {"id": "8000000000000005", "display": "Ann"},
                                "createdAt": "2026-05-20T09:20:59.753+0000",
                                "updatedAt": "2026-05-20T09:21:00.085+0000",
                            }
                        ],
                    }
                ),
            )
        ],
        effect=Effect.READ,
    ),
    # The MCP tool reaches the report type too, without the author filter the CLI offers.
    Case(
        "tracker.entities.search",
        args=("report", {"orderBy": "updatedAt"}),
        cli=None,
        mcp=(
            "tracker_entities_search",
            {"entity_type": "report", "body": {"orderBy": "updatedAt"}},
        ),
        exchanges=[
            (
                Sent("POST", "entities/report/_search", json={"orderBy": "updatedAt"}),
                Reply(json={"hits": 0, "pages": 0, "values": []}),
            )
        ],
        effect=Effect.READ,
    ),
    Case(
        "tracker.entities.permissions_get_direct",
        args=("project", "655f17"),
        cli=["tracker", "entities", "permissions-get-direct", "project", "655f17"],
        mcp=(
            "tracker_entities_permissions_get_direct",
            {"entity_type": "project", "entity_id": "655f17"},
        ),
        exchanges=[
            (
                Sent("GET", "entities/project/655f17/permissions"),
                Reply(
                    json={
                        "READ": {"users": [], "groups": [], "roles": []},
                        "GRANT": {
                            "users": [{"id": "8000000000000002", "display": "Ann"}],
                            "groups": [],
                            "roles": ["AUTHOR", "OWNER"],
                        },
                        "WRITE": {
                            "users": [],
                            "groups": [{"id": "5", "display": "All users"}],
                            "roles": ["CLIENT", "AUTHOR", "FOLLOWER", "OWNER", "MEMBER"],
                        },
                    }
                ),
            )
        ],
    ),
    Case(
        "tracker.entities.permissions_update_direct",
        args=(
            "goal",
            "g18",
            DirectPermissionsUpdate(
                grant=ACLInput(
                    read=ACLPrincipalsInput(users=["ann"], groups=["7"]),
                    write=ACLPrincipalsInput(roles=["MEMBER"]),
                ),
                revoke=ACLInput(grant=ACLPrincipalsInput(users=["bob"], roles=["OWNER"])),
            ),
        ),
        cli=[
            "tracker",
            "entities",
            "permissions-update-direct",
            "goal",
            "g18",
            "--grant",
            '{"READ": {"users": ["ann"], "groups": ["7"]}, "WRITE": {"roles": ["MEMBER"]}}',
            "--revoke",
            '{"GRANT": {"users": ["bob"], "roles": ["OWNER"]}}',
        ],
        mcp=(
            "tracker_entities_permissions_update_direct",
            {
                "entity_type": "goal",
                "entity_id": "g18",
                "body": {
                    "grant": {
                        "READ": {"users": ["ann"], "groups": ["7"]},
                        "WRITE": {"roles": ["MEMBER"]},
                    },
                    "revoke": {"GRANT": {"users": ["bob"], "roles": ["OWNER"]}},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "entities/goal/g18/permissions",
                    json={
                        "grant": {
                            "READ": {"users": ["ann"], "groups": ["7"]},
                            "WRITE": {"roles": ["MEMBER"]},
                        },
                        "revoke": {"GRANT": {"users": ["bob"], "roles": ["OWNER"]}},
                    },
                ),
                Reply(
                    json={
                        "READ": {
                            "users": [{"id": "11", "display": "Ann"}],
                            "groups": [],
                            "roles": [],
                        },
                        "GRANT": {"users": [], "groups": [], "roles": ["AUTHOR"]},
                        "WRITE": {"users": [], "groups": [], "roles": ["MEMBER"]},
                    }
                ),
            )
        ],
    ),
    # One side only: the other is left out of the body.
    Case(
        "tracker.entities.permissions_update_direct",
        args=(
            "portfolio",
            "pf19",
            DirectPermissionsUpdate(revoke=ACLInput(read=ACLPrincipalsInput(groups=["9"]))),
        ),
        cli=[
            "tracker",
            "entities",
            "permissions-update-direct",
            "portfolio",
            "pf19",
            "--revoke",
            '{"READ": {"groups": ["9"]}}',
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "entities/portfolio/pf19/permissions",
                    json={"revoke": {"READ": {"groups": ["9"]}}},
                ),
                Reply(json={"READ": {"users": [], "groups": [], "roles": []}}),
            )
        ],
    ),
]

# The query parameters the published API lists beyond the body (#196): what the reply carries
# and who is notified. Each case repeats the operation's first one with them.
_REPLY_AND_NOTICE = {
    "expand": "attachments",
    "fields": "checklistItems",
    "notify": False,
    "notify_author": True,
}
_REPLY_AND_NOTICE_CLI = [
    "--expand",
    "attachments",
    "--fields",
    "checklistItems",
    "--no-notify",
    "--notify-author",
]
_REPLY_AND_NOTICE_SENT = {
    "expand": "attachments",
    "fields": "checklistItems",
    "notify": "false",
    "notifyAuthor": "true",
}
_COMMENT = {"expand": "html", "is_add_to_followers": False, "notify": False, "notify_author": True}
_COMMENT_CLI = ["--expand", "html", "--no-is-add-to-followers", "--no-notify", "--notify-author"]
_COMMENT_SENT = {
    "expand": "html",
    "isAddToFollowers": "false",
    "notify": "false",
    "notifyAuthor": "true",
}
CASES += [
    with_query(
        CASES,
        "tracker.entities.create",
        kwargs={"fields": "summary"},
        cli=["--fields", "summary"],
        params={"fields": "summary"},
    ),
    with_query(
        CASES,
        "tracker.entities.update",
        kwargs={"expand": "attachments", "fields": "summary"},
        cli=["--expand", "attachments", "--fields", "summary"],
        params={"expand": "attachments", "fields": "summary"},
    ),
    with_query(
        CASES,
        "tracker.entities.attachments_attach",
        kwargs=_REPLY_AND_NOTICE,
        cli=_REPLY_AND_NOTICE_CLI,
        params=_REPLY_AND_NOTICE_SENT,
    ),
    with_query(
        CASES,
        "tracker.entities.checklists_create",
        kwargs=_REPLY_AND_NOTICE,
        cli=_REPLY_AND_NOTICE_CLI,
        params=_REPLY_AND_NOTICE_SENT,
    ),
    with_query(
        CASES,
        "tracker.entities.checklists_update",
        kwargs=_REPLY_AND_NOTICE,
        cli=_REPLY_AND_NOTICE_CLI,
        params=_REPLY_AND_NOTICE_SENT,
    ),
    with_query(
        CASES,
        "tracker.entities.checklists_items_update",
        kwargs=_REPLY_AND_NOTICE,
        cli=_REPLY_AND_NOTICE_CLI,
        params=_REPLY_AND_NOTICE_SENT,
    ),
    with_query(
        CASES,
        "tracker.entities.checklists_delete",
        kwargs=_REPLY_AND_NOTICE,
        cli=_REPLY_AND_NOTICE_CLI,
        params=_REPLY_AND_NOTICE_SENT,
    ),
    with_query(
        CASES,
        "tracker.entities.checklists_items_delete",
        kwargs=_REPLY_AND_NOTICE,
        cli=_REPLY_AND_NOTICE_CLI,
        params=_REPLY_AND_NOTICE_SENT,
    ),
    with_query(
        CASES,
        "tracker.entities.checklists_move",
        kwargs=_REPLY_AND_NOTICE,
        cli=_REPLY_AND_NOTICE_CLI,
        params=_REPLY_AND_NOTICE_SENT,
    ),
    with_query(
        CASES,
        "tracker.entities.comments_create",
        kwargs=_COMMENT,
        cli=_COMMENT_CLI,
        params=_COMMENT_SENT,
    ),
    with_query(
        CASES,
        "tracker.entities.comments_update",
        kwargs=_COMMENT,
        cli=_COMMENT_CLI,
        params=_COMMENT_SENT,
    ),
    with_query(
        CASES,
        "tracker.entities.comments_delete",
        kwargs={"notify": False, "notify_author": True},
        cli=["--no-notify", "--notify-author"],
        params={"notify": "false", "notifyAuthor": "true"},
    ),
    with_query(
        CASES,
        "tracker.entities.events_list",
        kwargs={"new_events_on_top": True, "direction": "backward"},
        cli=["--new-events-on-top", "--direction", "backward"],
        params={"newEventsOnTop": "true", "direction": "backward"},
    ),
]
CASES += [
    # ``selected`` asks for one window around an event: no following page is requested.
    Case(
        "tracker.entities.events_list",
        args=("portfolio", "pf15"),
        kwargs={"limit": 5, "selected": "e7"},
        cli=[
            "tracker",
            "entities",
            "events-list",
            "portfolio",
            "pf15",
            "--limit",
            "5",
            "--selected",
            "e7",
        ],
        mcp=(
            "tracker_entities_events_list",
            {"entity_type": "portfolio", "entity_id": "pf15", "limit": 5, "selected": "e7"},
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    "entities/portfolio/pf15/events/_relative",
                    {"perPage": "5", "selected": "e7"},
                ),
                Reply(json={"events": [{"id": "e7"}, {"id": "e6"}, {"id": "e8"}], "hasNext": True}),
            )
        ],
    ),
]
