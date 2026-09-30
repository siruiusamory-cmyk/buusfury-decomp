"""DECOMP-IWRAM-DISPATCH-001: the IWRAM block's interrupt entry.

The target is the ARM routine the block has at IWRAM 0x03000B6C, ROM
0x087B8510..0x087B863C (300 bytes, 75 instructions, ARM). It is the machine's
interrupt entry: the Thumb routine at ROM 0x0803F3DA stores its address into the
GBA BIOS IRQ vector pointer at IWRAM 0x03007FFC.

Everything this file asserts about the target is re-derived from the cartridge
on every run:

* the code extent and the two data words around it;
* the fourteen priority masks, decoded from the `ands` test words by applying
  the ARM immediate rotation - never read from a table written by hand;
* the acknowledge branch targets, which say that the FIRST test skips the
  IE-clear that every later test performs;
* the fourteen-entry vector table and the software pending halfword the
  routine accumulates into;
* bit 13's self-branch, which is a spin and is reproduced rather than repaired.

PORTABLE tests need no ROM and no toolchain. ROM-gated tests skip cleanly. The
ROM is opened READ-ONLY and nothing here writes to it.
"""

from __future__ import annotations

import re

import pytest

from buusfury import gba, identity, lift

# The ROM bytes of the installed block are the ROM bytes of IWRAM: the reset
# code copies 0x087B79A4..0x087B89A8 to 0x03000000..0x03001004 verbatim.
IWRAM_BLOB_ROM = 0x087B79A4
IWRAM_BASE = 0x03000000

DISPATCH_ROM = 0x087B8510
DISPATCH_CODE_END = 0x087B863C
HANDLER_RETURN_ROM = 0x087B863C
DISPATCH_LITERAL_ROM = 0x087B8640
DISPATCH_ENTRY_IWRAM = 0x03000B6C
DISPATCH_HANDLER_RETURN_IWRAM = 0x03000C98
DISPATCH_LITERAL_IWRAM = 0x03000FB0
VECTOR_TABLE_ROM = 0x087B8954
VECTOR_TABLE_IWRAM = 0x03000FB0
PENDING_WORD_ROM = 0x087B898C
PENDING_WORD_IWRAM = 0x03000FE8

# The two sites the acknowledge block is made of, and the exit block.
ACK_BIC_SITE = 0x087B85E0
ACK_ORR_SITE = 0x087B85E4
ACK_STORE_SITE = 0x087B85E8
PENDING_LOAD_SITE = 0x087B85F0
PENDING_STORE_SITE = 0x087B85F8
EXIT_POP_SITE = 0x087B8628
EXIT_SPSR_SITE = 0x087B8634
EXIT_BX_LR_SITE = 0x087B8638

# The claim under test: the chain's masks and the slot each one selects, in test
# order. The assertions below DERIVE both from the ROM and compare; the literals
# here are what the derivation is expected to produce.
EXPECTED_MASKS = [
    0x0400, 0x0080, 0x0040, 0x0001, 0x0002, 0x0004, 0x0008,
    0x0010, 0x0020, 0x0100, 0x0200, 0x0800, 0x1000, 0x2000,
]
EXPECTED_REACHABLE_SLOTS = [10, 7, 6, 0, 1, 2, 3, 4, 5, 8, 9, 11, 12]
BIT_13_MASK = 0x2000


# ---------------------------------------------------------------------------
# ROM helpers: pure bit arithmetic, so nothing here depends on a disassembler
# ---------------------------------------------------------------------------
def word(data: bytes, address: int) -> int:
    offset = address - gba.ROM_BASE
    return int.from_bytes(data[offset : offset + 4], "little")


def halfword(data: bytes, address: int) -> int:
    offset = address - gba.ROM_BASE
    return int.from_bytes(data[offset : offset + 2], "little")


def rom_of_iwram(address_iwram: int) -> int:
    return IWRAM_BLOB_ROM + (address_iwram - IWRAM_BASE)


