import pytest


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    """Shared Yandex 360 credentials for every test.

    autouse so tests that never request it explicitly (registration-only / annotation-only
    tests) still get valid env, matching the ~47 files that previously relied on a local
    autouse fixture. Tests that need NO credentials always delete these env vars themselves
    (in their own body, or a file-local autouse fixture that runs after this one, since
    conftest.py autouse fixtures execute before module-level ones of the same scope) — which
    correctly overrides this fixture regardless of the values it pre-set.
    """
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
