# TOOLKIT-032 - Runtime execution of an authored script body

Canonical ROM `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
(`Dragon Ball Z - Buu's Fury (U).gba`, 8,388,608 bytes). Read-only throughout.
Baseline `0000000000000000000000000000000000000000`.

TOOLKIT-031 proved **RUNTIME-PROVEN AUTHORED BEHAVIOR: YES** - the engine
executes a behavior the SDK attached to a newly authored entity. It left one
boundary standing: the behavior, its descriptor and its script body were all
canonical content the SDK *selected*. Nothing was *created*.

This ticket removes that boundary.

> **AUTHORED SCRIPT BODY: YES**
>
> **RUNTIME-PROVEN NEW BEHAVIOR CONTENT: YES**

```text
authored entity           map:0040/authored:tk032
-> authored descriptor    map:0040/authored:tk032/behavior         0x087EA420
-> authored script body   map:0040/authored:tk032/behavior/script  0x087EA428
-> engine instantiates    live slot 4 carries 0x087EA400
-> descriptor dispatched  pc 0x08004220, r0 = 0x087EA420
-> script pointer taken   [r0+4] = 0x087EA428
-> interpreter enters     pc 0x0800403A, cursor = 0x087EA428
-> authored bytes walked  00 54 00 4B 07 14 11
-> STOP
```

## 1. The authored script body

| | |
|---|---|
| Bytes | `00 54 00 4B 07 14 11` (7 bytes) |
| Semantic identity | `map:0040/authored:tk032/behavior/script` |
| Authored form | `["push_byte 84", "push_byte 75", "add", "pop", "terminate"]` |

Decoded under `stack_be16_buu_v1`:

| Offset | Opcode | Name | Semantics evidence |
|---|---|---|---|
| +0 | `0x00` | `push_byte(0x54)` | CONFIRMED_ROM |
| +2 | `0x00` | `push_byte(0x4B)` | CONFIRMED_ROM |
| +4 | `0x07` | `add` | CONFIRMED_ROM |
| +5 | `0x14` | `pop` | CONFIRMED_ROM |
| +6 | `0x11` | `terminate` | CONFIRMED_ROM |

Every opcode used already carried CONFIRMED_ROM semantics before this ticket;
none of the ten UNKNOWN-semantics opcodes (`2, 3, 10, 21..26, 30`) appears. No
branch, no native call, no dialogue, no save flag, no variable.

**The body computes a value and discards it.** That is deliberate: the ticket's
acceptance is *execution of authored content*, and a script whose only effect is
internal to the VM stack cannot be confused with a canonical side effect.

### Why seven bytes and not three

The obvious minimal body is `push_byte(N); terminate` - three bytes. It was
measured and **rejected**:

| Candidate | Occurrences in canonical ROM |
|---|---|
| `00 2A 11` | 3 |
| `00 37 11` | 4 |
| `00 5B 11` | 5 |
| `00 7D 11` | 2 |
| **`00 54 00 4B 07 14 11`** | **0** |

A three-byte body appears incidentally in canonical bytes, which would have
weakened the independence claim to "these bytes are at a new address" rather
than "these bytes are new". The seven-byte body occurs **zero** times in the
whole 8 MB image, so the stronger claim is available and is the one made.

### Production codec, not a byte literal

The body is produced by `formats/script_vm.assemble_source`, which encodes the
mnemonic list, validates each instruction through the production
`decode_instruction`, and then proves the whole body by `disassemble` /
`assemble` round-trip. Measured: `opaque == ()` and `assemble(ir) == body`.

`assemble_source` encodes only the two operand widths a straight-line body can
use - `none` and `u8`. Branch displacements (`be16`) and varints (`sm7`) are
refused **by name** rather than mis-encoded. This is deliberately not a script
compiler; arbitrary branching remains out of scope.

The author-facing form is a list of opcode mnemonics resolved against the
profile's own verified `OpcodeSet`, so an authored body can only ever contain
instructions this toolkit decoded from canonical bytes. No raw ROM address is
accepted as an authoring input.

## 2. The authored descriptor

| | |
|---|---|
| Bytes | `1f 42 00 08 28 a4 7e 08` |
| Decoded | `DescriptorRecord(handler=0x0800421F, payload=0x087EA428)` |
| Semantic identity | `map:0040/authored:tk032/behavior` |

