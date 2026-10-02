# Resource library curation (RESOURCE-LIBRARY-CURATION-001)

How the canonical Buu's Fury resource library becomes a human-browsable
resource pack, and why each rule is what it is. The curator itself is
`tools/export/buu_resource_curate.py`; this document records the decisions, the
name authority, and the measured deduplication so a later reader does not have
to re-derive them.

## Two libraries, two jobs

The raw library is the extractor's output:
86,444 artifacts named by numeric identity, one per structural record. It is
structural truth and it stays untouched.

The curated library is a separate, human-first resource pack. It keeps every identity the raw library establishes
and stops repeating payloads that several identities share. Every image is a
byte copy of a raw artifact; nothing is re-encoded, rescaled, recoloured or
"cleaned up". Every curated path is tied back to the raw paths it came from in
`Index/Source Map.json`.

## Name authority

Three sources, in strict priority, and nothing else:

1. **ROM-derived names.** A map's `MapEntry +0x0C` low half and an appearance
   definition's `+0x00` resolve through the verified text pointer table. These
   are recorded as ROM text in the raw library's `metadata/names.json`. The
   strings that appear as human-facing names here - `West City`,
   `Buu's House`, `Grand Kai's Planet`, `Babidi`, `Android #18` - come from that
   file, never from the author's head.

2. **Verified LOGExtractor names.** The external tool's animation-slot table is
   `mainant/LOGExtractor` at revision
   `3a78bb35ad181082fbc9da01057538e5a78e8c2d`,
   `CharacterSpriteExtractor/Program.cs` line 21: a 23-entry array read as
   `anim_names[a]` for animation-array position `a`. The canonical corpus never
   declares more than 23 slots on a definition, so the table covers every
   position. The three `unknown*` entries are placeholders, not names.

   **Status is recorded, not promoted.** The accepted project record
   (`docs/PROJECT_STATE.md`, LOGX-SPRITE-001) still classes LOGExtractor's
   slot names as unproven engine facts. Curation uses them in a local resource
   pack where the human has verified them for that purpose, and every animation
   record carries its name source (`LOGEXTRACTOR_SOURCE`) so the distinction is
   never lost. No engine-behaviour claim is made by giving a folder the name
   `Walk`.

3. **Neutral one-based fallback.** Where neither source supplies a name - an
   unnamed map, an unnamed sprite, an animation position the external table does
   not cover - a neutral label is used. Unnamed maps and sprites take a
   contiguous human sequence independent of their canonical id (`Map 1` …
   `Map 23`, `Sprite 1` … `Sprite 99`); an unnamed animation position is
   `Animation 5`. These are labels, not claims: they describe position in the
   corpus, not what the thing is, and the canonical id stays in the metadata.

## Windows-safe human names

`clean_name` keeps normal spacing and punctuation - an apostrophe, a space, an
ampersand, a hyphen inside a real name such as `Z-Mart` - and touches only what
a filesystem cannot represent:

- control characters and the Windows-reserved set `< > : " / \ | ? *` become a
  space;
- trailing dots and trailing spaces are dropped (Windows strips them);
- runs of whitespace collapse and the ends are trimmed;
- an empty result, or a reserved device name (`CON`, `NUL`, `COM1`, `LPT1`), is
  replaced by a neutral label by the caller.

Nothing is lower-cased, title-cased or re-spaced. Case is folded only when two
names are *compared* for collision, never when one is written.

### Two names, one folder

A verified name two canonical resources share becomes a flat one-based group
rather than a collision: the 50 maps carrying `Inside Babidi's Ship` become
`Inside Babidi's Ship 1` … `Inside Babidi's Ship 50`, and the map ids stay in
the index. No id is ever appended to a filename to disambiguate: `West City 1`
and `West City 2`, never `West City 017`.

### Plain one-based ordinals, no padding

Neutral ordinals are written as the number a person reads (`Layer 1`, `Pose 7`,
`Chunk 1`, `Tileset 12`, `Palette 2`), with no zero padding. The canonical
zero-based index stays in the metadata where it belongs; a human-facing name
never carries a fixed-width technical form.

