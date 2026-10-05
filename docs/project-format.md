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
  graphics/assets/        7,390 indexed PNGs, one per distinct payload (TOOLKIT-010)
  sprites/sprites.toml    one new actor-sprite identity, and its actor
  sprites/**/*.png        the source sheets that identity is drawn from
```

One file per table rather than per record: 141 single-record files would be a
worse Git experience, not a better one. Only the supported content types get
directories - no empty directories are reserved for systems that do not exist.

`text/strings.toml` is written only when the verified profile declares a string
table, and a project without it simply authors no text. All 1,534 strings share
one file rather than being split per scene, because nothing yet knows which
scene a string belongs to and inventing a grouping would mean inventing facts.

Graphics are the bulk of an extraction - 7,390 PNGs, one per distinct container
offset reachable by a piece, against a few dozen TOML files, measured at 44.0s
versus 1.8s on the canonical image - so
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
would turn 7,390 real payloads into 11,005 fictional ones and would make a global
edit look local. The object palette travels as raw GBA 15-bit words, never as
RGB, because an 8-bit triple cannot round-trip to a unique word.

**Editing a PNG is how a project authors pixels, and the build consumes it.**
Each manifest asset also records the digest of the PNG extraction wrote
(`png_sha256`) and of the indices it encoded (`pixels_sha256`). An asset whose
file no longer matches its recorded digest is an authored override: the build
decodes it, refuses anything that is not the indexed form, refuses a changed
dimension or an index above the piece's bit depth, and plans the result through
the same `GraphicsOverrides` surface the palette overrides use. There is no
registration step and no separate command - `extract`, edit the PNG, `validate`,
`build` is the whole workflow, and one resolver runs in both `validate` and
`build` so the two cannot disagree about which graphics a project authors.
Palette and pixel edits merge into the one write plan, so neither can overwrite
the other.

A re-encoded payload that fits the extent its original container occupied is
written in place, and the bytes between the new payload and the end of that
extent are left untouched rather than rewritten. A payload that does not fit is
placed by the allocation authority and every confirmed reference to the old
payload is rewritten in the same batch; the original bytes are left intact, so a
reference this toolkit did not discover still reaches the art it always reached.
`docs/research/GRAPHICS_PIXEL_OVERRIDE.md` records what is proven about that
boundary, including the one property it leaves `UNKNOWN`.

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
text needs relocation, which needs profile-declared free space. Buu's Fury declares
one small verified region (`[0x007EA400, 0x007EA500)`, 256 bytes, TOOLKIT-028),
which is far too small to relocate a text pool, so canonical growth is still
refused with the exact byte deficit. The relocation machinery itself is proved on synthetic fixtures.

**Repeated text is not shared text.** 153 texts occur more than once, but each
occurrence has its own bytes, so editing one changes only that one.

## New actor sprites

SPRITE-NEW-PROJECT-SURFACE-001. A **new actor-sprite identity** is content the
canonical image does not contain: a sprite the engine answers to by an id it has
never had, plus the one map actor that draws it. `sprites/sprites.toml` describes
exactly one, and the sheets it draws from are PNGs beside it.

```toml
[sprite.cui]
sprite_id = 307
donor_sprite_id = 10
free_palette_entries = [8, 9, 103, 193, 236]

[sprite.cui.animation.stand]
sheet = "sprites/cui/stand.png"
frames = 2

[sprite.cui.animation.walk]
sheet = "sprites/cui/walk.png"
frames = 4

[sprite.cui.actor]
map = "map:0102"
family = "map-sibling-08017da3"
position = [209, 580]
retained_raw = 0
data_pointer_raw = 142104172
behaviour_template = "map:0102/object:0007"
wander_box = [192, 544, 272, 624]
```

- **Exactly one identity per build, and that is a property of the image.** An
  identity is added by growing the character registry and repointing the two
  literal words that name it, so a second identity in one build would grow the
  same registry again and point the same two words at a different table. A
  document declaring two is refused rather than half-applied.
- **`sprite_id` is stated, not derived.** The engine id an identity answers to is
  the id its appended registry entry yields, and the planner accepts exactly that
  number; stating it is what keeps a build from silently attaching an actor to an
  id this build did not author.
- **`donor_sprite_id` names an identity the image already contains, and it
  supplies both the geometry and the shape.** Its character-structure header is
  cloned and its first frame supplies the geometry every authored frame copies -
  placement offsets, pixel extents and packed OAM attributes. Before that, every
  frame of every animation slot the donor structure names is decoded (a slot whose
  animation word is null names no record and is skipped) to measure the one frame
  rect the donor proves: `width x height`, its anchor, its pixel count and its
  piece count (`sprite_identity.measure_donor_envelope`). A donor whose own frames
  occupy more than one rect, or one rect at more than one anchor, proves no single
  shape or placement and is refused, and every sheet cell must be exactly the
  measured rect. A larger cell is a composition shape this build cannot prove and
  a smaller one would need a placement nothing has measured, since the authored
  frame copies the donor's own anchor; both are refused. The docstring of
  `sprite_identity.plan_new_sprite_identity` and
  `docs/research/SPRITE_NEW_COMPOSITION_GUARD.md` carry the measurement.
- **Animation slots are ordered by name.** A TOML table has no order to inherit,
  and the engine reads an animation by its slot index, so the order is a stated
  rule: `stand` precedes `walk`, and a build emits them in that order.
- **A sheet is one row of square cells in four facing groups**, `frames` of them
  per facing. The file's own width states the same count, so a sheet whose
  dimensions and declaration disagree is refused instead of resolved by
  preferring one. Eight-bit RGB and RGBA are both accepted; a fully transparent
  pixel is a hole and becomes the transparent entry, and a partly transparent one
  is refused because a sprite pixel is one palette index. The hole a sheet draws
  in colour rather than in alpha is `(255, 0, 255)`: that is the chroma key the
  planner uses, a fully transparent pixel's colour is normalised to it, and a
  pixel that is that colour is a hole whether the sheet meant it or not.
- **`free_palette_entries` is the author's claim, and it is checked.** The SDK
  decodes the actor-sprite graphics but not every payload that shares the 256-entry
  object palette, so it cannot derive which entries are free; it verifies the
  claim against what it can prove - no decoded actor-sprite graphic draws a
  requested entry - and refuses an entry that fails rather than recolouring
  another asset.
- **The actor is authored, carried or resolved, and the three are kept apart.**
  `map`, `position` and `wander_box` are authored. `retained_raw` and
  `data_pointer_raw` are the new object header's `+0x04` and `+0x0C` words, whose
  meanings are UNRESOLVED: they are stored as the raw words they are, carried
  verbatim, and never dereferenced. `behaviour_template` names an existing slot of
  the **same** map's object array; the build copies that record's inline behaviour
  entry and writes the authored wander box into it, so the actor starts from a
  behaviour the engine already runs on that map. A ROM address is not an
  authoring API and is never accepted here.
- **Two combinations are refused because only one writer can win.** The actor's
  plan re-emits that map's `MapEntry` record and object array, so a project that
  also edits that record's fields, or gives that map an authored placement
  expansion, is refused rather than silently dropped or reported later as a
  byte-range overlap.

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
  project omits;
- for a new actor sprite: every source sheet (present, the accepted PNG form, the
  declared frame count), every claimed free palette entry against the decoded
  corpus, the behaviour template against its map's own object array, and both
  placements. Validation runs the same materialization the build does, so the two
  cannot disagree about what may be authored.

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
