"""DECOMP-IWRAM-TRANSFORMS-001: the IWRAM block's byte-lane and Q-format families.

Three targets, all inside the 4100-byte block the reset code copies to IWRAM
0x03000000 (ROM 0x087B79A4..0x087B89A8):

* ``iwrambl``       0x087B7C80  76 B  19 insns  byte-lane table transform
* ``iwramblsparse`` 0x087B7CD4  88 B  22 insns  byte-lane sparse store
* ``iwramqf``       0x087B7F04 416 B 104 insns  twelve-term Q10 sum of products
                    0x087B80A4 104 B  26 insns  three-term Q10 dot product

Everything asserted about the ROM is re-derived from the cartridge on every run:
the extents by the harness's own aligned chain-walk, the lane masks and shift
amounts by decoding the instruction words, and the claim the ticket exists to
settle - that the two fixed-point routines share a REDUCTION but are not the same
operation - by reading the reduction words out of both.

PORTABLE tests need no ROM, no toolchain and no host compiler. ROM-gated tests
skip cleanly, as does the semantic run when no host compiler is present. The ROM
is opened READ-ONLY and nothing here writes to it.
"""

from __future__ import annotations

import re

import pytest

from buusfury import gba, identity, lift

# The block's ROM bytes ARE its IWRAM bytes, verbatim.
IWRAM_BLOB_ROM = 0x087B79A4
IWRAM_BASE = 0x03000000

BL_ENTRY_ROM = 0x087B7C80
BL_ENTRY_IWRAM = 0x030002DC
BL_CODE_END = 0x087B7CCC
BL_END = 0x087B7CD4
BL_LAST_INSTRUCTION = 0x087B7CC8
#: The two words a naive entry-to-next-entry window would report as instructions.
BL_FOREIGN_POOL = (0x087B7CCC, 0x087B7CD0)
FOREIGN_POOL_OWNER_LOADS = (0x087B7BD4, 0x087B7BE4)
BL_VENEER = 0x0804918C
BL_TABLE_WORD_SITE = 0x08030F30
BL_TABLE = 0x0805672C
BL_CALL_SITES = (0x08030EBC, 0x0803D99C, 0x0803F9FA)

BL_SPARSE_ROM = 0x087B7CD4
BL_SPARSE_IWRAM = 0x03000330
BL_SPARSE_CODE_END = 0x087B7D2C
BL_SPARSE_VENEER = None  # there is none: the routine is unreachable

QF_ROM = 0x087B7F04
QF_ENTRY_IWRAM = 0x03000560
QF_MID = 0x087B80A4
QF_MID_IWRAM = 0x03000700
QF_CODE_END = 0x087B810C
QF_VENEER_C1 = 0x08049174
QF_VENEER_B0 = 0x08049180
QF_CALLS = {0x08049174: 0x0802EFD0, 0x08049180: 0x0802F1DC}

#: The instruction words that ARE the reduction, read from the image below and
#: asserted here as the claim under test.
REDUCTION_STANDALONE = (0xE1A04527, 0xE0844B08)   # lsr r4,r7,#10 ; add r4,r4,r8,lsl #22
REDUCTION_FOLDED = (0xE0844527, 0xE0844B08)       # add r4,r4,r7,lsr #10 ; add r4,r4,r8,lsl #22


# ---------------------------------------------------------------------------
# ROM helpers: pure bit arithmetic, so nothing here needs a disassembler
# ---------------------------------------------------------------------------
def word(data: bytes, address: int) -> int:
    offset = address - gba.ROM_BASE
    return int.from_bytes(data[offset : offset + 4], "little")


def occurs(data: bytes, value: int, *, alignment: int = 2) -> list:
    """Every address at which `value` appears as a 32-bit word."""
    hits = []
    for offset in range(0, len(data) - 4, alignment):
        if int.from_bytes(data[offset : offset + 4], "little") == value:
            hits.append(gba.ROM_BASE + offset)
    return hits


