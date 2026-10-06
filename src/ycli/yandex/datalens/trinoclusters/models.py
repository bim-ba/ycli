"""DataLens Trino cluster models: the public names of the generated classes it uses."""

from ycli.yandex.datalens.schemas.trino_clusters import (
    AddTrinoClusterCatalogArgsCatalog as TrinoCatalogToAdd,
)
from ycli.yandex.datalens.schemas.trino_clusters import (
    CreateTrinoClusterArgsCatalogsConfigItem as TrinoNewCatalog,
)
from ycli.yandex.datalens.schemas.trino_clusters import (
    CreateTrinoClusterArgsWorkerConfig as TrinoWorkerConfig,
)
from ycli.yandex.datalens.schemas.trino_clusters import (
    ListTrinoClustersResult as TrinoClustersPage,
)
from ycli.yandex.datalens.schemas.trino_clusters import (
    ListTrinoResourcePresetsResult as TrinoResourcePresetsPage,
)
from ycli.yandex.datalens.schemas.trino_clusters import TrinoCluster, TrinoResourcePreset

__all__ = [
    "TrinoCatalogToAdd",
    "TrinoCluster",
    "TrinoClustersPage",
    "TrinoNewCatalog",
    "TrinoResourcePreset",
    "TrinoResourcePresetsPage",
    "TrinoWorkerConfig",
]
