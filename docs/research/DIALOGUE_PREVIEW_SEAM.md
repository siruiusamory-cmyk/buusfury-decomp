# The dialogue preview seam: what the engine actually does

Written for the text tool's preview by the session that measured the engine, so the preview draws what the
game draws. Every number is measured - from the ROM bytes or from native 240x160 captures - and the source
of each is named. Nothing here is inferred from a document.

## Glyphs

- The font is reached through a 12-byte DESCRIPTOR at file `0x6EE6C`: `{u32 table, u16 wide_advance,
  u32 wide_base}` = `{0x0806E05C, 11, 0}`. The descriptor's own address is NOT the table.
- The table at file `0x6E05C` is 256 `u16` code -> record offset in `u16` units, indexed by the RAW code,
  followed by the records. A record is `u16 width` then `width + 1` `u16` columns: column k is pixel column
  k, bit r of a column is pixel row r with row 0 at the TOP, 16 rows.
- ADVANCE = stored width + 1. Codes below `0x20` have no record: nothing drawn, advance 1. Codes at or
  above `0xFF` take the fixed class (advance `wide_advance + 1` = 12, no glyph).
- Population: 224 records, 150 with ink, 74 blank, 32 absent. Glyph codes are the text's own UTF-16 units.

## Layout

- Text origin `(8, 3)` in the surface's own coordinates; line spacing **14** pixels, not the 16 the cell
  arithmetic suggests; the glyph cell is 16 rows tall.
- The surface is 160x64, one byte per pixel, stride `0xA0`, and it IS the container at file `0x71758`
  (or `0x71A6C` for the other layout): a capture matches it at 9,723 of 10,240 pixels, the rest being the
  text painted over it.
- INK is an 8bpp palette index. The dialogue path paints **index 2**, which is white in the object palette.

## Line breaking - the part a preview gets wrong

- Greedy **word** wrap (`FUN_0803DE6A`): it skips spaces and `0x0A`/`0x0B`, accumulates each glyph's
  advance, and compares the sum against a limit passed in by the caller (`0x0803DEE4 cmp r4,r2`). On
  overflow it breaks at the LAST SPACE it saw, so a trailing space is never drawn.
- THE LIMIT IS NOT A CONSTANT. `FUN_0800AE74` passes `[[text_object+0x4C] + 0x04]` (`0x0800AF12`,
  `0x0800AF32`); the whole ROM holds exactly TWO such layout records:
  - `0x08071730`: limit **144**, art container `0x08071758`
  - `0x08071744`: limit **128**, art container `0x08071A6C`
  A `-0x14` reduction exists at `0x0800AF30` and needs `FUN_0800AE00` non-zero AND `[text_object+0x28] == 0`;
  no capture has shown it, so treat **108 as unconfirmed**.

## The box scrolls

- The box draws a WINDOW of the record, not necessarily its first character. TWO captures were
  reproduced pixel-exactly only with the window starting part way in: **159 characters** into one record and
  **75** into another.
- Consequence for a preview: a long record cannot be previewed correctly by always starting at character 0.
  The scroll-advance rule is NOT established yet; this document will carry it when it is.

## What "correct" was checked against

- 12 of the 13 captures that contain a dialogue box are reproduced PIXEL-EXACT: zero engine ink pixels
  missed, zero pixels drawn that the engine did not. The 13th (`shot-3300`) is open and described in the
  tracker; a preview that reproduces the 12 is reproducing the engine, not an approximation of it.

## Provenance of the captures, stated plainly

