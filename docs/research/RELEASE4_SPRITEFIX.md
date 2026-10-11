# Release 4 sprite fix: restore the bytes release 3.1 wrote over sprite data

Ticket RELEASE4-SPRITEFIX-001. Base image: the Release 4 image
(`2867b2cc43103e4b02d92f2942f557d249ec17ff4fc96b64dd75683fade67f08`, 10,170,720
bytes), itself built on Release 4A Broly (`a21c1e27...`). Canonical reference:
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

## 1. Identity

| | |
| --- | --- |
| input | `release4.gba`, 10,170,720 bytes, `2867b2cc43103e4b02d92f2942f557d249ec17ff4fc96b64dd75683fade67f08` |
| output | 10,170,720 bytes, `cff4b9fcb630cc9ac1162cd16df72037590ad23d7d9b4eb63302c602358224b8` |
| builder | `tools/research/apply_release4_spritefix.py` |
| verifier | `tools/research/verify_release4_spritefix.py` (imports neither the builder nor the engine) |
| reproduced | twice, byte-identical |
| bytes changed | 28, across nine four-byte words |

## 2. What is being repaired

Release 3.1's rename builder found dialogue record words by shape alone and rewrote
every hit. Nine of those words lie outside the event-resource pool, where that
filter is near-random, so the release wrote renamed handle values over sprite
graphics and over unclassified data. RELEASE4-SPACES-001's review classified all
nine (finding O1); its engine now refuses to write outside the pool, but the
damage is already in the shipped chain, and Release 4A and the Release 4 image both
carry it.

| offset | what lives there | canonical word | measured defect in the base | after the fix |
| --- | --- | --- | --- | --- |
| `0x316A18` | unclassified low-entropy data, consumer not identified | sha256 `1a6e2bef6eed` | four wrong values, effect unknown | equals canonical |
| `0x40E178` | character 033, animation 005, frame 000, direction 0 | sha256 `50d3a83ab16f` | decodes, 1,230 of 4,096 bytes wrong from 1810 | decodes identically to canonical |
| `0x4567CC` | character 042, animation 003, frame 003, direction 1 | sha256 `6448cb76868f` | does not decode: 4,092 of a declared 4,096 | decodes identically to canonical |
| `0x46C29C` | character 042, animation 007, frame 002, direction 0 | sha256 `3f4fca41569f` | does not decode: 2,046 of a declared 2,048 | decodes identically to canonical |
| `0x4D99A8` | character 099, animation 002, frame 003, direction 0 | sha256 `780674c71910` | does not decode: back-reference distance 5,400 at output 1,380 leaves the output | decodes identically to canonical |
| `0x545A04` | character 114, animation 015, frame 003, direction 1 | sha256 `1213090509d4` | does not decode: 1,018 of a declared 1,024 | decodes identically to canonical |
| `0x5C6FB4` | character 123, animation 002, frame 003, direction 0 | sha256 `2721a77458b8` | does not decode: back-reference distance 3,380 at output 942 leaves the output | decodes identically to canonical |
| `0x725474` | uncompressed 8bpp tiles at `0x7253DC + 0x98`, named by OAM descriptor `0x72A5F0` | sha256 `fbc923d82de4` | three pixels change palette index | equals canonical over the 512-byte window |
| `0x726074` | the same tile data duplicated at `0x725FDC + 0x98`, descriptor `0x72A620` | sha256 `fbc923d82de4` | three pixels change palette index | equals canonical over the 512-byte window |

The `canonical word` column is the first 12 hex digits of the sha256 of the four
canonical bytes, not the bytes: this repository keeps ROM-derived content out of
Git history, and the owner restated that rule on 2026-10-11. The two tile sites
share a fingerprint because their words are identical in canonical. Offsets,
identities and fingerprints are enough to re-find every site in any copy of the
images; the builder reads the bytes themselves from the canonical image at run
time and the manifest pins that image by digest.

The character, animation, frame and direction identities are the atlas's own
attribution (`build/atlas/graphics_extents.jsonl`, produced by
`tools/webfoot/graphics.py`). Two cautions, both from the review that passed this
ticket:

* the atlas's container index numbers (0584, 1016, ...) are that atlas's current
  numbering and change with it, so they are NOT used as names here; an offset is.
