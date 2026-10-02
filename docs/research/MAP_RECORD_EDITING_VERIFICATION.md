# Map content editing and round trip

Editing map content with a byte-identical round-trip proof: the supported corpus,
the semantic edit proof, the cross-subsystem write safety and the remaining
unknowns.


## Tests and results

`869 passed, 0 failed` across the whole repository (was 804; **+65**), three
pre-existing marker warnings unrelated to this record.

TOOLKIT-007 contributes **65**, which is exactly the 869 - 804 delta:

| File | Tests |
| --- | --- |
| `tests/unit/test_map_slots.py` | 18 |
| `tests/unit/test_maps.py` | 14 |
| `tests/unit/test_map_project.py` | 10 |
| `tests/integration/test_local_maps_rom.py` | **23** |

The 42 unit tests are portable, synthetic bytes only, no proprietary fixtures.
The 23 ROM-gated tests cover corpus round-trip, the confirmed fixture, graph
determinism, project lifecycle, cross-subsystem write safety, validation and CLI,
and skip cleanly when the user-supplied ROM is absent.

An unrelated pre-existing environment fault affects `tmp_path` on this machine
(`PermissionError` on the default pytest temp root); it reproduces on the
untouched `tests/unit/test_text_project.py` and is worked around with
`--basetemp`. It is not caused by, and does not affect, this record's code.

## Supported map corpus

| Extent | Measured |
| --- | --- |
| MapEntry records | **452** |
| Readable slot arrays | **152** |
| Slots | **873** |
| Slot bytes | **6,984** |
| Typed arrays | **35** |
| Typed slots (= graph edges) | **89** |
| Typed slot bytes | **712** |

## Byte-identical round-trip proof

Every MapEntry record and every readable slot extent re-encodes to its original
bytes: 452/452 records, 152/152 arrays, 0 mismatches. `webfoot map
validate-round-trip` reports the same figures and exits 0.

