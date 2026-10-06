import pytest
from pydantic import SecretStr, ValidationError

from ycli.yandex.models import WIRE, Ack, APIModel, DisplayStr, KeyStr, RequestBody, _extract


def test_a_reply_keeps_a_field_the_model_does_not_declare():
    cfg = APIModel.model_config
    assert cfg["extra"] == "allow"
    assert cfg["validate_by_name"] is True
    # Runtime behaviour, not just the config dict: a field Yandex adds shows up at once, untyped.
    instance = APIModel.model_validate({"brandNew": {"nested": 1}})
    assert instance.model_dump() == {"brandNew": {"nested": 1}}


def test_a_request_body_refuses_a_field_the_model_does_not_declare():
    class Rename(RequestBody):
        name: str

    assert RequestBody.model_config["extra"] == "forbid"
    with pytest.raises(ValidationError, match="nmae"):
        Rename.model_validate({"name": "Sprint", "nmae": "typo"})


def test_extract_pulls_field_from_wrapper_and_passes_scalars_through():
    pull = _extract("key")
    assert pull({"key": "x", "display": "X"}) == "x"  # wrapper → bare field
    assert pull("already-flat") == "already-flat"  # scalar passes through
    assert pull(None) is None  # None passes through
    assert _extract("display")({"display": "d"}) == "d"


def test_ref_annotations_accept_a_bare_scalar():
    from pydantic import TypeAdapter

    assert TypeAdapter(KeyStr).validate_python("flat") == "flat"
    assert TypeAdapter(DisplayStr).validate_python({"display": "d"}) == "d"


def test_ack_defaults_ok_true_and_detail_empty():
    ack = Ack()
    assert ack.ok is True and ack.detail == ""


def test_ack_deleted_bare():
    assert Ack.deleted("board", 5) == Ack(detail="deleted board 5")


def test_ack_deleted_with_on():
    assert Ack.deleted("column", 5, on="board 73") == Ack(detail="deleted column 5 on board 73")


def test_ack_deleted_with_from():
    assert Ack.deleted("macro", 3, from_="queue TEST") == Ack(
        detail="deleted macro 3 from queue TEST"
    )


def test_ack_published():
    assert Ack.published("survey", "686d") == Ack(detail="published survey 686d")


def test_ack_unpublished():
    assert Ack.unpublished("survey", "686d") == Ack(detail="unpublished survey 686d")


def test_ack_linked():
    assert Ack.linked("project", "655f", "658", "relates") == Ack(
        detail="linked project 655f -> 658 (relates)"
    )


def test_ack_unlinked():
    assert Ack.unlinked("project", "655f", "658") == Ack(detail="unlinked project 655f -> 658")


def test_ack_removed():
    assert Ack.removed("tag", "obsolete", from_="queue TEST") == Ack(
        detail="removed tag 'obsolete' from queue TEST"
    )


def test_ack_cleared():
    assert Ack.cleared("search scroll resources") == Ack(detail="cleared search scroll resources")


SECRET = "S3cret-value"


class _Login(RequestBody):
    user: str
    password: SecretStr | None = None


class _Source(RequestBody):
    host: str
    login: _Login
    spares: list[_Login] | None = None
    headers: dict[str, SecretStr] | None = None
    tokens: list[SecretStr] | None = None


def _source() -> _Source:
    # A caller gives a secret as the plain string it is.
    return _Source.model_validate(
        {
            "host": "db",
            "login": {"user": "reader", "password": SECRET},
            "spares": [{"user": "second", "password": SECRET}],
            "headers": {"Authorization": SECRET},
            "tokens": [SECRET],
        }
    )


def test_a_request_carries_a_secret_as_it_is_and_nothing_else_does():
    """#388, both sides: the value goes out in a request body; every other view masks it."""
    source = _source()
    assert source.model_dump(mode="json", context=WIRE) == {
        "host": "db",
        "login": {"user": "reader", "password": SECRET},
        "spares": [{"user": "second", "password": SECRET}],
        "headers": {"Authorization": SECRET},
        "tokens": [SECRET],
    }
    for seen in (
        source.model_dump_json(),  # what a command prints and a tool returns
        repr(source.model_dump()),
        repr(source),
        str(source),
    ):
        assert SECRET not in seen and "**********" in seen
    assert source.login.password is not None
    assert source.login.password.get_secret_value() == SECRET  # the SDK reads it on purpose


def test_a_secret_left_out_of_a_dump_is_not_put_back():
    wire = _source().model_dump(mode="json", context=WIRE, exclude={"headers", "tokens"})
    assert "headers" not in wire and wire["login"]["password"] == SECRET
    assert _Login(user="reader").model_dump(mode="json", context=WIRE) == {"user": "reader"}


@pytest.mark.parametrize(
    "body",
    [
        {"host": "db", "login": {"user": "reader", "password": {"value": SECRET}}},
        {"host": "db", "login": {"user": 1, "password": SECRET}},
        {"host": "db", "login": {"user": "reader", "password": SECRET}, "typo": SECRET},
    ],
)
def test_an_error_about_a_body_does_not_quote_the_body(body):
    """A value that fails validation is raw: no ``SecretStr`` has been built to mask it."""
    with pytest.raises(ValidationError) as refused:
        _Source.model_validate(body)
    assert SECRET not in str(refused.value)
    assert refused.value.errors()[0]["loc"]  # the field is still named


def test_a_generated_connection_keeps_its_secret_out_of_everything_but_the_request():
    """A member of a union, and the union refused by its tag before any secret is built."""
    from ycli.yandex.datalens.schemas.connection import ConnectionCreate, UpdateConnectionRequest

    new = {"type": "clickhouse", "name": "Sales", "host": "db", "password": SECRET}
    made = ConnectionCreate.model_validate(new)
    assert made.model_dump(mode="json", context=WIRE) == new
    assert SECRET not in made.model_dump_json() and SECRET not in repr(made)
    change = UpdateConnectionRequest.model_validate(
        {"connectionId": "c1", "data": {"secret_headers": {"Authorization": SECRET}}}
    )
    sent = change.model_dump(mode="json", context=WIRE)
    assert sent["data"]["secret_headers"] == {"Authorization": SECRET}
    assert SECRET not in change.model_dump_json()
    # A value that is no object fits no kind; what it held is not quoted.
    with pytest.raises(ValidationError) as refused:
        ConnectionCreate.model_validate([SECRET])
    assert SECRET not in str(refused.value)


def test_the_secrets_of_forms_reach_the_request_and_nothing_else():
    """An API key of a form and the secret of a subscription's variable (#388)."""
    from ycli.yandex.forms.subscriptions.models import SubscriptionVariable
    from ycli.yandex.forms.surveys.models import SurveyAPIKey
    from ycli.yandex.models import secret_keys

    key = SurveyAPIKey.model_validate({"name": "crm", "value": SECRET})
    assert key.model_dump(mode="json", context=WIRE) == {"name": "crm", "value": SECRET}
    variable = SubscriptionVariable.model_validate({"id": "v1", "type": "x", "secret": SECRET})
    assert variable.model_dump(mode="json", context=WIRE)["secret"] == SECRET
    for model in (key, variable):
        assert SECRET not in model.model_dump_json() and SECRET not in repr(model)
    assert secret_keys(SurveyAPIKey) == {"value"}
    assert secret_keys(SubscriptionVariable) == {"secret"}
