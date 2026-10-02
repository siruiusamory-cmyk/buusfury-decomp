# The shop dialogue scenario consumer

How the original Buu's Fury engine consumes a known shop-dialogue scenario and feeds
its text into the live dialogue path: the static census, the runtime chain and the
community reconciliation.

## Objective

Establish how the original Buu's Fury engine consumes one known shop-dialogue
scenario and feeds its text into the live dialogue path.

## Result

> **SHOP SCENARIO MODEL: PARTIAL** (structure confirmed, community type numbering differs)
>
> **SHOP DIALOGUE CONSUMER: NOT RUNTIME-PROVEN**
>
> **DIALOGUE CURSOR CONNECTION: NOT RUNTIME-PROVEN**

**Outcome B.** The static model is fully understood and materially stronger than
the record asked for: the region's ownership is resolved, the script framing and
type census are measured across all 61 targets, the type dispatcher is located in
the executable, and TOOLKIT-036's relocation gate is evaluated and satisfied for
all 61 scripts. The runtime chain is incomplete because the located dispatcher
**provably cannot** be the consumer of a plaintext body, and no runtime capture
was performed.

Full evidence: [BUU_SHOP_SCENARIO_MODEL.md](../../research/BUU_SHOP_SCENARIO_MODEL.md).

## Identity

- Canonical start SHA `a commit since folded into its successor`, local `master`.
- `origin/master` is a **stale local ref** at `9f5b5b7491dc20655374d6b0973db60885b86190`; local `master` is **10
  commits ahead**. SSH fetch fails with `Permission denied (publickey)`, the
  condition ROM-ATLAS-001 already recorded, so the GitLab API was not reachable
  from this session and origin state could not be independently re-read.
  **ROM-ATLAS-001's work is local-only and unpublished**, as the record
  anticipated.
- Canonical ROM `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`,
  size 8,388,608, verified before and after every read, unchanged. The atlas
  pipeline independently recorded `sha_before == sha_after` at the same value.
- Static analysis only. No save, state, memory dump or emulator run.

## Target

- **Shop**: Hercule City Z-Mart.
- **Scenario array**: `0x0877F3B0`, 10 entries, 40 bytes.
- **Event identity**: entry **28** of `event_resource.pointer_table`
  (`0x0879B704`), record extent 52 bytes.
- **Descriptor**: `0x0877F3A8`, 8 bytes, type `0x05`, count 10.
- **Recognisable first line**: script slot 1 at `0x0877F096`, type `0x03` -
  `"Welcome to the Hercule City Z-Mart! How can I help you?\n\n-Buy\n-Sell\n\n-End"`.
- **Shop object record**: `0x08074360`, scenario pointer at field `+0x0C`.
- Map / NPC placement: **NOT DETERMINED**. The scenario was reached through the
  event table and the low-ROM object record, neither of which names a map.

## Static census

All 61 targets across the six scenarios, measured against the canonical image.

### Script framing

```
+0 u16  next_script_index
+2 u8   type
+3 u8   0 or 2          (0x00 in 53 targets, 0x02 in 8)
```

### Type distribution

Every observed value, not only the ones external evidence predicted:

| type | count | payload, measured | size range |
|---:|---:|---|---|
| `0x00` | 18 | bytecode; short, repeating halfword structure | 8..30 B |
| `0x03` | 17 | UTF-16LE plaintext beginning at `+4` | 98..236 B |
| `0x04` | 20 | compressed; high entropy, shared leading bytes across shops | 44..172 B |
| `0x05` | 6 | the scenario descriptor itself | 8 B |

No other value occurs.

### Next-index validity

Valid for all six scenarios with no exception: every value in `0..entry_count`,
exactly two terminal (`next == 0`) scripts per scenario, and the last slot's
`next` equal to the entry count.

| array | count | next values |
|---|---:|---|
| `0x0877F3B0` | 10 | 1, 3, 3, 4, 5, 0, 4, 4, 0, 10 |
| `0x0877F73C` | 10 | 1, 3, 3, 4, 5, 0, 4, 4, 0, 10 |
| `0x0877FAB8` | 11 | 1, 4, 4, 4, 5, 6, 0, 5, 5, 0, 11 |
| `0x0877FE00` | 10 | 1, 3, 3, 4, 5, 0, 4, 4, 0, 10 |
| `0x08780008` | 8 | 1, 2, 3, 0, 2, 2, 0, 8 |
| `0x087803E4` | 12 | 1, 2, 3, 0, 2, 2, 2, 2, 2, 2, 0, 12 |

