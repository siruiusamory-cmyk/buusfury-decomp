from __future__ import annotations

import csv
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import generate_tilebank as generator
import pngsheet
import tilebank

ROM = os.path.join(generator.ROOT, "baserom.gba")
ASSETS = os.path.join(generator.ROOT, "assets", "tilebank")
MANIFEST = os.path.join(HERE, "tilebank_manifest.csv")
NAME = "test_the_187_tile_banks_round_trip_byte_for_byte"
NEEDS_SHEETS = pytest.mark.skipif(not os.path.exists(os.path.join(ASSETS, generator.REFUSALS)),
                                  reason="no extracted sheets: run extract.cmd")
HAND = (bytearray([10, 20, 30, 5, 5, 9]), 3, 2)
HAND_FILTERED = {
    1: bytes([10, 10, 10, 5, 0, 4]),
    2: bytes([10, 20, 30, 251, 241, 235]),
    3: bytes([10, 15, 20, 0, 249, 248]),
    4: bytes([10, 10, 10, 251, 241, 245]),
}


def refused(call):
    try:
        call()
    except (tilebank.TileBankError, pngsheet.SheetError):
        return True
    return False


def hand_png(path, filter_type):
    width, height = HAND[1], HAND[2]
    filtered = HAND_FILTERED[filter_type]
    raw = bytearray()
    for row in range(height):
        raw.append(filter_type)
        raw += filtered[row * width:(row + 1) * width]
    blob = pngsheet.SIGNATURE
    blob += pngsheet._chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))
    blob += pngsheet._chunk(b"PLTE", bytes(range(96)))
    blob += pngsheet._chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    blob += pngsheet._chunk(b"IEND", b"")
    open(path, "wb").write(blob)


def test_a_short_re_encode_is_padded_with_zeros():
    header = struct.pack("<II", 1, 4)
    bank = tilebank.Bank(1, 4, b"abcd", 12)
    assert tilebank.encode(bank, lambda payload: header + b"\x05") == header + b"\x05" + bytes(3)


def test_a_re_encode_outside_the_zero_tail_rule_is_refused():
    header = struct.pack("<II", 1, 4)
    bank = tilebank.Bank(1, 4, b"abcd", 12)
    assert refused(lambda: tilebank.encode(bank, lambda payload: header + bytes(20)))
    assert refused(lambda: tilebank.encode(bank, lambda payload: header + bytes(4) + b"\x09"))
    assert refused(lambda: tilebank.encode(bank, lambda payload: struct.pack("<II", 1, 5) + bytes(4)))


def test_a_bank_that_overruns_its_slot_or_the_block_is_refused():
    header = struct.pack("<II", 1, 4)
    bank = tilebank.Bank(1, 4, b"abcd", 12)
    compress = lambda payload: header + bytes(4)  # noqa: E731
    assert refused(lambda: tilebank.encode_block([bank], [0], 8, compress))
    assert refused(lambda: tilebank.encode_block([bank, bank], [0, 4], 128, compress))