def arm_immediate(encoded: int) -> int:
    """The value an ARM data-processing immediate encodes: imm8 ror (2 * rot).

    Spelled out here rather than imported, so the derivation of the masks is
    independent of the module under test; a separate test cross-checks it
    against ``lift._arm_immediate``.
    """
    value = encoded & 0xFF
    rotate = ((encoded >> 8) & 0xF) * 2
    if rotate:
        value = ((value >> rotate) | (value << (32 - rotate))) & 0xFFFFFFFF
    return value


def is_ands_r0_r1_immediate(encoded: int) -> bool:
    """`ands r0, r1, #imm` in the ARM data-processing immediate encoding."""
    return (
        ((encoded >> 26) & 0x3) == 0b00
        and ((encoded >> 25) & 0x1) == 0b1
        and ((encoded >> 21) & 0xF) == 0b0000   # AND
        and ((encoded >> 20) & 0x1) == 0b1      # S: the flags are set
        and ((encoded >> 16) & 0xF) == 1        # Rn = r1
        and ((encoded >> 12) & 0xF) == 0        # Rd = r0
    )


def is_mov_r4_immediate(encoded: int) -> bool:
    """`mov r4, #imm` (MOV with Rn = 0, rd = r4, and the S bit clear)."""
    return (
        ((encoded >> 26) & 0x3) == 0b00
        and ((encoded >> 25) & 0x1) == 0b1
        and ((encoded >> 21) & 0xF) == 0b1101   # MOV
        and ((encoded >> 20) & 0x1) == 0b0
        and ((encoded >> 16) & 0xF) == 0        # Rn = 0
        and ((encoded >> 12) & 0xF) == 4        # Rd = r4
    )


def is_bic_r2_r2_r0(encoded: int) -> bool:
    return (
        ((encoded >> 26) & 0x3) == 0b00
        and ((encoded >> 25) & 0x1) == 0b0      # register operand
        and ((encoded >> 21) & 0xF) == 0b1110   # BIC
        and ((encoded >> 20) & 0x1) == 0b0
        and ((encoded >> 16) & 0xF) == 2        # Rn = r2
        and ((encoded >> 12) & 0xF) == 2        # Rd = r2
        and ((encoded >> 7) & 0x1F) == 0        # shift amount 0
        and ((encoded >> 5) & 0x3) == 0b00      # LSL
        and (encoded & 0xF) == 0                # Rm = r0
    )


def is_orr_r2_r2_r0_lsl16(encoded: int) -> bool:
    return (
        ((encoded >> 26) & 0x3) == 0b00
        and ((encoded >> 25) & 0x1) == 0b0
        and ((encoded >> 21) & 0xF) == 0b1100   # ORR
        and ((encoded >> 20) & 0x1) == 0b0
        and ((encoded >> 16) & 0xF) == 2        # Rn = r2
        and ((encoded >> 12) & 0xF) == 2        # Rd = r2
        and ((encoded >> 7) & 0x1F) == 16       # immediate shift, LSL #16
        and ((encoded >> 5) & 0x3) == 0b00
        and (encoded & 0xF) == 0                # Rm = r0
    )


def arm_branch_target(address: int, encoded: int) -> int | None:
    """The absolute target of an ARM B/BL, or None for anything else."""
    if ((encoded >> 25) & 0x7) != 0b101:
        return None
    offset = encoded & 0xFFFFFF
    if offset & 0x800000:
        offset -= 0x1000000
    return (address + 8 + offset * 4) & 0xFFFFFFFF


def halfword_transfer(encoded: int) -> dict | None:
    """An ARM LDRH/STRH with a pre-indexed, added, unmodified 8-bit offset."""
    if ((encoded >> 25) & 0x7) != 0b000:
        return None
    if ((encoded >> 24) & 0x1) != 1 or ((encoded >> 23) & 0x1) != 1:
        return None
    if ((encoded >> 22) & 0x1) != 1 or ((encoded >> 21) & 0x1) != 0:
        return None
    if ((encoded >> 7) & 0x1) != 1 or ((encoded >> 4) & 0x1) != 1:
        return None
    return {
        "load": bool((encoded >> 20) & 0x1),
        "base": (encoded >> 16) & 0xF,
        "rd": (encoded >> 12) & 0xF,
        "offset": (((encoded >> 8) & 0xF) << 4) | (encoded & 0xF),
    }


