import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "symbols"))

import generate_symbols  # noqa: E402
import split_ledger  # noqa: E402

BASE = 0x08000000


def test_a_promoted_span_is_dropped_and_the_rest_is_cut_into_pieces():
    rows = [(0x100, 40, "thumb", "code_0100", "asm/buu.s", "transcription", "byte-proven", 30)]
    slices = [(0x110, 0x10)]
    runs = [(0x110, 0x120)]
    states = [(BASE + 0x100, "$t"), (BASE + 0x120, "$t")]
    out, changed, dropped, before, after = split_ledger.split(rows, slices, runs, states)
    assert changed == 1 and dropped == 16
    assert [(row[0], row[1]) for row in out] == [(0x100, 0x10), (0x120, 0x8)]
    assert [row[3] for row in out] == ["code_0100", "code_0100_000120"]
    assert all(row[5] == "transcription" for row in out)
    assert (before, after) == (30, 24), "the promoted span takes its own instruction bytes with it"


def test_a_row_the_promotion_covers_whole_is_removed_and_a_data_piece_gets_no_instruction_bytes():
    rows = [(0x200, 16, "data", "code_0200", "asm/buu.s", "transcription", "byte-proven", 0)]
    out, changed, dropped, before, after = split_ledger.split(rows, [(0x200, 0x10)], [],
                                                             [(BASE + 0x200, "$d")])
    assert out == [] and dropped == 16 and changed == 1


def test_a_pieces_isa_comes_from_the_mapping_symbol_at_its_own_start():
    rows = [(0x300, 32, "thumb", "code_0300", "asm/buu.s", "transcription", "byte-proven", 16)]
    states = [(BASE + 0x300, "$t"), (BASE + 0x310, "$d")]
    out, *_ = split_ledger.split(rows, [(0x308, 8)], [], states)
    assert [(row[0], row[2]) for row in out] == [(0x300, "thumb"), (0x310, "data")]


def test_the_split_is_idempotent_on_its_own_output():
    rows = [(0x100, 40, "thumb", "code_0100", "asm/buu.s", "transcription", "byte-proven", 20)]
    slices = [(0x110, 0x10)]
    states = [(BASE + 0x100, "$t"), (BASE + 0x120, "$t")]
    once, *_ = split_ledger.split(rows, slices, [], states)
    twice, changed, dropped, _, _ = split_ledger.split(once, slices, [], states)
    assert twice == once and changed == 0 and dropped == 0


def test_the_committed_ledger_carries_no_incbin_byte():
    if not os.path.exists(os.path.join(ROOT, "baserom.gba")):
        import pytest
        pytest.skip("baserom.gba is absent; run extract.cmd first")
    import gate
    slices = gate.incbin_ranges()
    bad = [row for row in split_ledger.read()
           if split_ledger.overlaps(row[0], row[0] + row[1], slices)]
    assert bad == [], "a ledger row still covers promoted bytes: %s" % bad[:2]
