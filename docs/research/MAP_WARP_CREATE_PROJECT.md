# MAP-WARP-CREATE-PROJECT-001 - creating a transition through the project and the build

STATUS: **IMPLEMENTED, VALIDATED AND INDEPENDENTLY REVIEWED - RETURNED FOR
REVIEW (2026-09-26).** Class: scoped project-format, SDK-authority, allocator and
build-integration pass. This is a **sub-pass of the parent capability
`MAP-WARPS-AND-CONNECTIONS-001`**, which stays active and unshipped in
[`PROJECT_<local-state-name>`](PROJECT_<local-state-name>); the parent's Workbench creation surface, human-operated
runtime proof and capability advance are explicitly **not** in scope here and were not
begun.

Baseline: `df81e7ab9bcffc99c526b7e9bffe768d8420214d` (the repository's `HEAD` at the
start of the pass, verified with `git rev-parse HEAD` on a clean tree, no drift).
Implementation: `5c0f6e4df77697031b92800dabb812a9ba5543bb`; frozen reviewed tip (the
correction commit): `7a0abc57fea6c20799bbc9079d3544809fea41b8`; commits after it are
**documentation only** and add this review record. All of them are on
`ticket/map-warp-create-project-001` in the ticket worktree
`<ticket-worktrees>\map-warp-create-project-001`. The primary checkout stays on
`master` at the baseline and was not committed, branched, pushed or archived; its
twelve changed files are byte-identical to the ticket branch's tip (verified by
SHA-256).

**public progress impact: NONE.** No capability ships, the registry stays at
**19 / 24 (79%)**, `EDIT` stays **7 / 8**, `src/data/capabilities.json` is untouched,
`warps` remains missing, and no published claim, blocker or questline entry changes
wording. `docs/PROJECT_<local-state-name>` is deliberately **not** touched: the parent
capability has not shipped, and the closed predecessor sub-passes recorded their
state in their own ticket records rather than in project state.

Scope boundaries honoured: no Workbench UI, no emulator or runtime proof, no
capability count change, no public-site change, no manual free offsets, no
`UNKNOWN` canonical space treated as free, no guessed value for an `UNRESOLVED`
field, no class-169 creation attempt, and no research script on the shipping path.

---

## RETURN

