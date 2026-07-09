"""Model parsing for Tracker saved filters."""

from ycli.yandex.tracker.filters.models import Filter


def test_filter_parses_fields_permissions_and_owner():
    flt = Filter.model_validate(
        {
            "id": 12345,
            "self": "https://api.tracker.yandex.net/v3/filters/12345",
            "name": "My open issues",
            "filter": {"assignee": "me()"},
            "fields": [{"id": "key", "display": "Key"}, {"id": "summary", "display": "Summary"}],
            "groupBy": {"id": "status", "display": "Status"},
            "favorite": False,
            "permissions": {
                "READ": {"users": [], "groups": [{"id": "5", "display": "Everyone"}], "roles": []},
                "WRITE": {"users": [{"id": "1", "display": "Ivan"}], "groups": [], "roles": []},
            },
            "owner": {"id": "1", "display": "Ivan", "passportUid": 1},
        }
    )
    assert [f.id for f in flt.fields] == ["key", "summary"]
    assert flt.group_by.display == "Status"  # ty: ignore[unresolved-attribute]
    assert flt.permissions.read.groups[0].display == "Everyone"  # ty: ignore[unresolved-attribute]
    assert flt.permissions.write.users[0].display == "Ivan"  # ty: ignore[unresolved-attribute]
    assert flt.owner.passport_uid == 1  # ty: ignore[unresolved-attribute]
