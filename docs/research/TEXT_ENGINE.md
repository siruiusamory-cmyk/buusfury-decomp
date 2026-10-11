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

An edit is one of three frozen dataclasses:

- `SlotEdit(slot, old, new)` for the 1,534-slot string table;
- `RecordEdit(selector, start, length, old, new)` for one dialogue record, where
  `old` must occur exactly once in the record's text;
- `RenameEdit(old, new, retail_test, relocated_slots)` for a character rename
  whose target is fixed by the canonical image.

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
- **Detection.** The container table is reached through the image's own literal
  word, the containers through the table, the records through their handles, and
  the string table through its declared base. Every candidate is then validated:
  header game code, all seven retail containers decoding with a non-zero declared
  payload, all 1,534 slots decoding to a terminated string, and at least 100
  dialogue records. A failure refuses the image and names the check. Another
  Webfoot title is one more entry in `PROFILES`.

## 4. Golden replay

Measured 2026-10-11 in the ticket worktree, with these images staged as real
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
| decisions | 37 `MOVE` (34 records, 3 slots), 60 records listed |
| output | 10,169,982 bytes, `f5c9648bbf7a9b448d801866cc775eb76abd270f7c16fb93d4e01630ef236201` |

That is the published release-3.1 image, byte for byte. The counts agree with
the release's own manifest: 34 rows, 60 left, 3 slots, and an appended container
declaring 23,790 bytes at file offset 10,146,136.

## 5. Tests

`tests/unit/test_text_engine.py`, 20 tests, all portable (`fast` gate): 17 on the
synthetic image and 3 golden replays that skip when the release images are not
staged. The fixture is a 450 KB synthetic image with seven stored containers,
real record words and the real 1,534-slot table, so every rule runs in CI
without any ROM.

| Rule | Test |
| --- | --- |
| byte coordinates | `test_an_in_place_edit_keeps_the_record_span_and_pays_the_tail_with_spaces` |
| refusal blocks the export | `test_a_refused_edit_blocks_the_export_and_writes_nothing` |
| boundary-safe | `test_a_span_with_another_record_boundary_inside_it_moves_instead_of_writing`, `test_a_record_that_merely_contains_the_span_is_not_a_boundary_conflict` |
| one-reference guard | `test_a_slot_whose_pointer_has_a_second_reference_is_refused`, `test_a_slot_with_one_reference_moves_and_reads_back`, `test_a_slot_edit_refuses_a_guard_that_does_not_match_the_slot` |
| carry-forward prefix | `test_a_moved_record_is_appended_after_the_carried_payload`, `test_a_carried_record_still_resolves_through_its_own_handle`, `test_the_first_use_of_the_grown_slot_warns_that_the_slot_was_taken` |
| per-occurrence decision | `test_a_record_holding_both_actors_renames_only_the_retail_occurrence`, `test_an_occurrence_with_no_retail_name_is_counted_unclear`, `test_a_rename_refuses_when_the_offsets_do_not_correspond` |
| destination refusal | `test_apply_refuses_the_input_file_as_its_own_destination`, `test_apply_refuses_a_destination_inside_the_protected_rom_directory` |
| detection | `test_an_image_with_a_foreign_game_code_is_refused`, `test_an_image_whose_live_selector_is_not_a_container_is_refused` |
| golden replay | the three tests of section 4, which skip when the release images are not staged |

## 6. Open limits

- **Control units are uninterpreted.** The engine knows a unit is a control unit
  and that an edit may not change the sequence, not what it draws. A chip that
  names a speaker or a portrait code cannot be authored from a meaning.
- **No box metrics.** There is no font or dialogue-box model, so nothing checks
  whether a line fits the box. The engine bounds a record by the handle's 4,094
  byte length field and the container's 65,534 byte start field, not by pixels.
- **The grown selector slot is taken on first use.** On the retail image that
  slot holds an IWRAM word, and the block past the seven live entries belongs to
  something else. The engine uses the slot (the project measured it as the
  reserved append slot and proved selector 7 at runtime), reports it as a warning
  when the slot did not already name a container, and lists the byte range it
  writes. Freeness in the P-027 sense has not been proven for that word.
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

Also `references/tools.md` T-011 records the module itself, its invocation, the
two golden digests and its limits.