Walking from slot 0 in `0x0877F3B0` gives `0 -> 1 -> 3 -> 4 -> 5` with types
`0x00, 0x03, 0x00, 0x03, 0x04`: bytecode preamble, greeting, bytecode, the
"What would you like to buy?" menu, compressed body. Correspondence of specific
branches to Buy / Sell / End remains **INFERRED**, not proven.

### Model verdict

> **SCENARIO SCRIPT HEADER MODEL: STATICALLY SUPPORTED**

### Ownership, the measurement TOOLKIT-037 named as blocked

A whole-image aligned-word scan over all 8,388,608 bytes:

```
targets                 61
with extra inbound       0
uniquely owned          61
```

Every script has exactly one word-aligned inbound reference in the entire image:
its own array slot. **TOOLKIT-036's per-entry relocation gate is satisfied for
all 61 scripts.**

### The overlap ROM-ATLAS-001 flagged is resolved

ROM-ATLAS-001's seed recorded an unresolved conflict: the shop region lies inside
`event_resource.record_pool`, which TOOLKIT-019 measured as exhaustively tiled
with zero gap, and neither document reconciled them
(`tools/webfoot/atlas_producers/seed.py:546`, since rewritten).

They reconcile: **the shop speech is that pool's own record payload.** The six
scenario arrays are pool records addressed by pointer-table entries
**28, 30, 31, 33, 34, 36**, and **0 of the 61 script targets** is itself a table
entry. `BUU_DIALOGUE_TEXT_STORES.md`'s `UNOWNED` label was correct for what it
measured and is now superseded.

## External leads

| lead | verdict |
|---|---|
| `0x0801226A` reaches message display, `r1` carries text | **REINTERPRETED by TEXT-HANDLE-002** |
| `0x0202BA70` is dialogue start/state | **NOT ESTABLISHED** |
| NPC structure contains a dialogue pointer | **CONFIRMED, stronger form** |

`0x0801226A` is real code inside `func.08012230` but is `movs r0, #0`. Later
TEXT-HANDLE-002 established that the preceding `ldr r1,[r5,#4]` has loaded the
packed compressed-text handle: it is not a text pointer, direct display
instruction, handler entry, or producer, but it can be a useful breakpoint
because `r1` already carries text-related state. The independently measured
byte-`0x05` dispatcher chain, not this single instruction, is the authoritative
explanation. The instruction-encoding test remains a check that the address is
not itself a message-display call.

`0x0202BA70` has **zero** word-aligned references anywhere in the image, nor at
±4 or ±8. It is reachable only by computed addressing, so static analysis can
neither confirm nor refute the label. A test guards that absence, because the
absence is what justifies leaving the lead open.

The NPC-pointer claim holds in stronger form: five fixed-layout shop object
records carry a **scenario** pointer (not a string pointer) at `+0x0C`. Fields
`+0x00/+0x04/+0x08/+0x10/+0x14/+0x18/+0x1C` are byte-identical across all five;
`+0x00/+0x10/+0x14` are Thumb callbacks that disassemble as object lifecycle
(IWRAM address return, 0x18-byte allocation, camera math) and none touches text.
Event 36 has no record in this cluster, so five records do not cover six
scenarios.

## Runtime chain

**No runtime capture was performed.** Every edge below is static, and labelled.

| edge | status |
|---|---|
| event table entry 28 -> scenario array `0x0877F3B0` | **CONFIRMED_ROM** |
| shop object record `0x08074360` +0x0C -> scenario | **CONFIRMED_ROM** |
| array slot -> script body | **CONFIRMED_ROM** |
| script body +2 -> type byte | **CONFIRMED_ROM** |
| dispatcher `0x08004098` reads the type byte at +2 | **CONFIRMED** (static executable) |
| type `0x00` -> interpreter `0x08004038` on body+3 | **CONFIRMED** (static executable) |
| type `0x04` -> expand `0x08049120`, then interpret | **CONFIRMED** (static executable) |
| type `0x03` -> any consumer | **UNKNOWN** |
| any body -> live cursor `0x03003898 +0x24C` | **NOT ESTABLISHED** |
| rendered shop dialogue observed | **NO** |

