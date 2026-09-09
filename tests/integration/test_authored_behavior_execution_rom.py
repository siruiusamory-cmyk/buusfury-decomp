"""TOOLKIT-031: does the behavior ATTACHED to an authored placement execute?

TOOLKIT-030 proved the engine consumes a placement body carrying the authored
descriptor, and deliberately claimed nothing about execution: the effect channel
it built turned out to be non-discriminating, and a broken instrument is not
evidence in either direction.

This module pins the STATIC half of TOOLKIT-031 -- the call-site census that
made the runtime experiment designable -- against the canonical image. The
runtime half cannot be re-run from a test (it needs an emulator and a human),
so what is pinned here is every measurement the runtime design depends on. If
one of these drifts, the runtime conclusion stops following and must be re-taken.

Evidence: docs/research/AUTHORED_BEHAVIOR_EXECUTION.md
"""
from pathlib import Path
import hashlib
import struct

import pytest

SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
ROM_BASE = 0x08000000
CODE_END = 0x00200000

#: The three behavior handlers a placement's `+0x14` descriptor can name
#: (TOOLKIT-016). Only the middle one runs a script.
HANDLER_NULL = 0x0800421D       # bx lr
HANDLER_SCRIPT = 0x0800421F     # ldr r1,[r0,#4] ; bl 0x08004038
HANDLER_OTHER = 0x0800424F

#: Entry addresses (the handlers above are Thumb pointers, so entry is even).
TRAMPOLINE = 0x0800421E
INTERPRETER = 0x08004038

#: The authored attachment under test, and the null descriptor it replaced.
AUTHORED_DESCRIPTOR = 0x0808D788
AUTHORED_PAYLOAD = 0x0808D77C
NULL_DESCRIPTOR = 0x080555A0

#: The canonical owner of the authored descriptor, used as the control target.
CONTROL_MAP = 428
CONTROL_RECORD = 0x0808D790

FACTORY = 0x0800FD55
MAP_TABLE = 0x0808E2E0
MAP_COUNT = 452
MAP_STRIDE = 0x38


@pytest.fixture(scope="module")
def data():
    rom = sorted(Path("roms").glob("*Buu*.gba"))
    if not rom:
        pytest.skip("canonical Buu ROM not present")
    blob = rom[0].read_bytes()
    if hashlib.sha256(blob).hexdigest() != SHA:
        pytest.skip("ROM is not the canonical image")
    return blob


def word(data, addr):
    return struct.unpack_from("<I", data, addr - ROM_BASE)[0]


def bl_targets(data):
    """Every Thumb BL target in the code region.

    Decoded from the halfword pair directly rather than from a linear
    disassembly. A linear sweep from offset 0 desynchronises on the ROM header
    and silently reports nothing, which is exactly the failure that made two
    early censuses in this ticket come back empty.
    """
    out = {}
    for off in range(0, CODE_END, 2):
        hi = struct.unpack_from("<H", data, off)[0]
        if not 0xF000 <= hi <= 0xF7FF:
            continue
        lo = struct.unpack_from("<H", data, off + 2)[0]
        if not 0xF800 <= lo <= 0xFFFF:
            continue
        disp = ((hi & 0x7FF) << 12) | ((lo & 0x7FF) << 1)
        if disp & (1 << 22):
            disp -= 1 << 23
        out.setdefault((ROM_BASE + off) + 4 + disp, []).append(ROM_BASE + off)
    return out


def test_descriptor_still_names_the_script_handler_and_root(data):
    """The whole experiment is addressed at this one descriptor."""
    assert word(data, AUTHORED_DESCRIPTOR) == HANDLER_SCRIPT
    assert word(data, AUTHORED_DESCRIPTOR + 4) == AUTHORED_PAYLOAD
    # And the control descriptor is still the do-nothing one.
    assert word(data, NULL_DESCRIPTOR) == HANDLER_NULL


def test_handlers_have_no_direct_callers(data):
    """The census question had to be restated because of this.

    No code calls the trampoline directly; it is reached only through a
    descriptor's `+0x00` word. So "who calls 0x0800421E" has no static answer,
    and the runtime observer must watch the address itself rather than trying to
    breakpoint a caller.
    """
    targets = bl_targets(data)
    for handler_entry in (0x0800421C, TRAMPOLINE, 0x0800424E):
        assert targets.get(handler_entry, []) == []