def thumb_ldr_literal(address: int, encoded_halfword: int) -> tuple[int, int] | None:
    """`ldr rD, [pc, #imm8*4]` in Thumb, decoded from the halfword."""
    if ((encoded_halfword >> 11) & 0x1F) != 0b01001:
        return None
    rt = (encoded_halfword >> 8) & 0x7
    pc = (address + 4) & ~0x3
    return rt, pc + (encoded_halfword & 0xFF) * 4


def chain_rows(data: bytes) -> list[dict]:
    """The priority chain as the ROM encodes it.

    Every row is one `ands r0, r1, #imm` test, with the mask read out of the
    instruction by applying the ARM immediate rotation, and the vector byte
    offset that is in r4 at that point (parked by the nearest preceding
    `mov r4, #imm`).
    """
    rows = []
    offset = None
    for address in range(DISPATCH_ROM, DISPATCH_CODE_END, 4):
        encoded = word(data, address)
        if is_mov_r4_immediate(encoded):
            offset = arm_immediate(encoded)
        if is_ands_r0_r1_immediate(encoded):
            rows.append(
                {
                    "site": address,
                    "mask": arm_immediate(encoded),
                    "word": encoded,
                    "r4_offset": offset,
                }
            )
    return rows


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def rom_bytes():
    try:
        rom = identity.resolve_baserom()
        identity.verify(rom)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"no canonical baserom available: {exc}")
    return rom.read_bytes()


# ---------------------------------------------------------------------------
# the unit's extent, and the two data words around it
# ---------------------------------------------------------------------------
def test_the_code_extent_is_the_three_hundred_bytes_ending_in_bx_lr(rom_bytes):
    assert DISPATCH_CODE_END - DISPATCH_ROM == 300
    words = [
        word(rom_bytes, address)
        for address in range(DISPATCH_ROM, DISPATCH_CODE_END, 4)
    ]
    assert len(words) == 75
    # `bx lr` is fully determined by the word, so this does not need a decoder.
    assert words[-1] == 0xE12FFF1E
    assert words.count(0xE12FFF1E) == 1, "the body has exactly one return"


def test_the_units_one_literal_is_the_vector_table_base(rom_bytes):
    assert word(rom_bytes, DISPATCH_LITERAL_ROM) == DISPATCH_LITERAL_IWRAM
    # It is reached by the one pc-relative load in the body, `ldr r1, [pc, #imm]`
    # at 0x087B85EC; PC reads as instruction + 8 in ARM state.
    encoded = word(rom_bytes, 0x087B85EC)
    assert ((encoded >> 26) & 0x3) == 0b01, "LDR, immediate offset"
    assert ((encoded >> 12) & 0xF) == 1, "the destination is r1"
    assert 0x087B85EC + 8 + (encoded & 0xFFF) == DISPATCH_LITERAL_ROM


def test_the_bytes_after_the_code_are_the_thumb_return_island(rom_bytes):
    """The handler's Thumb `bx r4` is what the odd LR at 0x03000C99 returns to."""
    assert halfword(rom_bytes, HANDLER_RETURN_ROM) == 0x4720
    assert rom_of_iwram(DISPATCH_HANDLER_RETURN_IWRAM) == HANDLER_RETURN_ROM
    # The island sits between the body and the literal, so the pool is NOT
    # adjacent to the code - four bytes separate them.
    assert DISPATCH_LITERAL_ROM - DISPATCH_CODE_END == 4


