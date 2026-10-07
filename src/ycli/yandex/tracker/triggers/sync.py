"""A trigger of a queue as a file: ``tracker/queues/<queue>/triggers/<id>.yaml``."""

from pydantic import Field

from ycli.yandex.sync.document import Link
from ycli.yandex.sync.formats import YAMLFile
from ycli.yandex.sync.kind import Kind, SentVersion
from ycli.yandex.tracker.triggers import endpoints
from ycli.yandex.tracker.triggers.models import TriggerUpdate


class TriggerLink(Link):
    """What ties a trigger file to its trigger."""

    id: int | None = Field(default=None, description="Id of the trigger.")
    version: int | None = Field(default=None, description="Version the trigger was read at.")


#: The API has no operation that deletes a trigger, so the kind names none.
TRIGGER = Kind(
    name="tracker/trigger",
    layout=YAMLFile(),
    link=TriggerLink,
    content=TriggerUpdate,
    find=endpoints.list_,
    read=endpoints.get,
    create=endpoints.create,
    update=endpoints.update,
    version=SentVersion(),
)
