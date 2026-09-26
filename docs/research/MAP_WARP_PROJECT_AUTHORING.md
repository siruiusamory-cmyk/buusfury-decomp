# MAP-WARP-PROJECT-AUTHORING-001 - persisting a semantic transition edit

STATUS: **RETURNED FOR REVIEW.** Class: scoped project-format, SDK-authority and
build-integration pass. This is a **sub-pass of the parent capability
`MAP-WARPS-AND-CONNECTIONS-001`**, which stays active and unshipped in
[`PROJECT_<local-state-name>`](PROJECT_<local-state-name>); the parent's Workbench surface, runtime proof,
allocation work and capability advance are explicitly **not** in scope here and
were not begun.

Baseline: `05870f1e9c90fc5ef83ddfd1fa69fdedb06f926a` (the ticket's stated baseline
and the actual start SHA - verified with `git rev-parse HEAD` on a clean tree, no
drift). This pass is **uncommitted and unstaged**; the frozen reviewed candidate is
recorded after the independent review gate.

**public progress impact: NONE.** No capability ships, the registry stays at
**19 / 24 (79%)**, `EDIT` stays **7 / 8**, `src/data/capabilities.json` is
untouched, `warps` remains missing, and no published claim, blocker or questline
entry changes wording. `docs/PROJECT_<local-state-name>` is deliberately **not** touched: no
baseline commit exists for this pass, the parent capability has not shipped, and the
closed predecessor sub-pass `MAP-WARP-FORMAT-001` recorded its state in its own
ticket record rather than in project state.

Scope boundaries honoured: no Workbench UI, no new transition creation, no
runtime/emulator proof, no capability count change, no public-site change, no
allocation, no relocation, no second serializer, no invented meaning for an
`UNRESOLVED` field, and no raw address required from the author.

---

## RETURN

```text
MAP-WARP-PROJECT-AUTHORING-001 - STATUS REPORT

BASELINE:
05870f1e9c90fc5ef83ddfd1fa69fdedb06f926a

PROJECT REPRESENTATION:
maps/transitions.toml - [transition."map:NNNN"."IIII"], one entry per edited
transition, each editable field stored as a prior/authored pair. No record bytes,
no offset, no address.

SEMANTIC IDENTITY:
TransitionIdentity(source_map, index) - the source MapEntry index plus the
position in that map's own root+0x44 array. The semantic key is
"map:NNNN/transition:IIII". No ROM offset is accepted from a project and none is
computed by it.

DESTINATION EDIT:
PASS - two key bytes, +0x11/+0x12 of the one named record.

REGION EDIT:
PASS - eight positional bytes, +0x08..+0x0F of the one named record.

SAVE/REOPEN:
PASS - create, save, close, reopen, same semantic edit, then build.

BUILD:
PASS - load by identity, verify the stored prior, apply through the authority,
validate, serialize the one record, emit provenance.

DETERMINISTIC REBUILD:
PASS - two builds of the same saved project are byte-identical in derivative and
manifest.

ALLOCATION:
NOT REQUIRED - the edit is a fixed-width in-place overwrite; the build requests no
free-space span and no generated expansion.

UNRESOLVED BYTE PRESERVATION:
PASS - +0x00, +0x04, +0x10, +0x13, +0x14, +0x16, +0x17 byte-identical in the
derivative.

UNRELATED RECORD SAFETY:
PASS - the other 734 canonical records are byte-identical, and nothing outside the
edited 24-byte extent moves at all.

NO-OP:
PASS - an entry whose authored value equals its stored prior emits no effective
change, no provenance and a byte-identical output.

M1-M4:
PASS - each mutation applied, the named test observed failing, the mutation
reverted.

MANUAL VALIDATION:
tests/unit/test_map_transition_project.py (60 passed, no ROM)
tests/integration/test_map_transition_project_rom.py (15 passed, canonical ROM
read-only)

BROAD SUITE:
RUN ONCE as the deliberate integration gate - see the validation section. Measured
4261 passed, 2 failed, 6 skipped in 1:26:11. Both failures are pre-existing at
05870f1 and not ticket-caused.

CANONICAL ROM:
UNCHANGED - SHA-256 940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e
before and after; refused as a write target.

PRODUCT CAPABILITY IMPACT:
NONE

DRAGONBYTE Z:
19 / 24 - 79%

NEXT:
RETURN FOR REVIEW
```

---

## 1. Project representation

