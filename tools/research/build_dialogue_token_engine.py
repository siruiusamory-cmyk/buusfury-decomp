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

Nothing here writes to any source image: the derivative is staged and published at
the path the caller names, and this ticket's runs put it under ignored `build/`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from tools.webfoot.write import WriteError, ensure_not_source_alias

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

#: The composition hook: the two halfwords at 0x0800B066 that the token variant
#: replaces with the branch into the cave. DIALOGUE-RENDER-PATH-001 proved this
#: site is where the reveal step reads the source unit, holds the persistent
#: cursor and consumes it exactly once.
COMPOSE_HOOK = 0x0800B066
COMPOSE_HOOK_BYTES = bytes([0x01, 0x88, 0x28, 0x1C])  # ldrh r1,[r0,#0] ; add r0,r5,#0

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


# --- the engine patch's second half: the token branch --------------------------
#
# The design's section 10 in one place, because the register discipline is the
# whole difficulty and it is worth being able to read it in one pass.
#
# `cave_fitter` is the relocated copy. Its width site, `ldr r5,[r0,#0xc]` +
# `cmp r4,#0xff` at 0x0803DEC8, becomes `bl token_advance`; the eleven displaced
# halfwords stay in the copy as dead bytes and `token_advance` long-jumps past them
# to the copy's accumulate point (`ldr r5,[r3,#8]; add r4,r5,r4` at 0x0803DEE0).
# `r5` is dead until that point, which is what makes it the free register for the
# jump-back address, and the copy saves LR in its prologue, which is what makes a
# `BL` inside it safe at all.
#
# Shared by both sides, so width and composition can never disagree about what an
# entry means:
#
#   token_lookup(r4 = unit) -> r5 = entry pointer, or 0
#       clobbers r1, r2, r3, r5; preserves r0, r4, r6, r7
#   glyph_advance(r0 = strip, r1 = glyph) -> r2 = width(glyph) + 1
#       clobbers r1, r2; preserves r0, r3, r4, r5, r6, r7
#
# `token_advance(r0 = strip, r4 = unit) -> r4 = the unit's full advance` preserves
# r0, r1, r2, r3, r6, r7 by pushing the three it needs, and never returns through
# LR: it jumps back into the copy.
#
# `cave_compose` replaces the two halfwords at 0x0800B066. At its entry the
# original code has `r0` = the source cursor, `r4` = obj, `r5` = strip,
# `r6` = obj+0x60, and `strip+4`/`strip+8` already hold x and y. The ordinary
# branch reproduces the displaced instructions and resumes at the game's own
# `bl 0x0803DE50` at 0x0800B06A, so the ordinary path is the game's code and not a
# copy of it. The expansion branch composes each glyph through that same
# `0x0803DE50`, advances the persistent x by that glyph's own advance, consumes
# exactly one source unit, and rejoins at 0x0800B094, which is the function's own
# epilogue. `r7` is free at that point (the two-glyph proof held its cursor in r7
# behind a push), and everything else the cave touches is on its stack.

#: Where the helper block starts, inside the cave: past the 144-byte fitter copy.
HELPERS_OFFSET = 0x90
#: The fitter copy's width site (0x0803DEC8) and the copy's accumulate point
#: (0x0803DEE0), as offsets from CAVE.
WIDTH_SITE_OFFSET = 0x5E
ACCUMULATE_OFFSET = 0x76

#: Where the engine-visible table starts inside the blob. The header is builder
#: metadata the engine never reads, so the descriptor literal points past it.
BLOB_ENTRY_OFFSET = 12

FUN_COMPOSE = 0x0803DE50
RESUME_ORDINARY = 0x0800B06A      # the game's own bl FUN_COMPOSE
REJOIN_EXPANSION = 0x0800B094     # the text object's epilogue

THUMB_NOP = 0x46C0


