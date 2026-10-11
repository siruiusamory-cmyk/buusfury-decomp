# The text-edit engine

The reusable module that the friend-v3 release scripts each carried a copy of.
Ticket: TEXT-ENGINE-001, 2026-10-10. This document records what the module does,
what was measured to prove it, and what it deliberately does not know.

Module: `tools/webfoot/textedit/` (`engine.py`, `__init__.py`).
Tests: `tests/unit/test_text_engine.py`.
No new dependency: the module composes `handles`, `compressed_dialogue`,
`dialogue_repack`, `formats.webfoot_lz`, `formats.text_tables`, `destination`
and `write`, all of which already existed.

## 1. What it replaces

Five per-release scripts, each with one route and its own hard-coded rows:

| Route | Was in |
| --- | --- |
| Copy records into the appended container | `tools/research/build_friend_v3_world_tournament_split.py` |
| Carry the previous payload forward, rewrite handles | `tools/research/apply_friend_v3_registration_rows.py` |
| Equal-or-shorter replacement inside the record's own span | `tools/research/apply_friend_v3_dialogue_text.py` |
| Replay the edit list from the input on every export | implied by every one of them |
| Per-occurrence rename decided against the canonical image | `tools/research/build_friend_v3_release31.py` |
| Approved wording as tracked data | `tools/research/friend_v3_text_approvals.py` |

## 2. The public API

```python
from tools.webfoot import textedit

model  = textedit.open(rom, canonical=canonical_rom)   # read-only model
built  = textedit.plan(model, edits)                   # deterministic plan
report = textedit.apply(built, out)                     # new file only
text, renamed, kept, unclear = textedit.rename_positions(
    current, counterpart, old="Videl", new="Lazuli")
```