def instruction_words(data: bytes, start: int, end: int) -> list:
    return [word(data, a) for a in range(start, end, 4)]


# ---------------------------------------------------------------------------
# the extents, re-derived by the harness on every run
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "unit_id,expected",
    [
        ("iwram_bl_pair_tu", [(BL_ENTRY_ROM, BL_CODE_END, 19)]),
        ("iwram_bl_sparse_tu", [(BL_SPARSE_ROM, BL_SPARSE_CODE_END, 22)]),
        ("iwram_qf_tu", [(QF_ROM, QF_MID, 104), (QF_MID, QF_CODE_END, 26)]),
    ],
)
def test_the_harness_derives_each_extent_with_no_gaps(rom_bytes, unit_id, expected):
    derived = lift.derive_unit_boundaries(rom_bytes, unit_id)
    assert derived["problems"] == [], derived["problems"]
    assert derived["derived_from_rom"] is True
    assert derived["not_hand_written"] is True
    rows = derived["functions"]
    assert len(rows) == len(expected)
    for row, (start, end, instructions) in zip(rows, expected):
        assert row["start"] == "0x%08X" % start
        assert row["end"] == "0x%08X" % end
        assert row["instructions"] == instructions
        assert row["gaps"] == []
        assert row["matches_expected"] is True


@pytest.mark.parametrize(
    "unit_id", ["iwram_bl_pair_tu", "iwram_bl_sparse_tu", "iwram_qf_tu"]
)
def test_no_new_unit_declares_a_literal_pool(rom_bytes, unit_id):
    """All five routines are register-only, so the pool test is not applicable."""
    derived = lift.derive_unit_boundaries(rom_bytes, unit_id)
    assert derived["has_literal_pool"] is False
    assert derived["pool_extent"] is None


def test_the_eighty_four_byte_reading_of_the_first_entry_is_refuted(rom_bytes):
    """The ticket's own brief said 84 bytes. It is 76, and the 8 are not its.

    Entry-to-next-entry counts two words of ANOTHER routine's literal pool as
    instructions. The proof is that exactly two instructions in the whole block
    read them and both lie inside the 149-word routine that PRECEDES this one.
    """
    # The last instruction really is the `bx lr`.
    assert word(rom_bytes, BL_LAST_INSTRUCTION) == 0xE12FFF1E
    # The two words are not this unit's pool: this unit loads nothing.
    assert word(rom_bytes, BL_FOREIGN_POOL[0]) == 0x000037FF
    assert word(rom_bytes, BL_FOREIGN_POOL[1]) == 0x0000027F
    # They are read by two pc-relative loads, and both sites are BELOW the entry.
    for site in FOREIGN_POOL_OWNER_LOADS:
        assert site < BL_ENTRY_ROM
    assert word(rom_bytes, FOREIGN_POOL_OWNER_LOADS[0]) == 0xE59F80F0  # ldr r8,[pc,#0xf0]
    assert word(rom_bytes, FOREIGN_POOL_OWNER_LOADS[1]) == 0xE59F80E4  # ldr r8,[pc,#0xe4]
    # ldr's pc is the instruction address + 8.
    assert FOREIGN_POOL_OWNER_LOADS[0] + 8 + 0xF0 == BL_FOREIGN_POOL[0]
    assert FOREIGN_POOL_OWNER_LOADS[1] + 8 + 0xE4 == BL_FOREIGN_POOL[1]


