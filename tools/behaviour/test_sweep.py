from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import testkit

import harness
import sweep


def image():
    return testkit.rom_bytes(os.path.join(harness.ROOT, "baserom.gba"),
                             digest=harness.ROM_SHA256, size=0x800000)


def test_the_probe_records_the_stores_and_the_calls_a_ran_start_makes():
    row = sweep.probe(image(), 0x08009220)
    assert [write for write in row["writes"]
            if 0x02000000 <= write[0] <= 0x0203FFFF] == [[0x02000000, 4, 0], [0x02000004, 4, 1],
                                                          [0x02000008, 4, 2], [0x0200000C, 4, 3]]
    assert row["calls"] == [0x08007A40] * 4


def test_the_probe_reports_why_a_start_the_harness_refuses_did_not_run():
    row = sweep.probe(image(), 0x0800FDFA)
    assert "why" in row
    assert "outside" in row["why"]
