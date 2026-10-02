"""EnvFile.upsert — back up, replace keys in place, preserve everything else."""

from dotenv import dotenv_values

from ycli.yandex.status.env_file import EnvFile


def test_upsert_creates_new_file(tmp_path):
    path = tmp_path / ".env"
    backup = EnvFile.upsert(
        path, {"YANDEX_ID_OAUTH_TOKEN": "tok", "YANDEX_ID_ORGANIZATION_ID": "org"}
    )
    assert backup is None
    assert dotenv_values(path) == {
        "YANDEX_ID_OAUTH_TOKEN": "tok",
        "YANDEX_ID_ORGANIZATION_ID": "org",
    }


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

    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[:3] == ["# a comment", "", "FOO=bar"]  # comment, blank, unrelated key kept
    assert dotenv_values(path) == {
        "FOO": "bar",
        "YANDEX_ID_OAUTH_TOKEN": "new",  # existing key replaced in place
        "YANDEX_ID_ORGANIZATION_ID": "org",  # missing key appended
    }


def test_upsert_replaces_an_export_line_instead_of_appending_a_duplicate(tmp_path):
    path = tmp_path / ".env"
    path.write_text("export YANDEX_ID_OAUTH_TOKEN=old\nFOO=bar\n", encoding="utf-8")

    EnvFile.upsert(path, {"YANDEX_ID_OAUTH_TOKEN": "new"})

    lines = path.read_text(encoding="utf-8").splitlines()
    assert [line for line in lines if "YANDEX_ID_OAUTH_TOKEN" in line] == [
        "YANDEX_ID_OAUTH_TOKEN=new"
    ]
    assert "FOO=bar" in lines
    assert dotenv_values(path) == {"YANDEX_ID_OAUTH_TOKEN": "new", "FOO": "bar"}


def test_upsert_keeps_the_file_and_its_backup_owner_only(tmp_path):
    path = tmp_path / ".env"
    path.write_text("FOO=bar\n", encoding="utf-8")
    path.chmod(0o644)

    backup = EnvFile.upsert(path, {"YANDEX_ID_OAUTH_TOKEN": "tok"})

    assert backup is not None
    assert path.stat().st_mode & 0o777 == 0o600
    assert backup.stat().st_mode & 0o777 == 0o600
