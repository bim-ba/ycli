"""``ycli sync``: the content of Yandex 360 as files of a git repository.

The engine is ``ycli.yandex.sync``; a resource declares itself a kind of file to it.
"""

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.registry import kinds as declared_kinds
from ycli.yandex.sync.kind import KindSummary, summary_of

app = typer.Typer(name="sync", help="Yandex 360 content as files in git.", no_args_is_help=True)


@app.command()
def kinds() -> ItemList[KindSummary]:
    """List the kinds of object that can be kept as files, and what guards a write of each."""
    return ItemList[KindSummary]([summary_of(kind) for kind in declared_kinds()])
