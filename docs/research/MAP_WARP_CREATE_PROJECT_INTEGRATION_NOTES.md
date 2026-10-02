# Creating a transition through the project and the build: integration notes

The condensed record of the transition-creation pass: what shipped, the
addressability answer and its limit, and the preserved follow-up debt.

## Scope

Advance the creation half of the parent's Required Work 1 and 2: let a project
create a supported selector-1 transition the canonical image does not contain, and
let the normal build materialize it - without a ROM offset in the project, without a
second serializer, and without guessing an `UNRESOLVED` field.

## What shipped

The first transition domain anywhere in the toolkit that allocates, and the first
writer of `root + 0x40` and `root + 0x44`:

* **Durable identity** `map:NNNN/transition:<name>` - a source map key and an
  authored name, with **no** address and **no** array index, because the index a
  created record will occupy does not exist until a build appends it.
* **A same-map 566-class template.** The created record is composed over a named
  canonical 566-class template of the same source map: the project authors the
  region, destination key, arrival pair and `+0x10`'s high nibble; the template
  supplies the class word, the invariant word, `+0x13` and `+0x10`'s low nibble, and
  the manifest publishes every field's source. A map with no supported 566-class
  record of its own is refused with that reason rather than initialized from another
  map's unresolved bytes - the deliberate fail-closed narrowing this sub-pass chose.
* **A sixth `maps/` document**, `maps/transition_creations.toml`, kept separate from
  `maps/transitions.toml` because removing the last transition edit deletes that
  document; a creation stored beside an edit would be destroyed by an author undoing
  an unrelated retarget.
* **Deterministic allocation above canonical EOF**: a new 24-byte record and the
  expanded `root + 0x44` array, both `EXPANDED_ONLY`; map 40's `root + 0x40` is
  rewritten from 2 to 3. Existing transitions keep their records, addresses and
  order, and the canonical array is left untouched at its own address.
* **A sharing guard that runs first**, because `root + 0x40`/`+0x44` live on the
  root and 11 canonical roots serve more than one map; the refusal names the real
  reason rather than the symptom.

## Addressability answer, and its limit

The build places the expanded array at file `0x00800000` (GBA `0x08800000`) and the
new record at file `0x0080000C` (GBA `0x0880000C`), both above the original 8 MiB
EOF. A full census measured every canonical `+0x44` field and every array element as
a full 32-bit little-endian GBA address (452/452 roots, 735/735 elements), so the
answer is **BUILD-PROVEN / ENCODING-PROVEN** and explicitly **not runtime-proven**.
The line this sub-pass did not cross was recorded rather than blurred: encoding-proven
and build-proven is not runtime-proven, and no capability count moved on this pass's
strength. `MAP-WARP-CREATE-RUNTIME-001` later supplied that runtime proof.

## Independent verification

Range reviewed `3d8d373beb931ad4275f8edabfa7426d07d2a7cf..282fb401ee86de6e5ce81b8e460f69f660b852bc`, an independent local review headless, independent context; job
`the review job`.

**Verdict: `APPROVE` - no blocking or major findings, one trivial non-blocking
finding.** The finding was a duplicated, unreachable shared-root guard in
`_resolve_creation`; it was resolved by a correction commit whose only change is the
deletion of those nine lines, `ffec6aac8b4b3b5b6d573af9e4bff7342616ad2e`, and the
verification pass confirmed by a follow-up pass (`the review job`, range
`fde0e4023ce36c7d5f3d350cb72a9ef350f1f265..ffec6aac8b4b3b5b6d573af9e4bff7342616ad2e`) that the verdict stands for the corrected tip. No reviewed commit
was amended. The verification pass reproduced both focused suites green, re-verified the
canonical ROM hash, and independently confirmed the aliasing refusal cannot be
bypassed, that the count and the array pointer cannot disagree, and that the
addressability claim is labelled encoding/build-proven and never runtime-proven.

## Lifecycle and integration

Baseline `3d8d373beb931ad4275f8edabfa7426d07d2a7cf`; implementation
`282fb401ee86de6e5ce81b8e460f69f660b852bc`; frozen reviewed tip `ffec6aac8b4b3b5b6d573af9e4bff7342616ad2e`; pushed
tip `2804e4fd007e1eb9b89b331313f8b62a8b667720`; opened as **MR !94**, CI pipeline
`2885987621` **SUCCESS** (`test-sdk` 3329 passed / 12 skipped), and merged as
`aea91c9ad6c811bffd450d5d9275c182c06e640f` with no squash and no amend. The merged
content is byte-identical to the reviewed tip over all twelve paths, and every cited
SHA is an ancestor of `origin/master`.

## Limitations and follow-up debt preserved

* **Creation is build-proven, not runtime-proven, at this pass.** The above-EOF
  consumption by the retail engine was the next sub-pass's job, and no count moved
  on this pass.
* **A map with no supported 566-class record of its own cannot gain a transition.**
  That is the deliberate fail-closed narrowing; a later record could widen it only
  with evidence for `+0x13` and the door gate bits, not by borrowing them from
  another map.
* **The sibling ROM-gated helpers take the first glob match.**
  `tests/integration/test_map_transition_project_rom.py` and
  `tests/integration/test_map_transitions_rom.py` resolve the canonical image with
  `sorted(glob("roms/*Buu*.gba"))[0]`, so in a checkout holding a warp-randomized
  derivative they skip silently unless `LOGX_CANONICAL_ROM` is set. The one-line fix
  belongs to whichever record next touches those files.
* **A pre-existing stale-page failure** in
  `tests/unit/test_capability_registry.py::test_the_built_page_renders_the_registry_list`
  is unrelated to this sub-pass and is already recorded as pre-existing.

## Test-policy deviation

**A manual broad-suite run was made ONCE IN ERROR against the standing policy and is
NOT repeated.** `python -m pytest tests` reported 3332 passed, 8 skipped and 1
pre-existing stale-dist failure. The number is recorded as history, not as evidence:
the focused named files are this sub-pass's evidence. The earlier integration record
for this branch reports the same deviation in the same terms.

## Stop

Stopped after the merge. The Workbench creation surface and the human-operated
runtime proof of a created transition remained; `MAP-WARP-CREATE-WORKBENCH-001` and
`MAP-WARP-CREATE-RUNTIME-001` followed, and the parent's own closeout states the
final result.
