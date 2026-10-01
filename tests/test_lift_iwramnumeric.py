"""DECOMP-IWRAM-NUMERIC-001: the IWRAM block's numeric and data-processing families.

Two targets, inside the 4100-byte block the reset code copies to IWRAM
0x03000000 (ROM 0x087B79A4..0x087B89A8):

* ``iwramq1814``       0x087B820C  484 B  121 insns  Q18.14 signed-byte resampler
* ``iwramfieldclamp``  0x087B83F0  148 B   37 insns  ten-bit field clamp

Everything asserted about the ROM is re-derived from the cartridge on every run:
the extents by the harness's own aligned chain-walk, the Q18.14 anchors, the MLA
and conditional-load counts, the eight shift sites of the clamp and its
saturation pattern, all decoded from the instruction words.

The two questions this ticket exists to settle are answered from the words:

* whether either routine has a sibling shape in the overlay - it does not, and
  the counts below are the refutation; and
* what the clamp's eight shift sites are, and why the brief's "sum 38" is the
  sum of the two DISTINCT amounts of one extraction pair rather than of all
  eight.

PORTABLE tests need no ROM, no toolchain and no host compiler. ROM-gated tests
skip cleanly, as does the semantic run when no host compiler is present. The ROM
is opened READ-ONLY and nothing here writes to it.
"""

from __future__ import annotations

import hashlib

import capstone
import pytest
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM

from buusfury import gba, identity, lift

#: The block's ROM bytes ARE its IWRAM bytes, verbatim.
IWRAM_BLOB_ROM = 0x087B79A4
IWRAM_BASE = 0x03000000

Q_ROM = 0x087B820C
Q_IWRAM = 0x03000868
Q_CODE_END = 0x087B83F0
Q_INSTRUCTIONS = 121
Q_BYTES = 484
#: sha1 of the whole 484-byte body, so the listing cannot drift unnoticed.
Q_BODY_SHA1 = "bb4766f12c739f41f3f44f1eb745b1b638068967"

C_ROM = 0x087B83F0
C_IWRAM = 0x03000A4C
C_CODE_END = 0x087B8484
C_INSTRUCTIONS = 37
C_BYTES = 148
C_BODY_SHA1 = "f614e2a46da3853be42e75e7e94eec160f1b1ccb"

#: `add r3, r5, r3, asr #14` - the Q18.14 high word of the STARTING position.
Q_ANCHOR_HI_ADDRESS = 0xE0853743
#: `lsl r7, r3, #0x12` - the low word of the same Q18.14 value.
Q_ANCHOR_LO_ADDRESS = 0xE1A07903
#: `lsl r8, r4, #0x12` and `asr r4, r4, #0xE` - the increment's two halves.
Q_ANCHOR_LO_STEP = 0xE1A08904
Q_ANCHOR_HI_STEP = 0xE1A04744
#: `ldrsbhs r0, [r3, #1]!` - condition HS, pre-indexed, writeback.
Q_CONDITIONAL_LOAD = 0x21F300D1
#: `cmp r4, #0` - selects the carry-only body when `B asr 14` is zero.
Q_SPECIALIZATION_TEST = 0xE3540000
#: The Duff's-device terminators.
Q_GROUP_SUB8 = 0xE2522008
Q_GROUP_BHI = 0x8AFFFFD9
Q_ODD_SUB1 = 0xE2522001

#: The four saturation instructions of the clamp.
C_CLAMP_CMP = 0xE354007F      # cmp r4, #0x7f
C_CLAMP_MOVGT = 0xC3A0407F    # movgt r4, #0x7f
C_CLAMP_CMN = 0xE3740080      # cmn r4, #0x80
C_CLAMP_MVNLT = 0xB3E0407F    # mvnlt r4, #0x7f
#: `stm r2!, {r8, ip}` with r8 = ip = 0 - the source pair is zeroed in place.
C_SOURCE_ZERO = 0xE8A21100
#: `subs r3, r3, #2` / `bgt` - the signed do-while over word pairs.
C_PAIR_SUB = 0xE2533002
C_PAIR_BGT = 0xCAFFFFDF