Whole-ROM: extract -> build reproduces canonical SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` with
**0 changed bytes**. Repeated extraction is byte-identical; repeated builds are
byte-identical.

## Semantic edit proof

`map:0039 music_id 15 -> 14` -> **exactly 1 byte** changed, at file offset
`0x0008EB8C` = record base `0x0008EB68` + `0x24` (`music_id_raw`). Manifest owner
`map:0039`, reason `map edit: music_id`. Canonical ROM unchanged.

## Cross-subsystem write safety

A map edit, a stat edit and a text edit build together in **one merged plan**:
3 changed bytes, three distinct owners (`map:0039`, `enemy:18`, `text:0001`), at
three non-overlapping offsets. A second owner claiming a map record's span is
refused with `OverlappingChangeError`. No map-specific write path was created -
maps call the same `plan_changes` / `emit_image` machinery as every subsystem.

## Capability matrix

| Target family | Rung |
| --- | --- |
| MapEntry records | **ROUND_TRIP** |
| Map-linked 8-byte extents (opaque) | **ROUND_TRIP** |
| Typed `{type, source_ref}` arrays | **ROUND_TRIP** |
| Transitions / connections | **DECODE** (89 edges, destinations UNKNOWN) |
| Trigger records, general semantics | **NOT ESTABLISHED** |
| Source references | **READ** (located, layout not claimed) |
| Collision | **DISCOVERED** |
| NPC targets | **DISCOVERED** |
| Object targets | **DISCOVERED** |
| Item targets | **DISCOVERED** |
| Script attachments | **DISCOVERED** |

Script attachments stay DISCOVERED because TOOLKIT-006's structural script
identities belong to the Legacy of Goku II static43 corpus and the Buu profile
declares no `scripts` capability. Promoting Buu's script-pointer fields would
assert a cross-game correspondence no evidence supports.

Collision was audited and left at DISCOVERED: no verified collision
representation exists in this project's records, and sec 14 forbids opening
broad collision RE for a future editor's benefit.

## Defects and corrections discovered

1. **`MapEntry +0x04` is not a general trigger-record count.** AUTO-012 read it
   as one from a single-entry static decode. Corpus-wide: 163 entries pair a
   positive count with a NULL pointer, 69 pair a zero count with a live ROM
   pointer, and only 35 of 153 readable arrays are uniformly shaped. Recorded as
   OLD CLAIM / NEW EVIDENCE / RESOLUTION in `research/AUTO_RE_STATE.md`.
2. **MapEntry 451's declared extent overruns the MapEntry table.** Four declared
   records at `0x0008E2D0` would consume the first 16 bytes of the table at
   `0x0008E2E0` that indexes it. Surfaced by `plan_changes` as a genuine overlap
   error, not worked around: `_resolve_slot_extent` now refuses an extent that
   collides with the table, leaving 152 readable.
3. **The verified source structure is reached from an opaque array.** MapEntry 39
   is not among the typed 35, so **no typed reference's target layout is
   verified**. An earlier draft of the evidence doc said "88 unverified targets",
   implying one was verified; corrected to 89.

4. **`docs/PROJECT_STATE.md` exceeded its documented bound (241).** The budget is
   enforced by `test_required_workflow_files_exist_and_are_bounded` and exists to
   push completed-record records into the continuation file. Fixed by moving the
   oldest COMPLETE entry (TOOLKIT-003, already marked "older baselines below are
   historical") verbatim into `docs/PROJECT_STATE.md`, which documents itself
   as holding exactly those records, **not** by raising the limit.
5. **Two workflow tests pinned the previous record's name.**
   `test_context_split_...` and `test_toolkit_activation_...` asserted literal
   `# TOOLKIT-006`, `Do not begin TOOLKIT-007` and `archive/TOOLKIT-005.md`, so
   they fail on every activation, the same class TOOLKIT-003 hit ("obsolete
   record assertions, fixed"). Rewritten to derive the id from the working queue's own
   heading, which is the convention
   `test_runner_dry_run_works_from_an_unrelated_directory` already states
   explicitly ("rather than pinning one record's name here"). The invariant they
   check is unchanged and now survives the next activation.

## Explicit tradeoff: the typed-array threshold

`_TYPED_HIGH_HALFWORD_LIMIT = 0x0010` (`tools/webfoot/formats/map_slots.py`) is
retained as an **explicit classifier heuristic and nothing more**.

* The threshold is **hand-picked, not measured from ROM semantics.** The
  confirmed example only ever shows `0x0002000X`, and nothing in this project
  establishes what the high halfword means or where its real boundary lies.
* **Corpus classification is invariant across the tested `0x0003`-`0x0100`
  range**, every limit in it yields the identical 35 arrays / 89 slots. Only
  removing the constraint entirely moves the result (to 40 / 112), so the
  reported corpus is a property of the ROM's data, not of the chosen number.
* **The current test guards that invariant**:
  `test_the_typed_corpus_is_insensitive_to_the_threshold`.
* **If that invariant ever fails, the classifier requires new evidence rather
  than threshold tweaking.** Retuning the number to restore a preferred corpus
  size would be fitting the constant to a desired answer.
* `0x0010` is **not** CONFIRMED, has no semantic status, and must not be
  promoted to either. No claim about the ROM rests on it.

It is called out rather than buried because it is the single knob deciding the
35/117 split, and therefore the typed ROUND_TRIP counts and the 89-edge graph.

## Canonical input status

Unchanged, verified before and after:

| File | SHA-256 |
| --- | --- |
| Buu's Fury `.gba` | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| Buu's Fury `.sav` | `7cf0a516ebebbc74a959d6fc1ebc7aac808fc99683ccbb9e4b82a0d58ba02a86` |
| Buu's Fury `.ss1` | `2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab` |
| Legacy of Goku `.gba` | `3ba9919e26704b0f5fdc2bfabc7f7a0404c71413761d38abcd94224c3bd4b1b9` |
| Legacy of Goku II `.gba` | `6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75` |

## Remaining map unknowns

* What `MapEntry +0x04` counts.
* Why 163 entries carry a count with no array, and 69 an array with no count.
* The layout of all 89 typed source targets.
* Every slot word in the 117 opaque arrays.
* Collision representation; canonical map display names.

## Scope and canonical growth

No graphical editor, no tileset UI, no LOGII map archaeology, no script-semantic
expansion, no free-space archaeology, no ROM growth, no AUTHOR_NEW maps, no fresh
RE on `+0x04`. Canonical growth remains blocked: no profile declares verified
free space, and none was manufactured.
