# FRIEND-V3-TEXT-AND-DIALOGUE-PASS-001: integration record

The change range is `59203721..HEAD`, four commits. This document is what the merge request
carries: what was built, what is proven, what is not, and what the next ticket inherits.

## What ships

One cumulative mainline derivative, built from the pre-BOOST foundation `a4c12a95818cab27…`
and reproduced byte-identically on every run:

| field | value |
| --- | --- |
| file | `v3-mainline-text-dialogue-pass.gba` |
| bytes | 10,141,220 (248 more than the foundation) |
| SHA-256 | `d2a25f9a56c9980e27ad4a6f4c23d653e87d15b71b908ee27bced48b88885543` |
| base | pre-BOOST Tulma-complete foundation `a4c12a95…` |
| not an ancestor | the BOOST speedrun image `acd98c2a…`, preserved as a separate testing derivative |

The artifact lives under the ignored `build/` tree and is not in git. The builder
`tools/research/build_friend_v3_text_derivative.py` produces it from the foundation with two
stages: the owner-approved text batch, then the trailing-pad repair.

## Lineage correction, and the evidence for it

The owner's 2026-10-10 correction separates the distribution image from the speedrun one.
Measured: the BOOST image differs from the pre-BOOST foundation in **exactly 25 bytes, all
inside the base-stat table at file `0x6FDA4C`**, the same 25 offsets the boost builder's own
manifest declares. The builder refuses any base that is not the foundation, and after the
final write it re-compares all 25 of those bytes against the foundation, so the exclusion is
checked in both directions.

## Included

- Everything the pre-BOOST foundation already carried: the character, text and Tulma chain
  through MR !165.
- Seven owner-approved biographies: slots 1059, 1069, 1187, 1189, 1191, 1193, 1195, written
  in place.
- The owner-approved slot 1065 grammar repair, by append and repoint because it is five units
  longer than its span.
- The trailing-pad repair: 32 dialogue records whose last units were padding spaces, repaired
  by reducing their handle's decoded length. 33 handle words, 41 bytes, no container byte
  moved.

## Verified

| check | result |
| --- | --- |
| approved wording reads back, seven in place and one relocated | PASS |
| no unedited text slot changed | 0 of the other 1,526 |
| bytes outside the declared sites | 0 |
| trailing-pad repair, four checks on the real image | PASS |
| container payload identical after the repair | yes |
| BOOST-only bytes in the finished image | none, on all 25 offsets |
| deterministic rebuild | byte-identical nine times |
| unit tests | `tests/unit/test_dialogue_trim_padding.py` 4 passed; runtime gates 93 passed, 34 skipped |

## NOT verified, and stated rather than implied

- **No runtime text evidence.** The derivative boots and renders a dialogue box on the
  packaged 0.11 build, shown by screenshot, and the savestate it was loaded from sits at an
  idle scene that cycles deterministically without executing the dialogue record copier at
  `0x0801227A`. So the repaired records have never been seen rendering. Reaching them needs
  an input driver from that state or a savestate captured at a dialogue trigger.
- **Static only** for the repair's safety argument. The payload is byte-identical, so no
  other record's bytes change, but whether the engine uses a record's length or its trailing
  spaces for anything beyond copying is not measured.
- **Interior padding, `Great Soyman` and the punctuated `Kakarot` to `Bandit` are not in this
  derivative.** All three need the handle-format work; they are deferred to a successor
  engine ticket by owner decision, and `dialogue_repack.plan_group` is not called by any
  stage here.
- **The World Tournament rewrite is not in this derivative.** Its records are located and
  preserved untouched; the wording is owner-authored and awaits implementation.

## Save compatibility

Battery saves are compatible: no stage touches the save layout, the game code or the
base-stat table. Savestates written on the foundation or the BOOST image are **not**
interchangeable: stage 1 moves one string and repoints one table word, so a state whose EWRAM
holds decoded text may show the old wording. Start from a battery save.

## What the successor engine ticket inherits

- The handle field is 6 bits of selector, 15 bits of start in halfwords, 11 bits of length in
  halfwords: a container may not exceed 65,534 decoded bytes, and the duplication repair needs
  128 KB in container 0 and 100 KB in container 2.
- The parse sites: `0x08012230` (parent), `0x0801227E` (child, where start and length are
  isolated), `0x0801227A` (the record copier). The selector sequence at `0x08012240` is
  `ldr r0,[r5,#4]` / `ldr r1,[pc]` / `lsls r0,#0x1A` / `lsrs r0,#0x18` / `ldr r0,[r1,r0]`.
- Measured engine facts for any observer: `emu:setBreakpoint(callback, address)` is the
  accepted signature; a pc sampled in a frame callback is not evidence about the register
  read.
- Two `dialogue_repack` limits are recorded in its own docstrings: a group re-layout cannot
  satisfy overlapping records whose claims about one unit differ, and the `--duplicate` route
  is stopped by the handle ceiling before it writes.