def test_trampoline_reads_the_descriptor_payload_and_enters_the_interpreter(data):
    """The observer records r0 and [r0+4] because of this exact shape.

    0800421E  push {lr}
    08004220  ldr  r1,[r0,#4]     <- r0 is the descriptor, r1 its script root
    0800422E  bl   0x08004038     <- the interpreter
    """
    assert struct.unpack_from("<H", data, TRAMPOLINE - ROM_BASE)[0] == 0xB500
    # ldr r1,[r0,#4] -> 0110 1 imm5=1 rn=0 rd=1
    assert struct.unpack_from("<H", data, 0x08004220 - ROM_BASE)[0] == 0x6841
    assert INTERPRETER in bl_targets(data)
    assert 0x0800422E in bl_targets(data)[INTERPRETER]


def test_constructor_stores_the_descriptor_instead_of_calling_it(data):
    """This is what refuted map construction as the trigger.

    0800F6E2  movs r3,#1
    0800F6E4  lsls r3,r3,#9       ; r3 = 0x200
    0800F6EA  adds r7,r4,r3       ; r7 = actor + 0x200
    0800F6F0  ldr  r3,[r5,#0x14]  ; the placement's descriptor
    0800F6F4  str  r3,[r7,#0x28]  ; -> actor + 0x228
    """
    assert struct.unpack_from("<H", data, 0x0800F6E2 - ROM_BASE)[0] == 0x2301
    assert struct.unpack_from("<H", data, 0x0800F6E4 - ROM_BASE)[0] == 0x025B
    # ldr r3,[r5,#0x14] -> imm5 = 5, rn = 5, rd = 3
    assert struct.unpack_from("<H", data, 0x0800F6F0 - ROM_BASE)[0] == 0x696B
    # str r3,[r7,#0x28] -> imm5 = 10, rn = 7, rd = 3
    assert struct.unpack_from("<H", data, 0x0800F6F4 - ROM_BASE)[0] == 0x62BB


def test_control_map_owns_the_authored_descriptor(data):
    """The positive control's target: map 428 slot 0 is the CANONICAL owner of
    the very descriptor TOOLKIT-030 attached, which is what makes it the right
    control rather than merely a similar one."""
    entry = MAP_TABLE + CONTROL_MAP * MAP_STRIDE
    count = word(data, entry + 0x04)
    array = word(data, entry + 0x14)
    assert count >= 1
    record = word(data, array)
    assert record == CONTROL_RECORD
    assert word(data, record) == FACTORY
    assert word(data, record + 0x14) == AUTHORED_DESCRIPTOR


def test_script_bearing_placements_are_absent_from_the_savestate_zone(data):
    """Why the control had to be built rather than walked to.

    The available savestate starts on map 40, whose zone byte is 1. No map in
    zone 1 carries a script-bearing placement, so the trampoline can never fire
    there however long it is watched -- which is why an idle run on map 40
    produced zero hits and why that zero was not evidence of anything.
    """
    script_maps = set()
    for index in range(MAP_COUNT):
        entry = MAP_TABLE + index * MAP_STRIDE
        count = word(data, entry + 0x04)
        array = word(data, entry + 0x14)
        if not 0 < count <= 64 or not ROM_BASE <= array < 0x08800000:
            continue
        for slot in range(count):
            record = word(data, array + slot * 4)
            if not ROM_BASE <= record < 0x08800000 or word(data, record) != FACTORY:
                continue
            descriptor = word(data, record + 0x14)
            if ROM_BASE <= descriptor < 0x08800000 and word(data, descriptor) == HANDLER_SCRIPT:
                script_maps.add(index)

    assert CONTROL_MAP in script_maps
    zone_of_40 = data[(MAP_TABLE + 40 * MAP_STRIDE) - ROM_BASE]
    for index in script_maps:
        assert data[(MAP_TABLE + index * MAP_STRIDE) - ROM_BASE] != zone_of_40
