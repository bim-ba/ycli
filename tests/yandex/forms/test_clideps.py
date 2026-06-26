"""TDD for the forms CLI deps — lazy client build cached on ctx.obj."""
import click

from ycli.yandex.forms._clideps import forms_client
from ycli.yandex.forms.client import FormsClient


def test_forms_client_lazy_caches_on_ctx(monkeypatch):
    built = []

    def _fake_from_env(cls):
        built.append(1)
        return "CLIENT"

    monkeypatch.setattr(FormsClient, "from_env", classmethod(_fake_from_env))
    ctx = click.Context(click.Command("x"))  # typer.Context subclasses this; ctx.obj is all we touch
    ctx.obj = None
    assert forms_client(ctx) == "CLIENT"
    assert forms_client(ctx) == "CLIENT"  # cached — not rebuilt
    assert len(built) == 1
