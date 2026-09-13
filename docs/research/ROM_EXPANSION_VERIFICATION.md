# ROM-EXPAND-001: Runtime-Prove Expanded ROM Allocation with Authored Dialogue

## Objective

Prove or refute that the retail Buu's Fury engine can consume a compressed
resource whose pointer targets generated ROM expansion space. The acceptance
payload is the already-valid selector-1 authored replacement “Nice work,
Goku!”; the persistent record and packed handle remain unchanged.

This blocks the SDK from authoring compressed NPC dialogue whose deterministic
recompression exceeds its retail allocation. Minimum evidence: a separate
expanded generated ROM, static proof of the relocated container, and mGBA
observation of the normal retail dialogue engine displaying the authored line.

## Context Delta

- Continuation point: [TEXT-HANDLE-002 closure](archive/TEXT-HANDLE-002-COMPLETE.md).
- Canonical Buu profile SHA-256:
  940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e.
  It is 0x800000 bytes (8 MiB) and remains read-only.
- DIALOGUE-AUTHOR-001 established selector 1’s source container at ROM
  0x087A04F0 / file 0x7A04F0, allocation [0x7A04F0, 0x7A46C8) (16,856
  bytes); the next container begins at that exclusive end.
- Rebuilding selector 1 with “Good luck, Goku!” replaced by “Nice work,
  Goku!” preserves its 0x20-byte decoded record and deterministically produces
  17,932 packed bytes: an in-place overflow of 1,076 bytes.
- The authoritative seven-container table is 0x087B5B64. Patch only selector
  1’s entry. Packed handle 0x02002641 remains selector 1, decoded start
  0x132, decoded length 0x20.

## Required Work

1. Record branch, HEAD, initial dirty/staged state, governing files read,
   atlas digest, canonical-ROM and fixture hashes, existing allocation/build
   architecture, and DIALOGUE-AUTHOR-001 compression result.
2. Before production changes, record focused authoritative platform research:
   normal GBA ROM addressability, mapping above 8 MiB, offset 0x00800000 to
   ROM address 0x08800000, image-sizing/power-of-two requirements, and
   emulator/flash-cart caveats. Separate documentation from project proof.
3. Search atlas/static material narrowly for an obvious blocker: 8 MiB masking
   or bounds, high-address truncation, or decoder pointer-width constraints.
   Do not claim exhaustive absence. If no blocker, run the bounded experiment.
4. From verified canonical bytes, produce a separate ignored ROM with the
   smallest conventional expansion size justified by platform evidence and
   deterministic platform-appropriate padding. Place the exact validated
   selector-1 packed container in expansion capacity and patch only its table
   word to the corresponding GBA ROM address. Do not change the dialogue
   record, packed handle, offsets, length, or other six table entries.
5. Fail closed before launch unless static validation proves deterministic size
   and padding; canonical prefix unchanged except the intended table word;
   complete relocated bytes; correct pointer conversion; generated-pointer
   decompression equals the authored stream; decoded 0x132..0x152 is authored;
   all other decoded bytes, pointers/resources, handle and record are intact.
6. With the tracked runtime launcher/client and private deterministic fixture,
   boot the generated ROM and trigger the dialogue normally. Observe “Nice
   work, Goku!” twice if practical and reload the fixture once if cheap. Where
   practical, capture the same ROM record/handle, selector, relocated pointer,
   decoded range, and displayed text.
7. Only after runtime success, add the smallest shared production foundation:
   an explicit generated-expansion region alongside retail owned regions,
   using the existing build-scoped shared allocator, reservations, and
   authoritative final overlap detection. Model input/output image sizes,
   range, padding, allocations and collisions. Generated capacity is not
   retail VERIFIED_FREE and must not extend the canonical retail atlas.
8. Route compressed-dialogue overflow through that shared allocator:
   recompress; reject in-place placement; allocate expansion capacity;
   relocate the container; repoint selector 1; build; repeat runtime
   acceptance. No dialogue-private allocator or manual address GUI.

## Runtime Inputs

Use only the trusted canonical ROM and established deterministic private
fixture. Locate and hash the fixture before use; preserve ROM, saves and states
read-only. Generated ROMs, output, captures and proprietary bytes remain
ignored/untracked. Verify canonical identity before and after each experiment.

## Scope Boundaries

- Expansion proof is primary. Do not implement bank repacking, retail-bank
  repacking, unrelated decoder research, or another strategy unless expansion
  is measured as refuted or unsuitable.
- Do not fabricate expanded coverage in the canonical retail atlas. ROM Bible
  impact is NONE by default.
- mGBA proof is mandatory. Document hardware compatibility evidence and
  remaining validation, but do not claim real-hardware proof without it.

## Ticket-Specific Validation

Focused tests cover sizing, deterministic padding, bounds, reservations and
overlap, source/output separation, expansion pointer conversion, relocated
round trip, canonical-prefix preservation, deterministic builds, and
insufficient-capacity failure. Include ROM-gated proof that the overflowed
dialogue relocates, decodes, preserves its handle, and leaves canonical input
unchanged. Add discriminating tests for critical safety bounds.

Run the warranted broad integration gate once after production code freezes.

## Required Review

An independent reviewer must inspect the frozen allocation/build/dialogue diff,
surrounding code, tests, evidence and generated-ROM validation. The review
explicitly covers address conversion, sizing, allocation bounds, overlap
prevention, padding determinism, source protection, atlas semantics, dialogue
integration, and out-of-range-write tests. Record and resolve the template
verdict.

## Public Progress

