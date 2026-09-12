"""ROM-gated proofs for the TOOLKIT-038 shop scenario / script model.

These lock the structural facts `docs/research/BUU_SHOP_SCENARIO_MODEL.md`
records as CONFIRMED_ROM, so a later pass cannot quietly contradict them:

* the six shop scenarios are entries of the already-proven 522-entry event
  pointer table, which resolves the overlap ROM-ATLAS-001 flagged between the
  shop region and `event_resource.record_pool`;
* every script begins `u16 next_script_index; u8 type`, with `next` in range and
  the last slot's `next` equal to the scenario's entry count;
* only four type values occur across the 61 targets;
* the type-0x05 descriptor's count cross-checks its array;
* all 61 scripts satisfy TOOLKIT-036's unique-ownership relocation gate;
* the dispatcher at 0x08004098 reads the type byte at +2 and accepts only types
  0 and 4, which is why it cannot be the consumer of a plaintext body.

They skip cleanly when the canonical ROM is absent, so the portable suite stays
runnable without proprietary data. The ROM is opened read-only and no
ROM-derived fixture is committed.
"""

from __future__ import annotations

import glob
import hashlib
import os
import struct

import pytest

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

BASE = 0x08000000

#: TOOLKIT-019's verified event resource, repeated rather than imported so this
#: test fails if the measured constants drift.
EVENT_TABLE = 0x0879B704
EVENT_COUNT = 522

#: TOOLKIT-038's measured scenarios: (array address, entry count, event index).
SCENARIOS = (
    (0x0877F3B0, 10, 28),
    (0x0877F73C, 10, 30),
    (0x0877FAB8, 11, 31),
    (0x0877FE00, 10, 33),
    (0x08780008, 8, 34),
    (0x087803E4, 12, 36),
)

TARGET_TOTAL = 61

#: The only type values observed across the 61 targets, with their counts.
TYPE_CENSUS = {0x00: 18, 0x03: 17, 0x04: 20, 0x05: 6}

SCENARIO_DESCRIPTOR_TYPE = 0x05
PLAINTEXT_TYPE = 0x03

#: The constant word every type-0x05 descriptor carries at +4. Its role is
#: UNKNOWN; the test pins the value, not a meaning.
DESCRIPTOR_CONSTANT = 0x02CE74C0

#: dialog.entry_point and its type dispatch, seeded CONFIRMED from
#: BUU_EVENT_RESOURCE.md and re-measured by TOOLKIT-038.
DISPATCHER = 0x08004098
TYPE_READ_SITE = 0x080040BA
INTERPRETER = 0x08004038

#: The shop object records and the field holding their scenario pointer.
SHOP_RECORDS = (0x08074360, 0x080743C4, 0x08074450, 0x080744B4, 0x0807451C)
RECORD_SCENARIO_FIELD = 0x0C

#: A Data Crystal breakpoint inside the confirmed packed-text consumer. It is
#: not itself a message-display instruction; r1 already holds the packed handle.
DC_MESSAGE_SITE = 0x0801226A
DC_RAM_SLOT = 0x0202BA70


def _rom_bytes() -> bytes:
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    data = open(matches[0], "rb").read()
    if hashlib.sha256(data).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return data


@pytest.fixture(scope="module")
def rom() -> bytes:
    return _rom_bytes()


def _u32(data: bytes, addr: int) -> int:
    return struct.unpack_from("<I", data, addr - BASE)[0]


def _u16(data: bytes, addr: int) -> int:
    return struct.unpack_from("<H", data, addr - BASE)[0]


def _u8(data: bytes, addr: int) -> int:
    return data[addr - BASE]


def _targets(data: bytes) -> list[int]:
    out = []
    for array, count, _ in SCENARIOS:
        for slot in range(count):
            out.append(_u32(data, array + slot * 4))
    return out


def test_scenarios_are_event_table_entries(rom):
    """The shop region is event-record payload, not a separate store.

    ROM-ATLAS-001 flagged the overlap and left it unresolved. Each scenario
    array being an event-table entry is what resolves it.
    """
    table = [_u32(rom, EVENT_TABLE + i * 4) for i in range(EVENT_COUNT)]
    for array, _, event_index in SCENARIOS:
        assert table[event_index] == array, (
            f"event {event_index} should address scenario {array:#010x}"
        )


def test_script_targets_are_not_themselves_event_entries(rom):
    """The 61 scripts are reachable only through their scenario.

    If any were separately addressable the ownership argument below would not
    hold, so this is a precondition rather than a detail.
    """
    table = {_u32(rom, EVENT_TABLE + i * 4) for i in range(EVENT_COUNT)}
    targets = _targets(rom)
    assert len(targets) == TARGET_TOTAL
    assert not (set(targets) & table)


def test_type_census_across_all_targets(rom):
    """Every observed type value, not only the ones external evidence predicted."""
    census: dict[int, int] = {}
    for target in _targets(rom):
        ty = _u8(rom, target + 2)
        census[ty] = census.get(ty, 0) + 1
    assert census == TYPE_CENSUS


def test_next_script_index_is_in_range(rom):
    """`next` never leaves the scenario, and the last slot encodes the count.

    Both conventions hold for all six scenarios, which is what makes the
    community model's framing claim structurally supported rather than a
    coincidence of small numbers.
    """
    for array, count, _ in SCENARIOS:
        nexts = [_u16(rom, _u32(rom, array + s * 4)) for s in range(count)]
        assert all(0 <= n <= count for n in nexts), (array, nexts)
        assert nexts[-1] == count, (array, nexts)
        # Exactly two terminal scripts per scenario, measured.
        assert nexts.count(0) == 2, (array, nexts)


