"""Contract cases for the DataLens tenant (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

TENANT = {
    "tenantId": "org_bpf00000000000000000",
    "orgId": "bpf00000000000000000",
    "settings": {"defaultColorPaletteId": "classic20"},
    "dlpEnabled": False,
    "foldersEnabled": False,
}

CASES = [
    Case(
        "datalens.tenant.details_get",
        cli=["datalens", "tenant", "details-get"],
        mcp=("datalens_tenant_details_get", {}),
        effect=Effect.READ,
        exchanges=[(Sent("POST", "rpc/getTenantDetails"), Reply(json=TENANT))],
    ),
]