The captures were taken of the **modified** image the release 4A work built (`v4a-broly.gba`, recorded in
the capture directory's `inputs.json`), while the font, the box art and the dialogue corpus are decoded
from the **canonical** retail image. Release 4A changes byte fields only and appends a region; it does not
touch the font table or the box containers, but the validator checks neither image's identity, so a
reviewer should read "the modified image draws this line the way the canonical font says" as measured for
those captures, not as a general proof about the canonical image.

The one capture that still differs, `shot-3300`, has a TWO-SIDED residual as the tracked tool prints it:
149 engine ink pixels the render misses and 148 the render draws that the engine does not, at limit 144. An
earlier note here called it one-sided; that was a different search's output, and the tool's numbers are the
ones above.

## Which layout record a box takes: the operand-7 rule

MEASURED from the code, and consistent with the two limits a runtime probe logged.

The text object's layout pointer is written at `0x0800B29E` inside the text-object builder, from its first
stack argument:

```
0800B290  ldr r0,[sp,#0x38]     ; the builder's FIRST STACK ARGUMENT = the layout index
0800B292  ldr r1,[0x0800B310]   ; the style base (pool word 0x08071720)
0800B294  lsls r3,r0,#2
0800B296  adds r0,r3,r0         ; index * 5
0800B298  lsls r0,r0,#2         ; index * 0x14   (a layout record is 20 bytes)
0800B29A  adds r1,#0x10         ; records begin 0x10 into that base
0800B29C  adds r0,r0,r1         ; layout = 0x08071720 + 0x10 + index*0x14
0800B29E  str r0,[r4,#0x4C]     ; text_object+0x4C = the layout
0800B2A2  ldr r0,[r0,#0x10]     ; layout+0x10 = the box ART container
0800B2A4  bl 0x0803D940         ; decode that art into the surface
```

The index is chosen by the dialogue box constructor `0x08012012` from the record's portrait operand:

```
08012104  movs r0,#0            ; default: index 0
08012106  cmp r6,#0x7
08012108  bne  0x0801210C
0801210A  movs r0,#1            ; index 1 ONLY when the portrait operand is exactly 7
08012148  str r0,[sp,#0x0]      ; first stack argument -> the builder's [sp+0x38]
```

**The rule: layout index 1 if the portrait operand is exactly 7, otherwise 0.** Operand 0 also means "no
portrait" but takes index 0, so what selects the second layout is the OPERAND VALUE, not whether a portrait
is drawn. Operands 1..6 (party) and 8 and above (array) all take index 0.

| index | layout | limit | box art |
| --- | --- | --- | --- |
| 0 | `0x08071730` | **144** | `0x08071758` |
| 1 | `0x08071744` | **128** | `0x08071A6C` |

Both confirm the runtime probe, which logged `limit=144 layout=0x08071730` for an ordinary box and
`limit=128 layout=0x08071744` for the other. A preview must apply the limit AND the art of the layout the
record's operand selects, not one of them.

### Runtime evidence for the rule

Logged from the owner's own savestate, which is a dialogue section with a box already on screen. The probe
records the operand site and the layout store, and the launcher now marks the moment the savestate loads, so
every line below is attributable to the loaded scene rather than to an instrument that never got there.

```
NOTE frame=0 STATE loaded
OPERAND frame=345 record=0x0202BB0C
LAYOUT  frame=346 layout=0x08071730 index=0 text_object=0x0203D750
FIT     frame=354 limit=144 layout=0x08071730 layout_limit=144 flag=0
OPERAND frame=641 record=0x0202BB0C
LAYOUT  frame=642 layout=0x08071730 index=0
OPERAND frame=885 record=0x0202BB0C
LAYOUT  frame=886 layout=0x08071730 index=0
OPERAND frame=1130 record=0x0202B274
LAYOUT  frame=1131 layout=0x08071730 index=0
OPERAND frame=1244 record=0x0202B274
LAYOUT  frame=1245 layout=0x08071730 index=0
OPERAND frame=1334 record=0x0202B274
LAYOUT  frame=1335 layout=0x08071730 index=0
```

**Settled:** six box events, two different records, every one took **index 0 → layout `0x08071730` → limit
**144**. The default branch of the rule is therefore observed at runtime, and the two limits the fitter
received match what the layout records hold.

**Not settled:** the `index 1` branch. No box whose portrait operand is 7 appeared in that scene, so
`operand 7 → limit 128 + art 0x08071A6C` still rests on the code alone. The operand byte the channels
logged came from an EWRAM copy of the record whose `+3` is not the operand, so the log carries the LAYOUT
per box rather than the operand; capturing the operand is the parked owner tap (one box of that kind).
