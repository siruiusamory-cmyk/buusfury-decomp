# Buu's Fury shop scenario / script model

Measured against canonical `buus_fury_usa_rev0_01c1707f`, sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, verified
unchanged before and after every read below. Static analysis only; the ROM was
opened read-only.

TOOLKIT-037 left the shop dialogue region `0x0877F09A..0x087801D4` as the next
measured blocker: real NPC speech with no located pointer table and no
identified consumer. TOOLKIT-038 answers the pointer-table and dispatcher half
of that blocker statically, and reconciles the overlap ROM-ATLAS-001 flagged
but did not resolve.

## Headline

**The shop dialogue region is event-record payload, not a separate store, and
the engine's script type byte lives at record offset +2.**

```
event_resource.pointer_table 0x0879B704  entry 28
    -> event record 0x0877F3B0, 52 bytes         the Hercule City Z-Mart scenario
        -> 10 stride-4 script pointers
            -> script 0x0877F096, type 0x03      "Welcome to the Hercule City Z-Mart!..."
    -> dialog.entry_point 0x08004098
        -> ldrb r1,[r0,#2]  at 0x080040BA        the type dispatch
            -> type 0x00  interpreter 0x08004038 on body+3
            -> type 0x04  expand 0x08049120 on body+4, then interpret
            -> else       assertion, ByteCodeInterpreter.cpp
```

Evidence class: **CONFIRMED_ROM** for the record/script framing, the type census
and the ownership measurement. **CONFIRMED (static executable)** for the
dispatcher. The runtime edge from a dispatched type-0x03 body to the live
dialogue cursor is **NOT ESTABLISHED** and is this ticket's stopping point.

## 1. The six shop scenarios are event records

ROM-ATLAS-001's seed carried an explicit unresolved overlap: the shop region
`[0x77F09A,0x7801D4)` lies inside `event_resource.record_pool`
`[0x77C5A4,0x79B704)`, which TOOLKIT-019 measured as exhaustively tiled by 522
records with zero gap, and neither document reconciled them. Both seed rows now
carry `OVERLAP RESOLVED by TOOLKIT-038` instead
(`tools/webfoot/atlas_producers/seed.py:537`, `:620`).

They reconcile as follows. Each of the six stride-4 pointer arrays in the region
is **exactly one entry of the 522-entry event pointer table**:

| event index | record address | size | entry count |
|---:|---|---:|---:|
| 28 | `0x0877F3B0` | 52 | 10 |
| 30 | `0x0877F73C` | 892 | 10 |
| 31 | `0x0877FAB8` | 84 | 11 |
| 33 | `0x0877FE00` | 520 | 10 |
| 34 | `0x08780008` | 44 | 8 |
| 36 | `0x087803E4` | 60 | 12 |

All six array base addresses appear in the event pointer table at
`0x0879B704`. **None of the 61 script targets does**: 0 of 61 are table
entries. So the arrays are the addressable events and the 61 scripts are payload
reached only through them.

`docs/research/BUU_DIALOGUE_TEXT_STORES.md` labelled this region UNOWNED. That
label was correct for what it measured and is now superseded: the region is
owned by the event resource, through the table TOOLKIT-019 had already proven.

## 2. The script framing

Each of the 61 targets begins with a 3-byte header:

```
+0 u16  next_script_index
+2 u8   type
+3 u8   0 or 2
```

Measured across all 61 targets, no exceptions.

### Type census

Every observed value, not only the ones external evidence predicted:

```
type 0x00: 18    bytecode
type 0x03: 17    plaintext UTF-16LE dialogue
type 0x04: 20    compressed
type 0x05:  6    scenario descriptor
```

No other value occurs. The `+3` byte is `0x00` in 53 targets and `0x02` in 8.

### Payload shape per type, measured

| type | n | size range | payload |
|---:|---:|---|---|
| `0x00` | 18 | 8..30 B | short, repeating halfword structure |
| `0x03` | 17 | 98..236 B | UTF-16LE prose beginning at `+4` |
| `0x04` | 20 | 44..172 B | high entropy, shared leading bytes across shops |
| `0x05` | 6 | 8 B | the descriptor itself |