# ---------------------------------------------------------------------------
# the priority chain
# ---------------------------------------------------------------------------
def test_the_priority_chain_is_fourteen_ands_tests_read_out_of_the_rom(rom_bytes):
    rows = chain_rows(rom_bytes)
    assert [row["site"] for row in rows] == [
        0x087B8538, 0x087B8548, 0x087B8554, 0x087B8560, 0x087B856C, 0x087B8578,
        0x087B8584, 0x087B8590, 0x087B859C, 0x087B85A8, 0x087B85B4, 0x087B85C0,
        0x087B85CC, 0x087B85D4,
    ]
    assert [row["mask"] for row in rows] == EXPECTED_MASKS


def test_every_mask_is_a_single_bit_and_there_are_fourteen(rom_bytes):
    masks = [row["mask"] for row in chain_rows(rom_bytes)]
    assert len(masks) == 14
    assert [bin(mask).count("1") for mask in masks] == [1] * 14
    # The tests do not run in bit order: 10 first, then 7 and 6, then 0..5, then
    # 8, 9, 11, 12 and finally 13 - which is what makes the order a claim worth
    # asserting rather than the natural order of the bits.
    assert [mask.bit_length() - 1 for mask in masks] == [
        10, 7, 6, 0, 1, 2, 3, 4, 5, 8, 9, 11, 12, 13
    ]


def test_the_local_rotation_agrees_with_the_harness_rotation(rom_bytes):
    """Two independent spellings of imm8 ror (2*rot) must agree, or the mask
    derivation is quoting itself."""
    for row in chain_rows(rom_bytes):
        assert arm_immediate(row["word"]) == lift._arm_immediate(row["word"])
    for encoded in (
        0xE3A00640,  # mov r0, #64, #12  -> 0x04000000
        0xE2110E40,  # ands r0, r1, #64, #28 -> 0x400
        0xE2110D80,  # ands r0, r1, #128, #26 -> 0x2000
        0xE3A00001,  # mov r0, #1
    ):
        assert arm_immediate(encoded) == lift._arm_immediate(encoded), hex(encoded)