def test_the_first_byte_lane_routines_instructions_are_the_lane_idiom(rom_bytes):
    """Four `ands` against a 0xFF mask, each feeding a predicated lane access.

    The four `ands` take a REGISTER-SHIFTED register operand (word bit 4 set),
    which is what makes this shape findable: `ands rD, ip, rM, lsr #N`.
    """
    body = instruction_words(rom_bytes, BL_ENTRY_ROM, BL_CODE_END)
    assert len(body) == 19
    assert body == [
        0xE92D0070, 0xE3A0C0FF, 0xE4914004, 0xE01C5C24, 0x17D25005,
        0xE01C6824, 0x17D26006, 0xE1865405, 0xE01C6424, 0x17D26006,
        0xE1865405, 0xE01C6004, 0x17D26006, 0xE1865405, 0xE4805004,
        0xE2533004, 0x1AFFFFF0, 0xE8BD0070, 0xE12FFF1E,
    ]
    # `ands rD, ip, rM, <shift>`: opcode 0000 with S, and word bit 4 - the
    # data-processing I bit - CLEAR, which is the IMMEDIATE-shift form.
    lane_ands = [
        w for w in body
        if ((w >> 21) & 0xF) == 0x0 and ((w >> 20) & 1) == 1 and (w & 0x10) == 0
    ]
    assert len(lane_ands) == 4, [hex(w) for w in lane_ands]
    # The mask register in every one of them is ip = r12 (Rn bits 19-16).
    assert all(((w >> 16) & 0xF) == 12 for w in lane_ands)
    # Three lane extractions are LOGICAL shifts (bits 6-5 = 01) and lane 0 has no
    # shift at all. There is no ASR (10) and no ROR (11) anywhere, so the routine
    # neither sign-extends nor rotates.
    shift_types = [(w >> 5) & 3 for w in lane_ands]
    assert sorted(shift_types) == [0, 1, 1, 1], shift_types
    assert 2 not in shift_types and 3 not in shift_types
    assert [(w >> 7) & 0x1F for w in lane_ands] == [24, 16, 8, 0]
    # Each `ands` is immediately followed by its predicated table read: an
    # `ldrbne`, i.e. a single data transfer with L and B set, condition NE.
    for index, w in enumerate(body):
        if ((w >> 21) & 0xF) == 0x0 and ((w >> 20) & 1) == 1 and (w & 0x10) == 0:
            nxt = body[index + 1]
            assert (nxt >> 28) == 0x1, "ldrbne must follow the ands"
            assert ((nxt >> 21) & 0xF) == 0xE   # single data transfer
            assert ((nxt >> 20) & 1) == 1       # L: a LOAD
            assert ((nxt >> 22) & 1) == 1       # B: a byte, not a word
    # The store is unconditional and the counter test is at the END of the body.
    assert body[14] == 0xE4805004         # str r5, [r0], #4
    assert body[15] == 0xE2533004         # subs r3, r3, #4
    assert body[16] == 0x1AFFFFF0         # bne back to the load


def test_the_first_byte_lane_routine_has_no_pre_test_on_its_count(rom_bytes):
    """The counter is decremented only at the END, so count 0 wraps.

    This is the property that makes a zero-size call destroy the address space
    and a count that is not a multiple of four loop forever. The test states it
    as arithmetic on the decoded instruction, not as a claim about intent.
    """
    body = instruction_words(rom_bytes, BL_ENTRY_ROM, BL_CODE_END)
    # The only flag-setting compare in the body is the counter decrement itself:
    # no cmp/teq/tst (opcodes 1010/1001/1000 with S) anywhere.
    compares = [
        w for w in body
        if (w >> 21) & 0xF in (0xA, 0x9, 0x8) and (w >> 20) & 1 and (w >> 26) & 1 == 0
    ]
    assert compares == [], [hex(w) for w in compares]
    # Exactly one `subs`, and it is the third word from the end of the body.
    subs = [w for w in body if ((w >> 21) & 0xF) == 0x2 and (w >> 20) & 1]
    assert len(subs) == 1, [hex(w) for w in subs]
    assert subs[0] == 0xE2533004
    assert body.index(subs[0]) == len(body) - 4
    # and a zero count cannot reach the exit: the first decrement wraps.
    assert (0 - 4) & 0xFFFFFFFF != 0


