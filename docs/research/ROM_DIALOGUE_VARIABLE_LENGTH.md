# Variable-length compressed dialogue

DIALOGUE-VARIABLE-LENGTH-001. This is the evidence record for authoring an
existing compressed-dialogue record at a **different decoded length** than the
one retail gave it: the durable handle is re-authored, the owning decoded
container is re-laid out, every word the engine reads as a handle is repointed,
the payload is repacked and relocated by the production allocator, and the retail
engine displays the whole longer line.

It supersedes the boundary recorded in
[`tickets/archive/ROM-CAPACITY-AND-ALLOCATION-001-COMPLETE.md`](../tickets/archive/ROM-CAPACITY-AND-ALLOCATION-001-COMPLETE.md)
§11, where exactly this request was refused by design and the route to reaching
it was named. Sections 1-10 of that record (the above-EOF allocator proof) stand
unchanged and are *used* here, not rebuilt.

## 0. Result

| Item | Value |
|---|---|
| Semantic record | `goku-greeting` |
| Retail text | `Good luck, Goku!` (32 decoded bytes) |
| Authored text | `Hot take: SSJ3 is the worst form imo` (72 decoded bytes) |
| Old durable handle | `0x02002641` (selector 1, start `0x132`, length `0x20`) |
| New durable handle | `0x04802641` (selector 1, start `0x132`, length `0x48`) |
| Decoded container | 65,474 -> 65,514 bytes |
| Packed container | 16,856 -> 17,952 bytes (`+1,096`) |
| Displaced records | 443, carrying 443 distinct handles |
| Handle words repointed | 470 (443 displaced records' 467 sites + the edited record's 3) |
| Allocator placement | file `0x00800000`, ROM `0x08800000`, size 17,952 |
| Selector table word | `0x007B5B68` = `00008008` (LE) |
| Derivative | 16,777,216 bytes, SHA-256 `dbeba9abc58db5343bd4a7c004207636c8fa6932b0f9527a866fe09ee2aba036` |
| Canonical ROM | unchanged, digest re-verified before and after every step |

## 1. The durable handle, re-derived

`tools/webfoot/handles.py` is the toolkit's ONE handle codec. Its bit layout:

```
bits 21-31   decoded length, in halfwords   (11 bits, 0..0x7FF)
bits  6-20   decoded start,  in halfwords   (15 bits, 0..0x7FFF)
bits  0-5    container/selector identity    ( 6 bits, 0..0x3F)
```

6 + 15 + 11 = 32, so there are **no reserved bits**.

This is not inferred from the field's shape. Static disassembly of the retail
consumer gives the same three fields, in this order, twice over - once at
`0x08012230` and independently at `0x080122B4`:

| Field | Instructions | Effect |
|---|---|---|
| handle load | `0x08012240 ldr r0,[r5,#4]` | the u32 at record `+0x04` |
| selector | `0x08012244 lsls r0,#0x1a` + `0x08012246 lsrs r0,#0x18` + `0x08012248 ldr r0,[r1,r0]` | `(handle & 0x3F) * 4` indexes `0x087B5B64` |
| length | `0x08012252 lsrs r1,r0,#0x15` then `0x0801225A lsls r2,r1,#1` | bits 21-31, halfwords, doubled to bytes |
| start | `0x08012254 lsls r0,#0xb` + `0x08012256 lsrs r0,#0x11` + `0x08012258 lsls r0,r0,#1` | bits 6-20, halfwords, doubled to bytes |

Two structural corroborations that the field widths are not arbitrary:

* the consumer allocates a `0x10000`-byte scratch buffer (`0x08012234-0x0801223E`)
  and decompresses the whole container into it: the 15-bit start field's maximum,
  `0x7FFF` halfwords = 65,534 bytes, fits inside it;
* the object it builds is `0x1008` bytes with the string inline at `+8`
  (`0x0801228C`, `0x08012260`): the 11-bit length field's maximum, `0x7FF`
  halfwords = 4,094 bytes, plus the consumer's own `0x0000` terminator at
  `0x08012272` is exactly 4,096 bytes.

**Nothing else bounds the string.** `0x08012230` contains no comparison at all:
it takes the length from the handle, copies that many bytes
(`0x08012264 bl 0x08049144`), and writes `0x0000` at exactly that length. It never
reads the next record, never reads the container header's declared size, and
never scans for a terminator. A widened length therefore widens the string. The
one residual caveat is measured rather than assumed: a downstream glyph layout
stops at an embedded `0x0000` (`0x0803DD7E`), which the authored line does not
contain, and the re-layout keeps every neighbouring record's bytes identical.

`DialogueHandle` is the authoring representation built on this layout, with
`decode`, `replace` and `encode`; `pack_handle` is the same encoder. No writer
path shifts bits itself.

