# Buu placement reuse census (TOOLKIT-023)

Canonical ROM `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
(`Dragon Ball Z - Buu's Fury (U).gba`). Read-only; the ROM is untouched.

**Result: SAFE EXISTING PLACEMENT REUSE PATH: NO.**

All 1,442 map-owned placement records are `LIVE_MAP_OWNED`. No record is orphaned,
dead, padding, or repurposable. Every apparent reuse candidate was investigated and
refuted on positive evidence, not on absence of a reference.

## Census method

The census is fully static. It uses the production model, not a re-derived walk:

* run provenance: `tools/webfoot/data/placement_contracts.py` `runs` (240 entries,
  each `map_index -> (array_pointer, count)`)
* record codec: `tools/webfoot/formats/map_placements.py`
  (`iter_placement_offsets`, `read_placement_record`), size `0x1C + 4 * child_count`
* script roots and descriptors: the same contract's `roots` / `owned_descriptors`

Every count below is measured against the canonical image, not carried from a prior
ticket. Where a number matches a TOOLKIT-016/017 pin, that is a reproduction.

## 1,442 reconciliation

| Quantity | Measured |
| --- | --- |
| Declared runs | 240 |
| Records reached | **1,442** |
| Distinct record offsets | 1,442 (zero double-claims) |
| Total record bytes | 46,244 |
| `child_count` = 1 / 2 / 3 / 4 | 1,427 / 7 / 6 / 2 |
| Records matching the legacy 32-byte tail predicate | 1,337 |

Walking all 240 runs raises no `MapPlacementError`: no overlapping bodies, no
non-placement pointer inside a declared run, no record claimed by two maps.

### Classification totals

| Class | Count |
| --- | --- |
| `LIVE_MAP_OWNED` | **1,442** |
| `LIVE_REFERENCED` | 0 |
| `SHARED` | 0 |
| `ORPHAN_STATIC` | 0 |
| `UNKNOWN` | 0 |
| `REPURPOSABLE_CANDIDATE` | 0 |
| `REPURPOSABLE_CONFIRMED` | 0 |
| **Total** | **1,442** |

The classes are orthogonal; a record reached by a declared run is `LIVE_MAP_OWNED`
and is not counted again. Descriptor *sharing* is real but is not a separate liveness
class: 1,361 records share the null-handler descriptor `0x080555A0` and 81 hold a
private descriptor, and all 1,442 are map-owned either way.

## The 147-record delta

```
full census      1,442
historical corpus 1,295
                 -----
additional         147
```

The legacy 1,295 subset is reconstructed per TOOLKIT-017 by stopping each map's run
at the first old-tail mismatch, **not** by filtering the full census for the old tail.
That reproduces 1,295 exactly, leaving 147 across 30 maps.

| Property of the 147 | Measured |
| --- | --- |
| `child_count` = 1 / 2 / 3 / 4 | 132 / 7 / 6 / 2 |
| Descriptor handler `0x0800421D` (null) | 66 |
| Descriptor handler `0x0800421F` (**runs a script**) | **57** |
| Descriptor handler `0x0800424F` | 24 |
| Records that *do* match the legacy 32-byte tail shape | 42 |
| Records that are the last record of their run | 30 |

**The 147 are not dead space, and the evidence is unusually strong.** All 57
script-bearing placements, the most demonstrably live records in the whole corpus,
across exactly the 10 maps TOOLKIT-016 pinned (19, 21, 22, 240, 309, 325, 428, 430,
432, 437), lie inside the delta. So do all 24 `0x0800424F` records.

**Why the old codec missed them:** the TOOLKIT-008 walker required the fixed 32-byte
tail and truncated each run at the first record that did not match. It was a
prefix-truncation artifact, never a statement about use. 42 of the 147 match the
legacy tail shape perfectly and were still dropped, purely because a non-matching
record preceded them in the run. Historical absence carries no liveness information.

## 240-run accounting

Every run was decoded into its exact variable-length record sequence.

* 214 runs: record bodies are physically contiguous, no interior gap.
* 26 runs: contain interior holes, **1,604 bytes** total across **85 holes**.

The holes are the obvious "free space inside a run" hypothesis. They are not free.