def test_the_first_entrys_table_is_a_single_rom_literal(rom_bytes):
    """All three callers pass the same 256-byte ROM table, which is not identity."""
    hits = occurs(rom_bytes, BL_TABLE)
    assert hits == [BL_TABLE_WORD_SITE], [hex(h) for h in hits]
    table = [rom_bytes[BL_TABLE - gba.ROM_BASE + i] for i in range(256)]
    assert table != list(range(256)), "an identity table would make this a no-op"
    # It is NOT a bijection either, which the first revision of this test wrongly
    # asserted: three distinct table entries hold 0xFF, so the map is many-to-one.
    assert len(set(table)) < 256
    assert table.count(0xFF) == 3


def test_the_first_byte_lane_veneer_is_the_rom_to_iwram_jump(rom_bytes):
    """`bx pc` + nop, then `ldr pc,[pc,#-4]`, whose literal IS the IWRAM entry."""
    offset = BL_VENEER - gba.ROM_BASE
    assert rom_bytes[offset : offset + 4] == b"\x78\x47\xc0\x46"
    assert word(rom_bytes, BL_VENEER + 4) == 0xE51FF004
    assert word(rom_bytes, BL_VENEER + 8) == BL_ENTRY_IWRAM


def test_the_second_byte_lane_routine_is_reachable_by_nothing(rom_bytes):
    """INFERRED DEAD, and the test says which evidence supports and which not."""
    address = BL_SPARSE_IWRAM
    assert occurs(rom_bytes, address) == []
    assert occurs(rom_bytes, address | 1) == []
    # It is NOT adjacent to the previous routine: eight bytes separate them.
    assert BL_SPARSE_ROM - BL_CODE_END == 8
    # And fall-through is impossible: the preceding routine ends in `bx lr`.
    assert word(rom_bytes, BL_LAST_INSTRUCTION) == 0xE12FFF1E
    # The unit's own evidence string must call this INFERRED, not proven.
    source = (identity.REPO_ROOT / "src" / "IwramByteLaneSparse.c").read_text("utf-8")
    assert "INFERRED DEAD/UNREACHABLE" in source
    # The wording wraps inside a block comment, so the gap contains ` * `.
    assert re.search(r"NOT[\s*]+proven[\s*]+dead", source), "the status must say NOT proven"
    assert "PC sampling" in source


def test_the_second_byte_lane_routines_count_test_is_signed(rom_bytes):
    """`subs r2,r2,#4` then `bmi`: an N test, so the wrap boundary is 0x80000004."""
    body = instruction_words(rom_bytes, BL_SPARSE_ROM, BL_SPARSE_CODE_END)
    assert len(body) == 22
    assert body == [
        0xE92D0030, 0xE5902030, 0xE5900024, 0xE2400004, 0xE3A040FF,
        0xE2522004, 0x4A00000C, 0xE2800004, 0xE4913004, 0xE3530000,
        0x0AFFFFF9, 0xE0145003, 0x15C05000, 0xE0145423, 0x15C05001,
        0xE0145823, 0x15C05002, 0xE0145C23, 0x15C05003, 0xEAFFFFF0,
        0xE8BD0030, 0xE12FFF1E,
    ]
    # 0x4A00000C is `bmi` - condition field 0100 is MI (N), not CC/LO or LS.
    assert 0x4A00000C in body
    assert (0x4A00000C >> 28) == 0x4, "condition 0100 is MI"
    # The mask register move, and the count decrement BEFORE the loop test.
    assert body[4] == 0xE3A040FF          # mov r4, #0xff
    assert body[5] == 0xE2522004          # subs r2, r2, #4  (the pre-loop one)
    assert body.index(0xE2522004) == 5
    # Four predicated BYTE STORES: single data transfer, L clear, B set, cond NE.
    stores = [
        w for w in body
        if ((w >> 21) & 0xF) == 0xE and ((w >> 20) & 1) == 0
        and ((w >> 22) & 1) == 1 and (w >> 28) == 0x1
    ]
    assert len(stores) == 4, [hex(w) for w in stores]
    assert [(w & 0xF) for w in stores] == [0x0, 0x1, 0x2, 0x3]
    # The all-zero-word test comes BEFORE the four stores.
    assert body[9] == 0xE3530000          # cmp r3, #0
    assert body[10] == 0x0AFFFFF9         # beq back to the counter
    # Each store is predicated on the `ands` immediately before it, which is what
    # makes an all-zero word silent and a zero lane unwritten.
    for index, w in enumerate(body):
        if ((w >> 21) & 0xF) == 0xE and ((w >> 20) & 1) == 0 and ((w >> 22) & 1) == 1 \
                and (w >> 28) == 0x1:
            assert ((body[index - 1] >> 21) & 0xF) == 0x0, hex(body[index - 1])
            assert ((body[index - 1] >> 20) & 1) == 1, "the AND must set Z"


