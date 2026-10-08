"""Build the DIALOGUE-RENDER-PATH-001 two-glyph diagnostic image.

WHAT IT IS FOR. The previous proof changed the glyph identity of one source unit
and showed the ordinary dialogue text change. This one makes one stored source
unit emit TWO different ordinary glyphs through the real strip compositor, which
is the structural question the future expansion-token work depends on.

THE CODE IT PATCHES. The reveal step reached through 0x0800AE74 and 0x0800AF7A
composes one ordinary character per invocation:

    0x0800B05C  ldrb r0,[r6,#0x4]      x = the text object's cursor x   (r6 = obj+0x60)
    0x0800B05E  ldrb r1,[r6,#0x5]      y = the text object's cursor y
    0x0800B060  str  r0,[r5,#0x4]      compose descriptor x := x        (r5 = obj+0x80)
    0x0800B062  str  r1,[r5,#0x8]      compose descriptor y := y
    0x0800B064  ldr  r0,[r4,#0x14]     r0 = the source cursor            (r4 = obj)
    0x0800B066  ldrh r1,[r0,#0x0]      r1 = THE SOURCE UNIT
    0x0800B068  add  r0,r5,#0x0        r0 = strip
    0x0800B06A  bl   0x0803DE50        compose_glyph(strip, unit)
    0x0800B06E  ldr  r2,[r4,#0x14]     r2 = the source cursor
    0x0800B070  ldrh r0,[r2,#0x0]      r0 = the same unit
    0x0800B072  ldr  r1,[r5,#0xc]      r1 = the font holder
    0x0800B074  cmp  r0,#0xff
    0x0800B076  bcc  0x0800b07e
    ...
    0x0800B07E  ldr  r1,[r1,#0x0]      font base
    0x0800B082  ldrh r0,[r1,r0]        glyph record index
    0x0800B086  ldrh r0,[r1,r0]        advance width
    0x0800B088  add  r0,#0x1
    0x0800B08A  ldrb r1,[r6,#0x4]      the OLD persistent x
    0x0800B08C  add  r0,r0,r1
    0x0800B08E  strb r0,[r6,#0x4]      persistent x := x + width + 1
    0x0800B090  add  r2,#0x2
    0x0800B092  str  r2,[r4,#0x14]     source cursor += 2, ONE unit consumed

THE EDIT. The two halfwords at 0x0800B066 become a Thumb BL to a cave, and the
two displaced halfwords move into the cave. The cave is:

    unit := source_unit
    if unit != TEST_UNIT:
        the original path, exactly: compose the unit, rejoin at 0x0800B06E
    else:
        compose GLYPH_A at x                      (strip+4 already holds x)
        x2 := x + width(GLYPH_A) + 1              (advance, persisted to strip+4 and obj+0x64)
        compose GLYPH_B at x2
        x_final := x2 + width(GLYPH_B) + 1        (persisted)
        source cursor += 2, ONE unit consumed
        rejoin at 0x0800B094, past the ordinary advance and consume

So the gated event composes twice and consumes once, and the persistent cursor
ends at exactly old_x + width(A) + 1 + width(B) + 1. The glyphs are ordinary
font glyphs from the same table the ordinary path reads.

Chosen by rendering the font, see tools/research/dialogue_font_probe.py:
    GLYPH_A = 0x41 'A', width 9
    GLYPH_B = 0x21 '!', width  2
    TEST_UNIT = 0x4B, width 10, occurs twice in the 3000-frame control run

Every patched site is asserted from the ROM bytes before and after the write, and
every branch is encoded and then DECODED back and compared with its intended
target, because an earlier session shipped a cave whose displaced instruction was
encoded wrong and only an assert caught it.

Nothing here writes to the canonical image.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
ROM_BASE = 0x08000000

HOOK = 0x0800B066
HOOK_CANONICAL = bytes([0x01, 0x88, 0x28, 0x1C])  # ldrh r1,[r0,#0] ; add r0,r5,#0
REJOIN_NORMAL = 0x0800B06E
REJOIN_EXPAND = 0x0800B094

CAVE = 0x082ED210
CAVE_RESERVED = 128

FUN_COMPOSE = 0x0803DE50
GLYPH_A = 0x41
GLYPH_B = 0x21
TEST_UNIT = 0x4B


def bl_encode(at: int, target: int) -> tuple[int, int]:
    """Encode a Thumb BL the way ARM7TDMI decodes it.

    ARM7TDMI is ARMv4T, which has no Thumb-2. Its Thumb BL is the 23-bit form:
    `11110 imm11` followed by `11111 imm11`, so the second halfword's bits 15..11
    are all ones. That is exactly the special case J1 = J2 = 1 of the Thumb-2
    25-bit encoding, which means the two forms agree only while the displacement
    fits in 23 signed bits.

    A 25-bit encoding whose J1 or J2 is clear is NOT a BL on this CPU: the second
    halfword decodes as another `11110` prefix and the pair is an undefined
    instruction. That is a silent failure with a spectacular symptom - the game
    takes an undefined-instruction exception and ends up back at its boot
    sequence - and it cost this ticket two runs. So the range is enforced here
    rather than discovered at run time, and reaching further needs a trampoline
    (`bl` to a nearby `ldr pc,[pc,#imm]` slot), not a wider branch.
    """
    offset = target - (at + 4)
    if offset % 2:
        raise ValueError(f"unaligned Thumb BL offset {offset:#x}")
    if not -(1 << 22) <= offset < (1 << 22):
        raise ValueError(
            f"Thumb BL displacement {offset:#x} is outside the ARMv4T 23-bit "
            f"range; a trampoline is required"
        )
    value = offset & 0x01FFFFFF
    sign = (value >> 24) & 1
    i1 = (value >> 23) & 1
    i2 = (value >> 22) & 1
    imm10 = (value >> 12) & 0x3FF
    imm11 = (value >> 1) & 0x7FF
    j1 = 1 - (i1 ^ sign)
    j2 = 1 - (i2 ^ sign)
    if (j1, j2) != (1, 1):
        raise ValueError(
            f"Thumb BL displacement {offset:#x} needs J1={j1} J2={j2}, which "
            f"ARM7TDMI cannot decode"
        )
    return 0xF000 | (sign << 10) | imm10, 0xD000 | (j1 << 13) | (j2 << 11) | imm11


def bl_decode(at: int, high: int, low: int) -> int:
    sign = (high >> 10) & 1
    imm10 = high & 0x3FF
    j1 = (low >> 13) & 1
    j2 = (low >> 11) & 1
    i1 = 1 - (j1 ^ sign)
    i2 = 1 - (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | ((low & 0x7FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return at + 4 + immediate


def beq_encode(at: int, target: int) -> int:
    offset = target - (at + 4)
    if offset % 2 or not 0 <= offset // 2 <= 0xFF:
        raise ValueError(f"conditional branch out of range: {offset}")
    return 0xD000 | (offset // 2)


def beq_decode(at: int, halfword: int) -> int:
    return at + 4 + ((halfword & 0xFF) * 2)


def word_at(words: list[int], address: int) -> tuple[int, int]:
    index = (address - CAVE) // 2
    return words[index], words[index + 1]


def assemble(gate: bool = True) -> tuple[bytes, dict[str, int]]:
    """Emit the cave and return its bytes plus the addresses the tests assert.

    ``gate=False`` emits a pure pass-through: the two displaced halfwords, the
    ordinary composition and the rejoin, with no test of the source unit. It
    exists to separate "the hook and rejoin mechanism is wrong" from "the gated
    expansion is wrong", which two identical failing runs could not.
    """
    words: list[int] = []

    def emit(halfword: int) -> int:
        words.append(halfword & 0xFFFF)
        return CAVE + (len(words) - 1) * 2

    def here() -> int:
        return CAVE + len(words) * 2

    if not gate:
        emit(0x8801)                    # ldrh r1,[r0,#0x0]   (displaced)
        emit(0x1C28)                    # add  r0,r5,#0x0     (displaced)
        normal = here()
        emit(0)
        emit(0)
        literal = here()
        emit(0)                         # ldr  r3,[pc,#imm]
        emit(0x4718)
        literal_normal = here()
        emit((REJOIN_NORMAL | 1) & 0xFFFF)
        emit((REJOIN_NORMAL | 1) >> 16)
        high, low = bl_encode(normal, FUN_COMPOSE)
        words[(normal - CAVE) // 2] = high
        words[(normal - CAVE) // 2 + 1] = low
        if bl_decode(normal, *word_at(words, normal)) != FUN_COMPOSE:
            raise SystemExit("pass-through compose call decodes wrong")
        base = (literal + 4) & ~3
        delta = literal_normal - base
        words[(literal - CAVE) // 2] = 0x4B00 | (delta // 4)
        if base + ((words[(literal - CAVE) // 2] & 0xFF) * 4) != literal_normal:
            raise SystemExit("pass-through rejoin literal decodes wrong")
        payload = bytearray()
        for halfword in words:
            payload += halfword.to_bytes(2, "little")
        return bytes(payload), {
            "expand": 0,
            "advance": 0,
            "normal_rejoin": literal_normal,
            "expand_rejoin": 0,
            "bytes": len(payload),
        }

    # The dispatcher. 0x0800B066 is the hook, so the two displaced halfwords come
    # first, then the gate, then either the original path or the expansion.
    emit(0x8801)                        # ldrh r1,[r0,#0x0]   (displaced)
    emit(0x2200 | TEST_UNIT)            # movs r2,#TEST_UNIT
    emit(0x4291)                        # cmp  r1,r2
    expand_branch = emit(0xD000 | 4)    # beq  expand          (patched below)
    emit(0x1C28)                        # add  r0,r5,#0x0     (displaced)
    normal_call = here()
    emit(0)                             # bl   FUN_COMPOSE
    emit(0)
    rejoin_literal = here()
    emit(0)                             # ldr  r3,[pc,#imm]   -> literal 0x0800B06F
    emit(0x4718)                        # bx   r3

    # The expansion path.
    emit(0xB480)                        # push {r7}
    emit(0x4607)                        # mov  r7,r0          r7 = source cursor
    emit(0x2100 | GLYPH_A)              # movs r1,#GLYPH_A
    emit(0x4628)                        # mov  r0,r5
    first_call = here()
    emit(0)
    emit(0)
    emit(0x2000 | GLYPH_A)              # movs r0,#GLYPH_A   the advance reads r0
    first_advance = here()
    emit(0)
    emit(0)
    emit(0x2100 | GLYPH_B)              # movs r1,#GLYPH_B
    emit(0x4628)                        # mov  r0,r5
    second_call = here()
    emit(0)
    emit(0)
    emit(0x2000 | GLYPH_B)              # movs r0,#GLYPH_B
    second_advance = here()
    emit(0)
    emit(0)
    emit(0x3702)                        # adds r7,#0x2
    emit(0x6167)                        # str  r7,[r4,#0x14]  consume exactly one unit
    emit(0xBC80)                        # pop  {r7}
    expand_literal = here()
    emit(0)                             # ldr  r3,[pc,#imm]   -> literal 0x0800B095
    emit(0x4718)                        # bx   r3

    # The advance helper: r0 = glyph code in, r0 = x + width + 1 out, and the
    # persistent cursor is stored. It clobbers r0, r1 and r2 only.
    advance = here()
    emit(0x68E9)                        # ldr  r1,[r5,#0xC]
    emit(0x6809)                        # ldr  r1,[r1,#0x0]  font base
    emit(0x0040)                        # lsls r0,r0,#1
    emit(0x5A08)                        # ldrh r0,[r1,r0]    glyph record index
    emit(0x0040)                        # lsls r0,r0,#1
    emit(0x5A08)                        # ldrh r0,[r1,r0]    advance width
    emit(0x3001)                        # adds r0,#0x1
    emit(0x7932)                        # ldrb r2,[r6,#0x4]  the old persistent x
    emit(0x1880)                        # add  r0,r0,r2
    emit(0x7130)                        # strb r0,[r6,#0x4]
    emit(0x6068)                        # str  r0,[r5,#0x4]  the compose cursor copy
    emit(0x4770)                        # bx   lr

    literal_normal = here()
    emit((REJOIN_NORMAL | 1) & 0xFFFF)
    emit((REJOIN_NORMAL | 1) >> 16)
    literal_expand = here()
    emit((REJOIN_EXPAND | 1) & 0xFFFF)
    emit((REJOIN_EXPAND | 1) >> 16)

    # Fix the branches, then decode each one back and check it.
    high, low = bl_encode(normal_call, FUN_COMPOSE)
    words[(normal_call - CAVE) // 2] = high
    words[(normal_call - CAVE) // 2 + 1] = low
    for site in (first_call, second_call):
        high, low = bl_encode(site, FUN_COMPOSE)
        words[(site - CAVE) // 2] = high
        words[(site - CAVE) // 2 + 1] = low
    for site in (first_advance, second_advance):
        high, low = bl_encode(site, advance)
        words[(site - CAVE) // 2] = high
        words[(site - CAVE) // 2 + 1] = low

    def word_at_site(address: int) -> tuple[int, int]:
        index = (address - CAVE) // 2
        return words[index], words[index + 1]

    checks = {
        "normal call": (normal_call, bl_decode(normal_call, *word_at_site(normal_call)), FUN_COMPOSE),
        "first call": (first_call, bl_decode(first_call, *word_at_site(first_call)), FUN_COMPOSE),
        "second call": (second_call, bl_decode(second_call, *word_at_site(second_call)), FUN_COMPOSE),
        "first advance": (first_advance, bl_decode(first_advance, *word_at_site(first_advance)), advance),
        "second advance": (second_advance, bl_decode(second_advance, *word_at_site(second_advance)), advance),
    }
    for name, (site, decoded, intended) in checks.items():
        if decoded != intended:
            raise SystemExit(
                f"{name} at {site:#010x} decodes to {decoded:#010x}, intended {intended:#010x}"
            )

    expand_index = (expand_branch - CAVE) // 2
    words[expand_index] = beq_encode(expand_branch, CAVE + 0x12)
    expand_target = beq_decode(expand_branch, words[expand_index])
    if expand_target != CAVE + 0x12:
        raise SystemExit(
            f"expand branch at {expand_branch:#010x} encodes {words[expand_index]:#06x} "
            f"and decodes to {expand_target:#010x}"
        )
    for name, site, literal in (
        ("normal rejoin", rejoin_literal, literal_normal),
        ("expand rejoin", expand_literal, literal_expand),
    ):
        # ldr r3,[pc,#imm8]: the base is the aligned address of PC, which is the
        # instruction plus four.
        base = (site + 4) & ~3
        delta = literal - base
        if delta % 4 or not 0 <= delta // 4 <= 0xFF:
            raise SystemExit(f"{name} literal is not reachable from {site:#010x}")
        words[(site - CAVE) // 2] = 0x4B00 | (delta // 4)
        decoded = base + ((words[(site - CAVE) // 2] & 0xFF) * 4)
        if decoded != literal:
            raise SystemExit(f"{name} literal decodes to {decoded:#010x}")

    payload = bytearray()
    for halfword in words:
        payload += halfword.to_bytes(2, "little")
    if len(payload) > CAVE_RESERVED:
        raise SystemExit(f"cave is {len(payload)} bytes, over the {CAVE_RESERVED} reserved")
    return bytes(payload), {
        "expand": CAVE + 0x12,
        "advance": advance,
        "normal_rejoin": literal_normal,
        "expand_rejoin": literal_expand,
        "bytes": len(payload),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(
    source: Path, destination: Path, *, patch_hook: bool = True, gate: bool = True
) -> tuple[str, dict[str, int]]:
    if sha256(source) != CANONICAL_SHA256:
        raise SystemExit("source is not the canonical image")
    original = source.read_bytes()
    image = bytearray(original)

    hook_offset = HOOK - ROM_BASE
    if bytes(image[hook_offset : hook_offset + 4]) != HOOK_CANONICAL:
        raise SystemExit(
            f"hook site is not the expected instructions: "
            f"{bytes(image[hook_offset:hook_offset + 4]).hex()}"
        )
    cave_offset = CAVE - ROM_BASE
    fill = set(image[cave_offset : cave_offset + CAVE_RESERVED])
    if len(fill) != 1 or fill.pop() not in (0x00, 0xFF):
        raise SystemExit("cave region is not a uniform 0x00 or 0xFF filler run")

    payload, labels = assemble(gate)
    high, low = bl_encode(HOOK, CAVE)
    if bl_decode(HOOK, high, low) != CAVE:
        raise SystemExit("hook branch does not decode back to the cave")
    if patch_hook:
        image[hook_offset : hook_offset + 4] = (
            high.to_bytes(2, "little") + low.to_bytes(2, "little")
        )
    image[cave_offset : cave_offset + len(payload)] = payload

    if patch_hook and bytes(image[hook_offset : hook_offset + 4]) != (
        high.to_bytes(2, "little") + low.to_bytes(2, "little")
    ):
        raise SystemExit("hook patch did not read back")
    if bytes(image[cave_offset : cave_offset + len(payload)]) != payload:
        raise SystemExit("cave patch did not read back")

    # The cave may contain bytes that already equal the filler, so the changed
    # count is not the payload length. What must hold is that nothing OUTSIDE the
    # two patched regions moved.
    allowed = set(range(cave_offset, cave_offset + len(payload)))
    if patch_hook:
        allowed.update(range(hook_offset, hook_offset + 4))
    stray = [i for i, (a, b) in enumerate(zip(image, original)) if a != b and i not in allowed]
    if stray:
        raise SystemExit(f"patch touched bytes outside its regions: {stray[:8]}")
    changed = sum(1 for a, b in zip(image, original) if a != b)
    if changed > len(payload) + (4 if patch_hook else 0):
        raise SystemExit(f"patch changed {changed} bytes, more than it wrote")

    if gate:
        verify_disassembly(bytes(image))

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(bytes(image))
    if sha256(source) != CANONICAL_SHA256:
        raise SystemExit("the canonical image changed during the build")
    if destination.stat().st_size != source.stat().st_size:
        raise SystemExit("derivative size differs from canonical")
    return sha256(destination), labels


#: Every halfword of the cave, checked by DECODING the built bytes rather than by
#: trusting the encoder. Two byte-access offsets in the first draft of this cave
#: were encoded with the word-access scaling rule (`ldrb r2,[r6,#1]` and
#: `strb r0,[r6,#1]` where `[r6,#4]` was meant), which read the wrong cursor byte
#: and wrote a byte of the text object, and the emulator wedged. This table is
#: what turns that class of mistake into a build failure.
DISASSEMBLY_CHECKS = (
    (0x00, "ldrh r1, [r0]"),
    (0x02, "movs r2, #0x4b"),
    (0x04, "cmp r1, r2"),
    (0x06, "beq #0x82ed222"),
    (0x08, "adds r0, r5, #0"),
    (0x0E, "ldr r3, [pc, #0x44]"),
    (0x10, "bx r3"),
    (0x12, "push {r7}"),
    (0x14, "mov r7, r0"),
    (0x16, "movs r1, #0x41"),
    (0x18, "mov r0, r5"),
    (0x1E, "movs r0, #0x41"),
    (0x24, "movs r1, #0x21"),
    (0x26, "mov r0, r5"),
    (0x2C, "movs r0, #0x21"),
    (0x32, "adds r7, #2"),
    (0x34, "str r7, [r4, #0x14]"),
    (0x36, "pop {r7}"),
    (0x38, "ldr r3, [pc, #0x1c]"),
    (0x3C, "ldr r1, [r5, #0xc]"),
    (0x3E, "ldr r1, [r1]"),
    (0x40, "lsls r0, r0, #1"),
    (0x42, "ldrh r0, [r1, r0]"),
    (0x44, "lsls r0, r0, #1"),
    (0x46, "ldrh r0, [r1, r0]"),
    (0x48, "adds r0, #1"),
    (0x4A, "ldrb r2, [r6, #4]"),
    (0x4C, "adds r0, r0, r2"),
    (0x4E, "strb r0, [r6, #4]"),
    (0x50, "str r0, [r5, #4]"),
    (0x52, "bx lr"),
)


def _normalise(text: str) -> str:
    return " ".join(text.lower().replace("0x", "0x").split())


def verify_disassembly(image: bytes) -> None:
    """Decode the cave out of the finished image and compare it with the table."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from thumb_disasm import decode_thumb_at  # noqa: PLC0415

    for offset, expected in DISASSEMBLY_CHECKS:
        item = decode_thumb_at(image, CAVE + offset)
        if item is None:
            raise SystemExit(f"cave offset {offset:#04x} does not decode")
        found = _normalise(str(item).split("  ", 1)[-1])
        if found != _normalise(expected):
            raise SystemExit(
                f"cave offset {offset:#04x} decodes as {found!r}, expected "
                f"{_normalise(expected)!r}"
            )