def test_scenario_descriptor_cross_checks_its_array(rom):
    """The last slot points at an 8-byte type-0x05 record describing the array."""
    for array, count, _ in SCENARIOS:
        descriptor = _u32(rom, array + (count - 1) * 4)
        assert descriptor == array - 8
        assert _u16(rom, descriptor) == count
        assert _u8(rom, descriptor + 2) == SCENARIO_DESCRIPTOR_TYPE
        assert _u8(rom, descriptor + 3) == 0
        assert _u32(rom, descriptor + 4) == DESCRIPTOR_CONSTANT


def test_every_script_is_uniquely_owned_by_its_slot(rom):
    """TOOLKIT-036's relocation gate, evaluated against the shop scripts.

    The gate is exactly one word-aligned inbound reference, and that reference
    being the entry's own table slot. TOOLKIT-037 named this measurement as
    blocked; it is the reason the shop region was labelled UNOWNED.
    """
    slots: dict[int, list[int]] = {}
    for array, count, _ in SCENARIOS:
        for s in range(count):
            slots.setdefault(_u32(rom, array + s * 4), []).append(array + s * 4)

    inbound: dict[int, list[int]] = {t: [] for t in slots}
    for offset in range(0, len(rom) - 3, 4):
        value = struct.unpack_from("<I", rom, offset)[0]
        if value in inbound:
            inbound[value].append(offset + BASE)

    for target, owning in slots.items():
        assert inbound[target] == owning, (
            f"{target:#010x} has inbound {[hex(x) for x in inbound[target]]}, "
            f"expected only its own slot(s) {[hex(x) for x in owning]}"
        )


def test_dispatcher_reads_the_type_byte_at_plus_two(rom):
    """`ldrb r1,[r0,#2]` at 0x080040BA is the same byte the census measures.

    Encoding: LDRB Rd,[Rn,#imm5] is 0111 1 imm5 Rn Rd, so imm5 must be 2.
    """
    encoded = _u16(rom, TYPE_READ_SITE)
    assert encoded & 0xF800 == 0x7800, f"not an LDRB immediate: {encoded:#06x}"
    assert (encoded >> 6) & 0x1F == 2, "dispatcher must read offset +2"


def test_dispatcher_accepts_only_types_zero_and_four(rom):
    """Why 0x08004098 cannot be the plaintext consumer.

    It compares against 0 and 4 and asserts otherwise, so a type-0x03 body
    routed here would fail. That is this ticket's stopping point, so it is
    pinned rather than left as prose.
    """
    # cmp r1,#0 ; beq ; cmp r1,#4 ; bne  -- CMP Rn,#imm8 is 0010 1 Rn imm8
    cmp_zero = _u16(rom, 0x080040BC)
    cmp_four = _u16(rom, 0x080040C0)
    assert cmp_zero & 0xF800 == 0x2800
    assert cmp_zero & 0xFF == 0
    assert cmp_four & 0xF800 == 0x2800
    assert cmp_four & 0xFF == 4

    # At least one plaintext script exists, so the mismatch is real and not
    # vacuous.
    types = {_u8(rom, t + 2) for t in _targets(rom)}
    assert PLAINTEXT_TYPE in types


def test_shop_records_carry_a_scenario_pointer(rom):
    """Data Crystal's "NPC structure has a dialogue pointer", in stronger form.

    The pointer is to a scenario, not to a string, and the records' other
    leading fields are identical across all five instances.
    """
    scenario_addresses = {array for array, _, _ in SCENARIOS}
    seen = []
    for record in SHOP_RECORDS:
        scenario = _u32(rom, record + RECORD_SCENARIO_FIELD)
        assert scenario in scenario_addresses, f"{record:#010x} -> {scenario:#010x}"
        seen.append(scenario)
    assert len(set(seen)) == len(SHOP_RECORDS)

    for field in (0x00, 0x04, 0x08, 0x10, 0x14, 0x18, 0x1C):
        values = {_u32(rom, r + field) for r in SHOP_RECORDS}
        assert len(values) == 1, f"field +{field:#04x} varies: {values}"


def test_data_crystal_message_site_is_packed_handle_breakpoint_not_direct_display(rom):
    """0x0801226A is `movs r0,#0`, following the packed-handle load into r1.

    This proves the address is not itself a message-display instruction. The
    preceding `ldr r1,[r5,#4]` explains its useful diagnostic value without
    promoting the external recipe to a handler or producer claim.
    """
    handle_load = _u16(rom, DC_MESSAGE_SITE - 2)
    assert handle_load & 0xF800 == 0x6800, f"expected LDR immediate: {handle_load:#06x}"
    assert (handle_load >> 6) & 0x1F == 1, "r1 load must use byte offset +4"
    assert (handle_load >> 3) & 0x7 == 5, "r1 must be loaded from r5"
    assert handle_load & 0x7 == 1, "packed handle must arrive in r1"
    encoded = _u16(rom, DC_MESSAGE_SITE)
    assert encoded & 0xF800 == 0x2000, f"expected MOVS immediate: {encoded:#06x}"
    assert encoded & 0xFF == 0


def test_data_crystal_ram_slot_has_no_static_reference(rom):
    """0x0202BA70 cannot be settled statically, so no claim is made about it.

    Zero word-aligned references means computed addressing only. This test
    guards the *absence* that justifies leaving the lead NOT ESTABLISHED.
    """
    for candidate in (DC_RAM_SLOT - 8, DC_RAM_SLOT - 4, DC_RAM_SLOT,
                      DC_RAM_SLOT + 4, DC_RAM_SLOT + 8):
        hits = [
            offset
            for offset in range(0, len(rom) - 3, 4)
            if struct.unpack_from("<I", rom, offset)[0] == candidate
        ]
        assert hits == [], f"{candidate:#010x} unexpectedly referenced at {hits}"