`0x0800421F` is `SCRIPT_DISPATCH_HANDLER` - the same handler TOOLKIT-031
observed dispatching at runtime. Serialization goes through the production
`DescriptorRecord.to_bytes`; no parallel descriptor format exists.

The `payload` word is the address the allocator gave the authored script body in
this build. Using the correct handler alone would not be sufficient, and the
build asserts the pointer equality against the ROM it emitted.

## 3. Measured allocation

Demand was **measured**, not estimated, by wrapping the production
`allocation.allocate` and recording every request the build actually issued.

| Structure | Size | Align | File offset | GBA address |
|---|---|---|---|---|
| placement body | 32 | 4 | `0x7EA400` | `0x087EA400` |
| authored descriptor | 8 | 4 | `0x7EA420` | `0x087EA420` |
| authored script body | 7 | 4 | `0x7EA428` | `0x087EA428` |
| expanded object array | 20 | 4 | `0x7EA430` | `0x087EA430` |
| **total** | **67** | | | |

Issue order is bodies first, array second: the array payload must contain the
bodies' addresses before it can be written. Region `[0x7EA400, 0x7EA500)` is 256
bytes, so **188 bytes remain**. Zero overlaps.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION - the 59-byte expectation

**OLD CLAIM.** Demand would be 59 bytes: 32 body + 12 array + 8 descriptor + 7
script, carrying the 12-byte array figure forward from TOOLKIT-028.

**NEW EVIDENCE.** Production requested **67**. TOOLKIT-028's 12-byte array was
map 10's, which has 2 canonical object slots. **Map 40 has 4**, so its expanded
array is 5 slots x 4 = **20 bytes**.

**RESOLUTION.** The measured demand is 67 bytes. The 59-byte figure was an
estimate transferred across maps and is superseded. The array size is a property
of the target map, never a constant.

## 4. Determinism and immutability

| | |
|---|---|
| Generated ROM SHA-256 | `3f32b629925b737074f3e18d76724a90d927f3e157dd396d4a757fb324e6490c` |
| Second build | byte-identical, same SHA, identical manifest |
| Changed bytes vs canonical | **71** |
| Canonical no-op build | `940ad5f0...f059e`, byte-identical to canonical |
| Canonical ROM after all work | `940ad5f0...f059e`, unchanged |
| Canonical savestate | `2d5740a8...1aab`, unchanged |

No generated ROM is committed; output stays under the ignored `build/` tree.

## 5. Independence

The claim is not that execution happened at a new address. It is that the
**script content itself** is new.

| Offset | canonical | control | authored |
|---|---|---|---|
| `0x7EA428` (script) | `ff ff ff ff ff ff ff` | `58 56 07 08 70 56 07` | **`00 54 00 4B 07 14 11`** |
| `0x7EA420` (descriptor) | `ff ff ff ff ff ff ff ff` | `20 56 07 08 38 56 07 08` | **`1f 42 00 08 28 a4 7e 08`** |

Whole-image occurrence counts of the exact authored byte sequences:

| Sequence | canonical | control | authored |
|---|---|---|---|
| script body (7 bytes) | **0** | **0** | 1 |
| descriptor (8 bytes) | **0** | **0** | 1 |

The control build is the TOOLKIT-029 authored entity *without* an authored
behavior - ROM `a425ae73...`. It contains neither structure, and the bytes at
those offsets are ordinary relocated array content, which is what makes the
comparison meaningful rather than a comparison against `FF` padding alone.

## 6. Runtime execution

Instrument: `tools/runtime/toolkit032_authored_script_watch.lua`, read-only,
under mGBA 0.11 dev (scripted-breakpoint API). Addresses are supplied from the
build manifest through the environment rather than hardcoded, so the observer
cannot be watching an address the build did not use.

### The discriminator

TOOLKIT-031 watched the trampoline `0x0800421E`. That is insufficient here,
because the script it ran was canonical. This observer additionally breakpoints
the interpreter `0x08004038` and asks whether the **live cursor** points into
`[0x087EA428, 0x087EA428 + 7)`, then reads those seven bytes back out of the
running machine.

The cursor register is probed, not assumed: the trampoline does
`ldr r1,[r0,#4]`, so `r1` is expected, but `r0`/`r2`/`r3` are also tested and the
hit is recorded by register name. This avoids both a false negative from
watching the wrong register and a false positive from asserting a register
convention that was never measured.

### OBSERVED

Three executions, identical attribution each time:

| Frame | Map | Descriptor dispatch | Interpreter entry | Cursor | Bytes at cursor |
|---|---|---|---|---|---|
| 4419 | 40 | `pc 0x08004220`, `r0 0x087EA420`, `[r0+4] 0x087EA428` | `pc 0x0800403A` | `0x087EA428` | `00 54 00 4B 07 14 11` |
| 6515 | 40 | same | `pc 0x0800403A` | `0x087EA428` | `00 54 00 4B 07 14 11` |
| 8154 | 40 | same | `pc 0x0800403A` | `0x087EA428` | `00 54 00 4B 07 14 11` |

Channel totals over 8,460 frames:

| Channel | Count | Meaning |
|---|---|---|
| `AUTHORED-SCRIPT-ENTERED` | **3** | interpreter entered the authored body |
| `AUTHORED-DESCRIPTOR` (trampoline) | **3** | authored descriptor dispatched, same frames |
| `LIVENESS` | **19** | instrument provably observes script execution |
| `AUTHORED-ATTACHMENT-LIVE` | **115** | authored entity resident with the authored chain |

### The map-departure control

The operator left map 40 during the session to reach NPCs. This **strengthened**
the run rather than compromising it.

Liveness hits 1 and 2 fired on **map 39**, where the authored entity does not
exist and the authored path is therefore impossible. The instrument proved it
sees interpreter execution on ground where our result cannot occur, and then the
authored path was observed **only** on map 40. That is a stronger instrument
validation than an uninterrupted map-40 session would have produced.

Per the standing rule (`docs/runtime-capture.md`, TOOLKIT-029/030 invalidations),
a silent channel is not evidence of absence. This run is in the "target fires"
row, and the liveness channel is nonzero independently.

## 7. OBSERVED vs INFERRED

**OBSERVED.** The interpreter's live cursor held `0x087EA428` - the exact
address this build's allocator assigned the authored script - at `pc 0x0800403A`
on frames 4419, 6515 and 8154, with the authored descriptor `0x087EA420`
carrying that pointer at the trampoline on the same frames, and the seven bytes
read back from that cursor in the running machine equal to the authored body.
The authored entity was resident with the authored chain throughout (115
structural samples).

**INFERRED.** That each of the five authored instructions retired individually.
The instrument proves entry into the body and the bytes present at the cursor;
it does not step the VM. Entry plus a terminating body is what is claimed.

**NOT CLAIMED.** Any visible gameplay effect. The script computes and discards.
No screen, actor or world-state change is attributed to it, and none was
observed. The ticket permits this when execution attribution is exact, and here
it is exact.

**NOT CLAIMED.** The exact trigger action. Its shape only: gameplay-driven and
intermittent, consistent with TOOLKIT-031's finding that map construction is
refuted as the trigger.

## 8. Exact next blocker

The SDK can now author executable behavior content. It cannot yet author
behavior with an **observable gameplay effect**.

Measured boundary:

* every opcode with a gameplay effect routes through `native_stack` (`0x02`) or
  `native_pop` (`0x03`) - `native_opcodes: (2, 3)` in the placement contract;
* both carry **UNKNOWN** semantics in `stack_be16_buu_v1`;
* the secondary native dispatch table `0x08055098` holds **283** Thumb handlers
  (`BUU_SCRIPT_VM.md`), none with established gameplay meaning.

> **NEXT BLOCKER: establish at least one gameplay-effect native handler semantic
> so authored behavior can produce an observable effect.**

Narrow by construction: **one** handler with proven meaning is enough to author
an intentional visible effect. This is not a 283-handler campaign, and nothing
here proposes one.

## 9. Validation

| Suite | Result |
|---|---|
| `tests/unit` (full) | **995 passed** (baseline 971, +24, zero regressions) |
| `tests/unit/test_authored_behavior_body.py` | included above (new) |
| `tests/integration/test_authored_behavior_body_rom.py` | included above (new) |
| `tests/unit/test_mgba_capture.py` | 68 passed - observer read-only guarantee |

Pinned by test: the authored declaration parses; identities are stable and
semantic; descriptor and script serialize through production codecs; the
descriptor's payload equals the allocated script address read back from the
built ROM; references resolve; allocations do not overlap; capacity accounting
is exact; output is deterministic; the canonical no-op stays byte-identical; the
canonical source is immutable; and **the authored 7-byte body occurs zero times
in the canonical ROM**.