| Hole byte accounting | Bytes |
| --- | --- |
| Total interior hole bytes | 1,604 |
| Covered by behavior descriptors (8 B each) and child-pointer targets | 542 |
| Additionally covered by trusted script-root extents | 569 |
| Residue after all known anchors | **493** |

The 493-byte residue was hexdumped rather than assumed. It is live structured data:

* Stride-12 records led by the word `0x08039F09`, which disassembles at file
  `0x039F08` as Thumb (`0a 1c 01 1c 00 20` = `mov r2,r1; mov r1,r0; mov r0,#0`).
  It is a live function pointer heading an interleaved record family, 30 word-aligned
  occurrences ROM-wide, the same factory-tag idiom as the placement family itself.
* Bytecode tails beginning `1d 02 ...` (opcode `0x1D` `push_many`), i.e. script text
  for the VM the toolkit already models.
* `0x0800A1D5`-led records (10 occurrences ROM-wide) in map 342's holes.

Zero residue bytes are `0xFF`. The 220 zero bytes are interior fields of those
records, not a free run. **No hole is padding, so no hole yields capacity.**

## Reuse candidates and why each was refuted

### Candidate class 1, records inside a run span but skipped by traversal

Scanning every word-aligned `0x0800FD55` inside each run's byte span and subtracting
the pointers the array actually lists gives **0 records**. Traversal consumes exactly
what the array points at. No placement hides inside an actively traversed run.

### Candidate class 2, factory-led records no run reaches

ROM-wide there are 1,571 word-aligned `0x0800FD55` words. 1,442 are reached by a
declared run, leaving **129 unreached** that all parse as well-formed placement
records. This is the entire remaining candidate pool.

A word-aligned pointer index over the whole image resolves them:

| Unreached record | Count | Verdict |
| --- | --- | --- |
| Referenced from exactly one ROM word elsewhere | 119 | live under another owner |
| Zero inbound word-aligned references | 10 | not placement records at all |

**The 119:** each is referenced from exactly one ROM word, and never from a declared
run array. Every referring word sits inside a *secondary* pointer array, a bounded
run of consecutive placement pointers owned by a different parent structure. All 119
are covered by **40** such arrays (lengths 1 to 16 records, every array address inside
the placement region), and 13 of those arrays are terminated by the factory word
`0x0800742D`, the 20-byte rect-descriptor family from TOOLKIT-012. These are owned
placements reached by a path this ticket did not need to model. They are live;
repurposing one would corrupt whatever structure lists it.

**The 10 zero-reference records are false positives, not orphans.** They lie at
`0x757A54` to `0x77B0B0`, far outside the placement region (`0x0728FC` to `0x08E188`).
Their surroundings are dense IWRAM pointers (`0x0300xxxx`) and vtable words: each has
1 to 16 IWRAM pointers within 64 bytes either side (mean 4.5). That separation is the
actual discriminator, and it is sharp in both directions: of 400 known-live records,
**zero** have even one IWRAM pointer in the same window. All 10 also carry `position_raw == 0` and
`flags_raw == 0`, whereas only 36 of 1,442 genuine live records have a zero position.
The bytes that make them "parse" are a coincidental recurrence of the legacy tail
sequence (`a0 55 05 08 / 01 00 00 00 / ec 16 07 08`) inside unrelated data. A
coincidental `0x0800FD55` word in a pointer-dense region is not a placement record,
and writing to it would corrupt whatever that region really is.

## Positive controls (instrument validation)

Per the TOOLKIT-021 lesson, a negative result counts only if the instrument
demonstrably finds known positives.

1. **Map-event placement control.** The reference walk classifies exactly 57 records
   across exactly the 10 maps TOOLKIT-016 promoted as script-bearing, all `LIVE`.
2. **Reference-detection control.** Of 200 known-live records sampled, **200 of 200**
   are found to have at least one inbound word-aligned reference, and all 200 refs
   land in a declared run array. The instrument does not produce false "unreferenced"
   verdicts on live records.
3. **Descriptor fan-in control.** The shared null-handler descriptor `0x080555A0`
   shows fan-in 1,361, independently reproducing the TOOLKIT-016 measurement.
