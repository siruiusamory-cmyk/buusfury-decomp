"""Build the expansion-token engine patch, and the control that isolates it.

WHY A CONTROL FIRST. `docs/research/DIALOGUE_EXPANSION_TOKEN_DESIGN.md` section 10
puts the measure side of the patch on a **relocated copy** of the line fitter
`FUN_0803DE6A`, because that function is a leaf (`push {r4,r5,r6,r7}` at
0x0803DE6A, `pop {r4,r5,r6,r7}` + `bx lr` at 0x0803DEA2/0x0803DEA4, no saved LR),
so a `BL` written into it in place would destroy the return address of all six of
its callers. Retargeting the two dialogue call sites at 0x0800AF3A and 0x0800AFC8
to a copy is therefore the design's own riskiest untested step: the composition
hook at 0x0800B066 is runtime-proven by DIALOGUE-RENDER-PATH-001, the copy is not.

The `fitter-control` variant exists to test exactly that one question and nothing
else. It writes the relocated copy **with the production prologue and epilogue**
(`push {r4,r5,r6,r7,lr}` / `pop {r4,r5,r6,r7,pc}`) and retargets the two callers,
and it changes no behaviour at all, because the copy is the original bytes. A run
on it must reproduce the canonical counters exactly; if it does not, the fault is
the relocation and the retargeting, not the token logic. That is the same
discipline that localised the ARMv4T undefined-instruction defect: separate the
mechanism from the feature before believing a negative.

WHAT IS VERIFIED HERE, AND HOW. The copy is compared against the original bytes
with the three known edits applied, so no instruction is transcribed by hand; the
build additionally asserts the properties the relocation depends on (the block
contains no `BL` and no PC-relative literal load, so every internal branch is
relative to a block that moved as a whole, and the last halfword is the loop-back
branch), decodes both retargeted callers back to the cave, and refuses any
displacement outside the ARMv4T 23-bit `BL` range.

Nothing here writes to any source image; the derivative goes under ignored
`build/`.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

ROM_BASE = 0x08000000

#: The relocated line fitter's home: inside a measured 3,019-byte all-zero run
#: (0x082ED210..0x082EDDDA) that DIALOGUE-RENDER-PATH-001 proved executes at
#: runtime. 0x082ED210 is 0x2E21AA from the composition hook and 0x2E22D2 /
#: 0x2E2244 from the two fitter call sites, all inside the 23-bit `BL` range.
CAVE = 0x082ED210
CAVE_RESERVED = 512

#: `FUN_0803DE6A`: the 144-byte fitter body, ending at the loop-back branch. The
#: next function begins at 0x0803DEFA, which is the halfword after this span.
FITTER_START = 0x0803DE6A
FITTER_BYTES = 144

#: The two dialogue-side callers of the fitter, and the only two retargeted. The
#: other four callers keep the original function, so no other subsystem can be
#: handed token pricing.
FITTER_CALLERS = (0x0800AF3A, 0x0800AFC8)
FITTER_CALLER_BYTES = bytes([0x32, 0xF0, 0x96, 0xFF])  # 0x0800AF3A
FITTER_CALLER_BYTES_2 = bytes([0x32, 0xF0, 0x4F, 0xFF])  # 0x0800AFC8

#: The three same-size edits that turn the body into a function that may call out.
PUSH_ORIGINAL = 0xB4F0        # push {r4,r5,r6,r7}
PUSH_SAVE_LR = 0xB5F0         # push {r4,r5,r6,r7,lr}
POP_ORIGINAL = 0xBCF0         # pop {r4,r5,r6,r7}
BX_LR = 0x4770
POP_RETURN = 0xBDF0           # pop {r4,r5,r6,r7,pc}
THUMB_NOP = 0x46C0            # mov r8, r8

EPILOGUE_OFFSET = 0x38        # 0x0803DEA2 - FITTER_START


def bl_encode(at: int, target: int) -> tuple[int, int]:
    """Encode a Thumb BL the way ARM7TDMI decodes it.

    ARM7TDMI is ARMv4T, which has no Thumb-2: its `BL` is the 23-bit form
    `11110 imm11` + `11111 imm11`, exactly the J1 = J2 = 1 special case of the
    Thumb-2 25-bit encoding. A 25-bit encoding with J1 or J2 clear is an undefined
    instruction on this CPU, and an undefined instruction here took the game back
    to its boot sequence and cost this line of work two runs, so the range is
    enforced at build time rather than discovered at run time.
    """
    offset = target - (at + 4)
    if offset % 2:
        raise ValueError(f"unaligned Thumb BL offset {offset:#x}")
    if not -(1 << 22) <= offset < (1 << 22):
        raise ValueError(
            f"Thumb BL displacement {offset:#x} is outside the ARMv4T 23-bit range"
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
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12)
                 | ((low & 0x7FF) << 1))
    if sign:
        immediate -= 1 << 25
    return at + 4 + immediate


def halfwords(data: bytes) -> list[int]:
    return [data[index] | (data[index + 1] << 8) for index in range(0, len(data), 2)]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class Body:
    """The original fitter body and the properties the relocation depends on."""

    words: list[int]
    has_bl: bool
    has_literal_load: bool

    @staticmethod
    def read(image: bytes) -> "Body":
        offset = FITTER_START - ROM_BASE
        words = halfwords(image[offset:offset + FITTER_BYTES])
        if len(words) * 2 != FITTER_BYTES:
            raise SystemExit("the fitter body is not where the design measures it")
        if words[0] != PUSH_ORIGINAL:
            raise SystemExit(f"fitter prologue is {words[0]:#06x}, not a push {{r4-r7}}")
        if words[EPILOGUE_OFFSET // 2] != POP_ORIGINAL or \
                words[EPILOGUE_OFFSET // 2 + 1] != BX_LR:
            raise SystemExit("fitter epilogue is not pop {r4-r7} + bx lr")
        # A BL is 11110/11111 in its first halfword; a PC-relative literal load is
        # ldr rX,[pc,#imm] = 01001 in bits 15..11. Both would have to be fixed up
        # if the block moved, and the design says the block has neither.
        has_bl = any(words[i] >> 11 == 0b11110 and
                     words[i + 1] >> 11 == 0b11111 for i in range(len(words) - 1))
        has_literal_load = any(words[i] >> 11 == 0b01001 for i in range(len(words)))
        return Body(words, has_bl, has_literal_load)

    def relocated(self) -> list[int]:
        """The body as the cave holds it: the prologue and epilogue edits only."""
        words = list(self.words)
        words[0] = PUSH_SAVE_LR
        words[EPILOGUE_OFFSET // 2] = POP_RETURN
        words[EPILOGUE_OFFSET // 2 + 1] = THUMB_NOP
        return words


def build_fitter_copy(image: bytes) -> bytes:
    """The relocated fitter: a byte-for-byte copy with two prologue/epilogue edits."""
    body = Body.read(image)
    if body.has_bl or body.has_literal_load:
        raise SystemExit(
            "the fitter body holds a BL or a PC-relative literal load, so it cannot "
            "be moved as one block without fixing that up"
        )
    payload = bytearray()
    for word in body.relocated():
        payload += word.to_bytes(2, "little")
    if len(payload) != FITTER_BYTES:
        raise SystemExit("the relocated copy is not the original's size")
    return bytes(payload)


def patch(source: Path, destination: Path, expected_sha256: str) -> dict[str, object]:
    # A source image is immutable. Refuse before opening anything: a check after
    # the write would only report the damage.
    if destination.resolve() == source.resolve():
        raise SystemExit(
            f"refusing to write the derivative over its own source image: {source}"
        )
    if sha256(source) != expected_sha256:
        raise SystemExit(
            f"source is not the declared image: {sha256(source)} != {expected_sha256}"
        )
    original = source.read_bytes()
    image = bytearray(original)
    body = Body.read(original)

    cave_offset = CAVE - ROM_BASE
    run = set(image[cave_offset:cave_offset + CAVE_RESERVED])
    if len(run) != 1 or run.pop() not in (0x00, 0xFF):
        raise SystemExit("the cave region is not a uniform filler run")

    # 1. the relocated copy.
    payload = build_fitter_copy(original)
    image[cave_offset:cave_offset + len(payload)] = payload

    # 2. the two dialogue callers.
    expected = {FITTER_CALLERS[0]: FITTER_CALLER_BYTES,
                FITTER_CALLERS[1]: FITTER_CALLER_BYTES_2}
    for caller in FITTER_CALLERS:
        offset = caller - ROM_BASE
        found = bytes(image[offset:offset + 4])
        if found != expected[caller]:
            raise SystemExit(
                f"caller {caller:#010x} is {found.hex()}, not the expected BL"
            )
        high, low = bl_encode(caller, CAVE)
        if bl_decode(caller, high, low) != CAVE:
            raise SystemExit(f"caller {caller:#010x} does not decode back to the cave")
        image[offset:offset + 4] = high.to_bytes(2, "little") + low.to_bytes(2, "little")

    # 3. nothing outside the two regions may move.
    allowed = set(range(cave_offset, cave_offset + len(payload)))
    for caller in FITTER_CALLERS:
        allowed.update(range(caller - ROM_BASE, caller - ROM_BASE + 4))
    stray = [i for i, (before, after) in enumerate(zip(image, original))
             if before != after and i not in allowed]
    if stray:
        raise SystemExit(f"the patch touched bytes outside its regions: {stray[:8]}")

    verify(bytes(image), original, payload)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(bytes(image))
    if sha256(source) != expected_sha256:
        raise SystemExit("the source image changed during the build")
    if destination.stat().st_size != source.stat().st_size:
        raise SystemExit("the derivative size differs from the source")
    body_words = len(body.words)
    return {
        "cave": CAVE,
        "copy_bytes": len(payload),
        "copy_halfwords": body_words,
        "callers": FITTER_CALLERS,
        "sha256": sha256(destination),
    }


def verify(image: bytes, original: bytes, payload: bytes) -> None:
    """Re-read the finished image and prove the copy and the branches."""
    cave_offset = CAVE - ROM_BASE
    if bytes(image[cave_offset:cave_offset + len(payload)]) != payload:
        raise SystemExit("the relocated copy did not read back")
    original_body = original[FITTER_START - ROM_BASE:FITTER_START - ROM_BASE + FITTER_BYTES]
    copy = bytes(image[cave_offset:cave_offset + len(payload)])
    differences = [index for index, (before, after) in enumerate(zip(original_body, copy))
                   if before != after]
    for index in differences:
        if not (0 <= index < 2 or EPILOGUE_OFFSET <= index < EPILOGUE_OFFSET + 4):
            raise SystemExit(
                f"the relocated copy differs from the original at byte {index}, "
                f"outside its prologue and epilogue"
            )
    for caller in FITTER_CALLERS:
        offset = caller - ROM_BASE
        words = halfwords(bytes(image[offset:offset + 4]))
        decoded = bl_decode(caller, words[0], words[1])
        if decoded != CAVE:
            raise SystemExit(f"caller {caller:#010x} decodes to {decoded:#010x}")
    # The copy's own loop-back branch must still land inside the copy: the whole
    # block moved, so every internal relative branch moved with it.
    last = CAVE + FITTER_BYTES - 2
    word = halfwords(bytes(image[last - ROM_BASE:last - ROM_BASE + 2]))[0]
    if word >> 11 != 0b11100:
        raise SystemExit(f"the copy's last halfword {word:#06x} is not a branch")
    displacement = word & 0x7FF
    if displacement & 0x400:
        displacement -= 0x800
    target = last + 4 + displacement * 2
    if not CAVE <= target < CAVE + FITTER_BYTES:
        raise SystemExit(
            f"the copy's last branch leaves the copy: {last:#010x} -> {target:#010x}"
        )


def dump(path: Path) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from thumb_disasm import decode_thumb_at  # noqa: PLC0415

    image = path.read_bytes()
    for name, start, end in (("relocated fitter", CAVE, CAVE + 0x20),
                             ("copy epilogue", CAVE + EPILOGUE_OFFSET - 4,
                              CAVE + EPILOGUE_OFFSET + 8),
                             ("caller 1", FITTER_CALLERS[0] - 4, FITTER_CALLERS[0] + 8),
                             ("caller 2", FITTER_CALLERS[1] - 4, FITTER_CALLERS[1] + 8)):
        print(f"=== {name} ===")
        address = start
        while address < end:
            item = decode_thumb_at(image, address)
            print(f"  {address:#010x}  {item}")
            address += 2 if item is None else item.size


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["fitter-control"], default="fitter-control")
    parser.add_argument("--rom", required=True, help="the source image")
    parser.add_argument("--expect-sha256", required=True,
                        help="the exact digest the source must have")
    parser.add_argument("--out", required=True, help="where to write the derivative")
    args = parser.parse_args()

    source = Path(args.rom)
    destination = Path(args.out)
    labels = patch(source, destination, args.expect_sha256.lower())
    print(f"variant        : {args.variant}")
    print(f"source         : {source}")
    print(f"source sha256  : {sha256(source)}")
    print(f"derivative     : {destination}")
    print(f"derivative sha : {labels['sha256']}")
    print(f"cave           : {labels['cave']:#010x} "
          f"({labels['copy_bytes']} bytes / {labels['copy_halfwords']} halfwords)")
    print(f"retargeted     : " + ", ".join(f"{caller:#010x}" for caller in labels["callers"]))
    print()
    dump(destination)
    return 0


if __name__ == "__main__":
    sys.exit(main())
