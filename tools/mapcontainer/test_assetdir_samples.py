from __future__ import annotations

import os
import random
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import assetdir_samples as census  # noqa: E402
from testkit import rom_bytes  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
ROM = os.path.join(ROOT, "baserom.gba")


def test_the_canonical_image_censuses_to_143_entries_and_733911_bytes():
    rom = rom_bytes(ROM, size=0x800000)
    rows = census.entries(rom)
    assert len(rows) == 143
    assert census.totals(rows, 733911) == 733911


def test_the_kinds_are_the_flags_words_two_measured_halves():
    assert census.kind(0) == ("flags=0", "aux=0")
    assert census.kind(1) == ("flags=1", "aux=0")
    assert census.kind(0x00010001) == ("flags=1", "aux=set")
    assert census.kind(0x012C0003) == ("flags=3", "aux=set")


def test_a_total_that_is_not_the_contracts_is_refused():
    rows = [{"length": 10}, {"length": 5}]
    assert census.totals(rows, 15) == 15
    with pytest.raises(ValueError) as error:
        census.totals(rows, 16)
    assert "16" in str(error.value)


def test_each_in_tree_container_tag_is_recognised_at_a_blocks_start():
    assert census.containers(struct.pack("<II", 1, 40) + bytes(40))["webfoot"]
    assert census.containers(b"JCAL" + bytes(40))["jcalg1"]
    assert census.containers(bytes([0x10]) + bytes(40))["lz77-tag"]
    assert census.containers(bytes([0x30]) + bytes(40))["rle-tag"]
    assert not any(census.containers(bytes(40)).values())


def test_a_ramp_is_coherent_and_a_shuffled_block_is_not():
    ramp = bytes(range(128))
    ramp_row = census.coherence(ramp, [{"offset": 0, "length": len(ramp)}], draws=3)[0]
    assert ramp_row["real"] > 0.9
    assert abs(ramp_row["null"]) < 0.1
    rng = random.Random(7)
    noise = bytes(rng.randrange(256) for _ in range(4096))
    noise_row = census.coherence(noise, [{"offset": 0, "length": len(noise)}], draws=3)[0]
    assert abs(noise_row["real"] - noise_row["null"]) < census.COHERENT


def test_the_histogram_finds_the_mode_and_the_zero_centred_runs():
    rom = bytes(200) + bytes([1, 2, 3]) + bytes(10)
    stats = census.histogram(rom, [{"offset": 0, "length": len(rom)}])
    assert stats["total"] == 213
    assert stats["mode"] == 0
    assert stats["runs"] == 2
    assert stats["zero_run_share"] == 1.0


def test_a_fixed_stride_header_is_counted_and_an_open_stream_is_not():
    header = bytes([0xAA, 0xBB, 0xCC, 0xDD]) * 20
    ramp = bytes((index * 7) % 256 for index in range(80))
    rows = [{"offset": 0, "length": 80}, {"offset": 80, "length": 80}]
    assert census.constrained(header + ramp, rows, strides=(4,))[4] == 4

def test_the_statistic_is_the_hand_computed_pearson_value():
    assert census.correlation([-3, -1, 1, 3, -3], 1) == pytest.approx(-0.2)
    assert census.correlation([-3, -1, 1, 3, 1, 3, -3, -1], 4) == pytest.approx(-0.6)


def test_a_repeat_at_the_stored_lag_is_reported_as_a_loop():
    rng = random.Random(11)
    cycle = bytes(rng.randrange(128) for _ in range(128)) * 2
    stats = census.loop_test(cycle, [{"offset": 0, "length": len(cycle), "flags": 128 << 16}], draws=8)
    assert stats["lag"] > 0.99
    assert abs(stats["random_lag"]) < 0.2


def test_the_loop_test_counts_a_constant_tail_and_reads_the_stored_point():
    pattern = bytes([0, 1, 2, 3, 2, 1]) * 2
    rom = pattern + bytes(96 - len(pattern))
    stats = census.loop_test(rom, [{"offset": 0, "length": 96, "flags": 0x00040000}], draws=3)
    assert stats["tails"] == 1
    assert stats["constant_tails"] == 1
    assert stats["stored"] == 1.0