```text
MAP-WARP-CREATE-PROJECT-001 - STATUS REPORT

BASELINE:
df81e7ab9bcffc99c526b7e9bffe768d8420214d (master, clean tree)

AUTHORED TRANSITION IDENTITY:
map:NNNN/transition:<name> - the source map's durable MapEntry key plus a lowercase
authored name (<= 64 chars, [a-z][a-z0-9_-]*). Deliberately contains no ROM address,
no allocated address and no array index: the index a created record occupies does not
exist until a build appends it, and the project outlives the build. Realised as
CreatedTransitionIdentity(source, name) in the authority and as
[creation."map:NNNN"."<name>"] in maps/transition_creations.toml. Proof transition:
map:0040/transition:volcano-gate.

SUPPORTED CREATED CLASS:
566 class only - CREATED_CLASS_RAW = 0x08007675. It is the only class whose
+0x14/+0x16 pair is an ABSOLUTE arrival (passed straight through to the warp routine
at 0x08007600); the 169 class's pair is a scene-relative delta the engine composes at
0x08007234..0x08007258, so "where the player lands" is not a value a project can state
for it. A 169-class template is refused by name. No 169 creation was attempted.

TEMPLATE / INITIALIZATION MODEL:
A created record is COMPOSED over a named canonical template: an existing 566-class
record of the SAME source map, named durably as map:NNNN/transition:IIII. The template
is required and is never a default. Byte accounting, one entry per physical field,
published per creation in the manifest as "record_fields":
  authored whole (14 bytes + 4 bits) - the four region u16 at +0x08..+0x0F, the two
    destination-key bytes at +0x11/+0x12, the arrival pair at +0x14/+0x16/+0x17, and
    the HIGH NIBBLE of +0x10 (the arrival-facing override, (direction+1)<<4);
  copied invariant/template (8 bytes) - +0x00's class/constructor word and +0x04's
    corpus-invariant word, whose meanings are UNRESOLVED;
  preserved unresolved (1 byte + 4 bits) - +0x13, an engine-read byte whose census is
    {0: 561, 1: 174} and whose meaning is UNRESOLVED, and the LOW NIBBLE of +0x10
    (the door gate bits and two untraced bits). Both are pinned in the document as
    prior_facing_raw and prior_unresolved_raw and checked against the live template
    before anything is written, so a template that drifted is refused rather than
    silently re-initializing the new record.
The two unresolved bytes are COPIED FROM A RECORD THE ENGINE ALREADY CONSUMES, not
invented, and not borrowed across maps: a template of another map is refused, and so
is a map whose only records are 169-class or which has none. That narrowing is the
ticket's "fail closed and report it" case: no evidence establishes what +0x13 or the
gate bits should be for a map with no 566-class record of its own.
The created record is independent after creation: the template's bytes are read from
the canonical image, the created record lives at its own address, and a creation whose
composition would equal its template is refused outright (creation, not aliasing).

CREATE:
PASS - one supported selector-1 transition that the canonical image does not contain
was created on map 40 by semantic identity, saved, and materialized by the normal
build. map:0040/transition:volcano-gate -> map:0435 (Volcano) with region
[[120,177],[240,265]], arrival (4,368) and facing East.

SAVE/REOPEN:
PASS - set_transition_creations -> close -> read_project -> reopen reproduces the
identity, the template, the destination, the region, the arrival, the facing and both
measured template priors exactly; the reopened project validates and builds.

DETERMINISTIC BUILD:
PASS - two builds of the same saved project produced byte-identical derivatives and
byte-identical manifests (BuildResult.manifest.dumps()).

ROOT COUNT:
2 -> 3 at map:0040's root+0x40 (file 0x002934B4).

POINTER ARRAY:
0x0829346C (canonical, file 0x0029346C, 8 bytes, packed immediately against its own
root at file 0x00293474) -> 0x08800000 (authored, file 0x00800000, 12 bytes). The
canonical array is left byte-identical in place and simply stops being referenced; the
expanded array carries the two canonical element pointers byte-for-byte followed by
the created element.

NEW RECORD ALLOCATION:
file [0x0080000C, 0x00800024) = GBA 0x0880000C, 24 bytes, AllocationKind
TRANSITION_RECORD, Addressability EXPANDED_ONLY, storage class PADDING_EXPANDED.

NEW ARRAY ALLOCATION:
file [0x00800000, 0x0080000C) = GBA 0x08800000, 12 bytes, AllocationKind
TRANSITION_POINTER_ARRAY, Addressability EXPANDED_ONLY, PADDING_EXPANDED.

ABOVE ORIGINAL EOF:
YES - both spans. The canonical image is 8,388,608 bytes; the new array begins at its
first byte past EOF (file 0x00800000) and the new record 12 bytes later.

CANONICAL-IMAGE DIFF:
Within the original 8,388,608-byte canonical span, **4 bytes changed**: one byte of
map:0040's count at file 0x002934B4 and three bytes of its array pointer at file
0x002934B8. Everything else inside that span is byte-identical, including all 735
records and both pointer arrays.
This is deliberately NOT a statement that the derivative differs from the canonical
image by four bytes. The derivative is a **16 MiB generated image**: the profile's
generated expansion appends 8,388,608 bytes past canonical EOF, of which the two
allocated spans carry the new pointer array ([0x00800000, 0x0080000C), 12 bytes) and
the new record ([0x0080000C, 0x00800024), 24 bytes); the remaining appended bytes are
the declared 0xFF padding. A whole-image diff against the canonical input therefore
reports the 4 canonical changes plus every padded/generated byte above EOF.

ROOT +0x44 ENCODING:
A full 32-bit little-endian GBA address, measured - not assumed - over the whole
corpus: 452 of 452 canonical roots carry a 4-byte-aligned in-image GBA address in
+0x44 (and 0 in the 104 roots that declare no array), and the engine's own walk loads
the pair with one ldm at 0x08009676 and indexes it with lsls r0,r4,#2 at 0x0801266E.
Nothing masks, shifts or truncates it. An above-EOF value therefore encodes: file
0x00800000 maps to GBA 0x08800000 inside the Game Pak window 0x08000000..0x09FFFFFF.

ARRAY ELEMENT ENCODING:
The same: a full 32-bit little-endian GBA address, 735 of 735 canonical elements
measured, every one 4-byte aligned and inside the canonical image.

EXPANDED TRANSITION ADDRESSABILITY:
BUILD-PROVEN / ENCODING-PROVEN. The normal build materializes both the expanded array
and the created record above the original EOF and the derivative re-reads through the
authority with the new transition at the appended index; the encoding is proven by
census over all 452 roots and all 735 elements. It is explicitly NOT runtime-proven:
no emulator was run in this ticket, and whether the retail engine follows +0x44 and an
array element above EOF is the claim the later human-operated runtime ticket owns.

TEMPLATE INDEPENDENCE:
PASS - the created record occupies its own allocation and is never the template
address; a creation whose 24 bytes would equal its template is refused; and one build
that BOTH edits the template's region and creates a transition over it produces a
template carrying the edit and a created record carrying its own region, with the
created record's unresolved bytes taken from the canonical template rather than the
edited one.

EXISTING RECORD SAFETY:
PASS - all 735 canonical records re-read from the derivative with identical bytes and
identical addresses, and the canonical array is byte-identical in place.

UNRELATED MAP SAFETY:
PASS - maps 39, 41 and 435 keep identical roots, counts, array pointers and records;
within the original canonical span the only changed bytes are map 40's count and array
pointer (4 bytes), and the only added bytes are the two allocated spans above EOF.

M1-M6:
ALL KILLED - each mutation failed both the focused portable file and a named ROM-gated
regression, and each production file was restored byte-identically (see the table
below).

MANUAL VALIDATION (the focused acceptance evidence, by exact file):
tests/unit/test_map_transition_create.py (66 passed)
tests/integration/test_map_transition_create_rom.py (30 passed, 0 skipped, canonical
  ROM present)
tests/integration/test_map_transitions_rom.py + test_map_transition_project_rom.py
  (30 passed, re-run with LOGX_CANONICAL_ROM forced, see the follow-up note)
tests/unit/test_map_transitions.py + test_map_transition_project.py +
  test_allocation_authority.py + test_allocation_provenance.py + test_map_resize.py +
  test_project_format.py (265 passed)
After the review-prescribed correction: the 66 portable tests and the 114 predecessor
  transition tests (180 passed), the 30 ROM-gated tests (passed), and git diff --check
  clean.

MANUAL BROAD SUITE:
RUN ONCE IN ERROR AGAINST STANDING POLICY

RESULT:
3332 passed
8 skipped
1 pre-existing stale-dist failure

DISPOSITION:
NOT REPEATED
NOT USED AS ACCEPTANCE EVIDENCE

(Command: `python -m pytest tests/unit -q`, which the ticket's test policy names as a
command not to run. It was issued once at the start of validation to bound the blast
radius of a change to the shared allocator and write layers, and is recorded rather
than hidden. The focused files above are the acceptance evidence.)

INDEPENDENT REVIEW:
APPROVE - candidate 5c0f6e4, range df81e7a..5c0f6e4, job cl-20260926-221253-299abe.
One non-blocking finding (a duplicated, unreachable shared-root guard), resolved by
correction 7a0abc5 and confirmed by follow-up job cl-20260926-222936-818c6b:
"APPROVE - verdict stands for the corrected tip". No blocking finding outstanding.

CANONICAL ROM:
UNCHANGED - SHA-256 940ad5f0...f059e before and after every run, and the canonical
path is still refused as a build output target (OutputPathError).

PRODUCT CAPABILITY IMPACT:
NONE

DRAGONBYTE Z:
19 / 24 - 79%

PARENT:
MAP-WARPS-AND-CONNECTIONS-001 - NOT SHIPPED

NEXT:
RETURN FOR REVIEW
```

