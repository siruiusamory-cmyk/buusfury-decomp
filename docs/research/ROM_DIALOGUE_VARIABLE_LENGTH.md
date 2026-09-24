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
| Runtime observation | the retail dialogue box displays the complete line `Hot take: SSJ3 is the / worst form imo`, wrapped by the engine (`varlen-001-human1`, §7) |
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

**Result: the retail engine displays the complete authored line.** The acceptance
observation is `varlen-001-human1`, a tracked `human` session in which the operator
walked to the greeting NPC and talked to them. The retail dialogue box shows the
authored line in full, wrapped by the engine's own renderer across two lines:

```text
Hot take: SSJ3 is the
worst form imo
```

That is the complete 36-character string - the wrap falls between two words, not
inside them - with no ellipsis, no clipping and no partial line.

### 7.1 The observation, and why "not truncated" is measured

The probe photographs the box at +8, +45 and +120 frames after the target record
is consumed. The three shots are a progressive reveal, which is what turns "the
line is complete" from an assertion into a measurement:

| Frame | File | Shows | SHA-256 |
|---|---|---|---|
| +8 | `varlen001-consumer-1-early.png` | world, **no box yet** | `793a7d8ffc40ed85fad52e0a2041b5f0576c009ce1716e66e8409196b59a23ff` |
| +45 | `varlen001-consumer-1-dialogue-box.png` | `Hot take: SSJ3 is the / worst for` (mid-reveal) | `4cc2a0bdf053e9ccac257db1e90baf5e1944a28955bf18c08864521042815197` |
| **+120** | **`varlen001-consumer-1-settled.png`** | **`Hot take: SSJ3 is the / worst form imo`** | `99e3bbc6aa67c13a8116d245e7630ec6cb4c64aecc0f88e10466fde641448509` |

The row the same session wrote at the consumer:

```text
ARMED,,,,0x08800000,selector 1 pointer at arm time; expected 0x08800000
LIVENESS,0x08004038,,,,shared interpreter reached
CONSUMER,0x08012240,0x04802641,1,0x08800000,target expanded selector consumed; widened decoded length honoured
```

`capacity001-dialogue.csv`, SHA-256
`33a4dcb65103d182870d152ca0436ee8754dadbad2226b2fc06d367c17415e710`. The
canonical ROM was re-verified unchanged before and after the session, and the run
directory lives inside the ignored `build/` tree.

So the engine read the **re-authored** handle `0x04802641` (selector 1) from the
record whose `+0x04` holds it, indexed the selector table to the address the
production allocator chose (`0x08800000`), honoured the record's **widened** 72-byte
decoded length, and drew all 36 characters. A consumer that had not honoured the
re-authored length could not have drawn more than the retail record's 16
characters.

**One caveat, stated because it bounds what the machine row proves.** The `STRING`
row for *this* hit reads `decoded_bytes=14` with byte values that are not text,
while the same mechanism returned perfect text for the intro narration in §7.4.
The deferred read (`object + 8`, two frames after the hit) is therefore reliable
only when the consumer was handed a heap object; on this dialogue path the caller
appears to pass an object whose storage is reused before the read. **The visual
capture is the evidence for acceptance criterion 14; the `STRING` row is not, and
it is not presented as such.**

### 7.2 The input correction that made the session possible

Earlier drafts of this record claimed that no key input reached the emulated core,
and that claim was **wrong**. It came from a flawed comparison: two `hold` runs
ended on byte-identical `+300` frames, but both held the same key for the same
frames, so identical frames were equally consistent with *both* having walked. The
`scripted` runs were likewise compared against each other rather than against a
no-input baseline.

This repository uses mGBA's two key APIs: `rom006_bootstrap.lua` presses with
`emu:addKey(C.GBA_KEY.A)` and `emu:clearKey`, while `p008_mash_driver.lua` uses the
plural mask form `emu:addKeys(1 << index)`. Measured against a baseline frame taken
before any input:

| Channel | Run | Result |
|---|---|---|
| `emu:setKeys(mask)` / `emu:addKeys(mask)` | `run4`, `script2`, `run6` | no input: the player never leaves the resume position |
| **`emu:addKey(C.GBA_KEY.START)`** | `varlen-001-keytest1` | **the STATUS menu opens** - input lands |
| **`emu:addKey(C.GBA_KEY.RIGHT / UP / DOWN)`** held 60 frames | `varlen-001-dirsweep` | **27,199 / 32,509 / 28,681 pixels change and the camera scrolls** - the player walks |
| `emu:addKey(C.GBA_KEY.LEFT)` held 60 frames | `varlen-001-dirsweep` | 350 pixels change: this spot blocks LEFT |
| `emu:addKey(C.GBA_KEY.LEFT)` held from a fresh boot | `varlen-001-boot-walk` | **the intro narration is skipped** (0 consumer rows against 21) |
| `emu:addKey(C.GBA_KEY.A)` pulsed from a fresh boot | `varlen-001-boot-long1` | **presses START at the title**; the game reaches gameplay (Other World, HUD up) by frame 21200, where the run with no A pulses is still on the title screen |
| `AppActivate` + `SendKeys` | `varlen-001-keys2` | `AppActivate` returned false; nothing sent |
| `PostMessage` `WM_KEYDOWN`/`WM_KEYUP` | `varlen-001-keys3` | 18 A presses, no dialogue |
| `SendInput` after raising every visible window | `varlen-001-input1` | 20 A presses, no dialogue |

