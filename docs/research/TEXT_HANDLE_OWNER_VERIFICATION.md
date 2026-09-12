# TEXT-HANDLE-001 - Locate the Producer of the Packed Compressed-Text Handle

## Objective

Determine where the packed compressed-text handle consumed from runtime object
`+0x04` comes from: identify the writer, or prove there is none and name the
durable owner instead.

## Result

> **LIVE TEXT HANDLE WRITE: NOT APPLICABLE, HANDLE IS ROM-RESIDENT**
>
> **PACKED TEXT HANDLE SOURCE: RUNTIME-PROVEN ROM-RESIDENT RECORD**
>
> **GOOD LUCK, GOKU! DURABLE MESSAGE IDENTITY: YES**
>
> **ATLAS-GUIDED LIVE OBSERVATION USED: YES**

There is no runtime write to find. The runtime object pointer points into a
ROM-resident record in the dialog pool, and the packed handle is already stored
at that record's `+0x04`. The persistent ROM record **is** the durable owner.
This is **Producer stopping point A**.

## Identity

- Start SHA `4ff5852` (master).
- Canonical ROM sha256
  `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, verified
  unchanged at the start and the end of every run.
- One commit landed during this ticket: `039ad86` "Adopt a ROM-resident-first
  default for authored content research" (`docs/DEVELOPMENT.md` plus its bound, and the
  `docs/DEVELOPMENT.md` pointer).

## Runtime fixture

- Savestate `roms/Dragon Ball Z - Buu's Fury (U).ss1`, sha256
  `2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab`, unchanged
  by the run.
- Evidence
  `build/toolkit031/text-handle-001-target-01-20260912-1319/text-handle-001.jsonl`
  : 75 rows, frames `973..11367`.
- The operator triggered the target line repeatedly, then deliberately talked to
  every NPC on screen to produce contrast.

## Object capture

- **65 CONSUMER hits, all at `0x08012230`.** The second consumer `0x080122B4`
  was armed and **never fired**.
- **21 distinct objects**, every one a ROM address inside the dialog pool
  `0x0877C5A4..0x0879B704`.
- Selector split, **both denominators**, which must not be conflated:

  | denominator | selector 1 | selector 0 |
  |---|---:|---:|
  | by HIT (65) | 41 | 24 |
  | by DISTINCT OBJECT (21) | 1 | 20 |

## Field write

**No FIELD-WRITE row exists, and none can.** The field lives in ROM. The
observer's arming guard requires an EWRAM address and correctly declined to arm
a write watch on a ROM address.

This is **stopping point A**: the experiment established *why* no write
exists, and it is **not** a missed capture.

## Decoded handle

- Target object `0x08781CF8`, handle `0x02002641`.
- Handle decodes: selector `1` -> container `0x087A04F0`, decoded start `0x132`,
  decoded length `0x20`, end `0x152`.
- Stored at ROM `0x08781CFC` (file offset `0x781CFC`, bytes `41 26 00 02`),
  inside dialog record 84 at `+0x48`.
- The atlas independently reports `container_index` 1,
  `decoded_offset_of_phrase` `0x132`, `char_count` 16 = 32 = `0x20` bytes. For
  this line the record boundary **is** the phrase, measured here, and it does
  **not** generalise.

## Repeated captures

The target object accounted for **41 hits across frames `973..11367`**, the
**same object and the same handle every time**.

Stability here is because the pointer is ROM-resident, not because a heap
allocation happened to be reused. The usual "same message, different runtime
address" expectation is **inverted** for this path.

## Contrast

Talking to every other NPC on screen produced the other 20 distinct objects.
All 20 were likewise ROM addresses inside the dialog pool, and all 20 were
selector-0 by distinct object. The contrast is what separates the by-hit and
by-distinct-object denominators above.

## Producer

There is no producer to find in the runtime. The chain terminates at a
persistent ROM record:

```
consumer 0x08012230  ->  object pointer (ROM, dialog pool)
                         object +0x04  ->  packed handle, already stored in ROM
```

`0x02002641` occurs word-aligned **exactly three times image-wide**:

| address | location |
|---|---|
| `0x08781C4C` | record 83 `+0x58` |
| `0x08781CB0` | record 83 `+0xBC` |
| `0x08781CFC` | record 84 `+0x48` |

The capture only ever read `0x08781CFC`.

## Durable identity

**IDENTITY IS PER-TEXT.** One packed-handle identity with three
reference/patch sites. This is **not** three messages. Any future patch of this
line must update the identity once and touch all three reference sites.

## Evidence levels kept separate

These levels are deliberately not collapsed.

**RUNTIME-PROVEN**

- The 65 consumer hits.
- The 21 ROM-resident object pointers.
- The handle value, read live.
- The absence of any write to a ROM field.

**STATIC-CONFIRMED**

- The handle's three word-aligned ROM occurrences.
- The bit layout of the packed handle.
- Container 0 decoding to 65,348 bytes, with 19 of 19 tested ranges yielding
  readable English NPC dialogue.
- The dialog record boundaries.
- **CORRECTION, stated plainly: the r1 calling convention is
  STATIC-CONFIRMED, not runtime-proven.** The capture latches from `r1` at
  entry, so it structurally could not have observed the object arriving in
  another register. The evidence JSONL's own ARMED row says "verified
  statically".

**INFERRED, explicitly not promoted**

- That `0xNN05` is the executable opcode.
- What `NN` means.
- What `0x1D00` means.

## Retractions

