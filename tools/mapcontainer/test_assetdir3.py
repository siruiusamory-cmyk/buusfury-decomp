from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import assetdir3  # noqa: E402
import generate_assetdir3  # noqa: E402

TABLE = 0x100
PAYLOAD = (0x400, 0x430)
ROWS = ((0x400, 0x420), (0x420, 0x430))
HEAD = bytes([0x04, 0x61, 0x70, 0x80, 0x40, 0x25, 0x08, 0x34, 0x07, 0xE1, 0x0F, 0x69, 0x16, 0x2D])
STREAM0 = 0x410


def image(head=HEAD, ramp0=0x00, stream=None, budget0=0x04, unexplained=0xF7):
    rom = bytearray(0x500)
    for index, (ramp_base, array_base) in enumerate(((0x40E, 0x41C), (0x420, 0x428))):
        at = TABLE + assetdir3.RECORD * index
        struct.pack_into("<II", rom, at, array_base + assetdir3.ROM_BASE,
                         ramp_base + assetdir3.ROM_BASE)
        for offset, value in assetdir3.FIXED.items():
            struct.pack_into("<I", rom, at + offset, value)
        struct.pack_into("<HH", rom, at + 0x10, 0x341 + index, 0)
    rom[0x400:0x400 + len(head)] = head
    rom[0x40E] = ramp0
    rom[0x40F] = budget0
    rom[0x410:0x41C] = bytes([unexplained] * 12)
    if stream is None:
        stream = bytes([0x51, 0x00])
    rom[STREAM0:STREAM0 + len(stream)] = stream
    struct.pack_into("<I", rom, 0x41C, 0x0800040F)
    rom[0x420] = 0x00
    rom[0x421] = 0x02
    rom[0x422:0x428] = bytes([0x21, 0x00, unexplained, unexplained, unexplained, unexplained])
    struct.pack_into("<II", rom, 0x428, 0x08000421, 0x08000421)
    return bytes(rom)


def records_of(rom):
    return assetdir3.descriptor(rom, table=TABLE, count=2, payload=PAYLOAD)


def walked(rom, **kwargs):
    return assetdir3.walk(rom, records_of(rom), payload=PAYLOAD, **kwargs)


def test_a_flag_takes_bits_zero_to_three_not_seven_to_four():
    rom = image(stream=bytes([0x21, 0xAB, 0x00]))
    _roles, entries, _stats, _origin = walked(rom)
    entry = [row for row in entries if row[1] == STREAM0][0]
    assert entry[3:7] == (2, 1, 0x04, b"\xab")
    assert assetdir3.operand_count(0x04) == 1
    assert assetdir3.operand_count(0x0F) == 5


def test_a_class_zero_operand_is_the_flag_and_class_one_reads_it_back():
    stream = bytes([0x03, 0x03, 0xAA, 0xBB, 0x13, 0xCC, 0xDD, 0x00])
    rom = image(stream=stream)
    _roles, entries, _stats, _origin = walked(rom)
    first = [row for row in entries if row[1] == STREAM0][0]
    second = [row for row in entries if row[1] == STREAM0 + 4][0]
    assert first[3:7] == (0, 3, 0x03, bytes([0x03, 0xAA, 0xBB]))
    assert second[3:7] == (1, 3, 0x03, bytes([0xCC, 0xDD]))


def test_a_zero_byte_ends_the_call_and_the_next_call_continues_after_it():
    stream = bytes([0x51, 0x00, 0x51, 0x00])
    rom = image(stream=stream)
    roles, entries, _stats, _origin = walked(rom)
    starts = sorted(row[1] for row in entries)
    assert STREAM0 in starts and STREAM0 + 2 in starts
    assert roles[STREAM0 + 2] == assetdir3.OPCODE


def test_the_budget_of_one_jumps_before_any_stream_byte():
    rom = image(budget0=0x01)
    roles, _entries, stats, _origin = walked(rom)
    assert stats[0]["calls"] >= 1
    assert roles[0x40F] == assetdir3.COUNT_BYTE
    assert roles[STREAM0] == assetdir3.OPCODE


def test_an_array_index_above_the_word_count_is_reported_not_crashed():
    rom = image(ramp0=0x05)
    _roles, _entries, stats, _origin = walked(rom)
    assert stats[0]["stop"].startswith("array index 5 outside")
    assert not stats[0]["saturated"]