## 2. The decoded container's layout policy

Measured on the canonical image with the reference inventory of §3:

| selector | decoded bytes | distinct records | carrier words | consecutive adjacent pairs |
|---|---|---|---|---|
| 0 | 65,348 | 521 | 630 | - |
| **1** | **65,474** | **447** | **473** | **410 of 446** |
| 2 | 65,464 | 464 | 483 | - |
| 3 | 65,334 | 421 | 427 | - |
| 4 | 65,322 | 486 | 498 | - |
| 5 | 65,394 | 460 | 476 | - |
| 6 | 436 | 6 | 6 | - |

So the decoded container is a stream of records placed consecutively from offset
0, each addressed by an **absolute** decoded start in its own handle. There is no
neighbouring-offset bound and records are **not** a clean partition: some handles
span several consecutive messages (an aggregate), and a container can hold
records that share a start and differ only in length - selector 1 holds three
that begin at offset 0.

The critical measurement for the edit: **exactly one record intersects the
boundary span `0x132..0x152`, and it is `goku-greeting` itself.** No record
contains it and extends past it, and no record starts inside it. That is what
makes the re-layout deterministic, and the production code re-checks it rather
than assuming it: a container whose records straddle the edited span is refused
with that reason.

The re-layout rule is therefore:

```
rebuilt_decoded = decoded[:start] + replacement + decoded[end:]
every record whose start >= end moves to start + (len(replacement) - (end - start))
records before start are untouched
```

## 3. The reference inventory, and why it is not a value pattern

A packed handle is read by the engine in exactly one structure: a record word
whose byte `+0x02` is the dispatch key `0x05`, whose `+0x04` is the handle
(TEXT-HANDLE-001 and TEXT-HANDLE-002, both runtime-proven; the three
runtime-observed carriers of the target handle all have that shape, e.g.
`07 00 05 68 41 26 00 02`).

Scanning for **any** word that merely unpacks to a plausible span is not a
reference inventory. On the canonical image, selector-1 words that pass that weak
test number **46,298 distinct values occurring 59,491 times**, of which only
**143** are ever read as handles. Rewriting them would corrupt code and data - the
low-offset occurrences are Thumb instructions such as `05 68`.

The structural query is therefore the inventory:

| population | count |
|---|---|
| `0x6805`-family record words image-wide (`byte+1 == 0`, `byte+2 == 0x05`) | 6,043 |
| ... whose handle names a container and an in-gate span | 2,993 |
| ... in the event-resource record pool (`0x77C5A4..0x79B704`) | 2,735 |
| ... elsewhere in the ROM (map scripts and other tables) | 258 |
| selector-1 carriers | 473 |

Dropping the `byte+1 == 0` requirement admits 4,296 more "carriers" that are
overwhelmingly Thumb code at low ROM offsets, so the requirement is what keeps
the query structural.

### Aliases versus coincidental equal words

`0x02002641` occurs word-aligned **exactly three times** image-wide, at
`0x781C4C`, `0x781CB0` and `0x781CFC`, and all three are record objects in dialog
records 83 and 84 - one identity with three reference sites, which is
TEXT-HANDLE-001's conclusion reached independently here. All three are updated
together.

Equal-valued words that are NOT carriers are left alone. Measured over the 443
distinct handles this edit supersedes:

| population | count |
|---|---|
| superseded distinct handles | 443 |
| superseded carrier sites | 467 |
| superseded values that also occur outside the carrier structure | 3 |
| such stray occurrences | 15 |

All fifteen are data - a table of ascending halfwords at `0x733E04`, a literal at
`0x20E4D0`, two in code at `0x2C994C`/`0x312E9C` - and none lies in the dialog
pool. They are pinned as the M4 control.

## 4. What the production code does

`tools/webfoot/handles.py`

* `DialogueHandle(selector, decoded_start, decoded_length)` with validation, and
  `decode` / `replace` / `encode`; `pack_handle` is the same encoder. One
  implementation, two directions.

`tools/webfoot/compressed_dialogue.py`

* `dialogue_record_inventory` - the structural reference query of §3;
* `DialogueLayout` - decoded bytes plus inventory, with `record_with_span`,
  `records_starting_at`, `sole_record_starting_at` and `records_crossing`;
* `validate_container_layout` - the container-wide invariant: every handle's
  fields are legal and round-trip, its selector is the container's, its span is
  inside the decoded data, no two records share a handle;
* `relayout_for_length` - the deterministic splice of §2, refusing a crossing
  record, a rebuild past the container decoder's limit, and any handle whose
  displaced start overflows the field;
* `validate_relayout` - the neighbour and reference-consistency invariant of §5;
* `_prepare_replacement` - repacks with the existing encoder, re-validates the
  retail termination contract, and either rewrites the retail allocation in place
  or asks `allocation.allocate` for a `PACKED_STREAM` span.

