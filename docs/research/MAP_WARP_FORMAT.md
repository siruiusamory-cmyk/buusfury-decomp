# MAP-WARP-FORMAT-001 - proving and productionizing the map-transition data model

STATUS: **COMPLETE, UNCOMMITTED, AWAITING REVIEW (2026-09-26).** Class: scoped
format and SDK authority pass. This is a **sub-pass of the parent capability
`MAP-WARPS-AND-CONNECTIONS-001`**, which stays active in
[`PROJECT_<local-state-name>`](PROJECT_<local-state-name>); the parent's Workbench surface, runtime proof and
capability advance are explicitly **not** in scope here and were not begun.

Baseline as given by the ticket: `fc8ba48b184a06fcff79dcbf3fc1d215e5af2046`
(which is 13 commits behind the checkout). Actual start SHA:
`82835a09c155f82f4af675f41e297fff0c365522`.

**public progress impact: NONE.** No capability ships, the registry stays at
**19 / 24 (79%)**, `src/data/capabilities.json` is untouched and `warps` remains
missing, and no published claim, blocker or questline entry changes wording - the
work is an SDK-internal data model, so no site edit is warranted.

Scope boundaries honoured: no Workbench UI, no runtime authoring proof, no
capability count change, no public-site change, no GUI serializer, no raw-offset
authoring API.

---

## 1. What was determined, and on what evidence

The transition family was **not re-derived**. It is read from
[`../research/LOGX_CONNECTOR_PROVENANCE.md`](../research/LOGX_CONNECTOR_PROVENANCE.md),
which established every field below from cited engine instructions, and it was
then re-measured through the production loader on the canonical image
(SHA-256 `940ad5f0…f059e`). No new reverse engineering was required and none was
done; no emulator was launched; the canonical image was opened read-only.

| Question | Answer | Status |
| --- | --- | --- |
| Record size | **24 bytes**, engine-accessed extent `+0x00..+0x17` | CONFIRMED (access widths + observed 24-byte spacing) |
| Source map identity | the `MapEntry` table index whose selector-1 root owns the array | CONFIRMED (route `MapEntry+0x2C` → word[0]) |
| Destination map identity | the two bytes at `+0x11` (high) and `+0x12` (low), resolved by the engine's own two-byte `MapEntry` key scan | CONFIRMED (735/735 resolve) |
| Source coordinates / region | four little-endian `u16` at `+0x08`, `+0x0A`, `+0x0C`, `+0x0E` forming **two ordered intervals** | CONFIRMED as ordered intervals (735/735 `A<=C`, `B<=D`, no degenerate pair) |
| Which interval is X, and in what unit | **UNRESOLVED** | no axis-naming engine comparison recovered; no axis name is used anywhere in the new API |
| Destination coordinates | **not in the record.** The engine adds `-112`/`-76` to a caller-supplied coordinate pair at `0x08008D52`/`0x08008D5C` | UNRESOLVED, and deliberately not modelled |
| Direction / type fields | `+0x00` is the class/constructor word the registry calls through `bx r1`; two values occur (`0x08007675` × 566, `0x080072CD` × 169) | CONFIRMED as a called function pointer; the **meaning of the two classes is UNRESOLVED**, so the word is carried and never authored |
| Other engine-read bytes | `+0x10`, `+0x13`, `+0x14`, `+0x16`, `+0x17` | CONFIRMED engine-read, semantics UNRESOLVED → preserved, not editable |
| `+0x04` | one invariant word on all 735 records | UNKNOWN; carried, and deliberately **not** validated (a constant read off one image is a corpus coincidence, not a rule) |
| Pointer / table ownership | root `+0x40` is the count, `+0x44` is a pointer to an array of 4-byte ROM pointers | CONFIRMED (`ldm r1,{r1,r2}` at `0x08009676`; `lsls r0,r4,#2` at `0x0801266E`) |
| Record count / terminator | the count is explicit; there is **no** terminator and no sentinel | CONFIRMED (the engine walks exactly `+0x40` elements) |
| Multiple transition families | **yes, two class variants within one record family**, tagged by `+0x00`; both share the identical 24-byte layout and field reads | CONFIRMED (full census) |
| Shared records | 735 references, 735 unique record addresses, **0 shared** in this image - a corpus fact, not a format rule, so a second claim is refused rather than assumed impossible | CONFIRMED |
| Addressability / alignment | every record address is 4-byte aligned and inside the image | CONFIRMED (735/735) |