Type `0x03` decodes directly, for example at `0x0877F096`:

```
Welcome to the Hercule City Z-Mart! How can I help you?\n\n-Buy\n-Sell\n\n-End
```

Type `0x04` payloads across different shops share identical leading bytes
(`90a0c020e56e2432...`, `40b29120706384e0...`), which is a compressed stream
with a common prefix rather than bytecode. **Not claimed**: which codec. The
dispatcher routes type 4 through `0x08049120`, and that routine was not decoded
here.

### next_script_index is structurally valid

Measured per scenario, every value falls in `0..entry_count` with no exception:

| array | entry count | next values |
|---|---:|---|
| `0x0877F3B0` | 10 | 1, 3, 3, 4, 5, 0, 4, 4, 0, 10 |
| `0x0877F73C` | 10 | 1, 3, 3, 4, 5, 0, 4, 4, 0, 10 |
| `0x0877FAB8` | 11 | 1, 4, 4, 4, 5, 6, 0, 5, 5, 0, 11 |
| `0x0877FE00` | 10 | 1, 3, 3, 4, 5, 0, 4, 4, 0, 10 |
| `0x08780008` | 8 | 1, 2, 3, 0, 2, 2, 0, 8 |
| `0x087803E4` | 12 | 1, 2, 3, 0, 2, 2, 2, 2, 2, 2, 0, 12 |

Two conventions are consistent across all six:

- `next == 0` marks a terminal script. Each scenario has exactly two.
- the **last** slot's `next` equals the scenario's entry count exactly.

Walking from slot 0 in `0x0877F3B0` yields slots `0 -> 1 -> 3 -> 4 -> 5` with
types `0x00, 0x03, 0x00, 0x03, 0x04`: a bytecode preamble, the greeting line,
more bytecode, the "What would you like to buy?" menu, then a compressed body.
That is the shape of a shop conversation, so the indices are chains rather than
coincidence.

**INFERRED, not confirmed**: that these are branch targets for Buy / Sell / End
specifically. The index values are valid and the chain is plausible, but no
runtime observation attributes a particular branch to a particular choice.

## 3. The type-0x05 descriptor

Every scenario's last slot points 8 bytes **below** its own array base, to:

```
+0 u16  entry_count       equals the array's entry count, all six
+2 u8   0x05
+3 u8   0x00
+4 u32  0x02CE74C0        identical across all six
```

So the count and type are self-describing and cross-check the array. Those 8
bytes fall inside the **preceding** event record's extent (record 27 spans
`0x0877F030..0x0877F3B0`), so whether they are a trailing field of record 27 or
an 8-byte prefix the engine reads before the array is **UNKNOWN** from bytes
alone. Both readings fit; only runtime separates them.

`0x02CE74C0` is not a ROM or EWRAM pointer at rest and its role is **UNKNOWN**.

## 4. Ownership: relocation gate evaluated

TOOLKIT-036's per-entry relocation gate requires exactly one word-aligned
inbound reference, and that reference being the entry's own table slot. A
whole-image aligned-word scan over all 8,388,608 bytes measures, for all 61
script targets:

```
targets                 61
with extra inbound       0
uniquely owned          61
```

**Every one of the 61 scripts has exactly one word-aligned inbound reference in
the entire image: its own array slot.** The gate is satisfied for all 61.

This is the measurement TOOLKIT-037 named as blocked and could not perform.

## 5. The dispatcher

`dialog.entry_point` at `0x08004098` was already seeded as CONFIRMED from
`docs/research/BUU_EVENT_RESOURCE.md:101`. This pass confirms it reads the same
type byte the script census measures, by disassembling it:

```
0x080040B8  ldr   r0, [r6]           ; the script body
0x080040BA  ldrb  r1, [r0, #2]       ; THE TYPE BYTE
0x080040BC  cmp   r1, #0
0x080040BE  beq   0x080040E8         ; type 0 -> body+3, interpret
0x080040C0  cmp   r1, #4
0x080040C2  bne   0x080040F4         ; neither -> assertion
0x080040C4  lsls  r0, r1, #9         ; type 4 path: allocate
0x080040C6  bl    0x0803D5B8
0x080040CE  adds  r1, r0, #4         ; body+4
0x080040D2  bl    0x08049120         ; expand
0x080040DC  bl    0x08004038         ; interpret the expansion
...
0x080040EA  adds  r1, r0, #3         ; type 0 path: body+3
0x080040EE  bl    0x08004038         ; interpret directly
```

The else-branch calls `0x0803DF14` with the source filename
`T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp`, which is Webfoot's own
build path and independently confirms this is the script/bytecode subsystem.

Ten BL sites call `0x08004098`: `0x08003242`, `0x08003276`, `0x080032BA`,
`0x08004C00`, `0x0800E1A6`, `0x0800E666`, `0x0800FC5E`, `0x0801096C`,
`0x0801A1B8`, `0x08026480`. The interpreter `0x08004038` has 29 callers.

**Important boundary.** The dispatcher handles types `0x00` and `0x04` and
asserts on everything else. The 17 type-`0x03` plaintext scripts and the 6
type-`0x05` descriptors would therefore **fail this dispatcher's assertion**.
So `0x08004098` is not the routine that consumes a plaintext dialogue body;
a type-0x03 body must be reached by different code, most plausibly by a
bytecode opcode executed for a type-0x00 script in the same scenario. That
routine is **NOT IDENTIFIED**, and it is the next measured blocker.

## 6. The shop object record

Five instances of a fixed-layout record in low ROM carry a scenario pointer:

| record | scenario |
|---|---|
| `0x08074360` | `0x0877F3B0` |
| `0x080743C4` | `0x0877F73C` |
| `0x08074450` | `0x0877FAB8` |
| `0x080744B4` | `0x0877FE00` |
| `0x0807451C` | `0x08780008` |

Fields `+0x00`, `+0x04`, `+0x08`, `+0x10`, `+0x14`, `+0x18`, `+0x1C` are
byte-identical across all five; `+0x0C` holds the scenario and the trailing
fields vary. `+0x00`, `+0x10` and `+0x14` are Thumb code pointers
(`0x0800775F`, `0x08007675`, `0x080077DF`), which disassemble as object
lifecycle callbacks: `+0x00` returns an IWRAM address, `+0x10` allocates 0x18
bytes, `+0x14` is camera/coordinate math. None of the three touches text.

This is the concrete form of Data Crystal's "NPC structure contains a dialogue
pointer" claim, and is stronger than the claim: the pointer is to a scenario,
not to a string. A master index listing every scenario array in the region sits
at `0x0879B774`.

`0x087803E4` (event 36) has no record in this cluster, so the five records do
not account for all six scenarios.

## 7. External lead verification

### `0x0801226A`: REFUTED

Data Crystal reports a breakpoint here reaching message display with `r1`
carrying a text-related value. It is real code inside `func.08012230`, but it is
not message display:

```
0x08012268  ldr   r1, [r5, #4]
0x0801226A  movs  r0, #0        <- the claimed address
0x0801226C  lsrs  r1, r1, #0x15
0x0801226E  lsls  r1, r1, #1
0x08012270  adds  r1, r1, r6
0x08012272  strh  r0, [r1, #8]
```

`r1` at that instruction holds `[r5,#4]` being shifted as a **packed
bitfield** to index a structure, not a text pointer. The enclosing function
calls the allocator `0x0803D5B8` and indexes table `0x087B5B64`. The claim is
refuted as stated.

### `0x0202BA70`: NOT ESTABLISHED

Zero word-aligned references to this address exist anywhere in the 8 MiB image,
nor to `±4` or `±8` of it. It can only be reached by computed addressing, so
static analysis can neither confirm nor refute the "dialogue start/state"
label. Runtime observation is required.