The single-key API is the one that works. The probe now logs what each key name
resolves to, because `emu:addKey` takes a `GBA_KEY` index rather than a mask and a
name missing from `C.GBA_KEY` would silently fall back to the mask value: measured,
`A=0 START=3 LEFT=5 RIGHT=4 UP=6 DOWN=7`.

### 7.3 The automatic trigger, and why it did not settle this

The fixture consumes the greeting without input **on some loads only**. Measured
over twenty identical tracked runs of the same derivative, the same savestate and
the same probe, it happened **once** - `varlen-001-run1`, whose +45 shot caught the
box mid-reveal at `Hot take: SSJ3 is the worst for` and which had no settled shot
at all, because the +120 schedule did not exist yet.

| Attempt | Result |
|---|---|
| `varlen-001-run1` | greeting consumed; +8 and +45 shots only |
| `run2`, `run3`, `run5`, `run7`, `quiet1` | core running (heartbeats), no consumer row, no liveness row |
| `run4`, `script2`, `script-single` | scripted walk + tap, no consumer row |
| `run6`, `tap2`, `tap-single` | A tapped every 45 frames for 9,000+ frames, no consumer row |
| `run8`, `run9` | probe self-loaded the same hash-verified state at frames 90 and 600, no consumer row |
| `varlen-001-sweep1` | **20 state loads in one run**, frames 180 to 4200: zero consumer, zero liveness - so the trigger is not a function of load timing |
| `varlen-001-keys2`, `keys3`, `input1` | OS-level key injection (three channels), no consumer row |
| `hit1`-`hit5` | five further identical repeats, no consumer row |

The greeting is an **interaction**, not something the fixture replays by itself:
at the resume position A alone does nothing (no NPC committed to the interaction)
and LEFT is blocked, and `varlen-001-route1` - UP then LEFT then A - moved the
player and fired the liveness channel but consumed no record. That is what made the
operator's session both necessary and sufficient.

### 7.4 The tracked human session, and the capture mechanism it exercised

The procedure's `human` mode is a human-in-the-loop workflow by design, and the
two-step session pair is its vehicle: the bounded runner stops the emulator once
`RunSeconds` expires, which would cut a played session short, while the `start`
script arms the probe, loads the state and returns.

```powershell
# 1. arm the probe and load the fixture; `human` is the probe's default mode, so no
#    CAPACITY001_* / VARLEN001_* variable may be set in the shell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File tools/runtime/start_capacity001_expansion_session.ps1 `
  -RomPath "build\varlen-001\derivative.gba" `
  -RomSha256 dbeba9abc58db5343bd4a7c004207636c8fa6932b0f9527a866fe09ee2aba036 `
  -RomSize 16777216 `
  -StatePath "<checkout>\roms\Dragon Ball Z - Buu's Fury (U).ss1" `
  -Label varlen-001-human1 -ExpectedPointer 0x08800000 `
  -LuaPath "tools\runtime\varlen001_dialogue_variable_length_probe.lua" `
  -MGBPath "build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe"

# 2. play: the fixture resumes beside the two NPCs just left of Goku; LEFT is
#    blocked at the resume spot, so go around them and talk with A. Close mGBA.

# 3. collect
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File tools/runtime/finish_capacity001_expansion_session.ps1 -Label varlen-001-human1
```

The tracked launcher's banner says the line reads "Nice work, Goku!" - that is
Checkpoint D's boilerplate, not this ticket's expectation, and it was left alone
rather than edited under the operator.

One independent, input-free confirmation of the same consumer came from a fresh
boot: the game auto-plays its intro narration through the very consumer under test,
and the deferred `STRING` read returned that narration byte-exactly - for example
`decoded_bytes=206`, `!Finally; after years of turmoil caused by Dr. Gero's
Androids; the Earth was brought back to normal...`. (`ascii=` replaces commas with
semicolons because the row is CSV; `hex=` is the exact UTF-16LE the engine
materialised.) That is the capture mechanism working on records nobody edited, and
it is why the mid-reveal +45 shot of §7.3 could be interpreted at all.

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