* naming one character per frame is the atlas's first reachability path, not the
  only one. The review's own walk also reaches `0x4565CC` and `0x46C29C` from
  character 043, and `0x5C6FB4` from characters 177 and 220, so every character
  that shares these animation frames is affected by the same repaired bytes.

The two tile blocks are not in that atlas, which is why they are named by the OAM
descriptor that points at them; the verifier re-reads each descriptor and checks it
names the block.

## 3. What the builder does, and what it proves before writing

It reads the canonical image's four bytes at each site, refuses when the base image
differs from canonical at any site by a byte count other than the 28 this ticket
names, builds the patched image in memory, and then proves, still in memory:

* every site word equals the canonical word;
* every compressed frame container decodes from the patched bytes and its decoded
  bytes equal the canonical image's own decode of that container;
* both uncompressed tile windows equal canonical over all 512 bytes.

A disagreement raises and nothing is written. The write itself is
`tools/webfoot/write.py` `emit_image`, so the destination guards (protected input
directories, the input file's own identity, an existing output), the staged
publish and the provenance manifest are the project's, not this script's.

## 4. Independent verification

`tools/research/verify_release4_spritefix.py` reads the base, the output and the
canonical image and re-derives everything:

* the output differs from the base at exactly the declared 28 bytes and no other
  byte (36 declared site bytes, of which 8 already matched canonical in the base);
* every site equals canonical;
* each of the six frame containers decodes from the output and equals canonical's
  decode, and the verifier also measures what the base did (five failed to decode
  and one decoded with 1,230 wrong bytes);
* both tile windows equal canonical over 512 bytes, and each OAM descriptor names
  its block;
* every byte outside the declared sites is identical to the base.

Result: `VERIFY PASS` on `cff4b9fc`.

## 5. Changes to the text engine and to the spacing verifier

The same ticket carries three corrections the RELEASE4-SPACES-001 review listed as
non-blocking:

* **The spacing verifier's allowed set was narrowed** from the whole 127,328-byte
  event-resource pool to the four bytes at each in-pool site word
  (`tools/research/verify_release4_spacing.py`). A write anywhere else in the pool
  is now a failure. Re-run against the Release 4 image: still `VERIFY PASS`, with
  all 4,590 changed pool bytes inside in-pool site words.
* **The spacing pass's table-slot write is guarded.** `_writable_table` copies the
  retail table into appended space and repoints its literal before ANY entry is
  written, and refuses when that literal is not named exactly once. Both the
  spacing relocation path and, closing finding F1 of the TEXT-ENGINE-001 review,
  the in-place relocation path go through it. `TitleProfile.retail_table`
  (`0x7B5B64`, the canonical image's own literal) is the measured constant that
  decides which table is the retail one.
* **The review's document corrections** are applied: the census now leads with the
  in-pool count (202/220 base, 18/21 output, 19/22 canonical) and keeps the wider
  non-record count beside it; the paired smoke records that the box visibly draws
  `Game Saved`, which is the in-pool record `0:3702:20` this pass moved to
  `0:3666:20`, instead of claiming the box is empty; the kept-run wording now says
  that five of the six multi-reader positions have an out-of-pool coincidence word
  as their second reader and only `0:5428` has two in-pool readers, which is also
  the count the review measured; the duplicated bullet in `TEXT_ENGINE.md` section
  6 is gone; and section 4.3 states what the nine words damaged and points here.

## 6. Limits

* **The nine words' bytes are restored, not audited in play.** No emulator run
  shows the repaired animation frames drawing; the proof is byte-level (each frame
  decodes identically to canonical). Whether those frames appear correctly on
  screen is owner visual acceptance, which is owner-reserved.
* **`0x316A18` still has no identified consumer.** Its four canonical bytes are
  restored because the shipped release wrote over them and canonical is the only
  authority available; what reads it remains unknown.
* **The atlas attribution is a walk, not a runtime observation.** It reaches a
  frame through the character and animation tables; it does not prove the game
  draws that frame in any particular scene.
* **This fix is additive to the Release 4 image**, which stays the base: it writes
  28 bytes and nothing else, so every other property of that image (including the
  spacing pass's own changes) travels unchanged.
