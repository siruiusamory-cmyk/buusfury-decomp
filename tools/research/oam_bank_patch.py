"""Patch an image so an actor's pieces can select a 4bpp palette bank.

WHY A PATCH IS NEEDED. `attr2` lives in the OAM entry's SECOND word, and the engine composes that word from the
object's tile base and priority byte while preserving bits 10..15, which means the palette nibble arrives
INHERITED from whatever the OAM buffer held. There is no write to borrow, so the nibble must be cleared and the
bank set by new code.

WHAT THE PATCH DOES, at the shared attr2 block `0x0800F2B2`..`0x0800F2BF` (the seven instructions before the
loop's piece advance):

* the block's tail is replaced with a PC-relative load and a `bx`, so control reaches an appended stub from any
  distance (a Thumb `b` cannot reach above EOF);
* the stub clears attr2 bits 0..9 and 12..15, sets the tile from `lr & 0x3FF`, sets the bank from the PIECE
  WORD's bits 25..27 carried in OAM word 0, and then clears those same bits in word 0 so a non-affine piece
  never carries a stray affine parameter select;
* it returns with an absolute `bx` to `0x0800F2C0`, the untouched start of the piece advance.

SAFETY FOR EVERY OTHER ACTOR, argued from measurement rather than hope: retail sets attr1 bits 9..11 on 0 of
11,005 pieces, so clearing them is a no-op there; retail's attr2 nibble is inert because the layer is 8bpp, so
clearing it changes no pixel; and the tile field is composed exactly as before. The bank therefore affects only
pieces whose data asks for one.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROM_BASE = 0x08000000

#: The seven instructions the patch replaces: 0x0800F2B2 mov r3,lr .. 0x0800F2BE str r6,[r1,#4].
BLOCK_SITE = 0x0800F2B2
BLOCK_BYTES = 14
#: The untouched resume address, the piece advance at 0x0800F2C0.
RESUME = 0x0800F2C0

#: The retail bytes of the block being replaced, read from the canonical image: `mov r3,lr` / `lsls r3,r3,#0x16`
#: / `lsrs r6,r6,#0xa` / `lsls r6,r6,#0xa` / `lsrs r3,r3,#0x16` / `orrs r6,r3` / `str r6,[r1,#4]`. The patch
#: refuses any image whose block differs, so a second run or a wrong image stops instead of corrupting.
EXPECTED_BLOCK = bytes.fromhex("73469b05b60ab6029b0d1e434e60")

#: The stub, hand-assembled Thumb. Every opcode is asserted against a disassembly in the tests, so a typo
#: cannot silently become a different instruction.
STUB = bytes.fromhex(
    "0230"      # adds r0,#2           the block's own side effect: the loop reads piece w/h from r0 at +0
    "b60a"      # lsrs r6,r6,#0xa      clear attr2 bits 0..9
    "b602"      # lsls r6,r6,#0xa
    "0b68"      # ldr  r3,[r1]         word 0, carrying the piece word
    "5f0e"      # lsrs r7,r3,#0x19     attr1 bits 9..11 -> bits 0..2
    "0723"      # movs r3,#7
    "1f40"      # ands r7,r3           bank 0..7
    "3f03"      # lsls r7,r7,#0xc      -> attr2 bits 12..14
    "f023"      # movs r3,#0xf0
    "1b02"      # lsls r3,r3,#0x8      = 0xF000
    "9e43"      # bics r6,r3           clear attr2 bits 12..15
    "3e43"      # orrs r6,r7           set the bank
    "7346"      # mov  r3,lr
    "9b05"      # lsls r3,r3,#0x16
    "9b0d"      # lsrs r3,r3,#0x16     tile = lr & 0x3FF
    "1e43"      # orrs r6,r3           tile into attr2 bits 0..9
    "4e60"      # str  r6,[r1,#4]      word 1
    "0b68"      # ldr  r3,[r1]         word 0 again
    "0727"      # movs r7,#7
    "7f06"      # lsls r7,r7,#0x19     attr1 bits 9..11
    "bb43"      # bics r3,r7
    "0b60"      # str  r3,[r1]         non-affine: no affine select
)


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def stub_layout(stub_address: int, body: bytes | None = None) -> dict:
    """Where the pieces of the stub live, so nothing has to hardcode an offset.

    The return uses `ldr r3,[pc,#0]`, which reads from `(PC & ~3)` with PC = instruction + 4. The body is
    therefore padded with nops to a multiple of four, so the load's target IS the literal that follows the
    `bx`, and the alignment holds by construction rather than by counting instructions.
    """
    padded = bytearray(STUB if body is None else body)
    while (len(padded) + 4) % 4:
        padded.extend(bytes.fromhex("c046"))            # nop
    load_at = stub_address + len(padded)
    literal_at = load_at + 4
    if (load_at + 4) & ~3 != literal_at:
        raise AssertionError("stub layout: the return load does not point at its literal")
    return {"body": bytes(padded), "load_at": load_at, "literal_at": literal_at,
            "end": literal_at + 4}


def patch(image: bytearray, body: bytes | None = None, padding: int = 0):
    """Apply the patch in place. Returns the stub address and the bytes it replaced.

    `body` overrides the stub, which the bisect uses to test the entry and return path on its own; `padding`
    inserts filler bytes before the stub so a variant can put it deeper into the ROM region.
    """
    if padding:
        image.extend(b"\x00" * padding)
    while len(image) % 4:
        image.append(0)
    stub_address = len(image)

    layout = stub_layout(stub_address, body)
    image.extend(layout["body"] + bytes.fromhex("4b00") + bytes.fromhex("1847"))
    image.extend(struct.pack("<I", RESUME + 1))
    if len(image) != layout["end"]:
        raise AssertionError("stub layout disagrees with what was written")

    # The stub's own return: the `ldr r3,[pc,#0]` at body end reads (PC & ~3) + 0 = the next word, which is
    # the literal, so the read address must be word aligned. The body is an even number of halfwords, so the
    # literal starts word aligned only when the stub address is word aligned; insist on it.
    if stub_address % 4:
        raise AssertionError(f"stub must start word aligned, got 0x{stub_address:X}")

    # The entry is 14 bytes: a literal load, two nop slots, the stub address, and `bx`. The load's target is
    # (PC & ~3) + 4 = the site + 6 rounded to a word boundary, so the literal sits at site + 6 and is read
    # from there; the last two bytes are an unreachable nop so the block's length is exactly preserved.
    entry = (bytes.fromhex("014b" "c046" "c046")
             + struct.pack("<I", (stub_address + ROM_BASE) | 1)
             + bytes.fromhex("1847" "c046"))
    if len(entry) != BLOCK_BYTES:
        raise AssertionError(f"entry must be {BLOCK_BYTES} bytes, got {len(entry)}")

    offset = BLOCK_SITE - ROM_BASE
    original = bytes(image[offset:offset + BLOCK_BYTES])
    if original != EXPECTED_BLOCK:
        raise AssertionError(
            f"the attr2 block at 0x{BLOCK_SITE:08X} is not the retail sequence, so this image is either "
            f"already patched or not the image this patch was written for; refusing. Found {original.hex()}")
    image[offset:offset + BLOCK_BYTES] = entry
    return stub_address, original


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Patch an image so a piece can select a palette bank")
    parser.add_argument("--image", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    image = bytearray(Path(args.image).read_bytes())
    stub, original = patch(image)
    Path(args.out).write_bytes(bytes(image))
    print(f"stub at 0x{stub + ROM_BASE:08X}, {len(bytes(image)) - len(Path(args.image).read_bytes())} bytes "
          f"appended, block replaced at 0x{BLOCK_SITE:08X}")
    print(f"was: {original.hex()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