def dump(path: Path) -> None:
    """Disassemble the patched sites from the image itself, with decoded targets."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from thumb_disasm import decode_thumb_at  # noqa: PLC0415

    image = path.read_bytes()
    for name, start, end in (
        ("hook window", HOOK - 6, HOOK + 0x1A),
        ("cave", CAVE, CAVE + 0x5C),
    ):
        print(f"=== {name} ===")
        address = start
        while address < end:
            item = decode_thumb_at(image, address)
            if item is None:
                print(f"  {address:#010x}  <undecodable>")
                address += 2
                continue
            print(f"  {address:#010x}  {item}")
            address += item.size


VARIANTS = {
    # name          hook patched, gate present, file suffix
    "full": (True, True, ""),
    "cave-only": (False, True, "-caveonly"),
    "passthrough": (True, False, "-passthrough"),
}


def build_selfbl(source: Path, destination: Path) -> str:
    """Hook the site with a BL whose target is the very next instruction.

    The displaced `ldrh r1,[r0,#0]` and `add r0,r5,#0` are gone, so this is not
    a faithful copy: the immediately following original `bl 0x0803DE50` runs with
    r0 still holding the source cursor rather than the strip. It is not meant to
    work. It exists to ask one question only: does a four-byte BL written over
    those two halfwords transfer at all? A `bl` to the next instruction is the
    smallest possible control-flow change.
    """
    if sha256(source) != CANONICAL_SHA256:
        raise SystemExit("source is not the canonical image")
    original = source.read_bytes()
    image = bytearray(original)
    offset = HOOK - ROM_BASE
    if bytes(image[offset : offset + 4]) != HOOK_CANONICAL:
        raise SystemExit("hook site is not the expected instructions")
    high, low = bl_encode(HOOK, HOOK + 4)
    if bl_decode(HOOK, high, low) != HOOK + 4:
        raise SystemExit("self branch does not decode back")
    image[offset : offset + 4] = high.to_bytes(2, "little") + low.to_bytes(2, "little")
    changed = sum(1 for a, b in zip(image, original) if a != b)
    if changed == 0:
        raise SystemExit("self branch changed nothing; the encoding is the original")
    destination.write_bytes(bytes(image))
    if sha256(source) != CANONICAL_SHA256:
        raise SystemExit("the canonical image changed during the build")
    return sha256(destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=sorted(VARIANTS) + ["selfbl"], default="full")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    source = root / "roms" / "Dragon Ball Z - Buu's Fury (U).gba"
    if args.variant == "selfbl":
        destination = root / "build" / "runtime-roms" / "dialogue-selfbl.gba"
        digest = build_selfbl(source, destination)
        print(f"variant       : selfbl (bl at {HOOK:#010x} -> {HOOK + 4:#010x})")
        print(f"built sha256  : {digest}")
        return 0

    patch_hook, gate, suffix = VARIANTS[args.variant]
    destination = root / "build" / "runtime-roms" / f"dialogue-twoglyph{suffix}.gba"
    digest, labels = build(source, destination, patch_hook=patch_hook, gate=gate)
    print(f"variant       : {args.variant}")
    print(f"source        : {source}")
    print(f"canonical     : {sha256(source)}")
    print(f"destination   : {destination}")
    print(f"built sha256  : {digest}")
    print(f"hook          : {HOOK:#010x} -> bl {CAVE:#010x}" if patch_hook else "hook          : NOT PATCHED")
    print(f"cave bytes    : {labels['bytes']}")
    print(f"expand label  : {labels['expand']:#010x}")
    print(f"advance label : {labels['advance']:#010x}")
    print(f"glyph A       : {GLYPH_A:#04x}, glyph B: {GLYPH_B:#04x}, test unit: {TEST_UNIT:#04x}")
    print()
    dump(destination)
    return 0


if __name__ == "__main__":
    sys.exit(main())