#: The eight shift sites of the clamp: (ROM address, kind, amount).
C_SHIFT_SITES = (
    (0x087B8404, "standalone", "asr", 22),
    (0x087B8408, "standalone", "asr", 22),
    (0x087B840C, "standalone", "lsl", 16),
    (0x087B8410, "standalone", "lsl", 16),
    (0x087B8414, "standalone", "asr", 22),
    (0x087B8418, "standalone", "asr", 22),
    (0x087B8460, "folded", "lsl", 8),
    (0x087B8468, "folded", "lsl", 8),
)
C_SHIFT_SUM = 136
#: The number the ticket's brief carried, and the pair it is the sum of.
C_BRIEF_SUM = 38


# ---------------------------------------------------------------------------
# ROM helpers: pure bit arithmetic, so nothing here needs a disassembler
# ---------------------------------------------------------------------------
def word(data: bytes, address: int) -> int:
    offset = address - gba.ROM_BASE
    return int.from_bytes(data[offset : offset + 4], "little")


def instruction_words(data: bytes, start: int, end: int) -> list:
    return [word(data, a) for a in range(start, end, 4)]


def scalar_shift(w: int):
    """(operator, type, amount) for a data-processing instruction with an
    immediate-shifted register operand, or None when there is no shift.

    Word bit 4 is the I bit: CLEAR means the shift amount is an immediate, which
    is the only form these two routines use. Shift type 0 is LSL, 1 LSR, 2 ASR,
    3 ROR, and the amount is bits 11..7."""
    if (w & 0x10) != 0:
        return None
    operand = (w >> 25) & 0x3
    if operand != 0:
        return None
    shift_type = (w >> 5) & 3
    amount = (w >> 7) & 0x1F
    return shift_type, amount


def is_standalone_shift(w: int) -> bool:
    """`mov Rd, Rm, <shift>` - opcode 1101 with a shifted register operand."""
    return ((w >> 21) & 0xF) == 0xD and (w & 0x10) == 0


def is_folded_shift(w: int, opcode: int) -> bool:
    return ((w >> 21) & 0xF) == opcode and (w & 0x10) == 0


