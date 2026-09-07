# Webfoot Project Format

TOOLKIT-002. A mod is a directory of text under version control, not a sequence
of edits applied to a binary.

## Lifecycle

```
webfoot extract <rom> <project-dir>
webfoot validate <project-dir> --rom <base-rom>
webfoot build <project-dir> --rom <base-rom> --output <output-rom> [--manifest <path>]
```

The base ROM is an input on every path and an output on none. A build always
writes a new image and refuses to overwrite an existing one.

## Layout

```
project/
  project.toml            identity: format version, profile, base ROM hash
  enemies/enemies.toml    141 enemy stat records
  characters/characters.toml   9 playable-character base-stat records
  text/strings.toml       1,534 strings                      (TOOLKIT-004)
  graphics/graphics.toml  sprite asset manifest + object palette (TOOLKIT-010)
  graphics/assets/        7,355 indexed PNGs, one per payload (TOOLKIT-010)
```

One file per table rather than per record: 141 single-record files would be a
worse Git experience, not a better one. Only the supported content types get
directories - no empty directories are reserved for systems that do not exist.

`text/strings.toml` is written only when the verified profile declares a string
table, and a project without it simply authors no text. All 1,534 strings share
one file rather than being split per scene, because nothing yet knows which
scene a string belongs to and inventing a grouping would mean inventing facts.

Graphics are the bulk of an extraction - 7,355 PNGs against a few dozen TOML
files, measured at 44.0s versus 1.8s on the canonical image - so
`extract_project(..., graphics=False)` (CLI: `extract --no-graphics`) omits them
for anyone editing stats or text. A build from such a project is **still
byte-identical**, because unchanged graphics are re-emitted from the base image
rather than from the project. The flag costs authoring reach, not correctness.

`graphics/` is the one content type written as **files plus a manifest** rather
than as a single table, because pixels are not text: an indexed PNG is what an
image editor can open, and one file per asset is what makes an edit reviewable.
The manifest carries what a PNG cannot - the dimensions the *piece* record
declares, the bit depth, the packed extent an edit is bounded by, and the list of
characters a change would affect - so none of that has to be inferred from the
image. A shared payload appears **once**: writing a private copy per consumer
would turn 7,355 real assets into 10,959 fictional ones and would make a global
edit look local. The object palette travels as raw GBA 15-bit words, never as
RGB, because an 8-bit triple cannot round-trip to a unique word.

Build outputs (`.gba`, manifests) are artefacts and belong outside the authored
tree; the repository `.gitignore` already excludes them. Extracted PNGs are
ROM-derived and are likewise never committed.

## `project.toml`

```toml
[project]
format_version = 1
name = "buus_fury_usa_rev0_01c1707f"

[base]
profile_id = "buus_fury_usa_rev0_01c1707f"
game = "buus_fury"
sha256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
size = 8388608
```

`sha256` is the contract: a build against any other image fails closed.
`profile_id` is checked independently, because a matching hash with mismatched
table extents would still be wrong.

**No filesystem path is recorded.** A path is a fact about one machine, and a
project that pinned one would stop being portable the moment it was cloned.

## Records

The wolf, exactly as extracted from the canonical ROM:

```toml
[enemy.434]
type_id = 434
hp = 175
exp = 225
level = 60
strength = 10
power = 0
endurance = 20
raw = "e1000000af000000b20100003c0a0014808000002089700829117108"
```

- **The table key is the durable identity**, not a table position. Enemy
  identity keys on `type_id`, which DATA-001 verified is unique across all 141
  records. Character identity keys on roster position and remains the weaker of
  the two, carried forward unchanged from TOOLKIT-001.
- **Values are semantic.** No offsets, no addresses. A project that stored them
  would break whenever anything moved and would be meaningless to a future
  decomp backend.
- **`raw` carries the record's undecoded bytes**, verbatim, and is validated
  against the base image on load. Both layouts have spans this project has not
  decoded - 12 bytes of enemy after-battle data, 6 character technique ids, the
  pad bytes - and byte-identical reconstruction requires every one of them. It
  is not intended for hand editing; a missing or tampered `raw` is refused
  rather than defaulted.
- **Enemies carry no alias.** This project has verified names for the 9
  characters and for no enemy, so extraction emits none rather than inventing
  labels that would then read as extracted facts. The slot exists for when a
  source is verified.

