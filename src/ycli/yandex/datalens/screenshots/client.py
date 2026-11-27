"""DataLens screenshots client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.screenshots import endpoints

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ycli.yandex.datalens.screenshots.models import ImageType, Screenshot


class ScreenshotsClient(Resource):
    """Pictures of a saved dashboard or chart, rendered by DataLens; they change nothing.

    The section is experimental in the DataLens document. DataLens takes about three of these
    calls a minute and answers the next with ``429``; the session retries that with a back-off,
    honouring ``Retry-After`` when the reply has one. A call is a read, but the picture shows
    the data.
    """

    def dashboard_get(
        self,
        dash_id: str,
        *,
        type: ImageType | None = None,  # noqa: A002  # the API's own name for it
        base64: bool | None = None,
        s3: bool | None = None,
        width: int | float | None = None,
        height: int | float | None = None,
        full_page: bool | None = None,
        query_params: Mapping[str, Any] | None = None,
    ) -> Screenshot:
        """``getDashScreenshot`` → a picture of a dashboard: a link to its file, or the file.

        Args:
            dash_id: The dashboard's id.
            type: The format of the picture: ``png`` (the API's default), ``jpeg`` or ``jpg``.
            base64: Whether ``data`` holds the file itself, base64-encoded.
            s3: Whether the file is put in S3 and ``data`` is its link; the API does so unless
                ``base64`` is set.
            width: The width of the page in pixels, at most 6000.
            height: The height of the page in pixels, at most 6000.
            full_page: Whether the picture holds the whole tab rather than one screen of it.
            query_params: Parameters of the page: ``{"tab": "<tab id>"}`` picks a tab,
                ``{"_theme": "dark"}`` the dark theme; a dashboard parameter goes by its name.

        Returns:
            ``data``: the link to the file, or with ``base64`` the file in base64.

        Examples:
            The link is illustrative: the form of a real one is not measured.

            >>> datalens.screenshots.dashboard_get("d1a0000000001").data
            'https://s3.example.invalid/d1a0000000001.png'
        """
        return self._session.send(
            endpoints.dashboard_get(
                dash_id,
                type=type,
                base64=base64,
                s3=s3,
                width=width,
                height=height,
                full_page=full_page,
                query_params=query_params,
            )
        )

    def chart_get(
        self,
        chart_id: str,
        *,
        type: ImageType | None = None,  # noqa: A002  # the API's own name for it
        base64: bool | None = None,
        s3: bool | None = None,
        width: int | float | None = None,
        height: int | float | None = None,
        full_page: bool | None = None,
        query_params: Mapping[str, Any] | None = None,
    ) -> Screenshot:
        """``getChartScreenshot`` → a picture of a chart: a link to its file, or the file.

        Args:
            chart_id: The chart's id.
            type: The format of the picture: ``png`` (the API's default), ``jpeg`` or ``jpg``.
            base64: Whether ``data`` holds the file itself, base64-encoded.
            s3: Whether the file is put in S3 and ``data`` is its link; the API does so unless
                ``base64`` is set.
            width: The width of the page in pixels, at most 6000.
            height: The height of the page in pixels, at most 6000.
            full_page: Whether the picture holds the whole page rather than one screen of it.
            query_params: Parameters of the page: values of the chart's parameters by name,
                ``{"_theme": "dark"}`` for the dark theme.

        Returns:
            ``data``: the link to the file, or with ``base64`` the file in base64.

        Examples:
            >>> datalens.screenshots.chart_get("ch000000000007", base64=True).data
            'iVBORw0KGgo='
        """
        return self._session.send(
            endpoints.chart_get(
                chart_id,
                type=type,
                base64=base64,
                s3=s3,
                width=width,
                height=height,
                full_page=full_page,
                query_params=query_params,
            )
        )