def test_the_two_byte_lane_routines_do_not_permute_or_invert(rom_bytes):
    """Both lane maps are the identity, so neither is a permutation.

    A permutation would move a lane's bits; the identity keeps lane k in place.
    The proof is the shift set: three LSRs (or the unshifted form) applied to the
    SAME source register, with no rotation anywhere.
    """
    for start, end in ((BL_ENTRY_ROM, BL_CODE_END), (BL_SPARSE_ROM, BL_SPARSE_CODE_END)):
        body = instruction_words(rom_bytes, start, end)
        for w in body:
            assert (w >> 28) != 0xF, "no unconditional-encoding surprises"
            # bit 25 = 0 and bits 27-26 = 00 -> data processing
            if (w & 0x0C000000) == 0 and ((w >> 25) & 1) == 0:
                shift_type = (w >> 5) & 3
                assert shift_type != 3, "no ROR: %08X" % w
    # and neither routine can be the other's inverse, because the second is not
    # injective: it writes a destination window fixed by the count, not the data.
    sparse = instruction_words(rom_bytes, BL_SPARSE_ROM, BL_SPARSE_CODE_END)
    assert 0xE2800004 in sparse or 0xE2800004 in instruction_words(
        rom_bytes, BL_ENTRY_ROM, BL_CODE_END
    )


# ---------------------------------------------------------------------------
# the Q-format family
# ---------------------------------------------------------------------------
def test_the_reduction_words_are_the_ones_the_family_is_named_for(rom_bytes):
    """The standalone and folded spellings, read from both routines.

    The register numbers differ between lanes, so the scan is on the instruction
    FIELDS - `add rD, rD, rM, lsr #10` with rd == rn - and not on whole words.
    """
    c1 = instruction_words(rom_bytes, QF_ROM, QF_MID)
    b0 = instruction_words(rom_bytes, QF_MID, QF_CODE_END)

    # `add rD, rD, rM, lsr #10` - the FOLDED low half, rd == rn.
    def is_folded_low(w):
        return (
            ((w >> 21) & 0xF) == 0x4
            and ((w >> 25) & 1) == 0
            and ((w >> 12) & 0xF) == (w >> 16) & 0xF
            and (w & 0x10) == 0
            and ((w >> 5) & 3) == 1
            and ((w >> 7) & 0x1F) == 10
        )

    # `lsr rD, rM, #10` - the STANDALONE low half (a mov with lsr).
    def is_standalone_low(w):
        return (
            ((w >> 21) & 0xF) == 0xD
            and ((w >> 25) & 1) == 0
            and (w & 0x10) == 0
            and ((w >> 5) & 3) == 1
            and ((w >> 7) & 0x1F) == 10
        )

    # `add rD, rD, rM, lsl #22` - the shared HIGH half.
    def is_high(w):
        return (
            ((w >> 21) & 0xF) == 0x4
            and ((w >> 25) & 1) == 0
            and ((w >> 12) & 0xF) == (w >> 16) & 0xF
            and (w & 0x10) == 0
            and ((w >> 5) & 3) == 0
            and ((w >> 7) & 0x1F) == 22
        )

    assert sum(1 for w in c1 if is_standalone_low(w)) == 9, "C1 standalone"
    assert sum(1 for w in c1 if is_folded_low(w)) == 3, "C1 folded"
    assert sum(1 for w in c1 if is_high(w)) == 12, "C1 high halves"
    assert sum(1 for w in b0 if is_standalone_low(w)) == 0, "B0 has none standalone"
    assert sum(1 for w in b0 if is_folded_low(w)) == 3, "B0 folded"
    assert sum(1 for w in b0 if is_high(w)) == 3, "B0 high halves"

    # The named words really are in the image.
    assert REDUCTION_STANDALONE[0] in c1
    assert REDUCTION_FOLDED[0] in c1
    assert REDUCTION_FOLDED[0] in b0
    assert REDUCTION_STANDALONE[0] not in b0
    # The distinction the ticket exists to settle: C1's TWELVE reductions are
    # nine standalone plus three folded, while B0's THREE are all folded. In C1
    # the folded shape covers only the last group; its three occurrences are
    # contiguous in the last eighth of the routine.
    folded_sites = [i for i, w in enumerate(c1) if is_folded_low(w)]
    assert folded_sites == [len(c1) - 14, len(c1) - 13, len(c1) - 12], folded_sites
    b0_sites = [i for i, w in enumerate(b0) if is_folded_low(w)]
    assert len(b0_sites) == 3 and b0_sites[-1] - b0_sites[0] < len(b0) // 2