1. **Selector-0 handles are REAL decoded dialogue**, not pointer-like
   misinterpretations. All 19 tested ranges decoded to literal readable English
   NPC dialogue.
2. **The narrow `0x6805`/`0x0205` discriminator was WRONG.**
3. **The measured family is `0xNN05` (bits 16-23)**: 2,936 pool words at
   95.13% followed by an in-gate handle versus 26.97% otherwise; 19 of the 21
   captured objects' word0 fall in this family, while the narrow cut scored only
   1 of 21. **Still INFERRED, not confirmed.**
4. **`0x00A0`/`0x00E9`/`0x00EF` are TEXT, not control units.** This landed in
   commit `4ff5852`; it is preserved here, not reopened.

## Atlas impact

Producer inputs updated; no generated artifact was hand-edited.
`tools/webfoot/atlas_producers/seed.py`: **5 rows added, 1 extended.**

| row | status |
|---|---|
| `compressed_text.pointer_table` | extended, OBSERVED |
| `compressed_text.consumer_08012230` | RUNTIME_CONFIRMED |
| `compressed_text.consumer_080122B4` | CONFIRMED, armed but never observed executing |
| `compressed_text.handle_owner_record_84` | RUNTIME_CONFIRMED |
| `compressed_text.handle_0x02002641` | RUNTIME_CONFIRMED |
| `compressed_text.container_0_selector_evidence` | CONFIRMED |

Determinism: two runs into separate directories, `diff -r` byte-identical across
all 15 artifacts.

| digest | meaning |
|---|---|
| `030fe799db12b37f62ba87eefb14d0bb3f2e76791673f7cea2b00274b96e7d57` | previous canonical digest, superseded |
| `e0bcf1b4a572401bd85a86e762c067ae2d9614fea58e9dc433388ea53352bd89` | canonical digest at TEXT-HANDLE-001 closure |

The seven-container structural gate is **UNCHANGED at 7**.

## Decoded-text search

- `tools/webfoot/cli.py`: `atlas text` gained an **optional** `--rom` flag.
  Without it the command still opens no image, so the no-ROM default is intact,
  and its boundary comments were updated to stay accurate rather than weakened.
- Emits one identity object with a `reference_sites` **list**: `packed_handle`,
  `handle_selector`, `handle_decoded_start`, `handle_decoded_length`,
  `reference_sites`, `reference_site_count`. Without `--rom`, `packed_handle` is
  null plus a reason string, never a guess.
- Recovery is by **containment** on the phrase span, with the
  narrowest-containing record winning, because a phrase is a substring of its
  record. Plain containment returns 13 candidates for the target phrase; the
  tie-break is what yields one.
- Not target-specific: "five million pushups" independently resolves to handle
  `0x0E7C5A00`, selector 0, container `0x0879BF2C`.
- 13 tests added to `tests/unit/test_decoded_text_index.py`, synthetic fixtures
  only, no commercial text committed. **82 pass.**

## Validation

- 82 decoded-text/atlas tests pass.
- 22 governance tests pass.
- 71 mgba capture guard tests pass.
- `tests/unit/test_atlas_producers.py` asserted an exact seed row count of 51,
  frozen at commit `0e05cac` and left stale by two later tickets. **Proven
  pre-existing red**: a clean detached worktree at `039ad86`, containing none of
  this ticket's work, fails the same test. It has been changed to a floor
  assertion (`>= 51`) with a comment explaining why an exact count is the wrong
  instrument for a test whose stated purpose is proving the producer needs no
  pre-existing artifact.

## Safety

- The ROM was opened read-only; its sha256 was verified unchanged at the start
  and the end of every run.
- The savestate fixture was unchanged by the run.
- No write watch could be armed on a ROM address, by design of the observer's
  arming guard.
- No commercial ROM text is committed; the only quoted phrase is the ticket's
  own subject line.
- Generated atlas outputs remain ignored; only producer inputs were edited.

## Public progress

`public progress impact: NONE`. The public frontier remains ordinary plaintext
dialogue display; this ticket resolved provenance behind that frontier without
changing what the SDK can do for an outside visitor.

## ROM Bible

`ROM_BIBLE_IMPACT: UPDATE RECOMMENDED`, after the technical state is committed.
The Bible was **not** modified by this ticket.

## Files changed

All unstaged except `039ad86`, which is committed.

| file | change |
|---|---|
| `tools/runtime/text_handle_001_producer_watch.lua` | new observer |
| `tools/runtime/stage_text_handle_001.ps1` | new staging wrapper; docstring corrected post-result, because it originally framed the work as a producer hunt |
| `tools/runtime/inject_mgba_lua.ps1` | +3, allowlist entry |
| `tools/webfoot/atlas_producers/seed.py` | +119/-4 |
| `tools/webfoot/cli.py` | +155/-8 |
| `tests/unit/test_decoded_text_index.py` | +244 |
| `tests/unit/test_atlas_producers.py` | stale assertion fixed |
| `docs/research/ROM_ATLAS_REGENERATION.md` | +26/-8, new digest recorded |
| `docs/research/BUU_DIALOG_RUNTIME.md` | two stale table rows and one stale prose section corrected |
| `docs/research/BUU_DIALOGUE_TEXT_STORES.md` | one stale table row and one stale comparison sentence corrected |

## Next measured blocker

Exactly one:

> Identify the executable handler for the `0xNN05` record family and statically
> confirm that it interprets record `+0x04` as the packed compressed-text
> handle.

**This ticket does not start it.**