def test_the_kind_partition_is_the_row_and_an_unread_byte_is_named():
    rom = image()
    roles, _entries, _stats, _origin = walked(rom)
    kinds = assetdir3.classify(rom, roles, payload=PAYLOAD)
    for row in ROWS:
        tally = assetdir3.counts(kinds, PAYLOAD, row)
        assert sum(tally.values()) == row[1] - row[0]
        assert sum(length for _at, length in assetdir3.runs(kinds, PAYLOAD, row)) \
            == tally.get(assetdir3.UNEXPLAINED, 0)


def test_the_machine_reads_no_byte_in_two_roles():
    rom = image(stream=bytes([0x03, 0x03, 0xAA, 0xBB, 0x13, 0xCC, 0xDD, 0x00]))
    roles, entries, _stats, _origin = walked(rom)
    space = set()
    for _record, start, size, _cls, _slot, _flag, _operands in entries:
        space |= set(range(start, start + size))
    assert space <= set(roles)


def test_a_clean_walk_has_no_invariant_problem():
    rom = image()
    roles, entries, stats, _origin = walked(rom)
    problems = assetdir3.verify(rom, records_of(rom), roles, stats, entries, payload=PAYLOAD)
    assert problems == []


def test_the_rows_re_encode_from_the_structure_byte_for_byte():
    rom = image(stream=bytes([0x03, 0x03, 0xAA, 0xBB, 0x13, 0xCC, 0xDD, 0x00]))
    roles, entries, _stats, _origin = walked(rom)
    members = {ROWS[0][0]: generate_assetdir3.structure(rom, ROWS[0][0], ROWS[0][1], roles,
                                                        entries, HEAD)}
    out = generate_assetdir3.encode(members, rom, HEAD, rows=ROWS)
    assert out[ROWS[0][0]] == rom[ROWS[0][0]:ROWS[0][1]]


def test_an_entry_whose_operands_disagree_with_its_flag_is_refused():
    rom = image(stream=bytes([0x03, 0x03, 0xAA, 0xBB, 0x13, 0xCC, 0xDD, 0x00]))
    roles, entries, _stats, _origin = walked(rom)
    parts = list(generate_assetdir3.segments(
        generate_assetdir3.structure(rom, ROWS[0][0], ROWS[0][1], roles, entries, HEAD)))
    broken = b""
    for op, body in parts:
        if op == generate_assetdir3.ENTRY and body[0] != 0:
            body = body[:2] + bytes([body[2] - 1]) + body[3:-1]
        broken += generate_assetdir3.segment(op, body)
    try:
        generate_assetdir3.encode({ROWS[0][0]: broken}, rom, HEAD, rows=ROWS)
    except generate_assetdir3.Refused as exc:
        assert "operands" in str(exc)
    else:
        raise AssertionError("a short entry was accepted")


def test_a_perturbed_head_byte_is_refused_by_the_class_flag_check():
    rom = image(stream=bytes([0x21, 0xAB, 0x00]))
    other = bytes([0x01] + list(HEAD[1:]))
    roles, entries, _stats, _origin = walked(rom)
    blob = generate_assetdir3.structure(rom, ROWS[0][0], ROWS[0][1], roles, entries, HEAD)
    try:
        generate_assetdir3.encode({ROWS[0][0]: blob}, rom, other, rows=ROWS)
    except generate_assetdir3.Refused as exc:
        assert "head[" in str(exc) or "operands" in str(exc)
    else:
        raise AssertionError("a perturbed head was accepted")


def test_a_ramp_byte_above_the_word_count_is_refused_by_address():
    rom = image(ramp0=0x05)
    roles, entries, stats, _origin = walked(rom)
    problems = assetdir3.verify(rom, records_of(rom), roles, stats, entries, payload=PAYLOAD)
    assert any(problem.startswith("ramp byte 5 is neither 0xFF") for problem in problems)


def test_an_array_word_outside_its_own_span_is_refused_by_address():
    rom = bytearray(image())
    struct.pack_into("<I", rom, 0x41C, 0x08000400)
    roles, entries, stats, _origin = walked(bytes(rom))
    problems = assetdir3.verify(bytes(rom), records_of(bytes(rom)), roles, stats, entries,
                                payload=PAYLOAD)
    assert any(problem.startswith("array word 0 points outside its own span")
               and problem.endswith("0x00041C") for problem in problems), problems
