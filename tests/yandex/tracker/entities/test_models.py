"""TDD for entities models — read parsing (aliases + nesting) and typed write-body dumps."""

from ycli.yandex.tracker.entities.models import (
    AclInput,
    AclPrincipalsInput,
    Attachment,
    BulkChangeOperation,
    BulkChangeUpdate,
    BulkChangeValues,
    ChecklistItemInput,
    ChecklistItemsInput,
    ChecklistMove,
    Comment,
    CommentCreate,
    CommentUpdate,
    DeadlineInput,
    Entity,
    EntityCreate,
    EntityEvent,
    EntityFieldsInput,
    EntityUpdate,
    ExtendedPermissions,
    ExtendedPermissionsUpdate,
    Link,
    ParentEntityInput,
)

# ---- read models -------------------------------------------------------------------------


def test_entity_parses_envelope_and_nested_fields():
    entity = Entity.model_validate(
        {
            "self": "u",
            "id": "655f",
            "version": 3,
            "shortId": 2,
            "entityType": "project",
            "createdBy": {"id": "11", "display": "Имя"},
            "attachments": [{"id": "9", "name": "f.pdf"}],
            "fields": {
                "summary": "Q4",
                "teamAccess": True,
                "author": {"display": "Автор"},
                "teamUsers": [{"display": "U1"}],
                "parentEntity": {"primary": {"id": "67f", "display": "Portfolio"}, "secondary": []},
                "checklistItems": [{"id": "5f", "text": "step", "checked": False}],
                "progressPercentage": 0.5,
                "issueQueues": [{"key": "DE", "display": "Data"}],
            },
        }
    )
    assert entity.short_id == 2 and entity.entity_type == "project"
    assert entity.created_by is not None and entity.created_by.display == "Имя"
    assert entity.attachments[0].name == "f.pdf"
    assert entity.fields is not None
    assert entity.fields.summary == "Q4" and entity.fields.team_access is True
    assert entity.fields.author is not None and entity.fields.author.display == "Автор"
    assert entity.fields.team_users[0].display == "U1"
    assert entity.fields.parent_entity is not None
    assert entity.fields.parent_entity.primary is not None
    assert entity.fields.parent_entity.primary.id == "67f"
    assert entity.fields.checklist_items[0].text == "step"
    assert entity.fields.progress_percentage == 0.5
    assert entity.fields.issue_queues[0].key == "DE"


def test_entity_key_result_item_with_progress_and_deadline():
    entity = Entity.model_validate(
        {
            "id": "1",
            "entityType": "goal",
            "fields": {
                "keyResultItems": [
                    {
                        "id": "k1",
                        "text": "Grow",
                        "type": "value",
                        "achieved": False,
                        "assignee": {"display": "Отв"},
                        "deadline": {"date": "2025-12-01", "deadlineType": "date"},
                        "progress": {"start": 0, "end": 100, "current": 40},
                    }
                ]
            },
        }
    )
    assert entity.fields is not None
    kr = entity.fields.key_result_items[0]
    assert kr.type == "value" and kr.achieved is False
    assert kr.assignee is not None and kr.assignee.display == "Отв"
    assert kr.deadline is not None and kr.deadline.deadline_type == "date"
    assert kr.progress is not None and kr.progress.current == 40.0


def test_attachment_metadata_parses():
    att = Attachment.model_validate(
        {"id": "5", "name": "f.jpg", "size": 20466, "metadata": {"size": "236x295"}}
    )
    assert att.size == 20466 and att.metadata is not None and att.metadata.size == "236x295"


def test_comment_aliases():
    comment = Comment.model_validate(
        {"id": 22, "longId": "lc1", "text": "hi", "createdBy": {"display": "A"}, "version": 1}
    )
    assert comment.long_id == "lc1"
    assert comment.created_by is not None and comment.created_by.display == "A"


def test_link_parses_field_values():
    link = Link.model_validate({"type": "relates", "linkFieldValues": {"summary": "S", "id": "1"}})
    assert link.type == "relates"
    assert link.link_field_values is not None and link.link_field_values.id == "1"


