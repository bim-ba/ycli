"""TDD for the binary CLI output helper — file-path branch and stdout branch."""

from __future__ import annotations

import io
import sys

import pytest

from ycli.cli.binary import write_output


def test_write_output_writes_raw_bytes_to_file(tmp_path):
    target = tmp_path / "download.bin"
    write_output(b"\x00\x01\x02payload", str(target))
    assert target.read_bytes() == b"\x00\x01\x02payload"  # verbatim, no serialization


@pytest.mark.parametrize("output", [None, "-"])
def test_write_output_streams_to_stdout_buffer(monkeypatch, output):
    fake_stdout = type("FakeStdout", (), {"buffer": io.BytesIO()})()
    monkeypatch.setattr(sys, "stdout", fake_stdout)
    write_output(b"BLOB", output)
    assert fake_stdout.buffer.getvalue() == b"BLOB"