class Emitter:
    """A tiny Thumb-1 emitter with labels and a PC-relative literal pool.

    It exists so the cave is written as named instructions with named targets
    rather than as hand-computed halfwords, and so every literal load is patched
    from its own site's alignment. Nothing here is a general assembler.
    """

    def __init__(self, base: int) -> None:
        self.base = base
        self.words: list[int] = []
        self.labels: dict[str, int] = {}
        self.literals: dict[str, int] = {}
        self.keys: list[str] = []
        self.references: list[tuple[int, int, str]] = []
        self.branches: list[tuple[int, int, str]] = []
        self.calls: list[tuple[int, str]] = []
        self.call_targets: dict[str, int] = {}
        self.blob_address = 0
        self.pool_words: dict[str, int] = {}

    def here(self) -> int:
        return self.base + len(self.words) * 2

    def emit(self, halfword: int) -> int:
        site = self.here()
        self.words.append(halfword & 0xFFFF)
        return site

    def label(self, name: str) -> None:
        self.labels[name] = self.here()

    def set_literal(self, key: str, value: int) -> None:
        self.literals[key] = value
        if key not in self.keys:
            self.keys.append(key)

    def ldr_pc(self, register: int, key: str) -> None:
        if key not in self.keys:
            self.keys.append(key)
        self.references.append((len(self.words), register, key))
        self.emit(0)  # patched once the pool's address is known

    def branch_to(self, condition: int, name: str) -> None:
        self.branches.append((len(self.words), condition, name))
        self.emit(0)

    def call(self, name: str) -> None:
        self.calls.append((len(self.words), name))
        self.emit(0)
        self.emit(0)

    @staticmethod
    def _branch_word(condition: int, site: int, target: int) -> int:
        offset = target - (site + 4)
        if condition == 0xE:
            if offset % 2 or not -2048 <= offset <= 2046:
                raise SystemExit(
                    f"branch from {site:#010x} to {target:#010x} is out of range"
                )
            return 0xE000 | ((offset // 2) & 0x7FF)
        # The Thumb B<cond> offset is a SIGNED 8-bit count of halfwords, so the range
        # is -128..127. An earlier version accepted 0..255, which would have encoded a
        # forward branch of 0x80 or more as a BACKWARD one.
        if offset % 2 or not -128 <= offset // 2 <= 127:
            raise SystemExit(f"conditional branch from {site:#010x} is out of range")
        return 0xD000 | (condition << 8) | ((offset // 2) & 0xFF)

    def branch(self, condition: int, target: int) -> None:
        self.emit(self._branch_word(condition, self.here(), target))

    def resolve(self) -> None:
        """Fill in every branch and call whose target was a forward label."""
        for word_index, condition, name in self.branches:
            site = self.base + word_index * 2
            self.words[word_index] = self._branch_word(condition, site, self.labels[name])
        for word_index, name in self.calls:
            target = self.labels.get(name, self.call_targets.get(name))
            if target is None:
                raise SystemExit(f"call target {name!r} was never defined")
            high, low = bl_encode(self.base + word_index * 2, target)
            self.words[word_index] = high
            self.words[word_index + 1] = low

    def pool_and_blob(self, *, entry_offset: int = 0) -> tuple[int, int]:
        """Place the literal pool, patch every load, and return (pool, end).

        The dictionary follows the pool, so the address the cave loads for it is
        computed here. `entry_offset` is how far into the blob the engine-visible
        table starts: the blob's 12-byte header is builder metadata that the engine
        never reads, so the descriptor literal must point PAST it. Handing the
        engine the header instead makes every lookup return magic bytes as if they
        were glyph codes, which is exactly the fault this parameter exists to make
        unrepresentable.
        """
        if len(self.words) % 2:
            self.emit(THUMB_NOP)
        pool_base = self.here()
        if "blob" not in self.keys:
            raise SystemExit("the cave never asked for the dictionary address")
        blob_end = pool_base + 4 * len(self.keys)
        self.blob_address = blob_end + (blob_end % 4)
        self.literals["blob"] = self.blob_address + entry_offset
        addresses: dict[str, int] = {}
        for key in self.keys:
            if key not in self.literals:
                raise SystemExit(f"literal {key!r} was never given a value")
            addresses[key] = self.here()
            value = self.literals[key]
            self.emit(value & 0xFFFF)
            self.emit((value >> 16) & 0xFFFF)
        self.pool_words = addresses
        for word_index, register, key in self.references:
            site = self.base + word_index * 2
            base = (site + 4) & ~3
            delta = addresses[key] - base
            if delta % 4 or not 0 <= delta <= 1020:
                raise SystemExit(f"literal {key!r} is unreachable from {site:#010x}")
            self.words[word_index] = 0x4800 | (register << 8) | (delta // 4)
        return pool_base, self.here()


def assemble_token_cave(image: bytes, blob: bytes, count: int,
                        base: int = 0xE000) -> tuple[bytes, dict[str, int]]:
    """Emit the whole cave region: the hooked fitter copy, the helpers, the cave.

    The register discipline, which is the whole difficulty, is documented in the
    block comment above the offsets. `base` is the window's first unit; the design
    fixes it at 0xE000, and it is a literal so that a diagnostic build can put the
    window on a unit that occurs naturally in retail text.
    """
    if count < 1:
        raise SystemExit("the dictionary declares no tokens")

    copy = bytearray(bytearray(build_fitter_copy(image)))
    words = halfwords(bytes(copy))
    if words[WIDTH_SITE_OFFSET // 2] != 0x68C5 or \
            words[WIDTH_SITE_OFFSET // 2 + 1] != 0x2CFF:
        raise SystemExit("the fitter width site is not ldr r5,[r0,#0xc] + cmp r4,#0xff")
    if words[ACCUMULATE_OFFSET // 2] != 0x689D:
        raise SystemExit("the fitter accumulate point is not ldr r5,[r3,#8]")

    e = Emitter(CAVE)
    for word in words:
        e.emit(word)
    if e.here() != CAVE + FITTER_BYTES:
        raise SystemExit("the fitter copy is not the size the offsets assume")
    e.set_literal("accumulate", (CAVE + ACCUMULATE_OFFSET) | 1)
    e.set_literal("term", 0xFFFF)
    e.set_literal("count", count)
    e.set_literal("base", base)
    # A BL encodes the instruction address: the Thumb bit belongs on a `bx`
    # target, not on a call.
    e.call_targets["compose_glyph"] = FUN_COMPOSE

    # --- token_lookup: r4 = unit -> r5 = entry pointer, or 0 ------------------
    e.label("token_lookup")
    e.ldr_pc(1, "blob")                 # r1 = dictionary base
    e.ldr_pc(2, "count")                # r2 = token count
    e.ldr_pc(3, "base")                 # r3 = the window's first unit
    e.emit(0x1AE5)                      # subs r5,r4,r3      index = unit - base
    e.branch_to(0x3, "lookup_none")     # bcc: below the window is not a token
    e.emit(0x4295)                      # cmp r5,r2          index vs count
    e.branch_to(0x2, "lookup_none")     # bhs: an id at or above count is not a token
    e.emit(0x00ED)                      # lsls r5,r5,#3      index * 8
    e.emit(0x186D)                      # adds r5,r5,r1      entry pointer
    e.emit(0x4770)                      # bx lr
    e.label("lookup_none")
    e.emit(0x2500)                      # movs r5,#0
    e.emit(0x4770)                      # bx lr

    # --- glyph_advance: r0 = strip, r1 = glyph -> r2 = width(glyph) + 1 -------
    e.label("glyph_advance")
    e.emit(0x68C2)                      # ldr r2,[r0,#0xC]   the font holder
    e.emit(0x6812)                      # ldr r2,[r2,#0]     the font base
    e.emit(0x0049)                      # lsls r1,r1,#1
    e.emit(0x5A51)                      # ldrh r1,[r2,r1]    glyph record index
    e.emit(0x0049)                      # lsls r1,r1,#1
    e.emit(0x5A52)                      # ldrh r2,[r2,r1]    advance width
    e.emit(0x3201)                      # adds r2,#1
    e.emit(0x4770)                      # bx lr

    # --- token_advance: r0 = strip, r4 = unit -> r4 = full advance -----------
    e.label("token_advance")
    e.emit(0xB40E)                      # push {r1,r2,r3}
    e.call("token_lookup")
    e.emit(0x2D00)                      # cmp r5,#0
    e.branch_to(0x0, "advance_ordinary")
    e.emit(0x2400)                      # movs r4,#0         the accumulator
    e.label("advance_loop")
    e.ldr_pc(3, "term")                 # r3 = 0xFFFF, reloaded each pass
    e.emit(0x8829)                      # ldrh r1,[r5,#0]    glyph
    e.emit(0x3502)                      # adds r5,#2
    e.emit(0x4299)                      # cmp r1,r3
    e.branch_to(0x0, "advance_done")
    e.call("glyph_advance")
    e.emit(0x18A4)                      # adds r4,r4,r2      accumulate
    e.branch(0xE, e.labels["advance_loop"])
    e.label("advance_done")
    e.emit(0xBC0E)                      # pop {r1,r2,r3}
    e.ldr_pc(5, "accumulate")
    e.emit(0x4728)                      # bx r5              back into the copy
    e.label("advance_ordinary")
    e.emit(0x68C1)                      # ldr r1,[r0,#0xC]   the original arithmetic,
    e.emit(0x2CFF)                      # cmp r4,#0xFF       exactly as the fitter does it
    e.branch_to(0x3, "advance_narrow")
    e.emit(0x684C)                      # ldr r4,[r1,#4]
    e.emit(0x3401)                      # adds r4,#1
    e.branch_to(0xE, "advance_exit")
    e.label("advance_narrow")
    e.emit(0x6809)                      # ldr r1,[r1,#0]
    e.emit(0x0064)                      # lsls r4,r4,#1
    e.emit(0x5B0C)                      # ldrh r4,[r1,r4]
    e.emit(0x0064)                      # lsls r4,r4,#1
    e.emit(0x5B0C)                      # ldrh r4,[r1,r4]
    e.emit(0x3401)                      # adds r4,#1
    e.label("advance_exit")
    e.emit(0xBC0E)                      # pop {r1,r2,r3}
    e.ldr_pc(5, "accumulate")
    e.emit(0x4728)                      # bx r5

    # --- cave_compose: the two halfwords at 0x0800B066, and the expansion ----
    e.set_literal("resume_ordinary", RESUME_ORDINARY | 1)
    e.set_literal("rejoin_expansion", REJOIN_EXPANSION | 1)
    e.label("cave_compose")
    e.emit(0xB4F1)                      # push {r0,r4,r5,r6,r7}
    e.emit(0x8801)                      # ldrh r1,[r0,#0]    displaced: the source unit
    e.emit(0x460C)                      # mov r4,r1          token_lookup's input
    e.call("token_lookup")
    e.emit(0x2D00)                      # cmp r5,#0
    e.branch_to(0x0, "compose_ordinary")
    e.emit(0x9C01)                      # ldr r4,[sp,#4]     obj
    e.emit(0x9E03)                      # ldr r6,[sp,#12]    obj+0x60
    e.emit(0x9802)                      # ldr r0,[sp,#8]     strip
    e.label("compose_loop")
    e.ldr_pc(2, "term")
    e.emit(0x8829)                      # ldrh r1,[r5,#0]    the next glyph
    e.emit(0x3502)                      # adds r5,#2
    e.emit(0x4291)                      # cmp r1,r2
    e.branch_to(0x0, "compose_done")
    e.emit(0xB403)                      # push {r0,r1}       strip and glyph across the call
    e.label("compose_call")
    e.call("compose_glyph")
    e.emit(0xBC03)                      # pop {r0,r1}
    e.call("glyph_advance")
    e.emit(0x7933)                      # ldrb r3,[r6,#4]    the old persistent x
    e.emit(0x18D2)                      # adds r2,r2,r3      x + width + 1
    e.emit(0x7132)                      # strb r2,[r6,#4]    persistent x
    e.emit(0x6042)                      # str r2,[r0,#4]     the compose cursor copy
    e.branch(0xE, e.labels["compose_loop"])
    e.label("compose_done")
    e.emit(0x9900)                      # ldr r1,[sp,#0]     the source cursor
    e.emit(0x3102)                      # adds r1,#2
    e.emit(0x9A01)                      # ldr r2,[sp,#4]     obj
    e.label("compose_consume")
    e.emit(0x6151)                      # str r1,[r2,#0x14]  ONE unit consumed
    e.emit(0xBCF1)                      # pop {r0,r4,r5,r6,r7}
    e.ldr_pc(3, "rejoin_expansion")
    e.emit(0x4718)                      # bx r3
    e.label("compose_ordinary")
    e.emit(0x9900)                      # ldr r1,[sp,#0]     the source cursor
    e.emit(0x8809)                      # ldrh r1,[r1,#0]    the unit
    e.emit(0x9802)                      # ldr r0,[sp,#8]     strip
    e.emit(0x9D02)                      # ldr r5,[sp,#8]     strip
    e.emit(0x9C01)                      # ldr r4,[sp,#4]     obj
    e.emit(0x9E03)                      # ldr r6,[sp,#12]
    e.emit(0x9F04)                      # ldr r7,[sp,#16]
    e.emit(0xB005)                      # add sp,#20
    e.ldr_pc(3, "resume_ordinary")
    e.emit(0x4718)                      # bx r3              the game's own bl at 0x0800B06A

    # Every address this cave reaches with `bx` must carry the Thumb bit. An even
    # target switches the processor to ARM state, and the four bytes there are not
    # ARM code: the CPU takes an undefined-instruction exception and the frame
    # never completes. The relocation's own jump-back is the one that is easy to
    # miss, because its target is a label inside the cave and not a game address.
    for name, key in (("advance jump-back", "accumulate"),
                      ("compose ordinary resume", "resume_ordinary"),
                      ("compose expansion rejoin", "rejoin_expansion")):
        if not e.literals[key] & 1:
            raise SystemExit(
                f"the {name} target {e.literals[key]:#010x} has no Thumb bit"
            )

    e.resolve()

    # The fitter copy's width site becomes the call, once token_advance exists.
    site = CAVE + WIDTH_SITE_OFFSET
    high, low = bl_encode(site, e.labels["token_advance"])
    e.words[WIDTH_SITE_OFFSET // 2] = high
    e.words[WIDTH_SITE_OFFSET // 2 + 1] = low

    # The compose hook's branch back to the cave is not here; it is the site patch
    # in `patch`. The cave needs the compose entry only as a label for that.
    pool, end = e.pool_and_blob(entry_offset=BLOB_ENTRY_OFFSET)
    blob_at = e.blob_address
    payload = bytearray()
    for word in e.words:
        payload += word.to_bytes(2, "little")
    if len(payload) % 2:
        raise SystemExit("the cave payload is not halfword aligned")
    while CAVE + len(payload) < blob_at:
        payload += b"\x00"
    if CAVE + len(payload) != blob_at:
        raise SystemExit("the dictionary does not land on its predicted address")
    if len(blob) != 12 + count * 8:
        raise SystemExit("the dictionary blob is not the size its header declares")
    payload += blob
    payload = bytes(payload)
    verify_token_table(payload, blob_at, e.pool_words["blob"], blob, count)
    return payload, {
        "cave": CAVE,
        "helpers": e.labels["token_lookup"],
        "lookup": e.labels["token_lookup"],
        "advance": e.labels["token_advance"],
        "glyph_advance": e.labels["glyph_advance"],
        "compose": e.labels["cave_compose"],
        "compose_loop": e.labels["compose_loop"],
        "compose_call": e.labels["compose_call"],
        "compose_consume": e.labels["compose_consume"],
        "pool": pool,
        "blob": blob_at,
        "table": e.literals["blob"],
        "count": count,
        "bytes": len(payload),
    }


def verify_token_table(payload: bytes, blob_at: int, descriptor_word: int, blob: bytes,
                       count: int) -> None:
    """Read the table the ENGINE will read, out of the cave bytes, and check it.

    The descriptor is fetched from the cave's own literal-pool word, not from the
    builder's variable: the engine loads it with `ldr rX,[pc,#imm]`, so a build whose
    pool word disagreed with the builder's intent would hand the renderer something
    else entirely, and this is the check that sees it. An earlier version read the
    builder's value and then claimed to be reading it as the engine does.

    The words are then fetched exactly as the lookup fetches them,
    `descriptor + index * 8`, and compared with the entries the builder meant to
    write. A descriptor pointing at the blob header passes every other check in this
    file and fails here, reporting the magic it would have handed the renderer.
    """
    def halfword(address: int) -> int:
        offset = address - CAVE
        if offset < 0 or offset + 2 > len(payload):
            raise SystemExit(
                f"the token table at {address:#010x} is outside the cave; the engine "
                f"would read whatever follows it"
            )
        return payload[offset] | (payload[offset + 1] << 8)

    table = (halfword(descriptor_word) | (halfword(descriptor_word + 2) << 16))
    expected = [blob[index] | (blob[index + 1] << 8)
                for index in range(BLOB_ENTRY_OFFSET, len(blob), 2)]
    actual = [halfword(table + index * 2) for index in range(count * 4)]
    if actual != expected:
        raise SystemExit(
            f"the token table the cave loads does not hold the dictionary: read "
            f"[{', '.join(f'{value:#06x}' for value in actual[:6])}] at {table:#010x}, "
            f"expected [{', '.join(f'{value:#06x}' for value in expected[:6])}]"
        )
    if table != blob_at + BLOB_ENTRY_OFFSET:
        raise SystemExit(
            f"the pool word names {table:#010x}, not the entries at "
            f"{blob_at + BLOB_ENTRY_OFFSET:#010x}"
        )




def patch(source: Path, destination: Path, expected_sha256: str, *,
          variant: str = "fitter-control", blob: bytes | None = None,
          count: int = 0, base: int = 0xE000) -> dict[str, object]:
    # A source image is immutable. Refuse before opening anything, and through the
    # repository's own guard rather than a comparison of path strings: a hard-link
    # alias of the source is the same file, and comparing resolved paths would not
    # see it. A check after the write would only report the damage.
    try:
        ensure_not_source_alias(source, destination)
    except WriteError as exc:
        raise SystemExit(str(exc)) from exc
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

    token = variant == "token"

    # 1. the cave: the relocated copy alone, or the copy plus the token branch.
    labels: dict[str, object] = {}
    if token:
        if blob is None:
            raise SystemExit("the token variant needs a dictionary blob")
        payload, labels = assemble_token_cave(original, blob, count, base=base)
    else:
        payload = build_fitter_copy(original)
    if len(payload) > CAVE_RESERVED:
        raise SystemExit(f"the cave is {len(payload)} bytes, over {CAVE_RESERVED} reserved")
    image[cave_offset:cave_offset + len(payload)] = payload

    # 2. the two dialogue callers of the fitter.
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

    # 3. the composition hook, in the token variant only.
    if token:
        offset = COMPOSE_HOOK - ROM_BASE
        found = bytes(image[offset:offset + 4])
        if found != COMPOSE_HOOK_BYTES:
            raise SystemExit(
                f"the composition hook is {found.hex()}, not ldrh r1,[r0,#0] + add r0,r5,#0"
            )
        target = int(labels["compose"])
        high, low = bl_encode(COMPOSE_HOOK, target)
        if bl_decode(COMPOSE_HOOK, high, low) != target:
            raise SystemExit("the composition hook does not decode back to the cave")
        image[offset:offset + 4] = high.to_bytes(2, "little") + low.to_bytes(2, "little")

    # 4. nothing outside the patched regions may move.
    allowed = set(range(cave_offset, cave_offset + len(payload)))
    for caller in FITTER_CALLERS:
        allowed.update(range(caller - ROM_BASE, caller - ROM_BASE + 4))
    if token:
        allowed.update(range(COMPOSE_HOOK - ROM_BASE, COMPOSE_HOOK - ROM_BASE + 4))
    stray = [i for i, (before, after) in enumerate(zip(image, original))
             if before != after and i not in allowed]
    if stray:
        raise SystemExit(f"the patch touched bytes outside its regions: {stray[:8]}")

    verify(bytes(image), original, payload, token=token)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Stage through an exclusively created temporary file, never a predictable
    # name beside the destination: a name like `<out>.partial` can itself be a
    # hard link to the source, which `write_bytes` would then truncate through.
    # A fresh inode cannot be an alias of anything. The publish is a rename, so
    # the destination name only ever points at the staged inode.
    with tempfile.NamedTemporaryFile(dir=destination.parent,
                                     prefix=destination.name + ".",
                                     suffix=".partial", delete=False) as handle:
        staged = Path(handle.name)
        try:
            handle.write(bytes(image))
        except BaseException:
            # NamedTemporaryFile(delete=False) leaves the file behind, and a stray
            # named `.partial` beside a build is exactly the predictable name this
            # staging exists to avoid.
            handle.close()
            staged.unlink(missing_ok=True)
            raise
    staged.replace(destination)
    if sha256(source) != expected_sha256:
        raise SystemExit("the source image changed during the build")
    if destination.stat().st_size != source.stat().st_size:
        raise SystemExit("the derivative size differs from the source")
    return {
        "cave": CAVE,
        "copy_bytes": len(payload),
        "copy_halfwords": len(body.words),
        "callers": FITTER_CALLERS,
        "compose_hook": COMPOSE_HOOK if token else None,
        "sha256": sha256(destination),
        **({"cave_labels": labels} if token else {}),
    }


def verify(image: bytes, original: bytes, payload: bytes, *, token: bool = False) -> None:
    """Re-read the finished image and prove the copy and the branches."""
    cave_offset = CAVE - ROM_BASE
    if bytes(image[cave_offset:cave_offset + len(payload)]) != payload:
        raise SystemExit("the cave did not read back")
    original_body = original[FITTER_START - ROM_BASE:FITTER_START - ROM_BASE + FITTER_BYTES]
    copy = bytes(image[cave_offset:cave_offset + FITTER_BYTES])
    # The width site is a fourth allowed difference in the token variant: its four
    # bytes are the call that replaces the displaced two-level width read.
    width_site = set(range(WIDTH_SITE_OFFSET, WIDTH_SITE_OFFSET + 4)) if token else set()
    for index, (before, after) in enumerate(zip(original_body, copy)):
        if before == after:
            continue
        if 0 <= index < 2 or EPILOGUE_OFFSET <= index < EPILOGUE_OFFSET + 4:
            continue
        if index in width_site:
            continue
        raise SystemExit(
            f"the relocated copy differs from the original at byte {index}, outside "
            f"its prologue, epilogue and width site"
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
    parser.add_argument("--variant", choices=["fitter-control", "token"],
                        default="fitter-control")
    parser.add_argument("--rom", required=True, help="the source image")
    parser.add_argument("--expect-sha256", required=True,
                        help="the exact digest the source must have")
    parser.add_argument("--out", required=True, help="where to write the derivative")
    parser.add_argument("--tokens", nargs="*", default=[],
                        help="the token variant's expansions, in id order")
    parser.add_argument("--token-base", default="0xE000",
                        help="the window's first unit. The design fixes this at "
                             "0xE000; a diagnostic build moves it onto a unit that "
                             "occurs naturally in retail text, because a token unit "
                             "never does and planting one needs a container edit")
    parser.add_argument("--splice-report",
                        help="the splice report whose dictionary this patch must use")
    args = parser.parse_args()

    base = int(args.token_base, 0)
    if args.splice_report:
        # The tokens a splice wrote and the tokens this patch expands must be the
        # same list in the same order, or the patch renders a different dictionary
        # than the image contains. Nothing else ties the two together.
        reported = json.loads(Path(args.splice_report).read_text(encoding="utf-8")).get(
            "tokens")
        if reported != list(args.tokens):
            raise SystemExit(
                f"the splice used {reported} and this patch was given "
                f"{list(args.tokens)}; they must be the same dictionary in id order"
            )
    if base != 0xE000:
        print(f"DIAGNOSTIC     : token base moved to {base:#06x}; not a shipping build")

    source = Path(args.rom)
    destination = Path(args.out)
    blob = None
    count = 0
    if args.variant == "token":
        from tools.webfoot.token_dictionary import TokenDictionary, build_blob
        dictionary = TokenDictionary(tuple(args.tokens))
        count = dictionary.count
        blob = build_blob(dictionary)
        print(f"dictionary     : {count} entries, {len(blob)} bytes")
        for entry in dictionary.entries():
            print(f"  U+{entry.unit:04X}  {dictionary.expansions[entry.index]!r}")
    labels = patch(source, destination, args.expect_sha256.lower(), variant=args.variant,
                   blob=blob, count=count, base=base)
    print(f"variant        : {args.variant}")
    print(f"source         : {source}")
    print(f"source sha256  : {sha256(source)}")
    print(f"derivative     : {destination}")
    print(f"derivative sha : {labels['sha256']}")
    print(f"cave           : {labels['cave']:#010x} ({labels['copy_bytes']} bytes)")
    print(f"retargeted     : " + ", ".join(f"{caller:#010x}" for caller in labels["callers"]))
    if labels.get("compose_hook"):
        print(f"compose hook   : {labels['compose_hook']:#010x} -> "
              f"{labels['cave_labels']['compose']:#010x}")
        for name in ("lookup", "advance", "glyph_advance", "compose", "compose_loop",
                     "compose_call", "compose_consume", "pool", "blob"):
            print(f"  {name:<15}: {labels['cave_labels'][name]:#010x}")
    print()
    dump(destination)
    return 0


if __name__ == "__main__":
    sys.exit(main())