`maps/transitions.toml`, owned by
[`tools/webfoot/project/model.py`](../../tools/webfoot/project/model.py) as
`TransitionEdits` / `AuthoredTransition`, and written and read by
`write_transition_edits` / `_read_transitions` on the same three-state rule every
other optional subsystem uses (absent means "authors no transition",
present-and-valid means it does, present-and-malformed is an error rather than an
empty edit set).

```toml
[transition."map:0039".0001]
prior_destination = "map:0040"
destination = "map:0041"
prior_region = [[592, 601], [136, 241]]
region = [[304, 960], [272, 544]]
```

Every element of the ticket's "expected information" is present and semantic:

| Expected information | Where it lives | Form |
| --- | --- | --- |
| transition semantic identity | the document position, `[transition."map:NNNN"."IIII"]` | source map key + array index |
| original/prior destination | `prior_destination` | durable `map:NNNN` key |
| authored destination | `destination` | durable `map:NNNN` key |
| original/prior region values | `prior_region` | two ordered `[low, high]` intervals, positional |
| authored region values | `region` | two ordered `[low, high]` intervals, positional |

**No raw address is required from the author, and none is storable.** The map key
is the same durable `map:NNNN` `maps/maps.toml` uses, the transition is named by
the position the engine's own array walk assigns, and the replacement is the
destination map's own lookup key. A pointer, a count and a file offset are all
refused for the reason the parent ticket refuses them: editing one moves a
structure this toolkit does not own. The written file is asserted to contain no
`0x`, no `offset`, no `address` and no `pointer`.

**Either editable group may be absent, and the pair is atomic.** `destination`
and `prior_destination` are stored together or not at all, and likewise for the
region. A field that is absent is not authored: its bytes come from the canonical
record at build time and are never derived from the project. That is what makes
"the author did not edit this" a property the build can prove rather than assume,
and it is why a destination-only entry stores no region at all.

**`prior_*` is stored, not merely derivable.** It is the value the record held,
so the document itself proves the image it was authored against - the same role
`AuthoredChunkEntry.prior` plays in `maps/chunks.toml`. A project whose stored
prior disagrees with the image is refused instead of reinterpreted.

**Unresolved record bytes are preserved by coming from the canonical authority.**
The project stores no record bytes at all. The 24-byte record's class word,
invariant word and five engine-read fields whose semantics are `UNRESOLVED` are
never re-serialized from a project value, so they cannot drift from the image; the
build's `changes()` re-encodes every record and `plan_changes` drops the untouched
ones as no-ops, which is what *proves* the round trip rather than assuming it.
Storing them would have been a second copy of the ROM able to disagree with the
first.

**The region is validated by the record codec itself.** `_region_from_document`
constructs
[`formats.map_transitions.TransitionRegion`](../../tools/webfoot/formats/map_transitions.py),
so the rule "two ordered, non-degenerate `u16` intervals" is stated once, in the
authority, and a project file cannot carry a region the build would refuse. No
axis name is invented: which interval is horizontal, and what the endpoints' unit
is, remain `UNRESOLVED` and are still stored positionally.

## 2. Semantic identity

The identity is
[`TransitionIdentity(source: MapIdentity, index: int)`](../../tools/webfoot/map_transitions.py),
whose string form is `map:0039/transition:0001`. It carries **no record address and
no file offset** - the field set is `{source, index}` and is asserted as such by the
predecessor's regression, which still passes.

The build reaches a record only through it:
`read_map_transitions(image, profile)` resolves the corpus, and
`corpus.entry(identity)` / `corpus.set_destination` / `corpus.set_region` are the
only accessors used. The project's `map:NNNN` keys are converted to `MapIdentity`
in exactly one place, `build._transition_requests`, and the array index is the
position in the map's own `root + 0x44` array, never a physical location.

`TransitionIdentity` keeps its total order, so a batch is applied in
`(source map, index)` order and two builds of the same project stage the same
edits in the same order.

## 3. Build

`build_project` gained one domain, in
[`build.py`](../../tools/webfoot/build.py), entered only when
`project.transitions` is non-empty. It performs exactly the five required steps:

1. **load canonical through `TransitionIdentity`** - `plan_transition_edits` calls
   `read_map_transitions(image, packaged_profile())`, the authority's own
   bytes-based loader, which is also what the file path now uses;
2. **apply the project semantic edit** - the stored prior is checked against the
   record the image actually holds, then the authored fields are staged through
   `MapTransitions.set_destination` and `MapTransitions.set_region`;
3. **validate through the existing authority** - those two methods refuse an
   unknown transition, an unknown destination map and an invalid region before
   anything is recorded, and `corpus.validate()` re-validates every record,
   edited and untouched, afterwards;