def test_an_indexed_png_round_trips_and_the_sheet_is_a_tile_grid():
    good = bytes(range(256)) * 64
    width, height, indices = pngsheet.sheet_of(good)
    assert (width, height) == (128, 128)
    scratch = tempfile.mkdtemp(prefix="tilebank-png-")
    try:
        path = os.path.join(scratch, "sheet.png")
        pngsheet.write_indexed(path, width, height, indices, [(1, 2, 3)] * 256)
        read_width, read_height, read, palette = pngsheet.read_indexed(path)
        assert (read_width, read_height) == (width, height)
        assert bytes(read) == bytes(indices)
        assert palette == [(1, 2, 3)] * 256
        assert pngsheet.payload_of(read, read_width, read_height, len(good) // 64) == good
        assert read[8] == good[64] and read[8 * width] == good[16 * 64]
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def test_the_reader_unfilters_every_filter_type():
    scratch = tempfile.mkdtemp(prefix="tilebank-png-")
    try:
        expected = bytes(HAND[0])
        for filter_type in sorted(HAND_FILTERED):
            path = os.path.join(scratch, "f%d.png" % filter_type)
            hand_png(path, filter_type)
            width, height, indices, _palette = pngsheet.read_indexed(path)
            assert (width, height, bytes(indices)) == (HAND[1], HAND[2], expected), filter_type
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def test_a_png_the_build_cannot_map_back_to_indices_is_refused():
    scratch = tempfile.mkdtemp(prefix="tilebank-png-")
    try:
        path = os.path.join(scratch, "rgb.png")
        raw = b"\x00" + bytes([1, 2, 3]) * 4
        blob = pngsheet.SIGNATURE
        blob += pngsheet._chunk(b"IHDR", struct.pack(">IIBBBBB", 4, 1, 8, 2, 0, 0, 0))
        blob += pngsheet._chunk(b"IDAT", zlib.compress(raw, 6))
        blob += pngsheet._chunk(b"IEND", b"")
        open(path, "wb").write(blob)
        assert refused(lambda: pngsheet.read_indexed(path))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def test_a_payload_that_is_not_a_whole_number_of_tiles_is_refused():
    row = {"declared_size": "100", "index": "0"}
    assert refused(lambda: pngsheet.sheet_of(bytes(100)))
    assert generator.refusal_reason(row, bytes(100)) is not None
    assert generator.refusal_reason({"declared_size": "64", "index": "0"}, bytes(64)) is None


@NEEDS_SHEETS
def test_the_187_sheets_reproduce_the_manifest_payloads():
    rows = generator.read_manifest(MANIFEST)
    equal = 0
    for row in rows:
        payload = generator.read_sheet(ASSETS, row)
        assert hashlib.sha256(payload).hexdigest() == row["payload_sha256"], row["index"]
        equal += 1
    print("%d/%d sheets reproduce their payload" % (equal, len(rows)))
    assert equal == len(rows) == generator.BANK_COUNT


@NEEDS_SHEETS
def test_the_census_accounts_for_every_container():
    rows = generator.read_manifest(MANIFEST)
    sheets = 0
    for row in rows:
        if generator.refusal_reason(row, generator.read_sheet(ASSETS, row)) is None:
            sheets += 1
    with open(os.path.join(ASSETS, generator.REFUSALS), newline="", encoding="utf-8") as handle:
        refused = list(csv.DictReader(handle))
    assert sheets == len(rows) == generator.BANK_COUNT
    assert refused == []
    sidecars = [name for name in os.listdir(ASSETS) if name.endswith(".json")]
    assert len(sidecars) == generator.BANK_COUNT


def test_no_rom_derived_sheet_is_tracked():
    proc = subprocess.run(["git", "ls-files", "assets/tilebank"], cwd=generator.ROOT,
                          capture_output=True)
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
    listed = proc.stdout.decode("utf-8", "replace").split()
    print("git ls-files assets/tilebank -> %s" % (listed or "nothing"))
    assert listed == []


def test_the_187_tile_banks_round_trip_byte_for_byte():
    if not os.path.exists(ROM):
        pytest.skip("%s is absent, so the tile banks cannot be decoded" % ROM)
    rom = open(ROM, "rb").read()
    assert hashlib.sha256(rom).hexdigest() == generator.ROM_SHA256
    banks = generator.read_banks(rom, generator.bank_table(rom))
    block = rom[generator.BLOCK_START:generator.BLOCK_START + generator.BLOCK_LEN]
    offsets = [offset - generator.BLOCK_START for _, _, offset, _ in banks]
    decoded = tilebank.decode_block(block, offsets)
    scratch = tempfile.mkdtemp(prefix="tilebank-test-")
    compress = generator.compressor(generator.COMPRESS, scratch)
    equal = 0
    try:
        for (index, _, offset, container), bank in zip(banks, decoded):
            blob = tilebank.encode(bank, compress)
            start = offset - generator.BLOCK_START
            if len(blob) == container.packed_size and blob == block[start:start + len(blob)]:
                equal += 1
            else:
                print("bank %d does not re-encode to its stored bytes" % index)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("%d/%d byte-equal" % (equal, len(banks)))
    assert equal == len(banks) == generator.BANK_COUNT


if __name__ == "__main__":
    test_a_short_re_encode_is_padded_with_zeros()
    test_a_re_encode_outside_the_zero_tail_rule_is_refused()
    test_a_bank_that_overruns_its_slot_or_the_block_is_refused()
    test_an_indexed_png_round_trips_and_the_sheet_is_a_tile_grid()
    test_the_reader_unfilters_every_filter_type()
    test_a_png_the_build_cannot_map_back_to_indices_is_refused()
    test_a_payload_that_is_not_a_whole_number_of_tiles_is_refused()
    test_the_187_sheets_reproduce_the_manifest_payloads()
    test_the_census_accounts_for_every_container()
    test_no_rom_derived_sheet_is_tracked()
    test_the_187_tile_banks_round_trip_byte_for_byte()
    print("PASS %s" % NAME)