### NPC dialogue pointer: CONFIRMED in stronger form

See section 6. The record's `+0x0C` is a scenario pointer.

## 8. Community model reconciliation

`kin.forever`'s model, reported on a Legacy of Goku fanserver, described a
scenario as a list of pointers to scripts, each script framed
`u16 next_script_index; u8 type; payload`.

| claim | measured | verdict |
|---|---|---|
| scenario is a list of pointers to scripts | 6 arrays, 61 targets, stride 4 | **CONFIRMED** |
| `u16 next_script_index` at `+0` | all 61 in range `0..entry_count` | **CONFIRMED** |
| `u8 type` at `+2` | 4 distinct values; dispatcher reads exactly this byte | **CONFIRMED** |
| type `0` = bytecode | 18 targets; dispatcher runs body+3 through the interpreter | **CONFIRMED** |
| type `1` = plaintext dialogue | no type `0x01` exists in this corpus; **plaintext is `0x03`** | **DIFFERS** |
| type `5` = compressed text | no compressed body carries `0x05`; **compressed is `0x04`**, and `0x05` is the scenario descriptor | **DIFFERS** |
| type `7` = compressed bytecode | no type `0x07` in this corpus | **NOT OBSERVED** |
| type `9` = pointer/chaining to another scenario | no type `0x09` in this corpus | **NOT OBSERVED** |
| one type = store/full-screen dialogue | not distinguishable; the shop conversation uses `0x03` | **NOT OBSERVED** |

The **structural model is confirmed and the type numbering differs**. The
reporter explicitly flagged the type numbers as recalled from memory, and that
caution was warranted: the framing was right, the constants were not. Types
`0x01`, `0x07` and `0x09` may well exist elsewhere in the 522-record pool; this
ticket censused only the 61 shop scripts and makes no claim beyond them.

## 9. Capability boundary

| Layer | Status |
|---|---|
| Shop region is event-record payload | **CONFIRMED_ROM** |
| Six scenarios are event-table entries 28/30/31/33/34/36 | **CONFIRMED_ROM** |
| Script framing `u16 next / u8 type` | **CONFIRMED_ROM** |
| Type census, 4 values across 61 targets | **CONFIRMED_ROM** |
| Type-0x05 descriptor cross-checks entry count | **CONFIRMED_ROM** |
| All 61 scripts uniquely owned by their own slot | **CONFIRMED_ROM** |
| Dispatcher reads the type byte at `+2` | **CONFIRMED** (static executable) |
| Dispatcher handles only types 0 and 4 | **CONFIRMED** (static executable) |
| Shop object record carries a scenario at `+0x0C` | **CONFIRMED_ROM** |
| Branch targets correspond to Buy / Sell / End | **INFERRED** |
| Type-0x04 codec identity | **UNKNOWN** |
| `0x02CE74C0` role | **UNKNOWN** |
| Consumer of a type-0x03 plaintext body | **UNKNOWN** |
| Type-0x03 body reaching the live dialogue cursor | **NOT ESTABLISHED** |
| `0x0801226A` is message display | **REFUTED** |
| `0x0202BA70` is dialogue state | **NOT ESTABLISHED** |
| Relocated authored dialogue | **NO** (unchanged) |

## 10. Next measured blocker

> The dispatcher at `0x08004098` accepts only script types `0x00` and `0x04`
> and asserts on all others, so it cannot be the consumer of the 17 type-`0x03`
> plaintext shop bodies. The routine that reads a type-`0x03` body and advances
> the live dialogue cursor at `0x03003898 +0x24C` is not identified.

The read-only observer `tools/runtime/toolkit038_scenario_watch.lua` is written
and armed against this question, with breakpoints on the shop record's hooks and
the two Data Crystal leads, and a channel that classifies a live cursor landing
inside the shop region separately from one in the declared pool. It requires an
operator to play into a Z-Mart; no runtime capture was performed this pass.