`tools/webfoot/write.py`

* `DialogueEditProvenance`, carried on `WritePlan`/`WriteManifest` and serialized
  into the existing manifest document as `dialogue_edits`. No third sidecar.

`tools/webfoot/dialogue.py`

* the user-facing contract is now "replace this existing dialogue record with
  this text". The old exact-length rule is gone; what remains is the field
  capacity (4,094 bytes) and, when a base image is supplied, the full layout
  plan;
* `resolve_dialogue_target` accepts the retail handle **or** the record's own
  anchor `(selector, decoded start)`, which is what lets a derivative reopen as
  the same semantic record after its handle changed;
* `get_dialogue_original` reads through the record's *current* handle, so the
  same call answers for the canonical ROM and for a derivative.

## 5. The invariants, and what each one catches

Production checks, in order, all failing closed before any plan exists:

1. **container-wide** (`validate_container_layout`) - legal fields, round-trip,
   selector exists, span inside the container, no shared handle;
2. **no crossing record**, **decoder limit**, **start-field overflow**;
3. **the edited record's span carries the replacement** and **its start did not
   move** - which is what makes "keep the old length" fail rather than produce a
   truncated line;
4. **every unedited record still decodes to exactly its own bytes** - the
   neighbour proof: a suppressed shift, a truncation or a record pointing into the
   middle of another all fail it;
5. **reference consistency** - every superseded handle's carrier sites are
   rewritten exactly once to the new value, and no word outside the carrier
   structure is written at all;
6. **retail termination** - the existing `validate_retail_termination`, unchanged,
   on the repacked payload.

Measured on the real edit: 446 of 447 records compared byte-for-byte, 0
mismatches; 470 required sites, 470 written, 0 stray words touched.

## 6. Capacity: three different numbers

| Bound | Value | Basis |
|---|---|---|
| ENCODABLE (length field) | 4,094 decoded bytes | 11-bit halfword field |
| PRODUCTION-BOUNDED (this target) | 94 decoded bytes | the rebuilt container must stay under the decoder's 64 KiB limit, and the retail container already decodes to 65,474 of 65,536 bytes |
| ENGINE-PROVEN | 72 decoded bytes | this ticket's runtime observation |

The middle bound is the interesting one and it is a property of the *toolkit's*
safety limit (`webfoot_lz.DEFAULT_MAX_OUTPUT`), not of the format: the engine
allocates a 64 KiB scratch buffer and reads the container's declared size, so a
container larger than 64 KiB would need its own bounded experiment. Because that
limit is smaller than what the start field can address, a displaced record's
shifted start can never overflow the field while the limit holds - the guard
exists, is tested directly, and is documented as defence in depth.

Display width is a further, separate limit and is unchanged by this ticket.

## 7. Runtime proof

See §7.1 for the run. Vehicle: the tracked Checkpoint D chain
(`tools/runtime/run_capacity001_expansion.ps1` +
`tools/runtime/varlen001_dialogue_variable_length_probe.lua`), which is a
free-running inject-then-load session - a frame-bounded Lua observer records zero
ticks under the GDB launcher, which is why this chain exists.

The probe is retargeted at the **re-authored** handle `0x04802641` and asserts
the allocator's address from the derivative's own provenance. It records the
selector table word at arm time, every consumer hit, a liveness hit on the shared
interpreter at `0x08004038`, screenshots at +8 and +45 frames after the target
record is consumed, and it separately flags a **neighbour** record from the same
rebuilt container (`0x0A002F41`, the record that followed the greeting and moved
by the displacement) if the session reaches one.

### 7.1 Result

**One run reached the greeting; fourteen did not.**

The successful run is `varlen-001-run1` (label `varlen-001-run1`, mGBA 0.11 dev,
the tracked runner, human mode, no input). Its artifacts, all under the ignored
`build/` tree:

| Artifact | SHA-256 |
|---|---|
| `capacity001-dialogue.csv` | `d9d394bfc5dc11b17867349fd14657bd43f83d1e741d9e5761f3da7908a03611` |
| `varlen001-consumer-1-early.png` (+8 frames) | `ba703d9b17166587c7ed8ad6ab03766c1fe9b32c6e3ba3bb46f3cc2cbbb7bf47` |
| `varlen001-consumer-1-dialogue-box.png` (+45 frames) | `48a8783027b6e2327e92ca0fe765c199554257004eb89a3b6fc0b9db627efeb3` |

The CSV, verbatim:

```text
ARMED,,,,0x08800000,selector 1 pointer at arm time; expected 0x08800000
LIVENESS,0x08004038,,,,shared interpreter reached
CONSUMER,0x08012240,0x04802641,1,0x08800000,target widened record consumed
```