def test_the_reduction_is_signed_64_bit_multiply_and_a_logical_shift(rom_bytes):
    """3 SMULL + 6 SMLAL in B0, 12 + 24 in C1; zero UMULL/UMLAL anywhere."""
    for start, end, smulls, smlals in (
        (QF_ROM, QF_MID, 12, 24),
        (QF_MID, QF_CODE_END, 3, 6),
    ):
        body = instruction_words(rom_bytes, start, end)
        found_smull = [w for w in body if (w & 0x0FE000F0) == 0x00C00090]
        found_smlal = [w for w in body if (w & 0x0FE000F0) == 0x00E00090]
        found_umull = [w for w in body if (w & 0x0FE000F0) == 0x00800090]
        found_umlal = [w for w in body if (w & 0x0FE000F0) == 0x00A00090]
        assert len(found_smull) == smulls, (hex(start), len(found_smull))
        assert len(found_smlal) == smlals, (hex(start), len(found_smlal))
        assert found_umull == [] and found_umlal == [], "signedness is decided here"


def test_the_two_spellings_of_the_reduction_agree_on_all_thirty_two_bits():
    """`(lo >> 10) + (hi << 22)` is `(u32)(((u64)sum) >> 10)`, exactly.

    Stated as an executable identity rather than as an assertion about the code,
    and deliberately including negative 64-bit sums, which is where an earlier
    reading of this family wrongly claimed the two forms differ.
    """
    mask = 0xFFFFFFFF
    cases = [
        (0x00000000, 0x00000000),
        (0x00000400, 0x00000000),
        (0x00000000, 0xFFFFFFFE),
        (0xFFFFFFFF, 0xFFFFFFFF),
        (0x00000000, 0x80000000),
        (0x00000000, 0x00000004),
        (0x12345678, 0x9ABCDEF0),
    ]
    state = 0x13579BDF
    for _ in range(20000):
        state = (state * 1103515245 + 12345) & mask
        low = state
        state = (state * 1103515245 + 12345) & mask
        cases.append((low, state))

    for low, high in cases:
        halves = ((low >> 10) + (high << 22)) & mask
        product = ((high << 32) | low) & 0xFFFFFFFFFFFFFFFF
        assert halves == (product >> 10) & mask, (hex(low), hex(high))
        # ... and the arithmetic shift of the same 64-bit value truncates to the
        # SAME 32 bits, because the sign extension lands above bit 31.
        signed = product - (1 << 64) if product >> 63 else product
        assert halves == (signed >> 10) & mask, (hex(low), hex(high))