# ---------------------------------------------------------------------------
# the extents, re-derived by the harness on every run
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "unit_id,expected",
    [
        ("iwram_q1814_tu", [(Q_ROM, Q_CODE_END, Q_INSTRUCTIONS)]),
        ("iwram_field_clamp_tu", [(C_ROM, C_CODE_END, C_INSTRUCTIONS)]),
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


@pytest.mark.parametrize("unit_id", ["iwram_q1814_tu", "iwram_field_clamp_tu"])
def test_no_new_unit_declares_a_literal_pool(rom_bytes, unit_id):
    """Both routines are register-only, so the pool test is not applicable."""
    derived = lift.derive_unit_boundaries(rom_bytes, unit_id)
    assert derived["has_literal_pool"] is False
    assert derived["pool_extent"] is None


def test_the_two_units_are_adjacent_and_the_boundary_is_shared(rom_bytes):
    """The clamp begins at exactly the byte the sampler ends at."""
    assert Q_CODE_END == C_ROM
    assert word(rom_bytes, Q_CODE_END - 4) == 0xE12FFF1E       # the sampler's bx lr
    assert word(rom_bytes, C_ROM) == 0xE92D01F0                # push {r4,r5,r6,r7,r8}
    assert word(rom_bytes, C_CODE_END - 4) == 0xE12FFF1E       # the clamp's bx lr


def test_the_recorded_bodies_are_the_recorded_bytes(rom_bytes):
    """Pin the whole listing by digest, so no instruction claim can drift."""
    q = rom_bytes[Q_ROM - gba.ROM_BASE : Q_CODE_END - gba.ROM_BASE]
    c = rom_bytes[C_ROM - gba.ROM_BASE : C_CODE_END - gba.ROM_BASE]
    assert len(q) == Q_BYTES and len(c) == C_BYTES
    assert hashlib.sha1(q).hexdigest() == Q_BODY_SHA1
    assert hashlib.sha1(c).hexdigest() == C_BODY_SHA1
    # both end in a single `bx lr`
    assert word(rom_bytes, Q_CODE_END - 4) == 0xE12FFF1E
    assert word(rom_bytes, C_CODE_END - 4) == 0xE12FFF1E


# ---------------------------------------------------------------------------
# the Q18.14 family - exactly two pairs, both here
# ---------------------------------------------------------------------------
def test_exactly_two_q1814_pairs_exist_in_the_whole_code_half(rom_bytes):
    """The ticket's question: does 0x03000868 have a sibling? The image says no.

    A Q18.14 anchor is a `lsl #18` and an `asr #14` on the SAME source register.
    Both routines' words are scanned, and then the whole 3908-byte code half, so
    the refutation is a measurement over the overlay rather than a claim about
    one function.
    """
    lsl18 = []
    asr14 = []
    for address in range(IWRAM_BLOB_ROM, IWRAM_BLOB_ROM + 0xF44, 4):
        w = word(rom_bytes, address)
        scal = scalar_shift(w)
        if scal is None:
            continue
        shift_type, amount = scal
        source = w & 0xF            # the shifted register in both spellings
        if shift_type == 0 and amount == 18:
            lsl18.append((address, source))
        if shift_type == 2 and amount == 14:
            asr14.append((address, source))

    assert [a for a, _s in lsl18] == [0x087B820C + 8, 0x087B820C + 12], [
        hex(a) for a, _s in lsl18
    ]
    assert [a for a, _s in asr14] == [0x087B820C + 16, 0x087B820C + 20], [
        hex(a) for a, _s in asr14
    ]
    # The same two source registers in the same order: r3 then r4.
    assert [s for _a, s in lsl18] == [3, 4]
    assert [s for _a, s in asr14] == [3, 4]
    # ZERO unpaired occurrences of either amount anywhere in the code half.
    assert len(lsl18) == 2 and len(asr14) == 2


def test_the_q1814_anchors_are_the_recorded_words(rom_bytes):
    body = instruction_words(rom_bytes, Q_ROM, Q_CODE_END)
    assert body[2] == Q_ANCHOR_LO_ADDRESS        # lsl r7, r3, #0x12
    assert body[3] == Q_ANCHOR_LO_STEP           # lsl r8, r4, #0x12
    assert body[4] == Q_ANCHOR_HI_ADDRESS        # add r3, r5, r3, asr #14
    assert body[5] == Q_ANCHOR_HI_STEP           # asr r4, r4, #0xE
    assert body[0] == 0xE92D07F0                 # push {r4,r5,r6,r7,r8,sb,sl}
    assert body[1] == 0xE8900078                 # ldm r0, {r3,r4,r5,r6}
    # `add r3, r5, r3, asr #14`: opcode 0100, rd 3, rn 5, rm 3, ASR 14.
    word_hi = body[4]
    assert ((word_hi >> 21) & 0xF) == 0x4
    assert ((word_hi >> 12) & 0xF) == 3
    assert ((word_hi >> 16) & 0xF) == 5
    assert (word_hi & 0xF) == 3
    assert ((word_hi >> 5) & 3) == 2 and ((word_hi >> 7) & 0x1F) == 14


def test_the_q1814_mla_and_ldrsb_census(rom_bytes):
    """21 value-accumulating MLA sites and 22 signed byte loads, all here.

    Every MLA has the form `Rd := r6 * Rs + Rn` with Rs the register the sample
    was loaded into, which is what makes them VALUE accumulation rather than
    pointer arithmetic.
    """
    body = instruction_words(rom_bytes, Q_ROM, Q_CODE_END)
    mla = [w for w in body if (w & 0x0FE000F0) == 0x00200090]
    assert len(mla) == 21, [hex(w) for w in mla]
    for w in mla:
        # MLA's operand order is Rd, Rm, Rs, Rn, so the multiplier Rm is the
        # LOWEST nibble - not bits 11..8, which is Rs.
        assert (w & 0xF) == 6, "the multiplier is the record's fourth word"
        assert ((w >> 12) & 0xF) == ((w >> 16) & 0xF), "Rn == Rd: accumulate"

    plain = [w for w in body if (w & 0x0FF00FF0) == 0x01D000D0]
    conditional = [w for w in body if w == Q_CONDITIONAL_LOAD]
    assert len(plain) == 12, [hex(w) for w in plain]
    assert len(conditional) == 10
    # `ldrsbhs r0,[r3,#1]!` is CONDITION HS (0010), P=1, W=1 and imm 1.
    assert (Q_CONDITIONAL_LOAD >> 28) == 0x2, "condition 0010 is HS (carry set)"
    assert ((Q_CONDITIONAL_LOAD >> 24) & 1) == 1, "P: pre-indexed"
    assert ((Q_CONDITIONAL_LOAD >> 21) & 1) == 1, "W: writeback"
    assert (Q_CONDITIONAL_LOAD & 0xF) == 1, "the offset is +1"
    assert Q_SPECIALIZATION_TEST in body, "cmp r4, #0 selects the carry-only body"


def test_the_q1814_group_structure_is_the_recorded_one(rom_bytes):
    """The Duff's device: a 1-element block, a 2-group, and an 8-subtracting loop.

    The asymmetry the model has to reproduce is that `tst r2,#4` skips the first
    4-element group while `subs r2,r2,#8` subtracts eight anyway.
    """
    body = instruction_words(rom_bytes, Q_ROM, Q_CODE_END)
    assert body.count(Q_GROUP_SUB8) == 2, "two `subs r2,r2,#8` sites: one per body"
    # The two `bhi`s differ only in their displacement, because each loops back
    # into its OWN body, so they are counted by condition and opcode.
    bhi = [w for w in body if (w >> 28) == 0x8 and ((w >> 25) & 7) == 5]
    assert len(bhi) == 2, [hex(w) for w in bhi]
    assert Q_GROUP_BHI in body and 0x8AFFFFE1 in body, [hex(w) for w in bhi]
    assert Q_ODD_SUB1 in body, "the 1-element block decrements by one"
    assert body.count(0xE3120001) == 1, "tst r2, #1"
    assert body.count(0xE3120002) == 2, "tst r2, #2, once per body"
    assert body.count(0xE3120004) == 2, "tst r2, #4, once per body"
    # There is NO pre-test on the count before the body: the only compares are the
    # bit tests and the specialization test.
    compares = [w for w in body if ((w >> 21) & 0xF) == 0xA and ((w >> 20) & 1)]
    assert compares == [Q_SPECIALIZATION_TEST], [hex(w) for w in compares]
    assert (Q_GROUP_BHI >> 28) == 0x8, "condition 1000 is HI (unsigned higher)"


def test_the_q1814_specialization_selector_is_the_high_word_of_B(rom_bytes):
    """`cmp r4,#0` where r4 = `B asr 14`: zero for 0 <= B <= 16383, and NOT for
    a negative B, whose arithmetic shift is all ones."""
    assert ((0x00003FFF) >> 14) == 0
    assert ((0x00004000) >> 14) == 1
    assert ((-1) >> 14) == -1
    assert ((-16384) >> 14) == -1
    source = (identity.REPO_ROOT / "src" / "IwramQ1814.c").read_text("utf-8")
    assert "0 <= B <= 16383" in source
    assert "NOT |B| < 2^14" in source or "NOT `|B| < 2^14`" in source
    # and the retention, which is the behaviour a "tidier" rewrite loses
    assert "RETAINED" in source
    assert "no load, no memory" in source


# ---------------------------------------------------------------------------
# the clamp family
# ---------------------------------------------------------------------------
def test_the_clamp_has_exactly_eight_shift_sites_and_they_sum_to_136(rom_bytes):
    """The brief said eight sites summing to 38. The amounts are 22,22,16,16,
    22,22,8,8 and the sum is 136; 38 is 22 + 16, the two DISTINCT amounts of one
    extraction pair."""
    body = instruction_words(rom_bytes, C_ROM, C_CODE_END)
    sites = []
    for index, w in enumerate(body):
        address = C_ROM + 4 * index
        scal = scalar_shift(w)
        if scal is None:
            continue
        shift_type, amount = scal
        name = {0: "lsl", 1: "lsr", 2: "asr", 3: "ror"}[shift_type]
        if amount == 0 and shift_type == 0:
            continue                       # an unshifted register operand
        if is_standalone_shift(w):
            sites.append((address, "standalone", name, amount))
        elif is_folded_shift(w, 0xC) or is_folded_shift(w, 0x4):
            sites.append((address, "folded", name, amount))
    assert sites == list(C_SHIFT_SITES), sites
    assert len(sites) == 8
    assert sum(amount for _a, _k, _n, amount in sites) == C_SHIFT_SUM
    assert sum(amount for _a, _k, _n, amount in sites) != C_BRIEF_SUM
    assert 22 + 16 == C_BRIEF_SUM, "the brief's number is these two amounts"
    # The low-field extraction is a PAIR on the same register: lsl #16 then
    # asr #22, and the intermediate 32-bit logical shift is what makes it a
    # ten-bit sign extension rather than a net >> 6.
    low = [s for s in sites if s[2] == "lsl" and s[3] == 16]
    high = [s for s in sites if s[2] == "asr" and s[3] == 22]
    assert len(low) == 2 and len(high) == 4
    assert 16 < 22, "the logical shift is the FIRST of the pair"


def test_the_clamp_shift_amounts_are_the_recorded_words(rom_bytes):
    assert word(rom_bytes, 0x087B8404) == 0xE1A05B44      # asr r5, r4, #0x16
    assert word(rom_bytes, 0x087B8408) == 0xE1A07B46      # asr r7, r6, #0x16
    assert word(rom_bytes, 0x087B840C) == 0xE1A04804      # lsl r4, r4, #0x10
    assert word(rom_bytes, 0x087B8410) == 0xE1A06806      # lsl r6, r6, #0x10
    assert word(rom_bytes, 0x087B8414) == 0xE1A04B44      # asr r4, r4, #0x16
    assert word(rom_bytes, 0x087B8418) == 0xE1A06B46      # asr r6, r6, #0x16
    assert word(rom_bytes, 0x087B8460) == 0xE1844406      # orr r4, r4, r6, lsl #8
    assert word(rom_bytes, 0x087B8468) == 0xE1855407      # orr r5, r5, r7, lsl #8


def test_the_clamps_saturation_pattern_occurs_once_in_the_whole_image(rom_bytes):
    """`cmp #0x7F ; movgt #0x7F ; cmn #0x80 ; mvnlt #0x7F` - four consecutive
    words - and the pattern occurs exactly ONCE in the 8 MiB image."""
    pattern = bytes(
        b for w in (C_CLAMP_CMP, C_CLAMP_MOVGT, C_CLAMP_CMN, C_CLAMP_MVNLT)
        for b in w.to_bytes(4, "little")
    )
    hits = []
    start = 0
    while True:
        index = rom_bytes.find(pattern, start)
        if index < 0:
            break
        hits.append(gba.ROM_BASE + index)
        start = index + 1
    assert hits == [0x087B841C], [hex(h) for h in hits]
    body = instruction_words(rom_bytes, C_ROM, C_CODE_END)
    assert body.count(C_CLAMP_CMP) == 1
    assert body.count(C_CLAMP_MOVGT) == 1
    assert body.count(C_CLAMP_CMN) == 1
    assert body.count(C_CLAMP_MVNLT) == 1
    # ARMv4T has no SSAT/USAT, so a saturation can only be a conditional move.
    assert (C_CLAMP_MOVGT >> 28) == 0xC, "GT after `cmp #0x7F`"
    assert (C_CLAMP_MVNLT >> 28) == 0xB, "LT after `cmn #0x80`"


def test_the_clamp_zeroes_its_source_pair_and_writes_two_post_indexed_halfwords(
        rom_bytes):
    body = instruction_words(rom_bytes, C_ROM, C_CODE_END)
    assert body.count(C_SOURCE_ZERO) == 1
    assert body.count(0xE8920050) == 1, "ldm r2, {r4, r6}"
    assert body.count(C_PAIR_SUB) == 1 and body.count(C_PAIR_BGT) == 1
    assert (C_PAIR_BGT >> 28) == 0xC, "condition 1100 is GT (signed)"

    # Two POST-INDEXED halfword stores, decoded rather than masked by hand: a
    # hand-written mask got the P/W/L field positions wrong twice while this
    # ticket was being assembled, so the shape comes from the decoder.
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    md.detail = True
    instructions = list(
        md.disasm(rom_bytes[C_ROM - gba.ROM_BASE : C_CODE_END - gba.ROM_BASE], C_ROM)
    )
    assert len(instructions) == C_INSTRUCTIONS
    stores = [i for i in instructions if i.mnemonic == "strh"]
    assert len(stores) == 2, [i.mnemonic for i in instructions]
    for ins in stores:
        assert ins.writeback is True, "the base IS advanced"
        # post-indexed: the memory operand carries the base and NO displacement,
        # and the offset is a third, immediate operand
        mem = ins.operands[1].mem
        assert mem.disp == 0
        assert ins.operands[2].type == capstone.arm.ARM_OP_IMM
        assert ins.operands[2].imm == 2
    assert {ins.operands[0].reg - capstone.arm.ARM_REG_R0 for ins in stores} == {4, 5}
    assert {ins.operands[1].mem.base - capstone.arm.ARM_REG_R0 for ins in stores} \
        == {0, 1}, "the two cursor registers r0 and r1"


def test_the_clamp_records_the_briefs_number_as_a_refuted_measurement():
    source = (identity.REPO_ROOT / "src" / "IwramFieldClamp.c").read_text("utf-8")
    assert "22, 22, 16, 16, 22, 22, 8, 8" in source
    registry = (identity.REPO_ROOT / "config" / "lift_targets.json").read_text("utf-8")
    assert "summing to 136 and not 38" in registry


# ---------------------------------------------------------------------------
# the sources, the shims and the protocol
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "decomp,shim,function",
    [
        ("src/IwramQ1814.c", "src/probes/IwramQ1814.c", "void sub_087B820C("),
        ("src/IwramFieldClamp.c", "src/probes/IwramFieldClamp.c",
         "void sub_087B83F0("),
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
        "src/IwramQ1814.c",
        "src/IwramFieldClamp.c",
        "src/probes/iwramq1814_selftest.c",
        "src/probes/iwramfieldclamp_selftest.c",
    ],
)
def test_the_sources_mention_no_defsym_and_no_absolute_path(relative):
    text = (identity.REPO_ROOT / relative).read_text("utf-8")
    assert "--defsym" not in text
    assert "C:\\" not in text and "C:/" not in text


