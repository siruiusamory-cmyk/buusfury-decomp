# Dialogue records and their control codes

Read from the canonical image, byte by byte. GBA address = file offset + `0x08000000`. Canonical ROM sha256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

This is the catalogue a text tool needs: what a record is, where its text comes from, which halfwords are
instructions, and which of those instructions are positional.

**No decoded game text appears in this document.** A dialogue record is identified by its site and its length.
The decoder can print the characters when it is pointed at an image, but nothing transcribed is committed.

## The handle, taken from the project's proven decoder

The packed handle's layout is **not re-derived here**. It comes from `tools/webfoot/handles.py`
(`unpack_handle`), which the shipped releases already validate and which DIALOGUE-VARIABLE-LENGTH-001
documents:

| bits | width | meaning |
| --- | --- | --- |
| 21 to 31 | 11 | decoded **length**, in halfwords (up to `0x7FF`) |
| 6 to 20 | 15 | decoded **start**, in halfwords (up to `0x7FFF`) |
| 0 to 5 | 6 | container **selector** |

The copier `0x08012230` takes the length at `0x08012252` (`lsrs #0x15`) and the start at `0x08012256`
(`lsrs #0x11` after `lsls #0xB` at `0x08012254`), unpacks the container, copies the span into a 64 KiB scratch
buffer and writes the NUL itself at `0x08012272`. Containers hold no terminator, so a tool must never write one
and must rewrite the handle whenever the span's size changes.

The container table's base literal sits at file `0x123CC` and holds `0x087B5B64`; the copier indexes it with
**the selector times four**, so an entry is at `base + 4*selector`. Multiplying by four twice reads the wrong
container, which is a defect this catalogue's first revision carried and which the review caught: it sent 2,437
of 2,936 records to the wrong container.

## The record is eight bytes, and the portrait is a FIELD

| offset | size | meaning |
| --- | --- | --- |
| `+0x00` | u16 | next-index: the page chain |
| `+0x02` | u8 | kind, `5` = dialogue |
| `+0x03` | u8 | **PORTRAIT OPERAND** |
| `+0x04` | u32 | packed container handle |

**There is no portrait code and no speaker code.** The portrait is the record's `+0x03` byte, read at
`0x080122A6` and passed to the box constructor as its third argument. The dialogue path never writes a name. The
only code in the image that joins a portrait to a name is the character panel at `0x08025056`, through the
appearance table `0x0874D380`, and that join is by value. A tool that shows a speaker is inferring it.

The portrait operand, from the constructor's own instructions:

| operand | effect |
| --- | --- |
| `7` | layout index 1; a null portrait pointer |
| `0` | layout index 0; a null portrait pointer |
| `1` to `6` | party: read the SAVE (`0x03001068`, index at `+0x68*slot+0x50C`), then `0x086B82EC + 24*index + 0x0F + operand`, which indexes the portrait array. Save-dependent, so not statically resolvable |
| `8` and above | indexes the portrait array `0x086F393C` directly, with no clamp and no null test |

KIND is a dispatch table, eight odd Thumb pointers at `0x080728AC` (the base is taken at `0x080124FA`):
kind 0 `0x080123E9`, 1 `0x0801240B`, 2 `0x0801241D`, 3 `0x08012465`, 4 `0x080123FB`, 5 `0x0801242D`
(dialogue), 6 `0x0801243B`, 7 `0x0801244B`. This is the only per-record dispatch in the engine.

`0x6BCE8` is the STRING STORE, 1,534 slots of UTF-16LE NUL-terminated strings. Character names live there, which
is why a name slot write targets it; dialogue text does not.

## The corpus, measured with the proven decoder

Records identified by the kind byte inside the event-resource pool `0x0877C5A4..0x0879B704`: **2,936** words,
of which **2,786 decode** and **150 do not**, carrying **223,420 units** in total.

| unreadable reason | records |
| --- | --- |
| the handle names a **zero length**, which is not a legal record | 33 |
| the selector's table entry is **not a container pointer** | 117 |

The second group is the interesting one: a kind byte alone does not prove a record, so part of the 150 are
almost certainly words that merely look like records, and part may be records whose selector the table does not
cover. **Falsifier:** an inventory that identifies records by their resource site rather than by a byte match;
if it yields fewer than 2,936, the difference is the false positives, not the table.

## The control codes

The parser recognises a code by **EQUALITY** against specific halfwords, not by a range, a table or a high bit.
Everything else is a glyph code. Sites: fitter `0x0803DE6A` (`0x00` `0x20` `0x0A` `0x0B` `0x08` `0xFF`),
dispatcher `0x0800AE00` (`0x0A` `0x08` `0x2D`), constructor `0x08012012` (`0x21` `0x40` `0x23`, first unit
only), reveal loop `0x0800B046` `0x08` and `0x0800B16E` `0x5E`, rasteriser `0x0803F444`.

Counts over the 2,786 readable records, with the number of records where the code is the FIRST unit:

| value | arguments | meaning | occurrences | leading |
| --- | --- | --- | --- | --- |
| `0x0000` | 0 | terminator, written by the copier | never in a container | |
| `0x0008` | **1** | ink: writes the argument to the strip ink byte | 360 | 47 |
| `0x000A` | 0 | line break | 118 | 0 |
| `0x000B` | 0 | page flag; **not** an end of record | 314 | 0 |
| `0x0020` | 0 | break point, skipped when leading | 38,669 | 27 |
| `0x0021` | 0 | box position 0x28, **first unit only**; also the glyph `!` | 3,813 | 246 |
| `0x0023` | 0 | box position 0x78, **first unit only**; also the glyph `#` | 82 | 62 |
| `0x002D` | 0 | hyphen join: skipped, following spaces eaten | 243 | 4 |
| `0x0040` | 0 | box position 0x50, **first unit only**; also the glyph `@` | 19 | 10 |
| `0x005E` | 0 | pre-reveal marker, first unit only | 5 | 1 |
| `>= 0x00FF` | 0 | fixed advance class (12), indexes nothing | not reached in retail | |

The positional rule is measured by the constructor's own first-unit comparisons, and it matters because
`0x21`, `0x23` and `0x40` are also ordinary glyphs with real widths:

* a record whose text should start with `!`, `#` or `@` silently becomes a box command and loses the character;
* any text a writer inserts **before** a leading command destroys it, and the box keeps its default position.

**Flow, choice, input wait and sound are NOT text units.** Those live in the dialogue state machine and the
other seven kind handlers.

## The byte-to-glyph path has no transformation

The stored halfword **is** the glyph code. The font descriptor at file `0x6EE6C` is `{0x0806E05C, 11, 0}`, a
two-level table: code to record offset in u16 units, then the record's width, and advance = width + 1. Codes
below `0x20` map to a zero offset, so they draw nothing and advance 1.

## Layout records

Stride `0x14`, fields as lines per page, wrap limit, text x, first y, box art container:

| index | record | lines | limit | x | y | art |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | `0x08071730` | 4 | **144** | 8 | 15 | `0x08071758` |
| 1 | `0x08071744` | 2 | **128** | 16 | 30 | `0x08071A6C` |

Index 1 is chosen **only** when the portrait operand is exactly 7 (`0x08012106`), written to
`text_object+0x4C` at `0x0800B29E`; the fitter reads the limit from `[[obj+0x4C]+4]`. The same operand decides
the box art and whether the surface widens: with a portrait the builder sets the surface to 224 px
(`text_object+0x54 = 0xE0`), decodes the 64x64 portrait into the surface's own buffer, copies that block to OBJ
VRAM at `0x06010000 + slot*32`, and restores the `0xA0` stride. **No palette is written on that path.** The
portrait's pixels resolve through the scene's own 256-entry OBJ bank.

## What a tool must not do

1. **Move or pad text before a leading command.** `0x21`, `0x23`, `0x40`, `0x5E` are positional.
2. **Separate `0x08` from its one argument unit.** Every occurrence in the corpus carries exactly one; a glyph
   between them becomes the ink value.
3. **Treat `0x0B` as the end of a record.** 314 occurrences, and records carry units after one.
4. **Write `0x0000`.** Containers hold none; the copier writes it. Inserting text means rewriting the handle.
5. **Write into a shared container span in place.** Handles share containers, so an in-place write corrupts
   neighbours.
6. **Think the portrait is a text code.** It is a record byte, and changing it changes the layout index, the
   wrap limit, the art, the surface width and the cell geometry.
7. **Assume a party operand is resolvable.** `1` to `6` read the save.
8. **Emit a value at or above `0x00FF`.** Nothing in retail does, and at `0x1D9D` it draws nothing.
9. **Re-derive the handle.** Use `tools/webfoot/handles.py`. Reading the field from the second of two shift
   instructions, or multiplying a selector that is already a byte offset, are both defects this catalogue's
   first revision carried.

## Open

1. The visible difference between `0x0A` and `0x0B`: proven is that the fitter returns differently and that
   `text_object+0x20` becomes non-zero; NOT proven is whether the units after a `0x0B` are drawn on a following
   page, scrolled, or dropped.
2. Which consumer reads `text_object+0x60`, the leading box command's target, and whether it moves the box art
   rather than the text.
3. Which of the 150 unreadable words are false positives, settled by an inventory keyed on the resource site.
4. Whether the `0xFF` class is ever executed at all.

## The tool

`tools/research/dialogue_codes.py`, read-only, and every function takes bytes:

```
python -m tools.research.dialogue_codes --image <image> --site 0x0877D914   # one record
python -m tools.research.dialogue_codes --image <image> --corpus            # counts over the pool
```

It prints the record fields, the proven handle split in halfwords and bytes, the layout the operand selects,
the unit count and the code histogram; `--events` adds the event list, and `--json` the whole report.
`tests/unit/test_dialogue_codes.py` drives the decoder with synthetic records and spans and needs **no ROM**.