## Curated layout

```text
Maps/<Name>/Map.png
Maps/<Name>/Layers/Layer <n>.png
Maps/<Name>/Map.json
Tilesets/Tileset <n>/Sheet.png
Tilesets/Tileset <n>/Tileset.json
Chunks/Chunks <a> to <b>/Chunk <n>.png
Sprites/<Name>/Sprite.json
Sprites/<Name>/Animations/<Animation>/Sheet.png
Sprites/<Name>/Animations/<Animation>/Poses/Pose <n>.png
Sprites/<Name>/Animations/<Animation>/Animation.json
Palettes/Palette <n>/Palette.png
Palettes/Palette <n>/Palette.json
Technical/Unique Sprite Graphics/Graphic <n>.png
Index/*.json
```

A map keeps one browsable entry per canonical map, even when two maps render the
same composite - a distinct `MapEntry` is what a romhacker looks for, so map
composites and map layers are **never** collapsed. A map 19 composite is a
derived, runtime-provisional artifact; its status is carried structurally, not
in a prose warning.

A tileset's sheet is the primary representation. The raw library's 47,857 loose
8x8 tile PNGs are nearly all distinct and are **not** copied into the curated
view: the sheet holds the same pixels, and `Tileset.json` records every tile's
index and sheet coordinates (index, x, y, column, row), which is enough to
identify or recover an individual tile.

## Deduplication is by rule, not by hash alone

A matching SHA-256 does not mean two identities are the same. The rules are:

- **Shared payload.** A sprite animation sheet whose canonical animation object
  is already written is not copied again; the artifact is attributed to the
  identity that reaches it first in the run's canonical order, and every other
  identity records that path. This is the same source object under two
  identities, so sharing it is safe; each identity still keeps its own record.

- **Direction collapse.** The raw dump emits `frame x direction` outputs, and
  four direction cells of a frame often render identically. Within one
  animation, identical direction renders collapse into one `Pose <n>`, and every
  `(frameIndex, directionIndex)` pair that renders it is recorded in
  `Animation.json`, so the 4-direction relationship is never lost.

- **Uncertainty keeps both.** Two different animation objects that render the
  same pixels stay separate identities with separate poses and separate records.
  First-pass curation does not solve global pixel-equivalence: when in doubt, the
  resource is kept.

- **`sprite_graphics`.** Measured over the canonical corpus, 7,349 of the 7,390
  structured graphics containers already appear byte-for-byte under the
  human-facing sprite tree. Those are indexed but not re-emitted; the 41 that
  exist nowhere else are kept under `Technical/Unique Sprite Graphics/`.

- **Context retained.** Maps, chunks and tilesets are contextual resources and
  are not hash-deduplicated: a chunk that renders like a map layer is still a
  chunk, and a duplicate composite under two map identities is still two maps.

## Traceability

`Index/Source Map.json` is the complete graph in a compact encoding: a
deduplicated `sources` table of raw path lists, one entry per curated artifact
(`{"path", "source"}` referencing a list index), a `backrefs` table that records
only the raw files participating in several curated entries (as entry indices),
and the sprite visual-alias list. Every curated artifact appears; shared payloads
record `sharedFrom`. The same mapping is written in full to the audit directory
(`path-map.json`) for verification.

Each per-asset record carries the structural identity it needs: a map records
its map id, raw directory and layer list; an animation records its name, source,
frame count, and the frame/direction pairs that map to each collapsed pose. The
`Source Map.json` is the authoritative curated-to-raw edge list, so per-asset
records stay lean rather than re-storing every raw path.

## What curation never does

- It never writes the raw library; it hashes it before and after the build and
  refuses to report success if a byte changed.
- It never invents a semantic label, never writes prose, and never writes a
  README, note or description. The prose guard from `tools/export/metadata.py`
  is applied to every document before it is written and re-scanned over the
  finished tree.
- It never re-encodes an image; every curated image is byte-identical to a raw
  artifact.
- It never exposes a raw identity, ROM address or hash in a human-facing path.
