from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import coverage_gap


LABELS = """gba-labels v1
rom-sha256 00
rom 08000100 t
rom 08000102 a
iwram 03000100 t
rom 08000104 t
"""

CHUNK = """static const RcgBlock rcg_blocks[] = {
{0x08000101u,g_08000100},
{0x08000102u,g_08000102},
{0x00000000u,g_00000000},
};
"""


def a_package(root, chunk=CHUNK, labels=LABELS):
    out = os.path.join(root, "out")
    os.makedirs(out)
    with open(os.path.join(out, "bf-bios.0.c"), "w", encoding="ascii", newline="\n") as handle:
        handle.write(chunk)
    path = os.path.join(root, "recorded.labels")
    with open(path, "w", encoding="ascii", newline="\n") as handle:
        handle.write(labels)
    return out, path


def test_a_recorded_point_is_covered_when_its_key_is_a_block(tmp_path):
    out, labels = a_package(str(tmp_path))
    keys = coverage_gap.blocks(out)
    points = coverage_gap.recorded(labels)
    assert keys == {0x08000101, 0x08000102, 0x00000000}
    assert coverage_gap.uncovered(keys, points) == [(0x03000100, "thumb", "iwram"),
                                                    (0x08000104, "thumb", "rom")]


def test_the_rom_and_iwram_counts_are_reported_separately(tmp_path, capsys):
    out, labels = a_package(str(tmp_path))
    csv_path = os.path.join(str(tmp_path), "missed.csv")
    assert coverage_gap.main(["--chunks", out, "--labels", labels, "--write", csv_path]) == 0
    printed = capsys.readouterr().out
    assert "covered 2 uncovered 2" in printed
    assert "rom 2 of 3" in printed
    assert "iwram 0 of 1" in printed
    with open(csv_path, encoding="ascii", newline="") as handle:
        assert handle.read().splitlines()[1:] == ["03000100,thumb,iwram", "08000104,thumb,rom"]


def test_a_chunk_directory_with_no_block_table_is_refused(tmp_path):
    out, labels = a_package(str(tmp_path), chunk="int nothing(void) { return 0; }\n")
    try:
        coverage_gap.main(["--chunks", out, "--labels", labels])
    except SystemExit as refused:
        assert "carries no block table" in str(refused)
    else:
        raise AssertionError("a directory with no block table was accepted")