The dispatcher, disassembled:

```
0x080040B8  ldr   r0, [r6]
0x080040BA  ldrb  r1, [r0, #2]     <- the type byte
0x080040BC  cmp   r1, #0
0x080040BE  beq   0x080040E8        type 0 -> body+3, interpret
0x080040C0  cmp   r1, #4
0x080040C2  bne   0x080040F4        neither -> assertion
0x080040EA  adds  r1, r0, #3
0x080040EE  bl    0x08004038
```

Its else-branch calls `0x0803DF14` with Webfoot's own source path
`<absolute path>`, which independently
confirms the subsystem identity. Ten BL sites call it; the interpreter has 29
callers.

**The decisive negative.** Because `0x08004098` accepts only types `0x00` and
`0x04` and asserts on everything else, it cannot be the routine that consumes the
17 type-`0x03` plaintext bodies. That is a measured structural result, not a
failure to look, and it is what makes this Outcome B rather than Outcome A.

### Type-byte proof status

The type byte's **role** is established statically: the dispatcher reads exactly
that byte and branches on it, and the branch destinations differ in a way that
matches the measured payload shapes. What is **not** established is runtime
execution of that branch for the chosen target, nor which code handles type
`0x03`. No type comparison across two live types was possible without a capture.

### Compression distinction

The chosen scenario's slot-1 greeting is **plaintext**, directly decoded, not
compressed. Type `0x04` bodies in the same scenario are compressed - high
entropy with a shared prefix across shops - and the dispatcher routes type 4
through `0x08049120`. **The codec was not identified and no compression support
was added**, per the record's boundary.

## Community reconciliation

`kin.forever`'s reported model versus measurement:

| claim | measured | verdict |
|---|---|---|
| scenario is a list of pointers to scripts | 6 arrays, 61 targets, stride 4 | **CONFIRMED** |
| `u16 next_script_index` at `+0` | all 61 in range | **CONFIRMED** |
| `u8 type` at `+2` | 4 values; dispatcher reads exactly this byte | **CONFIRMED** |
| type `0` = bytecode | 18 targets; body+3 through the interpreter | **CONFIRMED** |
| type `1` = plaintext | no `0x01` exists here; **plaintext is `0x03`** | **DIFFERS** |
| type `5` = compressed text | **compressed is `0x04`**; `0x05` is the descriptor | **DIFFERS** |
| type `7` = compressed bytecode | not observed in this corpus | **NOT OBSERVED** |
| type `9` = scenario chaining | not observed in this corpus | **NOT OBSERVED** |
| a store/full-screen type | not distinguishable; this shop uses `0x03` | **NOT OBSERVED** |

**The framing is confirmed and the constants differ.** The reporter explicitly
flagged the type numbers as recalled from memory, and that caution was warranted.
Types `0x01`, `0x07`, `0x09` may exist elsewhere in the 522-record pool; only the
61 shop scripts were censused and no claim extends beyond them.

A concise summary suitable for replying in the `Bytecode Scripts` thread is in
section 8 of the evidence document. **It was not posted**, per the record.

## Atlas impact

Producer inputs were updated; no generated output was hand-edited.

`tools/webfoot/atlas_producers/seed.py`: 51 -> **69 rows**, +18.

- 6 `shop_scenario.array_*` (CONFIRMED, sized)
- 6 `shop_scenario.descriptor_*` (CONFIRMED, 8 B each)
- 5 `shop_object.record_*` (CONFIRMED, extent not measured)
- 1 `shop_scenario.master_index` at `0x0879B774` (**CANDIDATE**: bounds and
  consumer not established)
- rewritten notes on `shop_dialogue_store`, `event_resource.record_pool` (both
  overlap warnings resolved) and `dialog.entry_point` (the new boundary finding)

Full regeneration from the canonical ROM, ~14 min, ROM hash verified by the
pipeline before and after:

| seed | `atlas.jsonl` sha256 |
|---|---|
| pre-038 baseline, 51 rows | `8b6e440023eb61fdaf0e00a3ee205ebb83e62774273b29bedf021081c7533adb` |
| **TOOLKIT-038, 69 rows (canonical at HEAD)** | `5350ba1d8708564e6408fe8db1e532b897a6cf746198d6384b5f6e290d20553a` |

The first value reproduced the digest `ROM_ATLAS_REGENERATION.md` recorded as
canonical at ROM-ATLAS-001 closure, which validates the comparison rather than
merely asserting it. Because this record's seed change is now committed, the
**second value is the canonical atlas at HEAD** and the first is retained as the
pre-038 comparison oracle in `build/atlas_v2a/`.

A later full regeneration from committed HEAD reproduced `5350ba1d...` and was
byte-identical to this record's run across **every** artifact, not only
`atlas.jsonl`, with the ROM hash verified unchanged before and after.

**The atlas delta is purely additive**: +18 rows, **0 removed, 0 reclassified**.
No coverage span, object, reference or observation moved, and zero unnamed
coverage rows changed inside the shop region. A second assembly over the same
artifacts reproduced `5350ba1d...` byte-identically, so determinism holds.

## Validation

Focused and read-only, per the record's proportionality rule. No shared
production behaviour changed - the only non-doc code change is one allowlist
entry - so the broad integration gate was not run.

| suite | result |
|---|---|
| `tests/integration/test_shop_scenario_rom.py` (new, 11 tests) | **11 passed** |
| `tests/unit/test_mgba_capture.py` | **68 passed**, 3 environment-blocked |
| `tests/unit/test_atlas*.py` | **64 passed**, 28 environment-blocked |

The 31 errors are all one cause and are **not record-caused**: `PermissionError
[WinError 5]` on the pytest `tmp_path` fixture root
(`<pytest temporary root>`). Every erroring test
requires `tmp_path`; none of them reached its body. Reproduced and preserved
rather than worked around, per the full-suite policy.

**Recorded as ONE known environment issue, not 31 findings, and deliberately
NOT worked around in product code.** The remedy belongs to the local temp-root
permissions, not to the repository: a `TMPDIR` / `--basetemp` override, or a
repaired ACL on `the per-user temporary directory`, clears every one of them without a single
source change. No machine-specific shim was added, and none should be.

`tests/unit/test_mgba_capture.py`
greps observer sources for input- and memory-writing API names and passes on the
new observer, so its read-only guarantee is enforced rather than asserted.

Observer validation: **none**. `tools/runtime/toolkit038_scenario_watch.lua` is
written, allowlisted and self-describing, but has **never been executed**, so it
carries no liveness evidence and supports no claim in this report.

## Next measured blocker

> The dispatcher at `0x08004098` accepts only script types `0x00` and `0x04` and
> asserts on all others, so it cannot consume the 17 type-`0x03` plaintext shop
> bodies. The routine that reads a type-`0x03` body and advances the live
> dialogue cursor at `0x03003898 +0x24C` is not identified.

The most probable mechanism, **INFERRED and untested**: a bytecode opcode
executed for a type-`0x00` script in the same scenario reaches the plaintext
sibling. The scenario chains bytecode and plaintext alternately
(`0x00 -> 0x03 -> 0x00 -> 0x03`), which is consistent with that reading.

### Continuation

Exactly this, and nothing wider:

> Runtime-prove the type-0x03 plaintext consumer using a shop savestate and the
> prepared TOOLKIT-038 observer.

> **BLOCKED ON HUMAN FIXTURE: shop-accessible mGBA savestate not yet available.**

`tools/runtime/toolkit038_scenario_watch.lua` is already written and
allowlisted, with breakpoints on the shop record hooks and both Data Crystal
leads, and a channel that separates a live cursor inside the shop region from
one in the declared pool. It has never run, so it carries no evidence yet. No
further static search for the plaintext consumer is warranted; the next step is
a capture.

> **SHOP SCENARIO MODEL: PARTIAL**
>
> **SHOP DIALOGUE CONSUMER: RUNTIME-PROVEN NO**
>
> **DIALOGUE CURSOR CONNECTION: RUNTIME-PROVEN NO**