**Not inferred to complete the schema.** The record has a schema for every byte
it physically contains, and every byte the evidence does not name is named
positionally (`byte_0x10_raw`, `word_0x14_raw`, …) and is not editable. No
"entry point", "facing", "script" or "effect" field was invented, and the
LOGExtractor `X += 8` viewer adjustment was not promoted into data - the
provenance document found no engine counterpart and it is not needed to resolve a
destination.

## 2. The supported family, and what fails closed

**Supported family:** the 24-byte transition record a map's **selector-1 root**
reaches through the root's `+0x40` count / `+0x44` array pair, restricted to the
two class words the canonical corpus measured. This family is enumerable,
semantically understood at the field level, used by ordinary retail maps (348 of
452 maps carry at least one; 735 records in total), and safe to round-trip
byte-identically.

The two class variants are supported **for reading, validation and round-trip**,
because the layout and the engine's field reads are identical for both and the
class word is carried rather than interpreted. They are **not** authorable. A
record whose class word is neither measured value is refused as an unsupported
form, and so is every other structure that is not this one.

Refused, each before any plan can exist:

- a class word outside `{0x08007675, 0x080072CD}`;
- a region whose intervals are unordered or degenerate;
- a destination key that resolves to no map in the table;
- two maps in the table sharing one two-byte lookup key (the engine's scan
  returns the first match, so such a destination would be ambiguous);
- a selector-1 source or root that is null, unaligned or outside the image;
- a root count and array pointer that are not null together;
- an array element that is unaligned, outside the image, or points at a record
  address that is unaligned, outside the image, or whose 24-byte extent runs past
  the image end;
- one record address reached by two maps;
- two records whose 24-byte extents overlap.

**No universal warp support is claimed.** A transition reached by another root
route, or tagged by another class word, is not addressable through this authority
at all.

## 3. Production authority

One authority, and no second path.

| File | Role |
| --- | --- |
| `tools/webfoot/formats/map_transitions.py` | the pure codec: the 24-byte layout, `TransitionRecord`, `TransitionRegion`, byte-exact `from_bytes`/`to_bytes`, the two controlled edits, and the fail-closed `validate()` |
| `tools/webfoot/map_transitions.py` | the SDK authority: enumeration, destination resolution, semantic identity, staged edits, `changes()` and `plan()` |
| `tests/unit/test_map_transitions.py` | 54 portable tests over a synthetic image assembled from the measured format |
| `tests/integration/test_map_transitions_rom.py` | 15 ROM-gated tests against the canonical image |

The authority composes with what already exists instead of restating it: the
selector-1 route, the root offsets and the `MapEntry` source field come from
`formats.map_graphics`; the `MapEntry` record and its table range come from
`formats.map_entry`; `MapIdentity` comes from `webfoot.maps`; the write path is
`webfoot.write`'s one `plan_changes`. A module-level guard fails if
`map_entry`'s layout ever stops placing the two-byte lookup key at `+0x00`/
`+0x01`, so this module cannot silently disagree with the record it reads.

The public authoring model names no offset and no address:

```python
transitions = load_map_transitions(rom_path, catalog)
identity = TransitionIdentity(MapIdentity(39), 1)
transitions.for_map(MapIdentity(39))          # enumerate
transitions.destination(identity)             # -> MapIdentity(40)
transitions.set_region(identity, region)      # controlled coordinate edit
transitions.set_destination(identity, MapIdentity(38))
plan = transitions.plan()
```

Editable fields are exactly two, each a self-contained fixed-width value the
engine's own reads establish: the destination `MapEntry` key, and the record's
two ordered interval pairs. Editing a pointer or a count is refused, for the
reason `webfoot.maps` refuses them - it is relocation, and no verified profile
authorizes it.

## 4. Semantic identity

**Identity is `(source map identity, index within that map's own array)`**, and
nothing else. It carries no ROM address, no file offset and no runtime address:
the record's `record_address`, `element_address` and `file_offset` live on
`TransitionEntry` as provenance for the build, never on the identity. A
retarget is a fixed-width in-place overwrite, so the array does not move and the
index stays valid; the addressable spelling is
`map:0039/transition:0001`.