---

## What was built

The parent capability's second half: a transition that does **not** exist in the
canonical image, created by a project and materialized by the normal build. It is the
first transition domain that allocates, and the first writer of `root + 0x40` and
`root + 0x44` anywhere in the toolkit.

| Layer | Change |
| --- | --- |
| `tools/webfoot/formats/map_transitions.py` | `CREATED_CLASS_RAW`, `CREATED_FIELD_AUTHORED_MASKS` (the 24-byte composition table) and `compose_created_record()`. The codec stays pure and remains the ONE encoder. |
| `tools/webfoot/allocation.py` | `AllocationKind.TRANSITION_RECORD` and `TRANSITION_POINTER_ARRAY`, both `EXPANDED_ONLY`, with the measured-encoding / not-runtime-proven split stated in the table's own comment. |
| `tools/webfoot/project/model.py` | `maps/transition_creations.toml`, `[creation."map:NNNN"."<name>"]`, `AuthoredTransitionCreation`, `TransitionCreations`, `transition_creation_identity`, `write_transition_creations`, and the `StatProject.transition_creations` field. |
| `tools/webfoot/map_transitions.py` | `CreatedTransitionIdentity`, `TransitionCreation`, `AuthoredTransitionCreation`, `TransitionRoot`, `MapTransitions.root_for`/`shared_root_maps`, `created_record_fields()`, `_resolve_creation()`, `materialize_transition_creations()`, and the `set`/`read`/`remove` persistence API. |
| `tools/webfoot/write.py` | `TransitionRecordFieldProvenance` and `TransitionCreationProvenance`, threaded through `plan_changes`, `WritePlan`, `WriteManifest` and `emit_image`. |
| `tools/webfoot/build.py` | `_check_transition_creations` (validation) and the creation build domain, wired after the edit domain with the build-scoped reservation set. |
| `tests/unit/test_map_transition_create.py` | 66 portable tests over the synthetic image, the document and every refusal. |
| `tests/integration/test_map_transition_create_rom.py` | 30 ROM-gated tests over the real image, the real map 40 and the real build. |

