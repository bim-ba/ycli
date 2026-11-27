"""Contract cases for DataLens screenshots (see tests/contract/)."""

import base64

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

# The live reply with `base64` (2026-11-26) is `{"data": <base64>}`, no `data:` prefix in front.
# A picture is cut to its first bytes here.
PNG = b"\x89PNG\r\n\x1a\n"
ENCODED = base64.b64encode(PNG).decode()
# An illustrative link on a host that does not exist: a reply without `base64` was not
# read live, so the form of a real one is not measured.
LINK = "https://s3.example.invalid/d1a0000000001.png"

CASES = [
    Case(
        "datalens.screenshots.dashboard_get",
        args=("d1a0000000001",),
        cli=["datalens", "screenshots", "dashboard-get", "d1a0000000001"],
        mcp=("datalens_screenshots_dashboard_get", {"dash_id": "d1a0000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getDashScreenshot", json={"dashId": "d1a0000000001"}),
                Reply(json={"data": LINK}),
            )
        ],
    ),
    Case(
        "datalens.screenshots.dashboard_get",
        args=("d2a0000000002",),
        kwargs={
            "type": "jpeg",
            "base64": False,
            "s3": True,
            "width": 1920,
            "height": 1080,
            "full_page": False,
            "query_params": {"tab": "tab__3", "_theme": "dark"},
        },
        cli=[
            *("datalens", "screenshots", "dashboard-get", "d2a0000000002", "--type", "jpeg"),
            *("--no-base64", "--s3", "--width", "1920", "--height", "1080", "--no-full-page"),
            *("--query-params", '{"tab": "tab__3", "_theme": "dark"}'),
        ],
        mcp=(
            "datalens_screenshots_dashboard_get",
            {
                "dash_id": "d2a0000000002",
                "type": "jpeg",
                "base64": False,
                "s3": True,
                "width": 1920,
                "height": 1080,
                "full_page": False,
                "query_params": {"tab": "tab__3", "_theme": "dark"},
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getDashScreenshot",
                    json={
                        "dashId": "d2a0000000002",
                        "type": "jpeg",
                        "base64": False,
                        "s3": True,
                        "width": 1920,
                        "height": 1080,
                        "fullPage": False,
                        "queryParams": {"tab": "tab__3", "_theme": "dark"},
                    },
                ),
                Reply(json={"data": "https://s3.example.invalid/d2a0000000002.jpeg"}),
            )
        ],
    ),
    # --output asks for the picture in the reply and writes it, decoded.
    Case(
        "datalens.screenshots.dashboard_get",
        args=("d3a0000000003",),
        kwargs={"base64": True},
        cli=["datalens", "screenshots", "dashboard-get", "d3a0000000003", "--output", "-"],
        mcp=None,
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getDashScreenshot",
                    json={"dashId": "d3a0000000003", "base64": True},
                ),
                Reply(json={"data": ENCODED}),
            )
        ],
        cli_output=PNG,
    ),
    Case(
        "datalens.screenshots.chart_get",
        args=("ch000000000007",),
        kwargs={"base64": True},
        cli=["datalens", "screenshots", "chart-get", "ch000000000007", "--output", "-"],
        mcp=None,
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getChartScreenshot",
                    json={"chartId": "ch000000000007", "base64": True},
                ),
                Reply(json={"data": ENCODED}),
            )
        ],
        cli_output=PNG,
    ),
    Case(
        "datalens.screenshots.chart_get",
        args=("ch000000000008",),
        kwargs={
            "type": "png",
            "s3": False,
            "width": 800,
            "height": 600,
            "full_page": True,
            "query_params": {"year": ["2025", "2026"]},
        },
        cli=[
            *("datalens", "screenshots", "chart-get", "ch000000000008", "--type", "png"),
            *("--no-s3", "--width", "800", "--height", "600", "--full-page"),
            *("--query-params", '{"year": ["2025", "2026"]}'),
        ],
        mcp=(
            "datalens_screenshots_chart_get",
            {
                "chart_id": "ch000000000008",
                "type": "png",
                "s3": False,
                "width": 800,
                "height": 600,
                "full_page": True,
                "query_params": {"year": ["2025", "2026"]},
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getChartScreenshot",
                    json={
                        "chartId": "ch000000000008",
                        "type": "png",
                        "s3": False,
                        "width": 800,
                        "height": 600,
                        "fullPage": True,
                        "queryParams": {"year": ["2025", "2026"]},
                    },
                ),
                # Written from the document: what neither base64 nor S3 replies is not measured.
                Reply(json={"status": 400, "code": "ERR.SCREENSHOT", "message": "no output"}),
            )
        ],
    ),
]
