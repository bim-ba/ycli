"""Contract cases for DataLens dashboards (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.dashboards.models import DashboardCreate, DashboardUpdate

DASH = "dash0000000001"
WB = "wb000000000001"
# The least a live `createDashboard` takes (measured through ycli, 2026-10-07): one tab
# with nothing on it, and every key here; DataLens answers 400 for a body without one.
TAB = {"id": "t1", "title": "Sales", "items": [], "layout": [], "connections": [], "aliases": {}}
# The document requires the first two settings and lets them be null: a live dashboard
# has them so, and DataLens refuses a save without them (#461).
SETTINGS = {
    "autoupdateInterval": None,
    "maxConcurrentRequests": None,
    "silentLoading": False,
    "dependentSelectors": True,
    "expandTOC": False,
}
DATA = {"counter": 1, "salt": "s", "settings": SETTINGS, "tabs": [TAB]}
# `meta` of a new dashboard must be an object: without it DataLens answers
# `400 entry.meta: expected record, received undefined` (measured, 2026-10-07).
NEW = {"workbookId": WB, "name": "Sales", "data": DATA, "meta": {}}
# `meta` of a dashboard to save is required too, and null when it has none.
CHANGE = {"entryId": DASH, "data": {**DATA, "counter": 2}, "meta": None}
# The document requires three fields with one value each: `scope`, an empty `type`, `version`.
ENTRY = {
    "entryId": DASH,
    "key": "Sales/Sales",
    "scope": "dash",
    "type": "",
    "version": 2,
    "workbookId": WB,
    "data": DATA,
    "revId": "rev1",
    "savedId": "rev1",
    "publishedId": "rev1",
}
SAVED = {**ENTRY, "data": CHANGE["data"], "revId": "rev2", "savedId": "rev2"}

CASES = [
    Case(
        "datalens.dashboards.get",
        args=(DASH,),
        kwargs={"branch": "saved"},
        cli=["datalens", "dashboards", "get", DASH, "--branch", "saved"],
        mcp=("datalens_dashboards_get", {"dashboard_id": DASH, "branch": "saved"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getDashboard", json={"dashboardId": DASH, "branch": "saved"}),
                Reply(json={"entry": ENTRY, "isFavorite": False}),
            )
        ],
    ),
    Case(
        "datalens.dashboards.get",
        args=(DASH,),
        kwargs={
            "rev_id": "rev1",
            "include_permissions": True,
            "include_links": False,
            "include_favorite": True,
            "workbook_id": WB,
        },
        cli=[
            *("datalens", "dashboards", "get", DASH, "--rev-id", "rev1"),
            *("--include-permissions", "--no-include-links", "--include-favorite"),
            *("--workbook-id", WB),
        ],
        mcp=(
            "datalens_dashboards_get",
            {
                "dashboard_id": DASH,
                "rev_id": "rev1",
                "include_permissions": True,
                "include_links": False,
                "include_favorite": True,
                "workbook_id": WB,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getDashboard",
                    json={
                        "dashboardId": DASH,
                        "revId": "rev1",
                        "includePermissions": True,
                        "includeLinks": False,
                        "includeFavorite": True,
                        "workbookId": WB,
                    },
                ),
                Reply(json={"entry": ENTRY, "isFavorite": False}),
            )
        ],
    ),
    Case(
        "datalens.dashboards.create",
        args=(DashboardCreate.model_validate(NEW),),
        cli=["datalens", "dashboards", "create", "--entry", json.dumps(NEW)],
        mcp=("datalens_dashboards_create", {"entry": NEW}),
        exchanges=[
            (
                Sent("POST", "rpc/createDashboard", json={"entry": NEW}),
                Reply(json={"entry": ENTRY}),
            )
        ],
    ),
    Case(
        "datalens.dashboards.update",
        args=(DashboardUpdate.model_validate(CHANGE),),
        kwargs={"mode": "save"},
        cli=["datalens", "dashboards", "update", "--mode", "save", "--entry", json.dumps(CHANGE)],
        mcp=("datalens_dashboards_update", {"entry": CHANGE, "mode": "save"}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/updateDashboard", json={"entry": CHANGE, "mode": "save"}),
                Reply(json={"entry": SAVED}),
            )
        ],
    ),
    Case(
        "datalens.dashboards.update",
        args=(DashboardUpdate.model_validate(CHANGE),),
        kwargs={"mode": "publish", "lock_token": "lock-token-1"},
        cli=[
            *("datalens", "dashboards", "update", "--mode", "publish"),
            *("--entry", json.dumps(CHANGE), "--lock-token", "lock-token-1"),
        ],
        mcp=(
            "datalens_dashboards_update",
            {"entry": CHANGE, "mode": "publish", "lock_token": "lock-token-1"},
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateDashboard",
                    json={"entry": CHANGE, "mode": "publish", "lockToken": "lock-token-1"},
                ),
                Reply(json={"entry": SAVED}),
            )
        ],
    ),
    Case(
        "datalens.dashboards.delete",
        args=(DASH,),
        cli=["datalens", "dashboards", "delete", DASH],
        mcp=("datalens_dashboards_delete", {"dashboard_id": DASH}),
        effect=Effect.DESTRUCTIVE,
        # Measured: 200 with `{}`.
        exchanges=[
            (Sent("POST", "rpc/deleteDashboard", json={"dashboardId": DASH}), Reply(json={}))
        ],
    ),
    Case(
        "datalens.dashboards.delete",
        args=(DASH,),
        kwargs={"lock_token": "lock-token-1"},
        cli=["datalens", "dashboards", "delete", DASH, "--lock-token", "lock-token-1"],
        mcp=("datalens_dashboards_delete", {"dashboard_id": DASH, "lock_token": "lock-token-1"}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/deleteDashboard",
                    json={"dashboardId": DASH, "lockToken": "lock-token-1"},
                ),
                Reply(json={}),
            )
        ],
    ),
]
