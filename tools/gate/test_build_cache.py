from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_cache
import gate


def test_the_key_follows_an_included_file(tmp_path):
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "buu.s").write_text("\tINCLUDE part.s\n", encoding="ascii")
    (asm / "part.s").write_text("|sub_08000000|\n\tBX lr\n", encoding="ascii")
    first = build_cache.digest(str(tmp_path), "asm/buu.s")
    (asm / "part.s").write_text("|sub_08000000|\n\tBX pc\n", encoding="ascii")
    assert build_cache.digest(str(tmp_path), "asm/buu.s") != first


def test_the_key_follows_an_incbin_slice(tmp_path):
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "buu.s").write_text("\tINCBIN a.extracted\n", encoding="ascii")
    (tmp_path / "a.extracted").write_bytes(b"\x01\x02")
    first = build_cache.digest(str(tmp_path), "asm/buu.s")
    (tmp_path / "a.extracted").write_bytes(b"\x01\x03")
    assert build_cache.digest(str(tmp_path), "asm/buu.s") != first


def test_a_missing_slice_changes_the_key(tmp_path):
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "buu.s").write_text("\tINCBIN a.extracted\n", encoding="ascii")
    absent = build_cache.digest(str(tmp_path), "asm/buu.s")
    (tmp_path / "a.extracted").write_bytes(b"\x01\x02")
    assert build_cache.digest(str(tmp_path), "asm/buu.s") != absent


def test_a_kept_object_is_restored_without_assembling(tmp_path, monkeypatch):
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "buu.s").write_text("|sub_08000000|\n\tBX lr\n", encoding="ascii")
    source, output = build_cache.UNITS["buu"]
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "buu.o").write_bytes(b"object")
    build_cache.keep(str(tmp_path), "buu", source, output)
    (tmp_path / "build" / "buu.o").unlink()

    def refuse(*_args, **_kwargs):
        raise AssertionError("assembled an unchanged unit")

    monkeypatch.delenv(build_cache.COLD_ENV, raising=False)
    monkeypatch.setattr(build_cache.subprocess, "call", refuse)
    assert build_cache.main(["buu"], root=str(tmp_path)) == 0
    assert (tmp_path / "build" / "buu.o").read_bytes() == b"object"


def test_a_cold_build_assembles_again(tmp_path, monkeypatch):
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "buu.s").write_text("|sub_08000000|\n\tBX lr\n", encoding="ascii")
    source, output = build_cache.UNITS["buu"]
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "buu.o").write_bytes(b"object")
    build_cache.keep(str(tmp_path), "buu", source, output)
    calls = []

    def assemble(argv, cwd=None):
        calls.append((argv, cwd))
        (tmp_path / "build" / "buu.o").write_bytes(b"object")
        return 0

    monkeypatch.setenv(build_cache.COLD_ENV, "1")
    monkeypatch.setattr(build_cache.subprocess, "call", assemble)
    assert build_cache.main(["buu"], root=str(tmp_path)) == 0
    assert calls and calls[0][0][0] == "armasm"


def test_a_missing_slice_is_reported_and_one_present_is_not(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "ROOT", gate.ROOT)
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "sub_08000000.s").write_text("\tINCBIN a.extracted\n", encoding="ascii")
    assert build_cache.slices(str(tmp_path)) == 1
    (tmp_path / "a.extracted").write_bytes(b"\x01")
    assert build_cache.slices(str(tmp_path)) == 0


def prepared(root):
    tools = root / "tools"
    tools.mkdir(exist_ok=True)
    (tools / "emit.py").write_text("print(1)\n", encoding="ascii")
    (root / "baserom.gba").write_bytes(b"rom")
    for name in build_cache.EMIT_OUTPUTS:
        path = root.joinpath(*name.split("/"))
        if "." in name:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"out")
        else:
            path.mkdir(parents=True, exist_ok=True)


def test_the_stamp_holds_until_an_output_or_a_tool_changes(tmp_path, monkeypatch):
    prepared(tmp_path)
    monkeypatch.delenv(build_cache.COLD_ENV, raising=False)
    assert not build_cache.emit_ready(str(tmp_path))
    build_cache.emit_record(str(tmp_path))
    assert build_cache.emit_ready(str(tmp_path))
    (tmp_path / "tools" / "emit.py").write_text("print(2)\n", encoding="ascii")
    assert not build_cache.emit_ready(str(tmp_path))
    build_cache.emit_record(str(tmp_path))
    (tmp_path / "build" / "strings.cpp").unlink()
    assert not build_cache.emit_ready(str(tmp_path))


def test_a_cold_build_never_restores_the_section_stamp(tmp_path, monkeypatch):
    prepared(tmp_path)
    build_cache.emit_record(str(tmp_path))
    monkeypatch.delenv(build_cache.COLD_ENV, raising=False)
    assert build_cache.emit_ready(str(tmp_path))
    monkeypatch.setenv(build_cache.COLD_ENV, "1")
    assert not build_cache.emit_ready(str(tmp_path))