**Why a separate document.** `maps/transition_creations.toml` is a sixth `maps/`
document rather than a second table of `maps/transitions.toml` for a reason of write
semantics: `write_transition_edits` *deletes* that document when the last edit is
removed, so a creation stored beside an edit would be destroyed by an author undoing
an unrelated retarget. The unit suite pins that separation
(`test_removing_the_last_edit_does_not_delete_a_creation`).

**Why the same-map template rule.** The template supplies the created record's
`+0x00`, `+0x04`, `+0x13` and `+0x10` low nibble. `+0x00` and `+0x04` are provably
constant across the corpus (566/169 and 735/735), but `+0x13` and the gate bits are
not: `+0x13` varies within a single map's own array (map 338 carries both 0 and 1).
Requiring the template to be a record of the same source map is the narrowest rule
this project can state, and its cost is explicit: a map with no supported 566-class
record of its own cannot be given a created transition, and is refused with that
reason rather than initialized from another map's unresolved bytes.

**Why the shared-root guard.** `root + 0x40` and `root + 0x44` live on the ROOT, and
11 canonical roots serve more than one map (2..10 maps each). Appending to a shared
root would silently give every map sharing it the same new connection. Measured: all
11 shared roots carry a count of 0, and a corpus in which two maps reached one
non-empty array would already be refused as a shared record - so a map on a shared
root has no 566-class record of its own to use as a template anyway. The sharing check
therefore runs FIRST, so the refusal names the real reason rather than the symptom,
and the unit suite exercises it directly on a synthetic image.

---

## Mutations

Each mutation was applied to production source as a single targeted edit, the named
focused regressions were run (`tests/unit/test_map_transition_create.py` in full, plus
a filtered run of the named ROM-gated regressions), and the file was then restored and
proved byte-identical by SHA-256. Harness:
`build/research/warpcreate_mutations.py` (ignored, not a shipping path).

