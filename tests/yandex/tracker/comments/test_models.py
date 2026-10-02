"""Model parsing for Tracker comments: the full ``GET …/comments/{id}?expand=all`` sample."""

from ycli.yandex.tracker.comments.models import Comment

SAMPLE = {
    "self": "https://api.tracker.yandex.net/v3/issues/JUNE-2/comments/123456",
    "id": 123456,
    "longId": "5fa15a24ac894475aa",
    "text": "My **first** comment",
    "textHtml": "<p>My <strong>first</strong> comment</p>\n",
    "attachments": [
        {
            "self": "https://api.tracker.yandex.net/v3/issues/JUNE-3/attachments/1",
            "id": "1",
            "display": "Untitled.png",
        }
    ],
    "createdBy": {"self": "…/users/11", "id": "11", "display": "Full Name"},
    "updatedBy": {"self": "…/users/12", "id": "12", "display": "Other Name"},
    "createdAt": "2017-06-11T05:11:12.347+0000",
    "updatedAt": "2017-06-12T05:11:12.347+0000",
    "version": 2,
    "type": "standard",
    "transport": "internal",
}


def test_comment_parses_the_full_get_reply():
    comment = Comment.model_validate(SAMPLE)
    assert comment.id == 123456 and comment.long_id == "5fa15a24ac894475aa"
    assert comment.created_by == "Full Name" and comment.updated_by == "Other Name"
    assert comment.text_html is not None and comment.text_html.startswith("<p>")
    assert comment.attachments is not None and comment.attachments[0].display == "Untitled.png"
    assert (comment.version, comment.type, comment.transport) == (2, "standard", "internal")


def test_comment_without_expand_has_no_html_or_attachments():
    comment = Comment.model_validate({"id": 1, "text": "plain"})
    assert comment.text_html is None and comment.attachments is None