4. **serialize only the intended record bytes** - the bytes come from
   `MapTransitions.changes()`, whose only encoder is
   `TransitionRecord.to_bytes`. **No second serializer exists in the project
   layer or in the build layer**: `build.py` never constructs record bytes, and
   `project/model.py` never sees one;
5. **emit normal change/provenance information** - the changes merge into the one
   `plan_changes` call every other subsystem uses, and
   `TransitionEditProvenance` travels into the `WritePlan` and the `WriteManifest`
   beside `chunk_edits` and `structure_edits`.

**Fixed size: no allocation and no relocation.** The domain requests no span from
the profile's free regions, contributes nothing to the build-scoped reservation
set, produces no `generated_allocations` and needs no generated expansion. It is
the only build domain with that property, and the placement comment in `build.py`
says so. Nothing reads or writes the root's `+0x40` count or its `+0x44` array -
those bytes are not part of any change.

**`validate_project` runs the same authority**, through `_check_transitions`, so
an illegal edit is a named validation problem before anything is emitted. Both the
check and the build are gated on the canonical profile identity, so a
non-canonical image reports "would silently drop every authored transition" rather
than emitting an image that ignores the project.

## 4. Save / reopen

`map_transitions.set_transition_edits(project_dir, profile, canonical_bytes, edits)`
is the one authoring path, shaped like `map_paint.set_layout_cells`: validate the
whole batch against the canonical image first, load the project once, apply the
batch on top of what is committed, and write only when the result differs.
`read_transition_edits`, `remove_transition_edit` and the project writer complete
the surface. The stored prior is **read from the image by this SDK**, never taken
from the caller.

The required lifecycle is covered end to end on the canonical image by
`test_a_destination_edit_saves_reopens_and_builds_only_the_key_bytes` and its
region and combined siblings: create, save, close, reopen, compare the semantic
edit, build. **The reopened project depends on no previous derivative ROM and on no
physical record address** - the file names a map, an array index and two semantic
values, and `test_the_written_file_carries_no_address_and_no_offset` pins that.

## 5. Determinism

Nothing in the path consults the clock, a path, a directory order or a random
source. `TransitionEdits.to_document` emits both key levels zero-padded and sorted,
so lexical order is numeric order; `plan_transition_edits` iterates a
`TransitionIdentity`-sorted mapping; `plan_changes` orders by offset. Two builds of
the same saved project produce a byte-identical derivative **and** a byte-identical
manifest, asserted by `test_two_builds_of_the_same_project_are_byte_identical`.

## 6. Safety proofs

Every claim below is a named assertion in the two focused files, not an inference.

| Safety claim | Where it is proved |
| --- | --- |
| unrelated transition records unchanged | `test_every_unrelated_transition_record_is_byte_identical_in_the_derivative` - all 734 other records, compared against the canonical image |
| unresolved bytes in the edited record unchanged | `test_the_unresolved_bytes_of_the_edited_record_are_preserved` - `+0x00`, `+0x04`, `+0x10`, `+0x13`, `+0x14`, `+0x16`, `+0x17` |
| canonical ROM unchanged | `test_the_canonical_rom_is_unchanged_and_refused_as_a_write_target` - re-hashed before and after |
| canonical ROM refused as a write target | same test - `build_project(project, rom, rom, catalog)` raises `OutputPathError` |
| invalid semantic identity refuses | `test_an_identity_the_image_does_not_have_is_refused` (integration) and `test_an_unknown_transition_identity_is_refused` / `..._never_reaches_a_plan` (unit) |
| unsupported transition family refuses | `test_an_unsupported_record_family_refuses_the_whole_corpus` - a record whose class word is outside the two measured values fails the whole load, the plan and the staging |
| invalid destination refuses | `test_a_destination_the_table_does_not_declare_is_refused` (integration) and `test_a_batch_with_one_illegal_entry_writes_nothing` / `test_an_invalid_destination_is_refused` (unit) |
| invalid region refuses | `test_an_invalid_region_is_refused_when_the_project_is_read` (integration) and `test_the_record_codec_is_the_region_authority` (unit, 5 cases) |
| no-op edit emits no effective transition change | `test_a_no_op_project_emits_no_effective_transition_change` - byte-identical output, no `transition_edits` key, `changed_byte_count == 0` |
| a stale prior refuses | `test_a_prior_that_does_not_match_the_image_is_refused` - both `validate_project` and `build_project`, with no output written |

