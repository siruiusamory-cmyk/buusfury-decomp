# Variable-length replacement of compressed dialogue

Replacing an existing compressed-dialogue record with text of a different decoded
length through the production path: the measured result and its bounds.

Evidence document: [`ROM_DIALOGUE_VARIABLE_LENGTH.md`](ROM_DIALOGUE_VARIABLE_LENGTH.md).

record: [`ROM_DIALOGUE_VARIABLE_LENGTH.md`](ROM_DIALOGUE_VARIABLE_LENGTH.md).

## Objective

Prove that an existing compressed-dialogue record can be replaced by text of a
**different decoded length** through the production path: the durable handle is
re-authored, the decoded container is re-laid out, every word the engine reads as
a handle is repointed, the payload is repacked and relocated by the production
allocator, provenance records the change, a derivative reopen resolves the same
semantic record, and the retail engine displays the whole longer line.

Acceptance case: `goku-greeting`, retail `Good luck, Goku!` (32 decoded bytes),
authored `Hot take: SSJ3 is the worst form imo` (72 decoded bytes).

## Context and measurements

Numeric shape of a handle, the consumer's reading of it, and the container's
layout policy as measured here (each with its evidence in the research record):

- The durable handle is **authored**, not frozen: selector in bits 0-5, decoded
  start in bits 6-20, decoded length in bits 21-31, both offsets in halfwords,
  no reserved bits. Re-derived from the consumer at `0x08012240` - where two
  independent implementations agree - and corroborated structurally by the
  consumer's `0x10000` scratch buffer and its `0x1008` object with the inline
  string plus terminator.
- Selector 1's decoded container is a stream of consecutively placed records with
  **absolute** starts: 447 distinct records, 410 of 446 adjacent pairs
  consecutive, and exactly one record intersects `0x132..0x152` - the target
  itself. Growth therefore splices and shifts.
- The reference inventory is a **structure**: a record word whose byte `+0x02` is
  the dispatch key `0x05`, with the handle at `+0x04` (TEXT-HANDLE-001/002, both
  runtime-proven). Selector-1 words that merely *unpack* plausibly number 46,298
  distinct values over 59,491 occurrences; only 143 are ever read as handles.
- `0x02002641` has exactly three carrier sites (`0x781C4C`, `0x781CB0`,
  `0x781CFC`). Of the 443 distinct handles this edit supersedes, three values have
  15 occurrences outside the carrier structure; all 15 are data, none is in the
  dialog pool, and they are the M4 control.

## Runtime Inputs

- Canonical ROM `roms/Dragon Ball Z - Buu's Fury (U).gba`, SHA-256
  `940ad5f0...059e`, read-only, digest verified before and after every step.
- Private savestate `roms/Dragon Ball Z - Buu's Fury (U).ss1`, SHA-256
  `2D5740A8C54180D153024A11B0E4D1143306957AF55A3AD0664C71CF7D9A1AAB`, copied
  into the ignored run directory before use and never modified.
- mGBA 0.11 dev build at the path the tracked runner already names and verifies.

## Work split

Two read-only investigations were delegated: static disassembly of the consumer
chain at `0x08012240`, and an operational map of the Checkpoint D runtime
workflow. Both are cited in the research record. The permanent independent-review
gate applies (nontrivial code-bearing record).

## Scope Boundaries

- Do not bypass the handle contract (no disabled check, no manual payload write,
  no fabricated length, no hand-patched pointer, no goku-greeting-specific
  addresses in the general implementation).
- Do not rebuild the capacity/allocation infrastructure; use it.
- Do not widen the seven-container structural limit.
- Do not claim the length field's 4,094-byte maximum is runtime-safe.
- Do not run the broad suite; focused files and nodes only.
- No Workbench redesign; leave the capability headless if GUI integration would
  cross the deferred CQA gates.

## Validation

- Explicit test files/nodes only: handles, dialogue authoring, compressed-dialogue
  write guard, the new variable-length authoring file, allocation/provenance,
  write invariants, mGBA capture guards, and the two ROM-gated dialogue proofs.
- Mutation validation runs only the node expected to detect each mutation.
- `git diff --check` clean; canonical ROM digest verified before and after.
