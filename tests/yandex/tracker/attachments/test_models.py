"""TDD for Tracker attachment models — full doc sample parse + list array."""

from ycli.yandex.tracker.attachments.models import Attachment, AttachmentList

SAMPLE = {
    "self": "https://api.tracker.yandex.net/v3/issues/JUNE-2/attachments/123",
    "id": "123",
    "name": "picture.jpg",
    "content": "https://api.tracker.yandex.net/v3/issues/JUNE-2/attachments/123/picture.jpg",
    "thumbnail": "https://api.tracker.yandex.net/v3/issues/JUNE-2/thumbnails/123",
    "createdBy": {"self": "…/users/11", "id": "11", "display": "Full Name"},
    "createdAt": "2017-06-11T05:11:12.347+0000",
    "mimetype": "image/jpg",
    "size": 19090,
    "metadata": {"size": "550x175"},
}


def test_attachment_parses_all_fields():
    attachment = Attachment.model_validate(SAMPLE)
    assert attachment.id == "123"
    assert attachment.name == "picture.jpg"
    assert attachment.created_by == "Full Name"  # createdBy object flattened to display
    assert attachment.created_at == "2017-06-11T05:11:12.347+0000"
    assert attachment.mimetype == "image/jpg"
    assert attachment.size == 19090
    assert attachment.self_url.endswith("/attachments/123")  # ty: ignore[unresolved-attribute]
    assert attachment.content.endswith("/picture.jpg")  # ty: ignore[unresolved-attribute]
    assert attachment.thumbnail.endswith("/thumbnails/123")  # ty: ignore[unresolved-attribute]
    assert attachment.metadata is not None
    assert attachment.metadata.size == "550x175"


def test_attachment_list_parses_array():
    out = AttachmentList.model_validate([SAMPLE, {"name": "notes.txt"}])
    assert isinstance(out, AttachmentList)
    assert [a.name for a in out.root] == ["picture.jpg", "notes.txt"]
    assert out.root[1].metadata is None  # absent metadata stays None
