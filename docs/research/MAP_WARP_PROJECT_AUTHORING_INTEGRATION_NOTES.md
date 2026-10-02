# Persisting a semantic transition edit: integration notes

The condensed record of the project-authoring pass: the stored value, the build,
the acceptance measurements and the questions left open.

## Goal

Let a project persist a semantic edit to an **existing** supported transition and
let the production build apply it - without exposing a ROM offset to an author,
without a second serializer, and without allocating or relocating anything.

## What was implemented

| File | Role |
| --- | --- |
| `tools/webfoot/project/model.py` | `maps/transitions.toml`: `TransitionEdits` / `AuthoredTransition`, the prior/authored pair rules, the read/write/reopen path |
| `tools/webfoot/map_transitions.py` | authority additions: `read_map_transitions` bytes seam, `TransitionEdit`, `AuthoredTransitionEdit`, `plan_transition_edits`, and `read_transition_edits` / `set_transition_edits` / `remove_transition_edit` |
| `tools/webfoot/build.py` | `_transition_requests`, `_check_transitions`, and the one build domain that allocates nothing |
| `tools/webfoot/write.py` | `TransitionEditProvenance` and its `WritePlan` / `WriteManifest` / `plan_changes` / `emit_image` plumbing |
| `tests/unit/test_map_transition_project.py` | 60 portable tests over the predecessor's synthetic image |
| `tests/integration/test_map_transition_project_rom.py` | 15 ROM-gated tests, read-only |
| `MAP_WARP_PROJECT_AUTHORING.md` | the evidence record |

`tools/webfoot/formats/map_transitions.py` - the codec `MAP-WARP-FORMAT-001` proved
- is **byte-for-byte unchanged** by this pass.

### The stored value

```toml
[transition."map:0039".0001]
prior_destination = "map:0040"
destination = "map:0041"
prior_region = [[592, 601], [136, 241]]
region = [[304, 960], [272, 544]]
```

The identity is the document position: the durable `map:NNNN` key plus the index in
that map's own `root + 0x44` array. The destination is the destination map's own
lookup key. The region is four positional endpoints as two ordered intervals, with
no axis name and no unit invented. **No record byte, file offset or ROM address is
storable, and none is required from an author.**

Either editable group may be absent, and a group that is absent is **not authored**:
its bytes come from the canonical record and are never re-serialized from a project
value, so an untouched field is structurally incapable of changing. The `prior_*`
values are **measured by the SDK** from the canonical image, never asserted by a
caller, and the build re-checks them - so a project authored against a different
image fails closed instead of being reinterpreted. Setting a field back to the value
the base holds **removes** the pair rather than recording a pretend edit.

### The build

`build_project` gained one domain, entered only when the project authors a
transition. It loads the canonical record through `TransitionIdentity`, verifies the
stored prior, stages the authored fields through `MapTransitions.set_destination` /
`set_region`, re-validates the corpus, and takes the authority's own byte plan. The
only encoder is `TransitionRecord.to_bytes` reached through
`MapTransitions.changes()`; neither the project layer nor the build layer constructs
record bytes. The edit is a fixed-width overwrite of one 24-byte record, so it
requests no free-space span, joins no reservation set, produces no generated
allocation and writes no count or pointer. `validate_project` runs the same
authority, so every refusal is a named validation problem before anything is
emitted.

## Acceptance, as measured

| Criterion | Result |
| --- | --- |
| Project parse / write / reopen | **MET** - destination, region, and both together each survive save and reopen; the written file carries no `0x`, offset, address or pointer |
| Destination edit | **MET** - exactly `+0x11`/`+0x12` of the one named record |
| Region edit | **MET** - exactly `+0x08..+0x0F`, with an authored region whose **eight encoded bytes all differ** from the retail record's |
| Build | **MET** - load by identity, verify prior, apply, validate, serialize the one record, emit provenance |
| Deterministic rebuild | **MET** - derivative and manifest both byte-identical across two builds |
| Prior verification | **MET** - refuses in `validate_project` and `build_project`, writing nothing |
| Unresolved byte preservation | **MET** - `+0x00`, `+0x04`, `+0x10`, `+0x13`, `+0x14`, `+0x16`, `+0x17` |
| Unrelated record safety | **MET** - the other 734 canonical records byte-identical, and nothing outside the edited 24 bytes moves |
| No-op | **MET** - a hand-written pair whose authored value equals its prior emits no change, no provenance and a byte-identical output |
| No allocation / relocation | **MET** - no span, no reservation, no generated allocation, no count or pointer write |
| No second serializer | **MET** - one encoder, reached through the authority |
| No accidental transition creation | **MET** - only the two editable field groups of an existing record can change |
| Canonical ROM unchanged | **MET** - SHA-256 `940ad5f0…f059e` before and after; refused as a write target |
| Mutations M1-M4 | **MET** - 3, 4, 3 and 4 named tests observed failing respectively; every mutation reverted |

## Independent verification

One pass, independent context, `the local reviewer` headless in the frozen record worktree. Job
`cl-20260926-105014-a10dbc`, exit 0, about 376 s, verdict read from
`local_headless`.

**Verdict: `PASS` - zero blocking findings, zero non-blocking notes, four NOTEs.**
The verification pass ran the two named test files itself (60 + 15 passed) against the
canonical image, re-checked the image hash either side, and confirmed no second
serializer, no allocation, byte locality, preservation, determinism, the semantic
identity without an address, and no capability overclaim. Details and the NOTEs:
[`../MAP-WARP-PROJECT-AUTHORING-001-review.md`](../MAP-WARP-PROJECT-AUTHORING-001-review.md).

**Cloud review: NOT RUN - readable verdict unavailable.** `cloud_attach` is
UNAVAILABLE on this account, so a cloud session would have produced no locally
readable verdict; `require_readable_verdict` was enforced and the local channel used.

## Manual broad-suite run

**RUN ONCE IN ERROR AGAINST STANDING POLICY.** `python -m pytest tests` was run once
before this ruling and is **not repeated**: 4261 passed / 2 pre-existing failed /
6 skipped. Both failures are pre-existing at the baseline and not record-caused -
`test_map_browser_rom.py::test_map_19_renders_the_accepted_terrain_field` was
reproduced at `05870f1` in a clean worktree with an identical digest mismatch, and
`test_capability_registry.py::test_the_built_page_renders_the_registry_list` reads a
stale git-ignored `dist/`. The full number is recorded here as history, not as
evidence for this record: the focused gates it names are the evidence.

## Boundaries observed

No Workbench UI. No new transition creation. No runtime capture, emulator launch,
save or state write. No capability-registry or site change. No allocation, no
relocation, no second serializer, no raw-offset authoring API. No meaning invented
for an `UNRESOLVED` field. The canonical image was read-only throughout.

## Still UNRESOLVED

Unchanged from `MAP-WARP-FORMAT-001`: the meaning of the two constructor/class
words; which region interval is horizontal; the region endpoints' unit; the
invariant word at `+0x04`; the semantics of `+0x10`, `+0x13`, `+0x14`, `+0x16`,
`+0x17`; where the destination position comes from; the origin of the LOGExtractor
`+8` viewer adjustment. This pass added no new unknown and promoted no new semantic.