The index is the element index in the `+0x44` array. The engine walks that array
descending; the identity uses the array position, and the engine's consumption
order is recorded as an observation about the walk rather than as part of
identity.

## 5. Round trip and controlled serialization

`changes()` encodes **every** record, not only the edited one, so the round trip
is proved by construction: an untouched record re-encodes to exactly its
original bytes and `plan_changes` drops it as a no-op. The root's count, the
pointer array and its elements are never written, so they are preserved by never
being touched.

Measured on the canonical image:

| Property | Result |
| --- | --- |
| Canonical records enumerated | **735** across **452** map identities (348 carry at least one) |
| Byte-exact unchanged round trip | **735 / 735** |
| Destination resolutions | **735 / 735**; no unresolved key |
| Class census | `0x08007675` × 566, `0x080072CD` × 169 |
| Self-link records | 9 records on 3 maps (125, 126, 127) |
| Unchanged pass emits differing bytes | **0** |
| Controlled destination edit (map:0039/transition:0001) | exactly the two key bytes at record `+0x11`/`+0x12` change |
| Controlled region edit (same record) | exactly the eight bytes at record `+0x08..+0x0F` change |
| Unrelated records after either edit | byte-identical |

## 6. Coordinates are load-bearing, and are not axis-named

The selected case is `map:0039/transition:0001`: region intervals
`(592, 601)` and `(136, 241)` on a record whose destination key is `010C`. All
four endpoints are distinct, the intervals are different lengths (9 and 105), so
the region is **non-square and asymmetric** and a transposition of either
interval, or of either interval's ends, changes both the decoded values and the
bytes. `tests/integration/test_map_transitions_rom.py::test_the_region_is_asymmetric_so_a_transposition_is_load_bearing`
and its portable sibling assert that shape explicitly.

Because no engine comparison was recovered that names the axes, the API calls
them `first` and `second` and does **not** call them X and Y. That is the honest
reading of claim 13 in the provenance document, and it is why an "X/Y swap"
mutation is caught by value rather than by an axis name.

## 7. Mutations

Four source mutations, applied and reverted with
`build/map-warp-format-001/mutate.py` (ignored scratch), each run against the
named nodes it must break.