The non-square/asymmetric region case is load-bearing and is present in both
files. `MAP_39_SECOND` carries the documented asymmetric retail region
`(592, 601) x (136, 241)`, and the authored region is chosen so that **every one
of the eight encoded bytes differs** from the retail record's
(`0x0250 -> 0x0130`, `0x0088 -> 0x0110`, `0x0259 -> 0x03C0`, `0x00F1 -> 0x0220`).
A region that reused a byte would let a serializer that wrote only part of the
positional field pass.

## 7. Focused tests

Named files only; no broad manual suite was run.

| File | Result |
| --- | --- |
| `tests/unit/test_map_transition_project.py` | **60 passed** - no ROM, synthetic image from the predecessor's measured fixture |
| `tests/integration/test_map_transition_project_rom.py` | **15 passed** - canonical ROM opened read-only |
| `tests/unit/test_map_transitions.py` (predecessor, unchanged) | **54 passed** - preserved |
| `tests/unit/test_map_layout_project.py` (adjacent format) | **29 passed** - preserved |

The unit file covers project parse/write/reopen, destination persistence, region
persistence, destination + region together, the byte locality of a planned edit,
no-op, deterministic planning, invalid identity, unsupported record, invalid
destination, invalid region, unrelated-record preservation, prior verification,
the batch refusal, the prior-measured-from-the-image rule, and the
removal-on-set-back-to-base rule.

The integration file covers the canonical baseline build, destination locality,
region locality, combined locality, unrelated-record preservation, unresolved-byte
preservation, canonical-ROM safety, no-op, deterministic rebuild, manifest
provenance, stale prior, invalid identity, invalid destination, invalid region on
disk, and the staging refusal.

### The full-suite gate

This pass changes shared production code - `write.py`'s plan/manifest plumbing,
`build.py`'s domain sequencing, the project format, a semantic identity and the
build boundary - so the expensive gate is warranted rather than skipped, and it was
run **once**, deliberately, after the focused files were green:

```text
python -m pytest tests -q -p no:cacheprovider
4261 passed, 2 failed, 6 skipped in 5171.39s (1:26:11)
```

**Both failures are pre-existing at the baseline and are not ticket-caused.** Each
was established by evidence, not by assertion:

| Failure | Why it is not this ticket |
| --- | --- |
| `tests/integration/test_map_browser_rom.py::test_map_19_renders_the_accepted_terrain_field` | **Reproduced at the pristine baseline.** A clean `git worktree` at `05870f1e9c90fc5ef83ddfd1fa69fdedb06f926a` fails this one test with the *identical* digest mismatch (`1b386a509aad…9fc57` observed against the pinned `2ece490ffb79…4cfeec`). The pass touches no rendering code and `tests/integration/test_map_browser_rom.py` is unmodified. |
| `tests/unit/test_capability_registry.py::test_the_built_page_renders_the_registry_list` | A **stale git-ignored `dist/` build**. `dist/index.html` was last written 2026-09-25 12:54, while `resize` shipped later the same day (18:42), so the rendered page still says `is-todo` for a capability the registry reports as shipped. `git check-ignore` confirms `dist/` is untracked; the same test **skips** in the clean baseline worktree where no `dist/` exists. This is exactly the pre-existing failure the predecessor's review request records. `src/` is untouched by this pass. |

No failure is attributed to this diff, and no assertion was weakened to reach a
green number. The focused files were re-run after the gate and are unaffected.

## 8. Mutations

Each mutation was applied to the working tree, the named tests were run, the
failure was observed, and the mutation was then reverted. `git status` and
`git diff --stat` confirm the reverted files carry only the intended change.

| Mutation | Applied where | Observed failure |
| --- | --- | --- |
| **M1** drop the destination edit during project reopen | `project/model.py`, `AuthoredTransition.from_document` ignores `prior_destination`/`destination` | **3 failed**: `test_a_destination_edit_survives_save_and_reopen`, `test_a_destination_and_a_region_together_survive_save_and_reopen`, `test_a_destination_edit_saves_reopens_and_builds_only_the_key_bytes`. The reopen raises `ProjectValidationError` on the now-empty entry, so the edit cannot be silently lost. |
| **M2** drop the region edit during build | `map_transitions.py`, `plan_transition_edits` skips `set_region` | **4 failed**: `test_planning_a_region_edit_writes_the_positional_slots`, `test_planning_a_destination_and_a_region_together_writes_only_those_ten_bytes`, `test_the_provenance_answers_which_transition_changed_and_from_what`, `test_a_region_edit_saves_reopens_and_builds_only_the_region_bytes` (`assert [] == [8 offsets]`). |
| **M3** resolve by physical address instead of semantic identity | `map_transitions.py`, `set_transition_edits` keys the stored entry by `entry.file_offset` instead of the array index | **3 failed**: `test_set_transition_edits_persists_and_reopens`, `test_removing_a_transition_edit_un_authors_it`, `test_a_destination_edit_saves_reopens_and_builds_only_the_key_bytes` (`KeyError: (39, 1)`). |
| **M4** overwrite one unresolved byte while applying an edit | `formats/map_transitions.py`, `with_destination_key` also bumps `byte_0x13_raw` | **4 failed**: `test_planning_an_edit_rewrites_only_that_record_and_its_own_bytes`, `test_planning_a_destination_and_a_region_together_writes_only_those_ten_bytes`, `test_the_unresolved_bytes_of_the_edited_record_are_preserved` (`0x13: assert 1 == 0`), and the predecessor's `test_an_edit_never_touches_the_unresolved_fields` (`0x13: assert 2 == 1`). |

