# Route C: a per-actor palette for a custom actor

Owner decision: Perfect Cell gets his own colours as a REUSABLE mechanism. This is the revised design note after
the review that blocked the first one. Nothing here is built.

Canonical Buu's Fury sha256 `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`; Legacy of Goku
II sha256 `6E6C370C339EC9171CB1956ADF837A0D342A197F78964882EF46C3086656FF75`.

## 1. The mechanism, corrected

The first revision claimed the 4bpp/8bpp choice was global and concluded that a per-actor palette needed a
background layer and a new renderer. **That was wrong.** Measured from the engine itself:

* **Colour depth is per sprite.** OAM `attr0` bit 13 selects 16-colour or 256-colour for that sprite alone.
* **The engine copies the piece attribute word verbatim** into the sprite's first OAM word
  (`0x0800F254`), so an actor's own data decides its depth. No global register is involved.
* **The palette bank is `attr2` bits 12 to 15**, and the OAM builder writes `attr2` here:

```
0800F2A0  ldr  r6,[r1,#0x4]     ; the attr2 word
0800F2A6  movs r3,#0x3
0800F2A8  lsls r3,r3,#0xA       ; 0xC00
0800F2AA  bics r6,r3            ; clears ONLY bits 10..11 (priority)
0800F2B6  lsrs r6,r6,#0xA
0800F2B8  lsls r6,r6,#0xA       ; clears ONLY bits 0..9 (tile index)
0800F2BC  orrs r6,r3            ; rs the tile index back in
0800F2BE  str  r6,[r1,#0x4]
```

So bits 12 to 15 are neither cleared nor set: whatever the buffer held survives. A palette bank can therefore
ride in, and the engine change is a handful of instructions at that site.

**No retail actor is 4bpp.** All 23,180 pieces across 297 actors carry `attr0` bit 13 set, so this is a new
path for this engine, not an existing one being reused. That is worth stating plainly: the mechanism is
supported by the hardware and by the engine's own copy-verbatim behaviour, but no shipped actor exercises it.

## 2. What the rule requires, and the two ways to satisfy it

A 4bpp sprite's pixels are local indices 0 to 15, and its bank selects sixteen of the **shared** 256-entry OBJ
palette. So a bank's colours can come from two places:

**C2, new colours in the bank.** The bank's sixteen entries are rewritten to Cell's colours. This is what
"his own palette" literally means, and it **recolours every other sprite that indexes those entries**, because
8bpp sprites address all 256. Measured over Cell's three maps: actor art alone paints **216 indices in map 32,
150 in map 137 and 94 in map 138**, and the union is **224 of 256**. Consequently **no bank of sixteen entries
is free** against all placements, with or without portraits:

| map | free banks, placements only | free banks, placements plus every portrait |
| --- | --- | --- |
| 32 | none | none |
| 137 | none | none |
| 138 | none | none |

That census is conservative, because it counts every placement in the map while only on-screen sprites matter.
Deciding C2 honestly therefore needs a **runtime census during a Cell fight**: the OAM entries actually
visible, their depths, and the palette entries their tiles use. Cell's scenes need story progress to reach, so
that census is a runtime task, and C2 would in any case be an owner-visible exception to the rule.

**C1, existing colours, no palette write.** The bank's entries are left exactly as they are, and Cell's art is
quantised onto whichever existing bank fits each piece best. **Nothing in the palette changes, so no other
actor can change, by construction**, and no runtime census is needed to prove it. The cost is fidelity, and
that cost is now measured.

## 3. C1 measured: which banks, and what it costs

In 4bpp the bank is selected by `attr2`, which is written **per piece**, so each piece of Cell can use a
different existing bank. Choosing the best bank per piece across all 24 pieces:

| result | measurement |
| --- | --- |
| distinct banks needed | **2**: bank 5 for 22 pieces, bank 1 for 2 pieces |
| pieces needing more than 16 distinct local indices | **0** |
| per-piece worst-case squared RGB error | min **8,613**, median **9,350**, max **9,350** |
| theoretical maximum squared error | 195,075 |

CORRECTED after the build. This section first said three banks (2, 5 and 0) with a worst case of 19,425. That
measurement read Buu's Fury's palette where Cell's own colours belong, so it compared the image against itself
and understated the fit. With the source read from the Legacy of Goku II palette at `0x081DA6C8` and the banks
from this image at `0x0805652C`, the per-piece choice needs **two** banks and the worst case is **9,350**.

The colour sets were read from the Legacy of Goku II palette, the shared banks from this image. A worst case of
9,350 squared error is roughly 56 per channel on the single worst colour of a piece. That is a visible shift on
close inspection and invisible in motion at 64x64 on a GBA screen; the owner should decide with those numbers in
front of him.

## 4. The reuse interface

1. **Data.** The piece attribute word carries the bank in **bits 25 to 27**, which are free: measured over every
   retail piece, those bits are zero (the only values seen in bits 25 to 28 are `0` in 18,130 pieces and `8` in
   5,050, where bit 28 is the `attr1` horizontal-flip that is already in use). Three bits are eight banks, and
   C1 needs three.
2. **A depth marker per actor.** One bit says "this actor renders 4bpp": it clears `attr0` bit 13 on his pieces.
   The natural home is the actor's definition or its appearance row, not the piece, because it is a property of
   the character.