| # | Mutation | Named node | Result |
| --- | --- | --- | --- |
| **M1** | `TransitionRecord.region` returns the two intervals transposed | `tests/unit/test_map_transitions.py::test_the_region_decodes_positionally_and_an_axis_swap_is_load_bearing`; `tests/integration/test_map_transitions_rom.py::test_the_region_is_asymmetric_so_a_transposition_is_load_bearing` | **2 failed** - coordinate regression fails |
| **M2** | `with_destination_key` writes the destination into `+0x10`/`+0x13` instead of the key bytes | `tests/unit/test_map_transitions.py::test_a_controlled_destination_edit_changes_only_the_two_key_bytes`; `tests/integration/test_map_transitions_rom.py::test_a_controlled_destination_edit_serializes_correctly` | **2 failed** - semantic regression fails |
| **M3** | `ARRAY_ELEMENT_WIDTH` `4 → 8` (the array stride) | `tests/integration/test_map_transitions_rom.py::test_the_canonical_transition_corpus_is_enumerated_canonically` (ERROR: `map:0034 element 1 points at 0x000C1043, which is not an aligned transition record address`); `tests/unit/test_map_transitions.py::test_the_record_is_twenty_four_bytes_of_engine_read_fields` (`assert 8 == 4`); `::test_the_corpus_enumerates_in_map_then_index_order` (`map:0002 element 1 points at 0x00000000`) | **2 failed, 1 error** - enumeration regression fails |
| **M3B** | `TRANSITION_SIZE` `24 → 32` (the record's own extent/stride) | both test files | **collection error in both** - the declared extent and the packer disagree, so no record can be read at all |
| **M4** | `validate()` no longer refuses an unmeasured class word | `tests/unit/test_map_transitions.py::test_an_unmeasured_class_word_is_refused` (6 parameters); `::test_an_unsupported_record_fails_the_whole_load` | **7 failed** - fail-closed regression fails |

No repository-wide mutation tooling was used; the harness is a single scratch
script with an explicit original/mutated text pair per mutation, and every file
was restored and re-verified afterwards.

## 8. Validation

Every command names explicit files or nodes. The broad suite was **not** run; CI
owns that when the parent capability branch is pushed.

| Command | Result |
| --- | --- |
| `pytest tests/unit/test_map_transitions.py` | **54 passed** |
| `pytest tests/integration/test_map_transitions_rom.py` | **15 passed** |
| `pytest tests/unit/test_map_transitions.py tests/unit/test_maps.py tests/unit/test_map_entry.py tests/unit/test_output_safety.py tests/unit/test_test_gates.py` | **116 passed** |
| `pytest tests/integration/test_map_transitions_rom.py tests/integration/test_logx_connector_rom.py` | **45 passed** |
| `pytest tests/integration/test_local_maps_rom.py` | **44 passed** (3 m 39 s) |
| `pytest tests/unit/test_workflow_migration.py tests/unit/test_capability_registry.py tests/unit/test_decisions_and_journeys.py tests/unit/test_code_review_workflow.py` | **51 passed, 1 failed** - the failure is pre-existing and not ticket-caused, see below |
| `git diff --check` (new files registered with `git add -N`, then unstaged) | clean |

**The one documentation-gate failure is not ticket-caused.**
`tests/unit/test_capability_registry.py::test_the_built_page_renders_the_registry_list`
fails with `resize renders with the wrong state class`. It reads only
`src/data/capabilities.json` and the git-ignored `dist/index.html`; the registry
says `resize` is shipped (MAP-RESIZE-AND-LAYERS-001) while the local page still
marks it todo. `dist/` is ignored build output (`.gitignore` line 33) last
written 2026-09-25 12:54, before that merge, and neither file is modified by this
ticket. Left as found rather than rebuilt, because rebuilding the site is
unrelated to this pass - and rebuilding it would be a public-site change, which
this ticket forbids.

The portable tests are ROM-free and use a synthetic image assembled from the
measured format. That fixture writes its layout with the **measured literals**,
not with the implementation's constants, so a mutation to either constant is
detected rather than silently followed - which is what M3 above demonstrates.

## 9. ROM, save and repository safety

- The canonical image was opened read-only on every path. Its SHA-256 is
  `940ad5f0…f059e` after every run, asserted in
  `test_the_canonical_rom_is_unchanged_and_refused_as_a_write_target`.
- The one mutated image is produced **in memory** by `webfoot.write.apply_plan`
  and is never emitted to disk.
- The canonical input is refused as a write target, by the shared write policy,
  before any byte is read: `emit_image(LOCAL_ROM, LOCAL_ROM, plan)` raises
  `OutputPathError`.
- No save, state, capture or memory dump was created or modified; no emulator was
  launched.
- No ROM-derived fixture is committed. No ROM, commercial content, extracted
  blob or generated artefact is staged.
- The four new files are **untracked and uncommitted**, as this pass requires.
  Nothing existing was modified.

## 10. What this pass did not do, and the handoffs

- **No Workbench surface.** No warp editor, no map overlay, no drawing of these
  records. The parent ticket's `PROJECT_<local-state-name>` requirement 3 is untouched.
- **No runtime proof.** The parent's human-operated leave-and-re-enter capture is
  untouched. The outstanding runtime question is still the one the provenance
  document hands off: whether the `+0x08` block is tested against a player
  position at run time, and when.
- **No count change.** `warps` is still missing in the registry; the parent
  ticket still owns 20 / 24.
- **No CLI surface** was added, deliberately: `map connections` already exists
  and reports the *slot-array* graph from `webfoot.maps`, whose destinations are
  explicitly `None`. Adding a second surface under a colliding name inside a
  scoped format pass would be a naming hazard, and the ticket's required surface
  is the SDK authority, which is complete.
- **Still UNRESOLVED, and now carried rather than guessed:** the meaning of the
  two class words; which region interval is horizontal and in what unit; the
  semantics of `+0x10`, `+0x13`, `+0x14`, `+0x16`, `+0x17`; the invariant word at
  `+0x04`; the LOGExtractor `+8` adjustment's origin.

**Next:** return for review. Do not begin the Workbench warp editor from this
pass.