`open` is the ticket's name; `open_rom` is the same function under a name that
does not shadow the builtin. `open` returns a `Model`: the image, its sha256,
the validated `Layout`, 1,534 `Slot`s (index, text, body offset, and the
canonical image's text when a canonical image was supplied), every `Record`
(selector, start, length, text, every carrying site, and the longer records that
cover it), and each record's locked control units.

An edit is one of four frozen dataclasses:

- `SlotEdit(slot, old, new)` for the 1,534-slot string table;
- `RecordEdit(selector, start, length, old, new)` for one dialogue record, where
  `old` must occur exactly once in the record's text;
- `RenameEdit(old, new, retail_test, relocated_slots)` for a character rename
  whose target is fixed by the canonical image;
- `SpacingEdit()` for the corpus-wide spacing rebuild of section 3. It needs the
  canonical image at open and must be the only edit in its plan.

`plan` decides one of `IN_PLACE`, `MOVE` or `REFUSED` per target, lists every
byte range the export will write, lists the covering records a move leaves
behind as warnings, and lists the records it left alone. `apply` refuses to write
at all when any target is refused; it refuses a protected destination and any
destination that is the input file itself (by file identity, so a hard link is
caught); it reads the built bytes back through the handles; and only then does it
stage and rename, returning the output sha256.

## 3. The rules, and where each came from

- **In place.** The replacement keeps the record's own byte count, paying the
  difference as trailing spaces, and only when no OTHER live record's start or
  end lies strictly inside the span. A covering record legitimately reads the new
  wording; a record whose boundary is cut by the shift does not, so that span
  moves instead. Boundary test: `boundary_safe` in
  `tools/research/apply_friend_v3_dialogue_text.py`.
- **Move.** The record is copied to the end of the image as a stored container on
  the grown selector, the payload that selector already named is carried forward
  as the prefix (so handles an earlier release wrote still resolve), the selector's
  table slot is repointed, and every handle word that carries the record is
  rewritten. Prefix and append: `apply_friend_v3_registration_rows.py` and
  `build_friend_v3_release31.py`.
- **The retail table is never written.** A table whose grown slot does not already
  name a container is the image's own table, and its words are live structure:
  measured on the canonical image, the grown slot holds `0x03004A68` and three
  code loads reach that word through the literal at file `0x03D92C`. The shipped
  releases never wrote it either; they ran on images whose table had already been
  moved into expansion space. On first use the engine therefore copies the whole
  64-slot table into appended space and repoints the one literal that names it
  (`0x123CC`), and it REFUSES when that literal is not named exactly once rather
  than writing a word whose owner is unproven (P-027). A table that already
  carries a container in the grown slot is the project's own append table, and one
  slot word of it is written.
  **One case is not yet byte-clean, and it is the first item of the UI ticket
  (finding F1 of this ticket's sign-off).** The in-place phase runs before the move
  phase, so in a plan that both relocates a container in place (a grown replacement
  that no longer fits the space its container occupies) and moves a record, the
  in-place phase writes that container's table entry in the image's own table
  before the table is copied. Measured example on the canonical image: a plan with
  `1:5498:12` grown and a move writes retail table slot 1 at file `0x7B5B68`. The
  write is dead, because the literal is repointed in the same export and nothing
  else names that word, but the retail block is then NOT byte-identical. The fix is
  to relocate the table before any container relocation, with a mixed-plan test
  asserting `0x7B5B64..0x7B5C64` unchanged; until it lands, byte-identity of the
  retail block is claimed only for plans that do not relocate a container in place,
  which is every plan this ticket reproves.
- **Carry-forward.** The prefix is the previous container's DECODED payload. The
  two release builders copied the stored bytes from the container's header, which
  coincides with the payload only because the container they carried was kind 0.
  A packed container's stored bytes are not its payload, so the engine decodes it.
- **One-reference guard.** A string-table slot with a grown text is appended and
  its single table word repointed, and the write refuses unless the old pointer
  occurs exactly once at a word-aligned offset in the whole image. Same guard as
  `tools/webfoot/dialogue_repack.py` and the release builders.
- **Per-occurrence rename.** The decision is made per occurrence, at the same
  character offset, against the canonical image; a length mismatch refuses. The
  engine counts an occurrence as `kept` when the canonical image names a
  different actor there, and `unclear` when it names nothing.
- **Locked control units.** A control unit is a halfword below 0x20 (0x0008
  consumes the next halfword as its operand); an edit whose replacements change
  that sequence is refused. What each unit draws is not known.
- **Spacing rebuild.** `SpacingEdit` collapses every interior 2+ space run in the
  DECODED STREAM, not inside a record, because the containers are chain-shared and
  a per-record fix re-creates the run in a covering record (pitfall P-023). Each
  record's handle is rewritten to the span its text now occupies, so no record
  keeps a length it paid for and no payback space exists. A run survives exactly
  where the canonical image's record at the same identity carries a 2+ space run at
  the same unit offset, and when the canonical run is shorter the base run is cut
  down to it. Every deletion is checked to be a space unit before it is made, and a
  non-space unit or a record whose text would collapse to nothing refuses the plan.
  Used by `tools/research/build_release4_spacing.py`; measured over Release 4A: 490
  units removed, 2,536 handle words rewritten, 20 retail runs kept, containers
  rewritten at the offsets they already occupied so the table never moves.
- **Proven handle carriers.** A handle word is written only inside the
  event-resource pool (`PROVEN_HANDLE_POOL`, the placement contract's
  `pool_start`/`table` pair, carried on the `Layout` at open). Outside the pool the
  inventory's shape filter is near-random: measured on Release 4A, 907
  record-shaped words lie outside it, 281 pass, and 256 of those name spans sharing
  no edge with any real record, against 11 of 2,639 inside. A word outside the pool
  is therefore a coincidence until someone proves which code reads it, and it keeps
  its bytes. A moved record whose only words are outside the pool is listed by a
  rename and REFUSED by a targeted edit. Measured effect: revision 1 of the release
  pass wrote 155 such words, 142 of them in code and graphics; revision 2 writes
  none, and the independent verifier's allowed-changed-byte set is the pool range
  rather than the shape-filtered site list, so the two cannot share the defect.
- **Detection.** The container table is reached through the image's own literal
  word, the containers through the table, the records through their handles, and
  the string table through its declared base. Every candidate is then validated:
  header game code, all seven retail containers decoding with a non-zero declared
  payload, all 1,534 slots decoding to a terminated string, and at least 100
  dialogue records. A failure refuses the image and names the check. Another
  Webfoot title is one more entry in `PROFILES`.

## 4. Golden replay

Measured 2026-10-10 in the ticket worktree, with these images staged as real
copies under `roms/` and verified by sha256.

### 4.1 Release 3, the wording stage

| | |
| --- | --- |
| input | `v3-release3.2-profile.gba`, 10,146,136 bytes, `639570e7dd05a963a85750e192ff261d6b498da9225c18d1670bc0c484c49ba9` |
| edits | the five approved wording edits, in the release's own order |
| decisions | five `IN_PLACE` |
| output | 10,146,136 bytes, `521bd0fa0a8bc198f36430e3419184807e335fa588bd718152996c076a8f15fd` |

That is the published release-3 image, byte for byte.

### 4.2 Release 3, replayed from the release's own base

Release 3 is three stages: `boss-retune`, `behaviour-profile`,
`dialogue-wording`. Only the third is a text edit, so the engine's release-3
edit list starts from the profile stage's output. Replaying it from the whole
release's base measures how much of the published image the engine owns:

| | |
| --- | --- |
| input | `v3-wt-split-2-1-a.gba`, 10,146,000 bytes, `018757c4e0dda9f463364675f32b307dff9e5ad89c7a0b932939aec320032389` |
| output | 10,146,000 bytes |
| differing from the published image | 23 bytes, all inside `0x70F7E4..0x711BCE`, the enemy stat table and the behaviour words the two non-text stages own |
| tail | the published image's extra 136 bytes are byte-identical to the profile stage's tail |

So release 3's published image is reproduced exactly when the list carries the
two stat and behaviour stages as well; the engine owns the wording stage and
nothing outside it.

### 4.3 Release 3.1

| | |
| --- | --- |
| input | `v3-release3.gba`, 10,146,136 bytes, `521bd0fa0a8bc198f36430e3419184807e335fa588bd718152996c076a8f15fd` |
| edit | one `RenameEdit` for `Videl` to `Lazuli`, relocated slots 138, 172, 1066 |
| decisions | 37 `MOVE` (34 records, 3 slots), 68 records listed |
| output | 10,169,982 bytes, differs from the published image only at the nine words below |

The published release-3.1 image is `f5c9648bbf7a9b448d801866cc775eb76abd270f7c16fb93d4e01630ef236201`.
This engine reproduces it every byte except **28 bytes across nine words outside
the event-resource pool**: `0x316A18`, `0x40E178`, `0x4567CC`, `0x46C29C`,
`0x4D99A8`, `0x545A04`, `0x5C6FB4`, `0x725474`, `0x726074`. Every one is a shape
coincidence the release's builder wrote because it used the inventory without the
pool rule; two of them (`0x725474`, `0x726074`) sit in a repeating tile-data run.
All 26 in-pool handle words the release wrote are reproduced byte for byte, and the
record counts agree with the release's own manifest: 34 rows, 3 slots, 60 records
listed for the owner. The further 8 listed records are the ones no pool word names.

Finding B1 of the RELEASE4-SPACES-001 review is what turned this up: the same
filter, used by a corpus-wide spacing pass, wrote 155 such words.

## 5. Tests

`tests/unit/test_text_engine.py`, 33 tests, all portable (`fast` gate): 29 on the
synthetic image and 4 that need the canonical or the release images and skip
without them. The fixture is a 450 KB synthetic image with seven stored containers,
real record words and the real 1,534-slot table, so every rule runs in CI without
any ROM.

| Rule | Test |
| --- | --- |
| byte coordinates | `test_an_in_place_edit_keeps_the_record_span_and_pays_the_tail_with_spaces` |
| refusal blocks the export | `test_a_refused_edit_blocks_the_export_and_writes_nothing` |
| boundary-safe | `test_a_span_with_another_record_boundary_inside_it_moves_instead_of_writing`, `test_a_record_that_merely_contains_the_span_is_not_a_boundary_conflict` |
| one-reference guard | `test_a_slot_whose_pointer_has_a_second_reference_is_refused`, `test_a_slot_with_one_reference_moves_and_reads_back`, `test_a_slot_edit_refuses_a_guard_that_does_not_match_the_slot` |
| carry-forward prefix | `test_a_moved_record_is_appended_after_the_carried_payload`, `test_a_carried_record_still_resolves_through_its_own_handle`, `test_a_record_already_in_the_grown_selector_moves_and_reads_back` |
| the retail table is not written | `test_the_first_move_relocates_the_table_and_leaves_every_retail_word_alone`, `test_a_table_with_more_than_one_reference_is_refused_instead_of_written`, and on the canonical image `test_the_canonical_table_words_are_untouched_when_a_record_moves` |
| readback per site | `test_an_in_place_edit_and_a_move_from_one_container_both_read_back` |
| spacing rebuild | `test_the_spacing_pass_collapses_a_chain_shared_run_and_rewrites_every_handle`, `test_a_run_the_canonical_image_carries_is_kept_and_the_other_collapses`, `test_a_spacing_plan_may_not_carry_another_edit`, `test_a_spacing_pass_without_the_canonical_image_is_refused` |
| proven carriers | `test_a_record_shaped_word_outside_the_pool_is_never_written`, `test_a_targeted_edit_refuses_a_record_no_pool_word_names` |
| per-occurrence decision | `test_a_record_holding_both_actors_renames_only_the_retail_occurrence`, `test_an_occurrence_with_no_retail_name_is_counted_unclear`, `test_a_rename_refuses_when_the_offsets_do_not_correspond` |
| destination refusal | `test_apply_refuses_the_input_file_as_its_own_destination`, `test_apply_refuses_a_destination_inside_the_protected_rom_directory`, `test_apply_refuses_the_canonical_reference_as_its_own_destination`, `test_apply_refuses_to_overwrite_an_existing_output` |
| detection | `test_an_image_with_a_foreign_game_code_is_refused`, `test_an_image_whose_live_selector_is_not_a_container_is_refused`, `test_an_image_truncated_inside_the_table_cannot_skip_a_live_selector` |
| golden replay | the three golden tests of section 4 plus the canonical-image test in the row above: four ROM-dependent tests in all, which skip when those images are not staged |

## 6. Open limits

- **Control units are uninterpreted.** The engine knows a unit is a control unit
  and that an edit may not change the sequence, not what it draws. A chip that
  names a speaker or a portrait code cannot be authored from a meaning.
- **A handle word is written only inside the event-resource pool.** The inventory's
  shape filter is near-random outside it (281 of 907 words pass on Release 4A, 256
  of those naming spans that share no edge with a real record). A word outside the
  pool is a coincidence until someone proves which code reads it, and this engine
  does not write it. A rename lists a record no pool word names; a targeted edit on
  one refuses. The cost of being wrong the other way is measured: revision 1 of the
  spacing pass wrote 155 such words, 142 of them in code and graphics.
- **No box metrics.** There is no font or dialogue-box model, so nothing checks
  whether a line fits the box. The engine bounds a record by the handle's 4,094
  byte length field and the container's 65,534 byte start field, not by pixels.
- **The table is relocated when the grown slot is not already a container.** On
  the retail image that slot holds `0x03004A68`, an IWRAM word three code loads
  reach through the literal at file `0x03D92C`, so the engine copies the whole
  table into appended space and repoints the `0x123CC` literal on first use, and
  refuses when that literal is not named exactly once. A table that already
  carries a container in the grown slot (the shape every shipped release has) gets
  one slot word written in place, which is the route the releases used.
- **A mixed plan writes a dead retail table word (F1).** If one plan both
  relocates a container in place and moves a record, the in-place phase writes the
  container's table entry into the image's own table before the table is copied.
  The write is dead, since the literal is repointed in the same export, but the
  retail block is then not byte-identical. Fix and test are the first item of the
  UI ticket; see section 3 for the measured example.
- **A move leaves the old bytes.** Every longer record covering the same span
  keeps the old wording; the plan reports each one and warns. Release 4's
  container rebuild is what removes the case.
- **The in-place payback comes out of the record's own span.** A record whose
  text ends on a visible character cannot absorb a shrink without losing its
  tail; the engine refuses a negative pad rather than writing one (P-022).
- **One profile.** Only Buu's Fury is described. `PROFILES` is the seam for
  another Webfoot title; the validator would have to name that title's own
  container table, string table and record shape.
- **A container over 64 KiB of declared payload** is refused by the existing
  decoder, not by this module.
- **The readback compares words, not padding, for records it did not move.** An
  in-place edit pays its difference as trailing spaces, so a covering record can
  legitimately lose interior spaces; those sites are compared with spaces removed,
  and a moved record's sites are compared exactly.
- **A spacing pass keeps retail runs, including one that a non-retail record also
- **A spacing pass keeps retail runs, including ones a second record also reads.**
  On the Release 4A image, run `0:47756` is retail spacing and is also inside a
  longer record's span, so that record still shows the two spaces. Five kept runs
  in all are each read by two records, and in every case both readers carry the run
  in the canonical image. Measured detail in `RELEASE4_SPACING.md` section 6.
- **A spacing pass can be defeated by an image whose canonical correspondence does
  not hold.** The keep rule maps the base's byte offsets straight onto the canonical
  payload. Every release preserved record lengths, so that correspondence holds for
  this corpus; on an image where it does not, the pass would keep the wrong runs and
  the verifier's independent rule would report it.
- **No CLI and no UI.** Ticket 1 is the engine. The desktop surface is ticket 2.

## 7. Harvest

Added to the RE Lab toolbelt (`references/pitfalls.md`, newest last) from this
ticket:

- **P-033**: a carry-forward route must prefix the previous container's DECODED
  payload, not the bytes at its header. The two release builders read raw bytes;
  that is correct only for a kind-0 container.
- **P-034**: a golden replay of a multi-stage release must name the stage's own
  input. Reproducing release 3 byte-identically needs the profile-stage image,
  because two of its three stages are not text edits; from the release's base the
  engine's output differs in exactly 23 bytes plus a 136-byte appended block, and
  those are the two non-text stages.
- **P-035**: a per-occurrence rename's "kept" count must come from the canonical
  text, never from the record's own text: comparing a record's text with itself
  is true by construction and counts every occurrence as kept.
- **P-036**: the review of this ticket found the engine WARNING and then writing a
  table slot that was not proven free, on an image whose table was still the
  retail one. The retail table's grown slot is live structure, reached by three
  loads through a second literal.
- **P-037**: the review found a readback keyed on the INPUT's per-selector record
  rows, which mis-checks a record that moved out of a container that was also
  edited in place; the expectation must be keyed on the SITE.
- **P-060**: the review of the spacing release found the engine and its verifier
  sharing ONE shape filter to find handle words, so 155 words outside the
  event-resource pool were written and the verifier's allowed-changed-byte set
  whitelisted exactly those words. The rule now names the pool, and the verifier's
  allowed set is the pool range rather than the filtered list.

Also `references/tools.md` T-011 records the module itself, its invocation, the
two golden digests and its limits.