3. **The builder change.** When the actor is 4bpp, map the piece word's bits 25 to 27 into `attr2` bits 12 to
   14, at the site quoted in section 1. Nothing else in the OAM path moves.
4. **The allocation rule between actors.** A bank is a property of the art, not a global resource, because C1
   writes nothing: two actors may use the same bank or different ones, and the only constraint is that each
   piece's local colours fit sixteen. A future actor ships art plus a bank number per piece and needs no engine
   change at all.
5. **The converter.** Take indexed art plus a bank selection, map every colour to its nearest entry in the
   chosen bank, emit 4bpp tiles with local indices, and report the error per piece. It must assert that no
   piece needs more than sixteen distinct local indices, and that local index 0 stays transparent (hardware
   requirement in 4bpp).

## 5. Size estimate

| piece | estimate |
| --- | --- |
| the converter, with per-piece bank choice and the error report | 100 to 150 lines |
| the builder change plus a per-actor depth flag | 40 to 60 lines, one small function and its call site |
| data plumbing: the depth flag and the per-piece bank in the ported definition | small, inside the existing port tool |
| tests: converter, bank mapping, and a ROM-free check of the builder's bit mapping | one test file |
| the runtime proof: Cell visible in a fight, with a before/after census of the other actors on screen | one session |

That is a small ticket, not the 400 to 700 line renderer the blocked revision proposed, because the correction
removes the need for a background layer entirely.

## 6. What remains before building

1. **The owner's call on C1 versus C2**, with the fidelity numbers above in front of him. C1 is provable by
   construction; C2 needs a runtime on-screen census and is an exception to the rule.
2. **A runtime census of the on-screen palette usage during a Cell fight**, required only for C2. It also
   provides the before/after evidence for whichever route is built.
3. **Confirm the bank bits survive the port's own writing**, since the port rebuilds definitions and pieces: a
   check that a piece attribute word with bits 25 to 27 set is preserved into the built image.

## 7. Recommendation

Build **C1**: per-piece bank selection among the existing banks, three of sixteen, with no palette write. It
satisfies the rule by construction rather than by argument, keeps the engine change to a few instructions, gives
a reusable interface for any future actor, and its only cost is measured colour fidelity. Record the fidelity
table as the evidence, and keep C2 as the option to revisit if the owner finds the shift unacceptable.

## 8. What the owner chose, and what is measured now (2026-10-12)

Section 7's recommendation is SUPERSEDED. The owner chose neither C1 nor C2 as written: **three written banks,
one joint triple for the whole character, written once after the scene constructor, chosen at RUNTIME from the
banks free at that moment, with a coded 16-colour fallback when fewer than three are free.** The ROM palette
table at file 0x05652C is never written, and no other actor's colours may change.

Measured since, all of it reproducible from the tools named in the toolbelt:

1. **A joint triple exists and is pixel-exact.** 21 source colours across 463 occupied 8x8 cells, banks of
   15/15/15 colours, 106 pieces over the eight frames (10, 9, 13, 13, 16, 15, 15, 15), OAM peak 16 of 128, and
   7,153 of 7,153 opaque pixels round-trip through the packed 4bpp bytes with zero mismatched, zero missed and
   zero overlap. A PAIR is impossible, proved by exact enumeration. Tool: `tools/research/joint_triple_exact.py`.
2. **The emitted artifact.** Three appended 16-halfword palettes, an animation record, and a copied definition
   whose animation count equals the slot pointers it carries. The emitted image differs from its base in 3 bytes
   in the common prefix (the Cell definition-table slot) plus 18,884 appended bytes, and the ROM palette table is
   byte-identical. Tools: `tools/research/emit_triple_port.py`, `tools/research/verify_triple_port.py`.
3. **The definition's leading byte is the ANIMATION COUNT**, not a slot count: sprite 73 has 23 with 23 slot
   pointers, sprite 38 has 22, Cell's retail id 252 has 20. The selector at 0x0800ECDA reads
   `[def + 0x54 + 4*index]` with no bound check, so an actor's animation index is the slot index.
4. **Correction to the earlier detour verdict.** The earlier note in this ticket that appending code and
   detouring to it hangs the engine was measured on an entry veneer that executed its own literal; that was
   fixed afterwards and never re-measured. With the current patcher both the bank-select stub and a zero-byte
   body complete over 1,500 frames with real program counters in the owner scene. Appended code runs from this
   site, so the runtime writer can be installed code rather than a one-shot copy patch.
5. **Where a runtime writer can live.** `tools/research/palette_writer_sites.py` censuses the OBJ palette write
   sites: 23 word-aligned literals hold 0x05000200, 30 Thumb load sites reach them, and the once-per-scene copy
   at 0x0800657C loads 0x0805652C, loads 0x05000200 and calls the IWRAM copy veneer 0x08049144 with r2 = 0x200.

Still owed, in order:

1. the palette writer itself: take the bank already in r7 after the bank-select body, compute the destination
   `0x05000200 + 32*bank` and the source `palette_table + 4*bank`, and copy 32 bytes through 0x08049144. Every
   opcode is asserted against a disassembly before it is used (the project's rule after a byte-reversed halfword
   hung five variants);
2. the coded 16-colour fallback for the moment fewer than three banks are free;
3. the runtime comparison: Cell's colours on screen against Legacy of Goku II, with the outside-Cell pixel
   difference and the before/after bank census;
4. the chain that turns the emitted image into a runnable one, pinned by digest rather than by a path in another
   worktree.