4. **Ownership control.** All 1,442 records classify `LIVE_MAP_OWNED`; the method
   labels no known-active record unused.
5. **Discriminator control.** The IWRAM-proximity test that rejects the 10 candidates
   is checked against the live population: 0 of 400 known-live records carry an IWRAM
   pointer within 64 bytes either side, versus 10 of 10 candidates. Without this the proximity
   claim would describe ten addresses rather than separate two populations.

Controls 1 and 3 reproduce prior pins exactly, so the census is not measuring a
different corpus than earlier tickets.

## Same-size reuse constraints

Not applicable, no `REPURPOSABLE_CONFIRMED` record exists. For the record, had one
been found, the constraint set the census would have had to satisfy is: the authored
clone must encode to the identical `0x1C + 4n` byte count, reuse the existing
descriptor and type relationship (the SDK cannot retype a placement, and no new event
may be authored), and change only position fields. None of that was reached.

## Corrections

**OLD CLAIM**: the 147 records added by TOOLKIT-017 might be unused, padding, or
free slots recoverable as authoring capacity.

**NEW EVIDENCE**: all 57 script-bearing placements and all 24 `0x0800424F` records
are inside the 147. The delta is a prefix-truncation artifact of the legacy fixed-tail
codec, and 42 of the 147 match the legacy tail shape yet were still dropped.

**RESOLUTION**: the 147 are ordinary live placements. Historical absence from the
1,295 corpus is evidence about the old codec, never about liveness. This ticket
opened with that hypothesis explicitly unresolved and closes it refuted.

---

**OLD CLAIM**: interior gaps inside a map-owned run span are candidate free space.

**NEW EVIDENCE**: the 1,604 hole bytes decompose into descriptors (542 B), script
roots (569 B), and a 493-byte residue that hexdumps as live `0x08039F09`-led
stride-12 records, `0x0800A1D5` records, and `0x1D`-led bytecode. Zero `0xFF` bytes.

**RESOLUTION**: run interiors carry interleaved live data from other families. A
placement run is not an exclusive extent, so its gaps are not allocatable.

## Remaining UNKNOWNs

* The owner of the 40 secondary pointer arrays that reference the 119 unreached
  records is not modelled here. It did not need to be: whatever lists them, they are
  referenced, so they are not reuse candidates either way. Modelling it would extend
  placement ownership coverage but is not required to answer the reuse question.
* The gameplay semantics of the `0x08039F09` and `0x0800A1D5` families remain
  UNKNOWN. Both are shown live; neither is decoded.
* The engine's run count/termination contract (the TOOLKIT-022 UNKNOWN) was **not**
  resolved and did **not** need to be. See below.

## Relation to the TOOLKIT-022 blocker

TOOLKIT-022 could not materialize an expanded run because the selected run was not
proven relocatable and the engine's count/termination semantics were UNKNOWN. This
ticket asked the cheaper question first and answered it without touching that
contract.

The census did not need the count/termination contract because it never had to prove
a record is *skipped*. Every record either is reached by a declared run (live) or is
referenced from elsewhere (live) or is not a placement record at all. There is no
surviving candidate whose classification depends on the traversal bound, so the
BLOCKED outcome does not apply, this is a clean negative, not an unprovable one.

Consequences:

* Run relocation remains necessary for any new entity instance.
* The count/termination semantics remain UNKNOWN but are **not** the blocker for this
  question. They stay blocking for run expansion.
* General placement `AUTHOR_NEW` stays blocked on relocation, unchanged.
* Same-size canonical-slot reuse is **not** supported: no safe slot exists.

## TOOLKIT-011 decision

> Does TOOLKIT-023 provide a safe placement reuse path that avoids free-space
> allocation for the next vertical slice?

**NO.** All 1,442 records are live; the 129 unreached factory words are 119 live
records plus 10 false positives; the 1,604 hole bytes are live interleaved data.

> Is TOOLKIT-011 now the binding next blocker?

**NO, relocation/count contract blocks first.** Reuse cannot substitute for capacity,
so a new placement requires growing or relocating a run. That needs the placement-run
relocation contract and the engine count/termination semantics *before* free-space
allocation becomes the operative constraint. TOOLKIT-011 is downstream of that, not
next.