| # | Mutation | Focused unit file | Named ROM-gated regression | Restored |
| --- | --- | --- | --- | --- |
| M1 | `root + 0x40` written back unchanged, so the count never increments | **KILLED** - 5 failed (`test_a_creation_appends_one_record_and_increments_the_root_count`, `test_two_creations_on_one_map_grow_the_array_once_and_keep_name_order`, `test_the_provenance_records_...`, ...) | **KILLED** - 2 failed (`test_the_canonical_region_gains_exactly_the_count_and_the_array_pointer`, `test_the_derivative_enumerates_the_new_transition_after_the_canonical_ones`) | byte-identical |
| M2 | the new record is written but `root + 0x44` still names the canonical array | **KILLED** - 8 failed (`test_the_root_array_pointer_is_rewritten_to_the_new_array`, `test_the_expanded_array_carries_the_canonical_elements_then_the_new_one`, ...) | **KILLED** - 1 failed (`test_the_derivative_enumerates_the_new_transition_after_the_canonical_ones`) | byte-identical |
| M3 | the expanded array is emitted in the wrong element order | **KILLED** - 4 failed (`test_every_existing_record_stays_byte_identical`, `test_the_expanded_array_carries_...`, ...) | **KILLED** - 2 failed (`test_the_canonical_array_is_left_in_place_untouched`, `test_the_derivative_enumerates_the_new_transition_after_the_canonical_ones`) | byte-identical |
| M4 | the created record's body is the template record's bytes (aliasing) | **KILLED** - 2 failed (`test_the_created_record_does_not_alias_the_template`, `test_the_created_record_is_authored_by_the_project_and_preserved_by_the_template`) | **KILLED** - 1 failed (`test_the_derivative_enumerates_the_new_transition_after_the_canonical_ones`) | byte-identical |
| M5 | the above-EOF record pointer is encoded as a file offset instead of a GBA address | **KILLED** - 6 failed (`test_the_created_record_lives_above_canonical_eof_and_its_pointer_decodes`, `test_the_expanded_array_carries_...`, ...) | **KILLED** - 2 failed (`test_the_created_record_and_the_array_live_above_the_original_eof`, `test_the_derivative_enumerates_the_new_transition_after_the_canonical_ones`) | byte-identical |
| M6 | the authored name is replaced by a positional key, so the identity does not survive reopen | **KILLED** - 9 failed (`test_a_creation_survives_save_reopen_and_build`, `test_a_project_build_of_creations_is_ordered_by_name`, ...) | **KILLED** - 1 failed (`test_a_created_transition_saves_reopens_and_builds`) | byte-identical |

**M6 needed a second target, and the reason is a real finding.** The first attempt
mutated `AuthoredTransitionCreation.from_document` to ignore the parsed name. The unit
suite caught it, but the ROM-gated reopen regression did **not**: the entry's own
`source`/`name` fields are redundant with the document's mapping key, and every
load-bearing path (`TransitionCreations.edits`, `transition_creations_to_requests`,
`to_document`) reads the key. The mutation that matters is therefore the one that
changes the **key** the document is written under, which is what the table records. The
redundancy itself matches the established shape of `AuthoredChunk`/`AuthoredChunks` and
is kept for consistency; it is not load-bearing and no path can make the two disagree.

---

## Independent review

Required by [`../../docs/DEVELOPMENT.md`](../../docs/DEVELOPMENT.md)'s independent code-review gate: a
nontrivial code-bearing ticket cannot report readiness on the implementer's own
verdict. The reviewer was a fresh-context local the review tool session with no part in the
implementation, given the frozen worktree, the start SHA, the frozen SHA and
[`MAP-WARP-CREATE-PROJECT-001-review-request.md`](MAP-WARP-CREATE-PROJECT-001-review-request.md).

| | |
| --- | --- |
| Range reviewed | `df81e7a..5c0f6e4` (implementation) |
| Verdict | **APPROVE**, no blocking or major findings, one trivial non-blocking finding |
| Job | `cl-20260926-221253-299abe` (the local reviewer, local headless) |
| Range reviewed after the correction | `5c0f6e4..7a0abc5` |
| Follow-up verdict | **APPROVE** - "verdict stands for the corrected tip" |
| Job | `cl-20260926-222936-818c6b` (the local reviewer, local headless) |

The reviewer reproduced both focused suites green at the candidate, re-verified the
canonical ROM hash, and probed the questions the brief listed rather than summarising
the implementation. Its own probes: a null `facing` writes a zero high nibble and
`South` writes one, so the two outcomes really are distinct; and
`CREATED_FIELD_AUTHORED_MASKS` matches what `compose_created_record` produces for every
non-facing field, so the published provenance is not a drifted table. It also confirmed
independently that the aliasing refusal cannot be bypassed (the `+0x10` low nibble is
copied, not authored), that the count and the array pointer cannot disagree about `N`,
that no canonical element address is recomputed, and that the addressability claim is
labelled **encoding/build-proven** and never runtime-proven.