def test_entity_event_with_changes():
    event = EntityEvent.model_validate(
        {
            "id": "e1",
            "author": {"display": "A"},
            "display": "Issue updated",
            "changes": [{"diff": "<added>x</added>", "field": {"id": "teamUsers", "display": "P"}}],
        }
    )
    assert event.display == "Issue updated"
    assert event.changes[0].field is not None and event.changes[0].field.id == "teamUsers"


def test_extended_permissions_parses_acl():
    perms = ExtendedPermissions.model_validate(
        {
            "acl": {
                "READ": {
                    "users": [{"id": "11"}],
                    "groups": [{"id": "1", "display": "G"}],
                    "roles": [],
                },
                "GRANT": {"roles": ["OWNER"]},
            },
            "permissionSources": [{"id": "67f"}],
        }
    )
    assert perms.acl is not None
    assert perms.acl.read is not None and perms.acl.read.groups[0].display == "G"
    assert perms.acl.grant is not None and perms.acl.grant.roles == ["OWNER"]
    assert perms.permission_sources[0].id == "67f"


def test_bulk_change_operation_aliases():
    op = BulkChangeOperation.model_validate(
        {"id": "656", "status": "CREATED", "executionChunkPercent": 0, "executionIssuePercent": 10}
    )
    assert op.execution_chunk_percent == 0 and op.execution_issue_percent == 10


# ---- typed write bodies ------------------------------------------------------------------


def test_entity_create_wraps_fields():
    body = EntityCreate(fields=EntityFieldsInput(summary="Q4", lead="u1")).model_dump(
        by_alias=True, exclude_none=True
    )
    assert body == {"fields": {"summary": "Q4", "lead": "u1"}}


def test_entity_fields_input_parent_and_aliases():
    body = EntityFieldsInput(
        summary="Q4",
        team_access=True,  # ty: ignore[unknown-argument]
        markup_type="md",  # ty: ignore[unknown-argument]
        team_users=["u1"],  # ty: ignore[unknown-argument]
        parent_entity=ParentEntityInput(primary="67f", secondary=["68a"]),  # ty: ignore[unknown-argument]
        entity_status="in_progress",  # ty: ignore[unknown-argument]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "summary": "Q4",
        "teamAccess": True,
        "markupType": "md",
        "teamUsers": ["u1"],
        "parentEntity": {"primary": "67f", "secondary": ["68a"]},
        "entityStatus": "in_progress",
    }


def test_entity_update_optional():
    body = EntityUpdate(comment="done").model_dump(by_alias=True, exclude_none=True)
    assert body == {"comment": "done"}


def test_comment_create_and_update():
    assert CommentCreate(text="hi", summonees=["u1"]).model_dump(
        by_alias=True, exclude_none=True
    ) == {"text": "hi", "summonees": ["u1"]}
    assert CommentUpdate(id=22, text="fixed").model_dump(by_alias=True, exclude_none=True) == {
        "id": 22,
        "text": "fixed",
    }


def test_checklist_items_input_and_deadline():
    body = ChecklistItemsInput(
        [
            ChecklistItemInput(text="a"),
            ChecklistItemInput(
                id="5f", text="b", checked=True, deadline=DeadlineInput(date="2025-12-01")
            ),
        ]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == [
        {"text": "a"},
        {
            "id": "5f",
            "text": "b",
            "checked": True,
            "deadline": {"date": "2025-12-01", "deadlineType": "date"},
        },
    ]


def test_checklist_move():
    assert ChecklistMove(before="6a").model_dump(by_alias=True, exclude_none=True) == {
        "before": "6a"
    }


def test_extended_permissions_update():
    body = ExtendedPermissionsUpdate(
        acl=AclInput(read=AclPrincipalsInput(roles=["OWNER"], users=["11"]))  # ty: ignore[unknown-argument]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {"acl": {"READ": {"users": ["11"], "roles": ["OWNER"]}}}


def test_bulk_change_update():
    body = BulkChangeUpdate(  # ty: ignore[missing-argument]
        meta_entities=["1", "2"],  # ty: ignore[unknown-argument]
        values=BulkChangeValues(fields={"lead": "u1"}, comment="done"),
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "metaEntities": ["1", "2"],
        "values": {"fields": {"lead": "u1"}, "comment": "done"},
    }
