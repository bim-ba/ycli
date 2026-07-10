"""EnvFile.upsert — back up, replace keys in place, preserve everything else."""

from ycli.yandex.status.env_file import EnvFile


def test_upsert_creates_new_file(tmp_path):
    path = tmp_path / ".env"
    backup = EnvFile.upsert(
        path, {"YANDEX_ID_OAUTH_TOKEN": "tok", "YANDEX_ID_ORGANIZATION_ID": "org"}
    )
    assert backup is None
    content = path.read_text(encoding="utf-8")
    assert "YANDEX_ID_OAUTH_TOKEN=tok" in content
    assert "YANDEX_ID_ORGANIZATION_ID=org" in content


def test_upsert_backs_up_and_preserves_other_lines(tmp_path):
    path = tmp_path / ".env"
    original = "# a comment\n\nFOO=bar\nYANDEX_ID_OAUTH_TOKEN=old\n"
    path.write_text(original, encoding="utf-8")

    backup = EnvFile.upsert(
        path, {"YANDEX_ID_OAUTH_TOKEN": "new", "YANDEX_ID_ORGANIZATION_ID": "org"}
    )

    assert backup is not None
    assert backup == tmp_path / ".env.bak"
    assert backup.read_text(encoding="utf-8") == original  # untouched original preserved

    content = path.read_text(encoding="utf-8")
    assert "# a comment" in content  # comment preserved (key is None)
    assert "FOO=bar" in content  # unrelated key preserved
    assert "YANDEX_ID_OAUTH_TOKEN=new" in content  # existing key replaced in place
    assert "YANDEX_ID_OAUTH_TOKEN=old" not in content
    assert "YANDEX_ID_ORGANIZATION_ID=org" in content  # missing key appended