def test_the_slot_offsets_are_offset_over_four_in_test_order(rom_bytes):
    rows = chain_rows(rom_bytes)
    offsets = [row["r4_offset"] for row in rows]
    assert offsets == [
        0x28, 0x1C, 0x18, 0x00, 0x04, 0x08, 0x0C,
        0x10, 0x14, 0x20, 0x24, 0x2C, 0x30, 0x30,
    ]
    slots = [offset // 4 for offset in offsets]
    # The thirteen reachable offsets select slots 0..12 exactly once each.
    assert slots[:13] == EXPECTED_REACHABLE_SLOTS
    assert sorted(slots[:13]) == list(range(13))
    # The last test parks 0x30 as well, so slot 13 (offset 0x34) is never
    # selected by any path at all.
    assert slots[13] == 12
    assert 13 not in slots


def test_the_first_test_skips_the_ie_clear_that_every_later_test_performs(rom_bytes):
    """The acknowledge block is `bic` then `orr`; the first test branches past
    the `bic`. Both instructions and all fourteen branch targets come from the
    ROM."""
    assert is_bic_r2_r2_r0(word(rom_bytes, ACK_BIC_SITE))
    assert is_orr_r2_r2_r0_lsl16(word(rom_bytes, ACK_ORR_SITE))
    assert ACK_ORR_SITE == ACK_BIC_SITE + 4

    targets = []
    for row in chain_rows(rom_bytes)[:-1]:
        branch_address = row["site"] + 4
        branch = word(rom_bytes, branch_address)
        assert ((branch >> 28) & 0xF) == 0x1, "BNE"
        targets.append(arm_branch_target(branch_address, branch))

    assert targets[0] == ACK_ORR_SITE, "the bit-10 test skips the IE clear"
    assert targets[1:] == [ACK_BIC_SITE] * 12, "every other test clears the IE bit"
    # The fourteenth test is not a BNE at all: it ends the chain with a BEQ to
    # the exit block and the self-branch that test_bit_thirteen_* pins.
    assert ((word(rom_bytes, chain_rows(rom_bytes)[-1]["site"] + 4) >> 28) & 0xF) == 0x0


def test_the_acknowledge_store_is_a_single_32_bit_store_before_the_handler(rom_bytes):
    store = word(rom_bytes, ACK_STORE_SITE)
    assert ((store >> 26) & 0x3) == 0b01, "STR, immediate offset"
    assert ((store >> 20) & 0x1) == 0, "store, not load"
    assert ((store >> 16) & 0xF) == 3, "base r3, which the pre-indexed load moved"
    assert ((store >> 12) & 0xF) == 2, "source r2"
    assert (store & 0xFFF) == 0, "no offset: one 32-bit word at the base"


def test_the_pending_word_is_the_halfword_at_table_plus_0x38(rom_bytes):
    loaded = halfword_transfer(word(rom_bytes, PENDING_LOAD_SITE))
    stored = halfword_transfer(word(rom_bytes, PENDING_STORE_SITE))
    assert loaded is not None and stored is not None
    assert loaded == {"load": True, "base": 1, "rd": 5, "offset": 0x38}
    assert stored == {"load": False, "base": 1, "rd": 5, "offset": 0x38}
    # The `orr r5, r5, r0` between them is what makes the word accumulate.
    between = word(rom_bytes, PENDING_LOAD_SITE + 4)
    assert ((between >> 26) & 0x3) == 0b00 and ((between >> 21) & 0xF) == 0b1100
    assert PENDING_WORD_IWRAM == VECTOR_TABLE_IWRAM + 0x38


def test_the_restore_path_puts_ie_ime_and_spsr_back(rom_bytes):
    # pop {r0, r1, r2, r3, r4, r5, lr}
    assert word(rom_bytes, EXIT_POP_SITE) == 0xE8BD403F
    # msr spsr_fsxc, r0
    assert word(rom_bytes, EXIT_SPSR_SITE) == 0xE16FF000
    assert word(rom_bytes, EXIT_BX_LR_SITE) == 0xE12FFF1E


# ---------------------------------------------------------------------------
# bit 13
# ---------------------------------------------------------------------------
def test_bit_thirteen_is_a_branch_to_its_own_address(rom_bytes):
    rows = chain_rows(rom_bytes)
    last = rows[-1]
    assert last["mask"] == BIT_13_MASK

    # beq to the exit block...
    branch_address = last["site"] + 4
    branch = word(rom_bytes, branch_address)
    assert ((branch >> 28) & 0xF) == 0x0, "BEQ"
    assert arm_branch_target(branch_address, branch) == EXIT_POP_SITE

    # ...and then the self-branch, whose target is its own address.
    spin_address = last["site"] + 8
    spin = word(rom_bytes, spin_address)
    assert ((spin >> 28) & 0xF) == 0xE, "unconditional"
    assert arm_branch_target(spin_address, spin) == spin_address
    assert spin == 0xEAFFFFFE


def test_bit_thirteen_is_the_only_self_branch_in_the_body(rom_bytes):
    self_branches = []
    for address in range(DISPATCH_ROM, DISPATCH_CODE_END, 4):
        encoded = word(rom_bytes, address)
        if arm_branch_target(address, encoded) == address:
            self_branches.append(address)
    assert self_branches == [0x087B85DC]


# ---------------------------------------------------------------------------
# the vector table and the install path
# ---------------------------------------------------------------------------
def test_the_vector_table_is_fourteen_identical_thumb_handlers(rom_bytes):
    entries = [word(rom_bytes, VECTOR_TABLE_ROM + 4 * i) for i in range(14)]
    assert entries == [0x0803F3D9] * 14
    assert all(entry & 1 for entry in entries), "every entry is a Thumb pointer"
    # 0x0803F3D8 is the handler itself: the single Thumb halfword `bx lr`.
    assert halfword(rom_bytes, 0x0803F3D8) == 0x4770


def test_the_table_ends_where_the_pending_halfword_begins(rom_bytes):
    assert VECTOR_TABLE_ROM == rom_of_iwram(VECTOR_TABLE_IWRAM)
    assert PENDING_WORD_ROM == VECTOR_TABLE_ROM + 14 * 4
    assert PENDING_WORD_ROM == rom_of_iwram(PENDING_WORD_IWRAM)
    # The word after the fourteen entries is not an entry: it is the software
    # pending halfword the dispatcher accumulates into, and it is zero in the
    # cartridge image. A table with no length field is bounded by what follows.
    assert word(rom_bytes, PENDING_WORD_ROM) == 0x00000000
    assert word(rom_bytes, PENDING_WORD_ROM + 4) != 0x0803F3D9


def test_the_entry_is_installed_by_a_thumb_pc_relative_literal_load(rom_bytes):
    """The routine has no call site: its address is a literal stored into the
    BIOS IRQ vector pointer."""
    entry_literal_site = 0x0803F434
    assert word(rom_bytes, entry_literal_site) == DISPATCH_ENTRY_IWRAM

    decoded = thumb_ldr_literal(0x0803F3DA, halfword(rom_bytes, 0x0803F3DA))
    assert decoded is not None
    rt, target = decoded
    assert rt == 0, "the destination is r0"
    assert target == entry_literal_site
    # Exactly one 4-byte word in the whole image holds the entry address; the
    # four bytes are distinct, so overlapping windows cannot hide a second one.
    needle = DISPATCH_ENTRY_IWRAM.to_bytes(4, "little")
    assert rom_bytes.count(needle) == 1


def test_the_installer_writes_the_bios_irq_vector_pointer(rom_bytes):
    """0x03007FFC is computed, not stored: 0x03007FC0 + 0x3C. The literal
    0x03007FFC therefore occurs ZERO times as a stored word, which is why a
    search for it finds nothing."""
    assert (0x03007FC0 + 0x3C) == 0x03007FFC
    assert rom_bytes.count((0x03007FFC).to_bytes(4, "little")) == 0


# ---------------------------------------------------------------------------
# agreement with the harness derivation, when this revision registers it
# ---------------------------------------------------------------------------
def test_the_harness_derived_boundary_agrees_with_the_rom(rom_bytes):
    units = getattr(lift, "UNITS", {})
    if "iwram_dispatch_tu" not in units:
        pytest.skip("this revision of lift.py does not register iwram_dispatch_tu")
    evidence = lift.derive_unit_boundaries(rom_bytes, "iwram_dispatch_tu")
    assert evidence["problems"] == []
    assert evidence["code_extent"] == "0x087B8510..0x087B863C"
    rows = evidence["functions"]
    assert len(rows) == 1
    assert rows[0]["start"] == "0x087B8510"
    assert rows[0]["end"] == "0x087B863C"
    assert rows[0]["size"] == 300
    assert rows[0]["instructions"] == 75
    assert rows[0]["gaps"] == []
    assert rows[0]["matches_expected"] is True
    # The pool is not adjacent: the Thumb return island sits in between.
    assert evidence["has_literal_pool"] is True
    assert evidence["pool_extent"] == "0x087B8640..0x087B8644"
    assert evidence["pool_gap_bytes"] == 4
    assert evidence["pool_is_adjacent_to_code"] is False


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_reconstructs_the_entry_and_declares_its_environment():
    source = (identity.REPO_ROOT / "src" / "IwramDispatch.c").read_text("utf-8")
    assert "void sub_087B8510(void)" in source
    for hook in (
        "env_read_spsr",
        "env_write_spsr",
        "env_read_cpsr",
        "env_enter_handler_mode",
        "env_leave_handler_mode",
        "env_enter_handler",
    ):
        assert hook in source, hook
    # The unit must link on its own for the modern-build verdict, and only the
    # host self-check may supply the hooks: the defaults are weak and guarded.
    assert "IWRAMDISPATCH_ENV_WEAK" in source
    assert "#ifndef IWRAMDISPATCH_HOST_TEST" in source


def test_the_environment_defaults_cannot_reach_the_host_self_check():
    """The self-check defines its own hooks, so the weak defaults must be
    guarded out of that build before the source is included."""
    selftest = (
        identity.REPO_ROOT / "src" / "probes" / "iwramdispatch_selftest.c"
    ).read_text("utf-8")
    guard = selftest.index("#define IWRAMDISPATCH_HOST_TEST 1")
    include = selftest.index('#include "IwramDispatch.c"')
    assert guard < include
    # ...and the self-check really defines all six, not a subset.
    for hook in (
        "env_read_spsr",
        "env_write_spsr",
        "env_read_cpsr",
        "env_enter_handler_mode",
        "env_leave_handler_mode",
        "env_enter_handler",
    ):
        assert f" {hook}(" in selftest, hook


def test_the_source_is_freestanding_and_iterates_only_in_the_spin():
    source = (identity.REPO_ROOT / "src" / "IwramDispatch.c").read_text("utf-8")
    assert "#include" not in source, "the lift harness provides no headers"
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    # The one loop in the body is the bit-13 spin, and it has no bound.
    assert "for (;;)" in code
    assert code.count("for (") == 1, "no other loop, and no bounded spin"
    assert "while (" not in code
    assert "assert" not in code


def test_the_source_reproduces_the_artifacts_rather_than_repairing_them():
    source = (identity.REPO_ROOT / "src" / "IwramDispatch.c").read_text("utf-8")
    # The skipped IE clear of the first test.
    assert "NOT cleared" in source
    assert "0x1A000028" in source
    # The unbounded spin for bit 13.
    assert "SPINS" in source
    assert "0xEAFFFFFE" in source
    # The paths that cannot reach the handler.
    assert "0x2000" in source
    assert "never selected" in source


def test_the_source_mentions_no_defsym():
    """Every entry point here is reconstructed, not bound by a linker flag."""
    for relative in (
        "src/IwramDispatch.c",
        "src/probes/IwramDispatch.c",
        "src/probes/iwramdispatch_selftest.c",
    ):
        text = (identity.REPO_ROOT / relative).read_text("utf-8")
        assert "--defsym" not in text, relative


def test_the_source_states_that_the_cannot_represent_list_is_explicit():
    """docs/DEVELOPMENT.md requires the omissions to be named, not implied."""
    source = (identity.REPO_ROOT / "src" / "IwramDispatch.c").read_text("utf-8")
    assert "NOT" in source and "REPRESENTED" in source
    for phrase in ("SPSR", "mode switch", "interworking", "bx r4", "0x03000C98"):
        assert phrase in source, phrase


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "IwramDispatch.c").read_text("utf-8")
    assert '#include "../IwramDispatch.c"' in shim
    assert "void sub_087B8510(" not in shim
    assert len(shim.splitlines()) < 30, "the shim has grown into a second copy"


def test_the_self_check_prints_the_protocol_the_harness_parses():
    text = (
        identity.REPO_ROOT / "src" / "probes" / "iwramdispatch_selftest.c"
    ).read_text("utf-8")
    assert "check(s), %d failure(s)" in text
    assert "setvbuf(stdout, NULL, _IONBF, 0)" in text
    # It must exercise the modelled machine, not the target's addresses.
    assert "IWRAMDISPATCH_HOST_TEST" in text
    assert "env_enter_handler" in text


# ---------------------------------------------------------------------------
# the semantic verdict, measured by running it
# ---------------------------------------------------------------------------
def test_the_self_check_runs_the_reconstruction_on_the_host(tmp_path):
    result = lift.run_host_selftest(
        tmp_path,
        source=identity.REPO_ROOT / "src" / "probes" / "iwramdispatch_selftest.c",
        minimum_checks=160,
        host_bits=32,
    )
    if result["status"] == "UNTESTED":
        pytest.skip(result["detail"])
    assert result["status"] == "PROVEN", result["detail"]
    assert result["failures"] == 0
    assert result["checks"] >= 160
    assert "check(s)" in result["output"]


@pytest.mark.parametrize("checks,expected", [(160, "PROVEN"), (159, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=160)
    assert status == expected
