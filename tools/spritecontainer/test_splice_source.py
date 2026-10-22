from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import splice_source as splice  # noqa: E402


def carrier(tmp_path, lines):
    (tmp_path / "asm").mkdir()
    (tmp_path / "asm" / "carrier.s").write_text("\n".join(lines) + "\n", encoding="ascii")


def test_an_included_carrier_fills_the_hole_between_the_old_tokens(monkeypatch, tmp_path):
    monkeypatch.setattr(splice, "ROOT", str(tmp_path))
    carrier(tmp_path, ["INCBIN  baserom.gba_0x100_0x120.extracted"])
    lines = ["INCBIN  baserom.gba_0x80_0x100.extracted",
             "INCLUDE carrier.s",
             "INCBIN  baserom.gba_0x120_0x130.extracted"]
    assert splice.contiguous_rows(splice.old_spans(lines, 0, 2)) == [
        (0x80, 0x100), (0x100, 0x120), (0x120, 0x130)]


def test_a_label_only_carrier_names_no_byte(monkeypatch, tmp_path):
    monkeypatch.setattr(splice, "ROOT", str(tmp_path))
    carrier(tmp_path, ["\tEXPORT\t|unk_08000100|", "|unk_08000100|"])
    lines = ["INCBIN  baserom.gba_0x80_0x100.extracted",
             "INCLUDE carrier.s",
             "INCBIN  baserom.gba_0x100_0x120.extracted"]
    assert splice.contiguous_rows(splice.old_spans(lines, 0, 2)) == [
        (0x80, 0x100), (0x100, 0x120)]


def test_a_carrier_that_leaves_a_gap_in_its_hole_is_refused(monkeypatch, tmp_path):
    monkeypatch.setattr(splice, "ROOT", str(tmp_path))
    carrier(tmp_path, ["INCBIN  baserom.gba_0x100_0x110.extracted"])
    lines = ["INCBIN  baserom.gba_0x80_0x100.extracted",
             "INCLUDE carrier.s",
             "INCBIN  baserom.gba_0x120_0x130.extracted"]
    with pytest.raises(SystemExit, match="tile"):
        splice.contiguous_rows(splice.old_spans(lines, 0, 2))
