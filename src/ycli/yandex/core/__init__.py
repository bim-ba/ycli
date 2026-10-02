"""The HTTP core on ``httpx2``: declare an :class:`~ycli.yandex.core.endpoint.Endpoint`, send it.

- ``endpoint`` — ``Endpoint[T]`` (method, path, body, response type, effect) and ``Paged``.
- ``pagination`` — one class per kind of Yandex pagination, stateless and I/O-free.
- ``session`` — ``SyncSession`` / ``AsyncSession`` and ``connect`` / ``connect_async``: typed
  errors, retries, logging, page walking.
- ``auth`` — ``httpx2.Auth`` for every Yandex auth kind; ``profile`` — ``ServiceProfile``.
- ``resource`` — ``Resource``, the base of every resource client.
"""