@pytest.mark.parametrize(
    "selftest",
    ["src/probes/iwramq1814_selftest.c", "src/probes/iwramfieldclamp_selftest.c"],
)
def test_each_self_check_prints_the_protocol_the_harness_parses(selftest):
    text = (identity.REPO_ROOT / selftest).read_text("utf-8")
    assert "check(s), %d failure(s)" in text
    assert "return failures ? 1 : 0;" in text


def test_the_q1814_self_check_pins_both_specializations():
    text = (identity.REPO_ROOT / "src" / "probes" / "iwramq1814_selftest.c").read_text(
        "utf-8"
    )
    # the retained sample, which is what a "tidier" single-loop rewrite loses
    assert "RETAIN" in text.upper()
    assert "0x00004080" in text, "the retained-sample expectation"
    assert "0x0000C180" in text, "and the value re-reading would produce instead"


def test_the_registry_entries_are_the_targets_this_ticket_added():
    targets = {t.id: t for t in lift.load_targets()}
    for target_id, unit, source, minimum in (
        ("iwramq1814", "iwram_q1814_tu", "src/IwramQ1814.c", 20000),
        ("iwramfieldclamp", "iwram_field_clamp_tu", "src/IwramFieldClamp.c", 60000),
    ):
        assert target_id in targets, target_id
        target = targets[target_id]
        assert target.ticket == "DECOMP-IWRAM-NUMERIC-001"
        assert target.probe_translation_unit == unit
        assert target.decomp_source == source
        assert target.isa == "arm"
        assert target.host_build_bits == 32
        assert target.semantic_minimum_checks == minimum


