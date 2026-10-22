from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import assetdirectory  # noqa: E402
import audiodir  # noqa: E402
import assetdir2  # noqa: E402
from testkit import refusal_message, rom_bytes  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")
BLOCK = bytes((0x00, 0xFF, 0x7F, 0x80))


def synthetic(tied=True, byte_length=4):
    image = bytearray(0x200)
    struct.pack_into("<IIHH", image, 0x80, 0x08000100, 1, byte_length, 16000)
    image[0x100:0x104] = BLOCK
    spec = assetdirectory.Spec(directory="synthetic_64", block="synthetic_64_block", base=0x80,
                              count=1, block_start=0x100, block_end=0x104, low_words={1: 1},
                              units={16000: 1}, tied=tied)
    namespace = {}
    assetdirectory.install(namespace, spec)
    return bytes(image), namespace


def test_the_stream_codec_round_trips_every_signed_byte():
    blob = bytes(range(256))
    samples = assetdirectory.decode_stream(blob)
    assert samples[:2] == [0, 1] and samples[127:130] == [127, -128, -127]
    assert assetdirectory.encode_stream(samples) == blob


def test_the_codec_refuses_a_sample_outside_the_signed_byte_range():
    assert refusal_message(lambda: assetdirectory.encode_stream([0, 128])) == (
        "sample 128 is outside the signed byte range")


def test_a_tied_block_re_encodes_from_its_decoded_stream():
    rom, module = synthetic()
    assert module["serialize_record"](rom, module["BLOCK"], 0x100, 4) == BLOCK
    assert assetdirectory.decode_stream(BLOCK) == [0, -1, 127, -128]


def test_a_block_that_disagrees_with_its_record_s_byte_length_is_refused():
    rom, module = synthetic(byte_length=5)
    assert refusal_message(lambda: module["serialize_record"](rom, module["BLOCK"], 0x100, 4)) == (
        "synthetic_64 record 0 names 5 B at 0x100, the block holds 4")


def test_a_block_no_record_names_is_refused():
    rom, module = synthetic()
    assert refusal_message(lambda: module["serialize_record"](rom, module["BLOCK"], 0x104, 4)) == (
        "synthetic_64 holds no record naming 0x104")


def test_an_untied_directory_serializes_its_block_as_its_extent():
    rom, module = synthetic(tied=False)
    assert module["serialize_record"](rom, module["BLOCK"], 0x100, 4) == BLOCK
    assert module["TIED"] is False


def test_the_music_table_is_the_one_the_four_contract_sites_load():
    rom = rom_bytes(ROM, size=0x800000)
    sites = audiodir.literal_sites(rom, 0x083BB78C)
    assert sites == [0x080008BC, 0x080041BA, 0x080053F8, 0x08008C86]
    calls = [0x080008D2, 0x080041CE, 0x0800540E, 0x08008C9A]
    assert [audiodir.calls(rom, site, audiodir.MUSIC_CALL) for site in sites] == [
        [call] for call in calls]
    assert audiodir.bl_target(rom, calls[0]) == audiodir.MUSIC_CALL
    assert audiodir.bl_target(rom, 0x0800083A) == audiodir.RECORD_CALL


def test_every_music_record_names_the_table_the_slot_engine_reads_at_plus_8():
    rom = rom_bytes(ROM, size=0x800000)
    assert len(audiodir.music(rom)) == 53
    assert all(row["samples"] == 0x0836D18C for row in audiodir.music(rom))
    assert audiodir.literal_sites(rom, 0x0836D18C) == []
    assert audiodir.reach(rom, 0x36D18C) == []
    assert audiodir.sample_bank(rom) is True


def test_the_plus_8_reader_is_the_pinned_instruction_chain():
    rom = rom_bytes(ROM, size=0x800000)
    assert audiodir.word(rom, audiodir.OBJECT_POOL) == audiodir.OBJECT_POOL_VALUE
    assert audiodir.word(rom, audiodir.OBJECT_WORD) == audiodir.OBJECT_VALUE
    assert [(address, text) for address, _value, text in audiodir.SAMPLES_PATH] == [
        (0x0803E536, "ldr r3, [pc, #0x270]"), (0x0803E53A, "subs r3, #4"),
        (0x0803E53C, "ldr r3, [r3]"), (0x0803E540, "ldr r3, [r3, #0xc]"),
        (0x0803E542, "ldr r5, [r3, #8]"), (0x0803E544, "lsls r3, r2, #1"),
        (0x0803E546, "adds r2, r3, r2"), (0x0803E548, "lsls r2, r2, #2"),
        (0x0803E54A, "adds r2, r5, r2"), (0x0803E54C, "str r2, [r0, #0x28]"),
        (0x0803F11C, "str r1, [r0, #0xc]"), (0x0803E0FA, "ldr r2, [r0, #0x28]")]


def test_a_moved_halfword_in_the_plus_8_reader_untie_s_the_directory():
    rom = bytearray(rom_bytes(ROM, size=0x800000))
    rom[0x3E542] ^= 0xFF
    assert audiodir.sample_bank(bytes(rom)) is False
    assert audiodir.tied_run(bytes(rom), assetdir2) is False


def test_the_tied_directory_is_the_one_the_allocator_call_sites_reach():
    rom = rom_bytes(ROM, size=0x800000)
    assert audiodir.reach(rom, 0x3192A8) == [0x0800082A] + audiodir.reach(rom, 0x3192A8)[1:]
    assert 0x0800082A in audiodir.reach(rom, 0x3192A8)
    assert audiodir.verdicts(rom) == [("asset_directory_64", True, True),
                                     ("asset_directory_79", True, True)]


def test_the_survey_ties_all_143_records():
    rom = rom_bytes(ROM, size=0x800000)
    rows = audiodir.survey(rom)
    assert audiodir.total(rows, True) == (143, 733911)
    assert audiodir.total(rows, False) == (0, 0)
    assert audiodir.total(rows, True)[1] + audiodir.total(rows, False)[1] == 733911
    assert all(row["tied"] for row in rows)


def test_every_record_re_encodes_from_its_decoded_model():
    rom = rom_bytes(ROM, size=0x800000)
    rows = audiodir.survey(rom)
    assert [row["tied"] for row in rows].count(True) == 143
    for row in rows:
        assert assetdirectory.encode_stream(row["samples"]) == (
            rom[row["block_offset"]:row["block_offset"] + row["byte_length"]])


def test_the_tied_serializer_takes_the_codec_branch(monkeypatch):
    rom, module = synthetic()
    calls = []
    real = assetdirectory.Directory.block_blob

    def counting(self, image, offset, size):
        calls.append((offset, size))
        return real(self, image, offset, size)

    monkeypatch.setattr(assetdirectory.Directory, "block_blob", counting)
    assert module["serialize_record"](rom, module["BLOCK"], 0x100, 4) == BLOCK
    assert calls == [(0x100, 4)]


def test_the_retail_tied_run_takes_the_codec_branch_for_every_record(monkeypatch):
    rom = rom_bytes(ROM, size=0x800000)
    import assetdir  # noqa: E402

    calls = []
    real = assetdirectory.Directory.block_blob

    def counting(self, image, offset, size):
        calls.append(offset)
        return real(self, image, offset, size)

    monkeypatch.setattr(assetdirectory.Directory, "block_blob", counting)
    rows = [row for module in (assetdir, assetdir2) for row in module.block_rows(rom)]
    for module in (assetdir, assetdir2):
        for offset, size in module.block_rows(rom):
            module.serialize_record(rom, module.BLOCK, offset, size)
    assert len(calls) == 143
    assert calls == [offset for offset, _size in rows]
