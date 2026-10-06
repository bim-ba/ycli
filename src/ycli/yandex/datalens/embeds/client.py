"""DataLens embeds client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.embeds import endpoints

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.datalens.embeds.models import Embed, EmbedDeleted, EmbedSettings
    from ycli.yandex.models import ItemList


class EmbedsClient(Resource):
    """Embeds: a chart or a dashboard shown on another site, signed with a key for embedding."""

    def list(self, entry_id: str) -> ItemList[Embed]:
        """``listEmbeds`` → the embeds of one entry.

        Args:
            entry_id: The id of the entry that is embedded.

        Returns:
            The embeds of the entry.

        Examples:
            >>> [embed.title for embed in datalens.embeds.list("ent0000000001").root]
            ['Sales on the portal']
        """
        return self._session.send(endpoints.list_(entry_id))

    def create(
        self,
        *,
        title: str,
        embedding_secret_id: str,
        entry_id: str,
        public_params_mode: bool,
        settings: EmbedSettings,
        deps_ids: Sequence[str] = (),
        unsigned_params: Sequence[str] = (),
        private_params: Sequence[str] = (),
    ) -> Embed:
        """``createEmbed`` — embed an entry → the embed.

        Args:
            title: The name of the embed.
            embedding_secret_id: The key for embedding that signs its links.
            entry_id: The entry to embed.
            public_params_mode: Whether the default mode of parameters is on.
            settings: The settings of the embed; an empty one is valid.
            deps_ids: The entries the embedded one depends on.
            unsigned_params: The parameters a link may carry unsigned.
            private_params: The parameters that go signed, inside the token.

        Returns:
            The embed.

        Examples:
            >>> from ycli.yandex.datalens.embeds.models import EmbedSettings
            >>> embed = datalens.embeds.create(
            ...     title="Sales on the portal",
            ...     embedding_secret_id="sec0000000001",
            ...     entry_id="ent0000000001",
            ...     public_params_mode=True,
            ...     settings=EmbedSettings(),
            ... )
            >>> embed.embed_id
            'emb0000000001'
        """
        return self._session.send(
            endpoints.create(
                title=title,
                embedding_secret_id=embedding_secret_id,
                entry_id=entry_id,
                public_params_mode=public_params_mode,
                settings=settings,
                deps_ids=deps_ids,
                unsigned_params=unsigned_params,
                private_params=private_params,
            )
        )

    def update(
        self,
        embed_id: str,
        *,
        title: str,
        embedding_secret_id: str,
        public_params_mode: bool,
        settings: EmbedSettings,
        deps_ids: Sequence[str] = (),
        unsigned_params: Sequence[str] = (),
        private_params: Sequence[str] = (),
    ) -> Embed:
        """``updateEmbed`` — save an embed as given → the embed.

        The embed is replaced whole: the API requires every field, so read the embed with
        :meth:`list` and send back what is to stay.

        Args:
            embed_id: The embed's id.
            title: The name of the embed.
            embedding_secret_id: The key for embedding that signs its links.
            public_params_mode: Whether the default mode of parameters is on.
            settings: The settings of the embed; an empty one is valid.
            deps_ids: The entries the embedded one depends on.
            unsigned_params: The parameters a link may carry unsigned.
            private_params: The parameters that go signed, inside the token.

        Returns:
            The embed as saved.

        Examples:
            >>> from ycli.yandex.datalens.embeds.models import EmbedSettings
            >>> embed = datalens.embeds.update(
            ...     "emb0000000001",
            ...     title="Sales, renamed",
            ...     embedding_secret_id="sec0000000001",
            ...     public_params_mode=False,
            ...     settings=EmbedSettings.model_validate({"enableExport": True}),
            ...     unsigned_params=["region"],
            ... )
            >>> embed.title
            'Sales, renamed'
        """
        return self._session.send(
            endpoints.update(
                embed_id,
                title=title,
                embedding_secret_id=embedding_secret_id,
                public_params_mode=public_params_mode,
                settings=settings,
                deps_ids=deps_ids,
                unsigned_params=unsigned_params,
                private_params=private_params,
            )
        )

    def delete(self, embed_id: str) -> EmbedDeleted:
        """``deleteEmbed`` — delete an embed → its id.

        Its links stop working. Deleting again answers ``404``.

        Args:
            embed_id: The embed's id.

        Returns:
            The id of the deleted embed.

        Examples:
            >>> datalens.embeds.delete("emb0000000001").embed_id
            'emb0000000001'
        """
        return self._session.send(endpoints.delete(embed_id))