**What this proves.** The retail consumer at `0x08012240` executed with `r5`
holding the event-resource record whose `+0x04` is the **re-authored** handle
`0x04802641` (selector 1), and the selector table word it indexes was
`0x08800000` - the address the production allocator chose. Liveness on the shared
interpreter fired, so the run is not a null result. The +8 frame shows the world
with no box (the engine still has to fetch and decompress 17,952 bytes); the +45
frame shows the ordinary retail dialogue box displaying the authored line.

**The widened decoded length was honoured, and that is visible in the capture.**
The box at +45 reads `Hot take: SSJ3 is the worst for` - **31 characters**. The
retail record's decoded length was 32 bytes = **16 characters**, so a consumer
that had not honoured the re-authored length could not have rendered more than 16
characters of this text. It rendered 31.

**What it does not prove, stated plainly.** The box reveals text progressively,
and +45 frames is mid-reveal: the first line is exactly full at 31 characters and
the remaining five (`m imo`) had not been drawn yet. The complete 36-character
line was therefore **not captured on screen**, and the machine-readable capture of
the engine's own copied string (§7.2) needs a later-frame read that did not exist
in the probe at the time of this run. Acceptance criterion 14 is **not**
established by this artifact.

### 7.2 Why no settled capture was obtained

The fixture consumes the greeting *without input* on resume - Checkpoint D
recorded that, and this ticket's run 1 reproduced it. It is not reproducible on
demand. Measured over 15 identical tracked runs of the same derivative, the same
savestate and the same probe:

| Attempt | Result |
|---|---|
| `varlen-001-run1` | **greeting consumed**, both screenshots written |
| `run2`, `run3`, `run5`, `run7`, `quiet1` | core running (heartbeats), no consumer row, no liveness row |
| `run4`, `script2` | scripted walk + tap, no consumer row |
| `run6`, `tap2` | A tapped every 45 frames for 9,000+ frames, no consumer row |
| `run8`, `run9` | probe self-loaded the same hash-verified state at frame 90 and 600, no consumer row |
| `keys2`, `keys3` | operator key presses (see below), no consumer row |
| `hit1`-`hit5` | five further identical repeats, no consumer row |

Three triggering mechanisms were ruled out by measurement rather than assumed:

* **the probe's own key API is inert in this vehicle.** `emu:addKeys(LEFT)` held
  for 300 frames moved the player nowhere: `varlen001-hold-010.png` and
  `varlen001-hold-300.png` are the same scene. (`emu:setKeys` behaved the same
  way, which is why the earlier scripted walk never moved either.) The two calls
  are the pair the proven P-008 driver uses, with this file's masks derived the
  same way, so the API is right and the vehicle is what differs.
* **`AppActivate` + `SendKeys` cannot deliver input here** - `AppActivate`
  returns false for the mGBA process in this session (recorded in
  `build/research/varlen_trigger_keys.ps1`'s output).
* **posting real key events to the emulator window did not either** - 18
  `WM_KEYDOWN`/`WM_KEYUP` pairs for mGBA's A key (`X`) reached the process's
  windows and produced no dialogue.

Deleting the generated `derivative.sav` (restoring the first-run save state) did
not reproduce it either, and mGBA's portable `qt.ini` holds only geometry, key
binds and the recent-file list.

**Conclusion.** The engine-side claim - the retail consumer reads the re-authored
handle and its widened decoded length, from the container the production
allocator placed above canonical EOF - is **runtime-proven**. The complementary
claim - that the complete 36-character line is drawn on screen with no truncation
- is **not established**, because the one run that reached the greeting was
captured mid-reveal and the trigger has not recurred.

This is recorded as a shortfall, not worked around: no artifact is presented as a
settled capture that is not one.


## 8. Boundaries and honest limits

* **One record, one container.** The re-layout is defined for the container the
  target lives in. Nothing here re-lays out a second container, and the selector
  count is untouched: Checkpoint A's seven-container structural limit is a
  separate problem and was not widened.
* **A crossing record is refused.** If another record's span straddled the edited
  one, growing it would have to rewrite that record's *content*, and no evidence
  defines how the engine expects an aggregate to be re-expressed. The canonical
  target has no such record; the refusal is the honest answer for a container
  that does.
* **The 64 KiB container limit is not lifted.** See §6.
* **One edit at a time.** `materialize_dialogues` processes requested
  replacements in name order; two records in one container would each re-layout
  against the same base and collide. The registered target set holds one record,
  and a second would need an explicit batch re-layout. Recorded, not claimed.
* **No GUI redesign.** The Inspector reaches the new capability through the
  existing validation and apply calls; the Build tab's validation performs the
  full layout plan. No CQA-05/06/07/08 work was done or required.