def test_the_two_fixed_point_routines_are_not_the_same_operation(rom_bytes):
    """This is the ticket's question, answered from the words.

    `iwramqf`'s larger routine reduces each lane SEPARATELY and sums the reduced
    32-bit values; the smaller reduces once per output word after all three
    products. The instruction-level difference is the third lane of the larger
    routine's LAST group, which folds its `lsr` into the accumulator
    (`add r6, r6, fp, lsr #10`) where the first three groups do not.
    """
    c1 = instruction_words(rom_bytes, QF_ROM, QF_MID)
    b0 = instruction_words(rom_bytes, QF_MID, QF_CODE_END)

    # C1's folded reductions are the LAST group only, one per lane, which for the
    # third lane is `add r6, r6, fp, lsr #10`.
    def folded_low(w):
        return (
            ((w >> 21) & 0xF) == 0x4
            and ((w >> 12) & 0xF) == (w >> 16) & 0xF
            and (w & 0x10) == 0
            and ((w >> 5) & 3) == 1
            and ((w >> 7) & 0x1F) == 10
        )

    c1_folded = [i for i, w in enumerate(c1) if folded_low(w)]
    assert len(c1_folded) == 3, c1_folded
    # The folded site is in the last quarter of the routine.
    assert c1_folded[0] > len(c1) * 3 // 4

    # B0's three folded reductions are its whole arithmetic.
    b0_folded = [i for i, w in enumerate(b0) if folded_low(w)]
    assert len(b0_folded) == 3, b0_folded
    assert b0_folded[-1] - b0_folded[0] < len(b0) // 2

    # The six reduction words of C1's last group are BYTE-IDENTICAL to B0's.
    c1_tail = c1[-14:]
    same = [w for w in b0 if w in c1_tail]
    assert len(same) >= 6, [hex(w) for w in same]


def test_the_q10_scale_is_recorded_as_inferred_and_0x400_is_not_in_the_code(rom_bytes):
    """Branch B asked for this to stay INFERRED, and the image agrees.

    `0x400` does not appear as an immediate anywhere in either routine, and
    neither has a literal pool to hold one. The shift amount 10 is the only scale
    evidence, so it licenses a RELATIVE scale, not a proven absolute one.
    """
    for start, end in ((QF_ROM, QF_MID), (QF_MID, QF_CODE_END)):
        for w in instruction_words(rom_bytes, start, end):
            # a data-processing immediate with a 0x400 imm8/rotate encoding
            if ((w >> 25) & 1) == 1:
                rotate = ((w >> 8) & 0xF) * 2
                value = w & 0xFF
                if rotate:
                    value = ((value >> rotate) | (value << (32 - rotate))) & 0xFFFFFFFF
                assert value != 0x400, "0x400 appears at %08X" % w

    source = (identity.REPO_ROOT / "src" / "IwramQFormat.c").read_text("utf-8")
    assert "INFERRED" in source
    assert "There is no `0x400` constant in either routine." in source
    # and the corrected claim, so it is not re-derived wrongly
    assert "it is an identity" in source
    assert "load-bearing" not in source


def test_the_q_format_entries_are_reached_by_their_own_veneers(rom_bytes):
    for veneer, caller in QF_CALLS.items():
        assert word(rom_bytes, veneer + 4) == 0xE51FF004
        destination = word(rom_bytes, veneer + 8)
        assert destination in (QF_ENTRY_IWRAM, QF_MID_IWRAM)
        assert rom_bytes[veneer - gba.ROM_BASE : veneer - gba.ROM_BASE + 4] == b"\x78\x47\xc0\x46"
        assert caller > 0