def test_adding_these_targets_did_not_restate_the_q_format_family():
    """The sibling's `notes` are byte-for-byte what they were.

    A registry `notes` string feeds that target's committed report, so a ticket
    that adds a family member does not own its sibling's prose. The sentence
    below is now stale - the routine it calls unlifted is this ticket's target -
    and it is deliberately PRESERVED here so `config/lift_iwramqf.json` stays
    byte-identical. docs/LIFT_IWRAM_NUMERIC.md records the staleness.
    """
    import json

    targets = {t.id: t for t in lift.load_targets()}
    notes = targets["iwramqf"].notes
    assert "It remains unlifted and is the recommended next cluster." in notes
    report = json.loads(
        (identity.REPO_ROOT / "config" / "lift_iwramqf.json").read_text("utf-8")
    )
    assert report["target"]["notes"] == notes
    doc = (identity.REPO_ROOT / "docs" / "LIFT_IWRAM_NUMERIC.md").read_text("utf-8")
    assert "stale" in doc.lower()


# ---------------------------------------------------------------------------
# the semantic verdict, measured by running it
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "selftest,minimum",
    [
        ("src/probes/iwramq1814_selftest.c", 20000),
        ("src/probes/iwramfieldclamp_selftest.c", 60000),
    ],
)
def test_the_self_check_runs_the_reconstruction_on_the_host(tmp_path, selftest,
                                                            minimum):
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


@pytest.mark.parametrize("checks,expected", [(20000, "PROVEN"), (19999, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=20000)
    assert status == expected
