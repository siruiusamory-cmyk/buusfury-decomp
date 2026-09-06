# Buu's Fury Text Format

Profile `buus_fury_usa_rev0_01c1707f`, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

Evidence labels follow `docs/DEVELOPMENT.md`. Every `CONFIRMED_ROM` claim below was
established by reading the canonical image directly and is reproduced by the
tests named in each section - not taken on an upstream project's word.

## Upstream audit, performed first

`yoav74/BuusFuryToolkit` (pinned `4353f6a23aa4ac980f1ed42a2c65bc281fa45cc7`) is
the only upstream with text tooling. What it actually contains:

- `Findings.txt`, in full: `On Screen Dialog - First Line - 0202CF10` and
  `Rom Dialog - 00057920/80057920`. One address, no structure.
- `PyFiles/DialogFinder.py`: a Tk GUI that finds text by **heuristic linguistic
  scanning** from a user-typed start offset - it walks the image two bytes at a
  time, keeps runs whose second byte is `0x00`, and filters the results by vowel
  count, alphanumeric count and bracket count. Edits are written in place, capped
  by counting trailing `00 00` pairs.
- `Buu's Fury.tbl`: an 88-line hex-to-character map that is essentially ASCII,
  including a `00=space` line its own loader deletes at runtime before use.
- `Extracted Text.txt`: 3,307 lines of that scan's output. Its tail is visibly
  garbage (`[FA][96]G`, `[AB]\nY`), which is the heuristic's false-positive rate
  made visible.

`VERIFIED_UPSTREAM`: text exists near `0x57920` and each character occupies two
bytes. That is the entirety of what upstream establishes.

`Arefu/Legacy` contains a `DBZKit/Assets/Dialog.cs`, but its detector evidence
covers `ALFE` (Legacy of Goku II) only; per `docs/upstream-audit.md` its findings
must not be promoted to Buu's Fury facts. `DragonByteZ` and `2genkidev/buusfury`
carry map, graphics, audio and compression knowledge, and no string-table
knowledge. No upstream describes a pointer table, a string count, or an extent.

Everything below is this project's own work.

## Encoding

`CONFIRMED_ROM`. The pool is **UTF-16LE**: each character is a 16-bit
little-endian unit, and the terminator is the unit `0x0000`. Strings are packed
contiguously with no padding or alignment between them.

Decoding a unit as a Unicode codepoint is correct, so **no custom character
table is required** and the upstream `.tbl` is redundant. The proof is unit
`0x00E9`, which occurs exactly once in the pool and is the accented `e` in
`Hercule Cafe` - a game-specific glyph map would have no reason to place the
acute-e at Latin-1's codepoint for it.

The upstream `.tbl`'s `00=space` entry is simply wrong: `00 00` is the
terminator.

## Control codes

`CONFIRMED_ROM`, by exhaustive census over all 1,534 strings.

| Unit | Count | Meaning |
|------|-------|---------|
| `0x0008` + one operand unit | 100 | style/colour select, operand **not decoded** |
| `0x000A` | 24 | newline |

`0x0008` is always a prefix: it is followed by exactly one further unit in every
occurrence and never appears as a string's last unit. Observed operands are
`0x02` (40), `0x05` (30), `0x76` (12), `0x03` (8), `0x06` (6), `0x07` (3) and
`0x1D` (1). Their semantics are `UNKNOWN` and are deliberately not guessed; the
codec preserves the operand verbatim.

Apart from those and the single `0x00E9`, every unit in the pool is printable
ASCII `0x20`..`0x7E`.

`printf`-style formatting is **in-band text, not control data**: `%d`, `%s` and
`%02d` appear literally as the ASCII bytes `0x25 0x64` and so on. They are
ordinary characters and round-trip as such.

Eleven of the 1,534 strings are empty (an immediate terminator), including index
0. An empty string is legal and must survive a round trip.

## Pool and pointer table

`CONFIRMED_ROM`.

| Region | File offset | Size |
|--------|-------------|------|
| String pool | `0x0005792C` .. `0x0006BCE6` | 82,874 bytes |
| Pointer table | `0x0006BCE8` .. `0x0006D4DF` | 1,534 entries, 6,136 bytes |

The table holds 1,534 little-endian GBA addresses (`0x08000000`-based) into the
pool. Two structural properties were verified and are the reason this subsystem
can claim a *complete* round trip rather than a sampled one:

- **Exhaustive tiling.** For every `i`, the end of the string at `ptr[i]`
  (terminator included) equals `ptr[i+1]` exactly. Zero gaps, zero overlaps. The
  table therefore describes the pool's entire extent, and every byte from
  `0x5792C` to `0x6BCE6` belongs to exactly one enumerated string.
- **No aliasing.** All 1,534 targets are distinct and strictly ascending. No two
  entries share a payload in this table, so an edit cannot silently change an
  unrelated line, and a no-op build cannot split or duplicate a shared string.

The two bytes between the last string's text and the table (`0x6BCE6`) are that
string's terminator. The table is followed by `0x00` padding.

## Shared strings

`CONFIRMED_ROM`. **Text is duplicated in content, never shared in storage.**

153 of the 1,264 distinct texts occur more than once. The extremes are
`"A crate with Hercule's logo on it."` at 25 occurrences and
`"A crate with a Z logo on it."` at 15; roughly 15,726 bytes of the pool are
occupied by repeated content.

Every occurrence has its own offset and its own bytes - the same fact as the
strictly-ascending, duplicate-free pointer list above, approached from the
content side rather than the pointer side.

This settles the edit semantics without needing a clone operation: editing one
occurrence changes only that occurrence. A tool that assumed sharing would
either wrongly rewrite all 25 crate lines at once or wrongly refuse the edit.

## Reference topology

`CONFIRMED_ROM`, and the finding that shapes the whole design.

- The **pool base** `0x0805792C` has exactly **one** word-aligned inbound
  reference in the entire 8 MiB image: the pointer table's own first entry.
- The **table base** `0x0806BCE8` is referenced from **51** word-aligned sites in
  code.

Access is therefore **by index into the table**, never by a direct pointer to a
string. Consequences:

- Relocating one string rewrites exactly **one** word - its table slot.
- Relocating the table itself would require rewriting all 51 base references.

Exactly **5** word-aligned words elsewhere in the image coincidentally equal a
string's start address (`0x2DD7B4`, `0x30C5DC`, `0x5A51B4`, `0x67907C`,
`0x6C8040`). All five sit inside compressed graphics data, and their neighbouring
bytes are plainly not pointers. They are classified `CANDIDATE_REFERENCE` and are
`INFERRED` to be coincidence; they are never treated as authoritative.

## Free space

`UNKNOWN`, unchanged from TOOLKIT-003. No verified free region is declared for
this profile, so **canonical growth and relocation remain blocked**. Per
`ARCH-TOOL-001`, free space is profile-declared with recorded evidence and is
never inferred by scanning for `0xFF` or `0x00` runs: a scan cannot distinguish
padding from data and yields different answers on an already-edited image,
destroying build reproducibility.

In-place canonical edits that fit the original allocation are supported.
Relocation behaviour is proved on portable synthetic fixtures instead.

## Open questions

- Semantics of each `0x0008` operand (`UNKNOWN`; preserved opaquely).
- Whether other text exists outside this table - the debug/assert strings visible
  around `0x08008A72` and `0x0803E024` are plain ASCII and are **not** part of
  this pool or table. They are out of scope for this ticket.
- Which table index each script/consumer site uses (`TOOLKIT-005` territory).