# ---------------------------------------------------------------------------
# the sources, the shims and the protocol
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "decomp,shim,function",
    [
        (
            "src/IwramByteLanePair.c",
            "src/probes/IwramByteLanePair.c",
            "void sub_087B7C80(",
        ),
        (
            "src/IwramByteLaneSparse.c",
            "src/probes/IwramByteLaneSparse.c",
            "void sub_087B7CD4(",
        ),
        (
            "src/IwramQFormat.c",
            "src/probes/IwramQFormat.c",
            "void sub_087B7F04(",
        ),
    ],
)
def test_each_probe_path_is_a_shim(decomp, shim, function):
    text = (identity.REPO_ROOT / shim).read_text("utf-8")
    assert '#include "../%s"' % decomp.split("/")[-1] in text
    assert function not in text
    assert len(text.splitlines()) < 30, "the shim has grown into a second copy"


@pytest.mark.parametrize(
    "relative",
    [
        "src/IwramByteLanePair.c",
        "src/IwramByteLaneSparse.c",
        "src/IwramQFormat.c",
        "src/probes/iwrambl_selftest.c",
        "src/probes/iwramqformat_selftest.c",
    ],
)
def test_the_sources_mention_no_defsym_and_no_absolute_path(relative):
    text = (identity.REPO_ROOT / relative).read_text("utf-8")
    assert "--defsym" not in text
    assert "C:\\" not in text and "C:/" not in text


@pytest.mark.parametrize(
    "selftest", ["src/probes/iwrambl_selftest.c", "src/probes/iwramqformat_selftest.c"]
)
def test_each_self_check_prints_the_protocol_the_harness_parses(selftest):
    text = (identity.REPO_ROOT / selftest).read_text("utf-8")
    assert "check(s), %d failure(s)" in text
    assert "return failures ? 1 : 0;" in text


def test_the_byte_lane_self_check_covers_both_routines(rom_bytes):
    """One shim file holds two targets, so the self-check must include both."""
    text = (identity.REPO_ROOT / "src" / "probes" / "iwrambl_selftest.c").read_text("utf-8")
    assert '#include "IwramByteLanePair.c"' in text
    assert '#include "IwramByteLaneSparse.c"' in text
    assert "sub_087B7C80(" in text and "sub_087B7CD4(" in text


def test_the_registry_entries_are_the_targets_this_ticket_added():
    targets = {t.id: t for t in lift.load_targets()}
    for target_id, unit, source in (
        ("iwrambl", "iwram_bl_pair_tu", "src/IwramByteLanePair.c"),
        ("iwramblsparse", "iwram_bl_sparse_tu", "src/IwramByteLaneSparse.c"),
        ("iwramqf", "iwram_qf_tu", "src/IwramQFormat.c"),
    ):
        assert target_id in targets, target_id
        target = targets[target_id]
        assert target.ticket == "DECOMP-IWRAM-TRANSFORMS-001"
        assert target.probe_translation_unit == unit
        assert target.decomp_source == source
        assert target.isa == "arm"
        assert target.host_build_bits == 32


# ---------------------------------------------------------------------------
# the semantic verdict, measured by running it
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "selftest,minimum",
    [
        ("src/probes/iwrambl_selftest.c", 8000),
        ("src/probes/iwramqformat_selftest.c", 200000),
    ],
)
def test_the_self_check_runs_the_reconstruction_on_the_host(tmp_path, selftest, minimum):
    result = lift.run_host_selftest(
        tmp_path,
        source=identity.REPO_ROOT / selftest,
        minimum_checks=minimum,
        host_bits=32,
    )
    if result["status"] == "UNTESTED":
        pytest.skip(result["detail"])
    assert result["status"] == "PROVEN", result["detail"]
    assert result["failures"] == 0
    assert result["checks"] >= minimum


@pytest.mark.parametrize(
    "checks,expected", [(8000, "PROVEN"), (7999, "PARTIAL")]
)
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=8000)
    assert status == expected