## 9. Provenance

`TransitionEditProvenance` is recorded in the existing `WriteManifest`, not in a
second manifest family, and answers from the manifest alone:

```json
{
  "identity": "map:0039/transition:0001",
  "source_map": 39,
  "index": 1,
  "file_offset": 2705736,
  "destination_changed": true,
  "prior_destination": "map:0040",
  "destination": "map:0041",
  "region_changed": true,
  "prior_region": [[592, 601], [136, 241]],
  "region": [[304, 960], [272, 544]]
}
```

* **which semantic transition changed** - `identity`, which carries no address;
* **prior destination -> authored destination** - the `prior_destination` /
  `destination` pair, as durable map keys;
* **prior region -> authored region** - the `prior_region` / `region` pair, in the
  record's own positional order with no axis name invented.

`file_offset` is present for the same reason `ChunkEditProvenance.template_address`
is: it says which bytes moved. It is deliberately **not** the author-facing
identity, and `test_the_manifest_records_the_semantic_identity_and_both_pairs`
asserts that the identity contains no `0x` while the change owned by that identity
carries the offset.

A group the author did not edit is reported as unchanged rather than restated, and
an entry whose authored value equals its prior produces no provenance entry at all.

## 10. What was not done

- **No Workbench surface.** Nothing under `tools/webfoot/workbench/` was touched,
  and no GUI serializer exists.
- **No new transition creation.** A count, a pointer array element and a root
  field are all untouched; only an existing record's two editable field groups can
  change, and the build's own byte diff shows that.
- **No runtime or emulator proof.** No emulator was launched and no savestate was
  read. This pass proves the project model, the build and the serialization; the
  retail engine consuming a warp remains the parent ticket's Required Work 4.
- **No capability count change.** `EDIT` stays 7 / 8 and DragonByte Z stays
  19 / 24 (79%). `warps` does not ship.
- **No public-site change.** `src/` is untouched.
- **No meaning invented for an `UNRESOLVED` field.** The class word, the invariant
  word and the five engine-read bytes keep their positional names and are not
  editable; the region is still stored positionally with no axis name.
- **No change to `tools/webfoot/formats/map_transitions.py`.** The codec that
  `MAP-WARP-FORMAT-001` proved is byte-for-byte unchanged.

## 11. Unresolved after this pass

These remain exactly as `MAP-WARP-FORMAT-001` recorded them and must not be
renamed or promoted: the class-word meanings, which interval is horizontal, the
interval unit, `+0x04`, `+0x10`, `+0x13`, `+0x14`, `+0x16`, `+0x17`, the
destination-position source, and the `+8` viewer adjustment origin. This pass adds
no new unknown; it also establishes no new semantics.

The parent's remaining Required Work - the Workbench transition surface, the
allocator/deferral question for any transition form that cannot be edited in place,
and the human-operated leave-and-re-enter runtime proof - is untouched.

## 12. Reproducing the validation

```powershell
# focused, no ROM required
python -m pytest tests/unit/test_map_transition_project.py -q

# focused, canonical ROM required (read-only); skips cleanly without it
python -m pytest tests/integration/test_map_transition_project_rom.py -q

# the deliberate full-suite gate (about 90 minutes); expect the two pre-existing
# failures named above and nothing else
python -m pytest tests -q -p no:cacheprovider
```

The integration file resolves the image from `roms/*Buu*.gba` and skips unless its
SHA-256 is the canonical
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`. Set a pytest
basetemp outside the work tree (or `TEMP`/`TMP`/`TMPDIR` accordingly): several
unrelated safety tests assert on repository boundaries, and an in-repo basetemp
makes them fail for a reason that has nothing to do with this diff.