If expansion is runtime-proven and unblocks authored compressed NPC dialogue,
public progress impact is UPDATED. Update capacity and dialogue milestones,
the next current blocker and every blocker field; validate, build, deploy and
verify the live site. Overall percentage remains an owner decision. Otherwise
record NONE with the required reason.

## Completion Criteria

Outcome A: mGBA displays “Nice work, Goku!” through the retail dialogue engine
from the relocated expansion-space resource. Record resource access as
RUNTIME-PROVEN, then finish minimal shared allocator and dialogue integration.

Outcome B: the engine cannot consume the expanded address. Record resource
access as REFUTED and the exact measured failure; do not speculate or overwrite
retail resources.

Outcome C: a platform/build-image issue blocks a safe experiment. Record the
exact blocker and do not silently fall back to retail-resource overwrite.

## Final Report Requirements

Include identity; platform evidence; experimental layout; relocation details;
static/runtime proof; allocator design; dialogue integration; focused,
ROM-gated, mutation and broad validation; review; canonical/save/state/artifact
and Git safety; atlas and ROM Bible impact; public progress; and exactly one
next measured authoring blocker.

Finally print:

    EXPANDED ROM RESOURCE ACCESS: RUNTIME-PROVEN YES/NO
    SHARED EXPANSION ALLOCATOR: SUPPORTED YES/NO
    AUTHORED COMPRESSED NPC DIALOGUE: RUNTIME-PROVEN YES/NO
    DIALOGUE CAPACITY BLOCKER: CLOSED YES/NO
    CANONICAL RETAIL ROM UNCHANGED: YES/NO
    PUBLIC AUTHORING FRONTIER MOVED: YES/NO

## Stop

Stop after Outcome A, B or C and required reporting. Do not begin TEXT-HANDLE-003.

## Result: Outcome A - DELIVERED

Delivered in commit `9bf88f0` ("Add shared generated ROM expansion
allocation"). The retail Buu's Fury engine consumed a compressed-dialogue
container whose authoritative table pointer was relocated into generated ROM
expansion space, and the shared production allocator + dialogue integration
followed. Full evidence: `docs/research/ROM_EXPANSION.md` (committed in the same
commit).

### Readout

    EXPANDED ROM RESOURCE ACCESS: RUNTIME-PROVEN YES
    SHARED EXPANSION ALLOCATOR: SUPPORTED YES
    DIALOGUE IN NORMAL PROJECT BUILD: YES
    SINGLE BUILD-SCOPED RESERVATION SET: YES
    EXPANSION ALLOCATION PROVENANCE: YES
    AUTHORED COMPRESSED NPC DIALOGUE: RUNTIME-PROVEN YES
    DIALOGUE CAPACITY BLOCKER: CLOSED YES
    CANONICAL RETAIL ROM UNCHANGED: YES
    INDEPENDENT REVIEW: PASS

### Evidence per line

- **EXPANDED ROM RESOURCE ACCESS / AUTHORED COMPRESSED NPC DIALOGUE:
  RUNTIME-PROVEN.** `docs/research/ROM_EXPANSION.md` records the mGBA 0.11 run:
  the retail consumer at `0x08012240` read packed handle `0x02002641`, selector
  1, and the relocated pointer `0x08800000`, and the deterministic-fixture
  snapshot showed "Nice work, Goku!" in the normal retail dialogue box. This is
  the ticket's stated runtime outcome, backed on disk by that committed research
  doc; the mGBA session was not independently re-run during this closure pass, so
  the runtime proof rests on the recorded capture, not on a fresh run.
- **SHARED EXPANSION ALLOCATOR: SUPPORTED / SINGLE BUILD-SCOPED RESERVATION
  SET.** `tools/webfoot/build.py` routes the authored dialogue into the SAME
  merged reserved set as every other domain (`reserved += dialogue_reserved`);
  overlap is a hard error rather than last-writer-wins.
- **DIALOGUE IN NORMAL PROJECT BUILD.** `tools/webfoot/build.py`
  `materialize_dialogues(...)` runs in the normal build path;
  `tools/webfoot/compressed_dialogue.py` rejects in-place placement on overflow,
  allocates expansion capacity, relocates the container, and repoints selector 1.
- **EXPANSION ALLOCATION PROVENANCE.** `tools/webfoot/write.py` carries a
  provenance record ("Why one generated-image span exists") with resource,
  source range, and hashes; `compressed_dialogue.py` threads `expansion_evidence`
  through the allocation.
- **CANONICAL RETAIL ROM UNCHANGED.** `generated_expansion` (`profile.py`) is a
  separate generated-image declaration, not stored in `free_regions`; the write
  plan verifies the canonical source hash and size first and materializes a
  separate non-existent output path (`write.py`). Canonical SHA-256 `940ad5f0...`
  is unchanged; the `generated_expansion` output is a distinct 16 MiB image,
  SHA-256 `3ccbef45...`.
- **DIALOGUE CAPACITY BLOCKER: CLOSED.** Overflowing compressed dialogue (the
  17,932-byte / +1,076-byte overflow of selector 1) now relocates into expansion
  capacity through the shared allocator instead of failing closed.
- **INDEPENDENT REVIEW: PASS.** Recorded as the reviewed production architecture
  per Required Review above; this closure pass records the verdict as stated, it
  did not itself re-run the review.

Tests: `tests/unit/test_rom_expansion.py`,
`tests/integration/test_rom_expand_001.py`, `tests/unit/test_project_format.py`,
`tests/unit/test_mgba_capture.py`.

Shared integration is complete; no stale "shared integration unfinished" blocker
language applies. Public progress is reflected in `src/data/project.ts` (Phase 4
owns any further site edits, not this doc pass). The next authoring frontier is
GUI dialogue editing (WORKBENCH-002).