## Strings

TOOLKIT-004. Text is variable-length, so it is authored differently from a
fixed-stride record:

```toml
[text."text:0010"]
text = "New Game"

[text."text:0041"]
text = "{08:05}HP:{08:02} {08:76}%d{08:05}/{08:76}%d{08:02}"
```

- **The key is the pointer-table index**, zero-padded to four digits so lexical
  order matches numeric order. It is identity because the game reaches a string
  *through* the table - see `docs/research/TEXT_FORMAT.md`.
- **`{08:XX}` is a control code**, `XX` being the operand byte in hex. The
  operand's meaning is `UNKNOWN` and is preserved rather than named. `{{` is a
  literal brace, so ROM text containing `{08:02}` cannot be mistaken for a
  control code on the way back in.
- **`%d` and `%s` are ordinary text.** The game's formatting is in-band ASCII,
  not control data.
- **Newlines are real newlines**, escaped as `\n` by the TOML emitter.
- **There is no `raw` blob and no address.** A stat record needs `raw` because
  only part of its stride is decoded; the text codec is lossless over the whole
  pool, so the authored string already *is* the complete description of its
  bytes. A second copy could only disagree with the first.

**Editing is in-place.** The pool is exhaustively tiled, so a string has no slack
to grow into: replacement text must fit the original allocation, and shorter text
is zero-padded to it deterministically rather than repacking the pool. Longer
text needs relocation, which needs profile-declared free space - and no verified
free region exists for Buu's Fury, so canonical growth is refused with the exact
byte deficit. The relocation machinery itself is proved on synthetic fixtures.

**Repeated text is not shared text.** 153 texts occur more than once, but each
occurrence has its own bytes, so editing one changes only that one.

## Determinism

Given the same project files, the same verified base ROM and the same toolkit,
the output ROM is byte-identical across repeated builds. This is asserted, not
assumed:

- records are ordered by durable identity, never by table position or by
  filesystem traversal order;
- files are written LF and end with exactly one newline, so extraction does not
  depend on which machine ran it;
- authored files and build manifests contain no timestamp, path, hostname,
  username or random value.

Writing is a small in-repo TOML emitter rather than a dependency: Python's
stdlib `tomllib` parses TOML but does not serialize it, the authored schema is a
closed set of integers and short strings, and key order, integer formatting and
quoting all have to be ours for determinism to be a property we can test.

## Build manifest

```json
{
  "schema_version": 1,
  "base": { "profile_id": "...", "sha256": "940ad5f0..." },
  "output": { "sha256": "9e714ca4...", "size": 8388608 },
  "changed_byte_count": 1,
  "changes": [
    {
      "offset": 7412700, "offset_hex": "0x00711BDC", "size": 28,
      "owner": "enemy:434", "reason": "enemy edit: hp",
      "old": "...", "new": "..."
    }
  ],
  "project": { "name": "...", "format_version": 1 }
}
```

Every emitted byte change names the semantic owner responsible, so the manifest
answers *which edit changed these bytes*, not merely *these bytes differ*.

## Validation

`validate` checks, and `build` re-checks before writing anything:

- project schema and format version;
- profile support and base ROM hash/size agreement;
- identity key and `type_id` agreement;
- semantic field ranges (enemy and character `level` cap at 200, from P-010's
  `cmp r6,#0xc8` at `0x08013A00` in the EXP award path);
- `raw` presence, length, and agreement with the base image;
- records the ROM lacks, and records the project omits;
- for text: identity key form and range, encodability (unsupported characters,
  malformed `{08:XX}` tokens, embedded NULs), whether the encoded text fits its
  allocation, duplicate identities, strings the ROM lacks, and strings the
  project omits.

A failure names the offending entity and field. Nothing is written when
validation fails.

## One plan per build

Stats and text produce their changes separately but are validated and applied as
a **single** write plan. Overlap detection is per-plan, so two subsystems in two
plans could each look valid while together writing the same bytes; merging turns
that into a hard error instead of silent last-writer-wins.

## Not in this format

No anchors, pointer graph, relocation, allocator or free-space management appear
in the authored files. Fixed-stride stat records need none of them, and text
relocation stays blocked on Buu's Fury for want of declared free space;
TOOLKIT-003 proves those mechanisms separately.