**The one finding, and its resolution.** `_resolve_creation` ran the shared-root guard
twice - the second copy byte-identical to the first and unreachable, because the first
always raises. The reviewer marked it trivial and explicitly "not a gate". It is
resolved anyway, by a correction commit whose only change is the deletion of those nine
lines: `7a0abc57fea6c20799bbc9079d3544809fea41b8`, confirmed by the follow-up review
above. The deletion cannot change behaviour - the removed block could not execute - and
the focused files were re-run on the corrected tip (180 portable tests and the 30
ROM-gated tests, all green).

The reviewer made no edit to the candidate; the implementer made the prescribed
deletion, and the reviewer inspected it.

---

## Measurements behind the addressability answer

| Question | Answer | Evidence |
| --- | --- | --- |
| Can the expanded pointer array live above the original EOF? | YES | Built: file `[0x00800000, 0x0080000C)` = GBA `0x08800000`. |
| Can `root + 0x44` address it? | YES, encoding-proven | `+0x44` is a 4-byte little-endian GBA address on 452/452 canonical roots; the derivative's own word is `0x08800000`. |
| Can the created 24-byte record live above the original EOF? | YES | Built: file `[0x0080000C, 0x00800024)` = GBA `0x0880000C`. |
| Can an array element address that record? | YES, encoding-proven | Every element is a 4-byte little-endian GBA address on 735/735 canonical elements; the derivative's third element is `0x0880000C`. |
| Are the pointers full 32-bit GBA addresses? | YES | Full-census measurement; nothing masks, shifts or truncates either field. |

The line this ticket does **not** cross: **encoding-proven and build-proven is not
runtime-proven.** The retail engine following an above-EOF `+0x44` and array element
is the parent's later human-operated emulator proof, and no capability count moves on
the strength of this pass.

---

## Safety results

- **Canonical ROM unchanged.** SHA-256 `940ad5f0...f059e` verified before and after
  every run, and re-verified after the whole validation sequence. The canonical path
  is still refused as a build output target.
- **Existing transition records unchanged.** All 735 canonical records re-read from
  the derivative byte-identically, at identical addresses.
- **Existing transition ordering unchanged.** The created record is appended at
  `index = N`; indices `0..N-1` keep their records and their positions.
- **Unrelated maps unchanged.** Maps 39, 41 and 435 keep identical roots and records;
  within the original canonical span the byte diff (4 bytes) is confined to map 40's
  count and array pointer, and the only added bytes are the two allocated spans above
  EOF.
- **Source/template transition unchanged.** The template's bytes and address are
  identical in the derivative, and a build that both edits and copies it keeps the two
  independent in both directions.
- **No pointer-array overlap.** The canonical array is not rewritten; the expanded
  array is a distinct allocated span, and `plan_changes` refuses any overlap.
- **No allocator overlap.** Both spans are allocator-issued against the build-scoped
  reservation set, and the reservation set is threaded from every earlier domain.
- **No unresolved byte guessed.** `+0x13`, `+0x04`, `+0x00` and `+0x10`'s low nibble
  come from the named template; the project authors nothing there and the manifest
  says so field by field.
- **No proprietary artefact** was created, staged or committed; no ROM-derived
  fixture was added, and no ROM, save or state was copied into the repository.

---

## Follow-ups (recorded, not done here - follow-up debt, not blockers)

1. **The sibling ROM-gated helper takes the first glob match.**
   `tests/integration/test_map_transition_project_rom.py` and
   `tests/integration/test_map_transitions_rom.py` resolve the canonical image with
   `sorted(glob("roms/*Buu*.gba"))[0]`. This checkout also holds a warp-randomized
   derivative whose name sorts first, so those two files **skip silently** unless
   `LOGX_CANONICAL_ROM` is set - they passed here only because it was set explicitly.
   The new file hashes every candidate instead. The one-line fix belongs to whichever
   ticket next touches those files.
2. **The pre-existing stale-page failure.**
   `tests/unit/test_capability_registry.py::test_the_built_page_renders_the_registry_list`
   fails in this checkout because the git-ignored `dist/index.html` was built on
   2026-09-25 12:54, before the `resize` capability shipped that evening. It is
   unrelated to this ticket (`resize renders with the wrong state class`), it is
   already recorded as pre-existing, and it skips in a clean worktree.
3. **A map with no supported 566-class record of its own cannot gain a transition.**
   That is this ticket's deliberate fail-closed narrowing, and it is the one place a
   later ticket could widen the capability - but only with evidence for `+0x13` and
   the door gate bits, not by borrowing them from another map.
