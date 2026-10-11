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
