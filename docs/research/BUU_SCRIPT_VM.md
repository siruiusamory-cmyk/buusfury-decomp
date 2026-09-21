# TOOLKIT-013 Buu script / event VM evidence

## Status
Selected family: the **static40 entry-root family** of Buu's Fury (USA rev 0,
SHA-256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`).
Buu **does** contain a real bytecode VM. It is the same architectural family as
the LOGII VM of TOOLKIT-006 but a **different implementation at different
addresses with different operand encodings**; no LOGII fact was transferred.

Corpus: 40 records, 120 entry roots, 548 bytes, 328 instructions, decoded
structurally and re-encoded **byte-identically over the full extent**.

## Prior knowledge audit
Consulted before fresh RE: TOOLKIT-006 (`SCRIPT_VM.md`) for the generic
abstractions only; TOOLKIT-004 text facts (`TEXT_FORMAT.md`); TOOLKIT-007/008/009
map, placement and placement-type evidence; TOOLKIT-011 free-space; TOOLKIT-012
`COLLISION_FORMAT.md` including the `MapEntry[+0x2C]` content-stream finding and
the `0x08046AA4` `__call_via_rN` correction; `SUBSYSTEM_MAP.md`; `AUTO_RE_<local-state-name>`.

Upstream audit: `extern/buusfury` is a **stub**, not a disassembly - it contains
only `src/strings.cpp`, `src/color_transforms.*` and seven small `asm/*.s` files
(413 lines total, header/crt0/RAM declarations). It carries **no** opcode table,
script walker or event structure. Its credits strings ("Lead Game Scripting",
"Script Writer") confirm the game was authored with scripts but are **not**
structural evidence. Arefu/Legacy `OpCodes.csv` + `BYTECODE_VM.cs` remain
unlicensed VERIFIED_UPSTREAM leads for LOGII only and were **not** used to
name or number any Buu opcode; every claim below is re-derived from Buu handler
code. TCRF/Data Crystal were not needed for this structural result.

## The interpreter (CONFIRMED_ROM)
Interpreter loop: **`0x08004038`**. It resets primary stack depth at
`object+0x00` and alternate depth at `object+0x44`, then repeats:

    ldrb r0,[r1]      ; fetch one opcode byte
    adds r1,#1        ; advance cursor
    lsls r0,r0,#2     ; opcode * 4
    ldr  r2,[r7,r0]   ; index primary dispatch table (r7)
    cmp  r2,#0
    beq  exit         ; a NULL slot terminates
    bl   0x08046AA4   ; __call_via veneer -> handler
    b    loop

Primary dispatch table: **`0x080554C0`**, resolved from the literal at
`0x0800415C`. Exactly **31 slots (0x00..0x1E)**; slot `0x11` is NULL =
terminate. The table ends sharply: slot `0x1F` onward is UTF-16 text
("Expected dialog to start with a c..."), so 31 is a measured bound, not an
assumption. Never extend the opcode set past `0x1E`.

Secondary native-dispatch table: **`0x08055098`** (283 Thumb handlers), with a
paired table at `0x08055478`. Both are referenced only from the interpreter
region `0x08003F40`..`0x08004034`, confirming one self-contained VM.

A ROM-wide census of contiguous Thumb-pointer runs (>=8) returns only **five**
candidate dispatch tables; three belong to this VM. Buu has exactly one
bytecode VM, not several.

## Opcode specification (structural; semantics mostly UNKNOWN)
Derived by disassembling all 31 handlers, not by transferring LOGII's table.

| Opcode | Handler | Operand encoding | Control flow |
|---|---|---|---|
| 00 | 08003C75 | one unsigned byte | next |
| 01 | 08003C8B | BE 7-bit continuation, signed magnitude | next |
| 02 | 08003CBF | one secondary-dispatch byte, native call | next |
| 03 | 08003CD5 | one secondary-dispatch byte, pops 1, native call | next |
| 04..10 | 08003CF7..08003E2D | none (logical / arithmetic / comparison) | next |
| 11 | NULL | none | **terminate** |
| 12 | 08003E47 | **two-byte big-endian** displacement | forward branch |
| 13 | 08003E57 | **two-byte big-endian** displacement | conditional forward branch |
| 14 | 08003E7D | none (pop) | next |
| 15..1A | 08003E85..08003F79 | one secondary-dispatch byte | next |
| 1B | 08003FA5 | none, transfer to alternate stack | next |
| 1C | 08003FC1 | **two-byte big-endian** displacement | **backward** loop branch |
| 1D | 08003FEF | count byte then N signed-magnitude varints | next |
| 1E | 08003D93 | none, native call | next |

### Buu-vs-LOGII divergences that would have corrupted a transferred decoder
1. **Branch width.** LOGII `0x12/0x13/0x1C` read **one unsigned byte**. Buu
   reads a **two-byte big-endian** displacement (`ldrb; ldrb +1; lsls #8; orrs`).
2. **Branch base.** LOGII targets are relative to the **post**-operand cursor.
   Buu adds/subtracts from the **pre**-operand cursor (`adds r0,r0,r2` where
   `r0` still points at the displacement).
3. **Direction.** Buu `0x12/0x13` add (forward); `0x1C` **subtracts**
   (`subs r0,r0,r2`), a backward loop branch.
4. **Slot 0x1E.** In LOGII slot `0x1E` holds a RAM address and is UNKNOWN. In
   Buu it is a genuine handler (`0x08003D93`) performing a native call.

Signed magnitude (opcodes 01, 1D) matches LOGII's contract: low bit is the sign,
remaining bits are the magnitude, 7 bits per byte big-endian until the high bit
clears. Negative zero is representable and must round-trip unchanged.

## Entry-root family (CONFIRMED_ROM)
29 Thumb `BL` sites target the interpreter. Most receive the script cursor as a
**caller-supplied register or runtime-allocated object field**, so they have no
statically enumerable roots. Exactly one site walks a **static ROM table**:

At `0x080141EE` the walker loads table base **`0x08720564`** (literal at
`0x0801441C`), forms `table + 16*i`, and calls the interpreter with the pointers
at record `+0x04`, then `+0x08`, then `+0x0C`, gated on the result at `[sp,#4]`.
The loop bound is `cmp r6,#0x28` = **exactly 40 records**.

Record layout (16 bytes): `+0x00` byte (values 0,1,2), `+0x01` byte (always 0),
`+0x02` halfword, `+0x04`/`+0x08`/`+0x0C` three script pointers.

Measured: **120 pointers, all non-null, all distinct, strictly ascending**,
spanning `0x08720340..0x0872055E`. The bytecode pool ends exactly where the
table begins, so pool extent is `0x08720340..0x08720564` = **548 bytes**.

## Corpus measurement and exhaustive ROUND_TRIP
- entry records: 40; entry roots: 120; distinct roots: 120 (no sharing)
- pool extent: 548 unique physical bytes
- instructions: 328; terminators: 120 (exactly one per root)
- **decode coverage: 548 of 548 bytes; uncovered: 0** - the roots tile the pool
  exhaustively, confirming the operand widths of the opcodes that occur
- roots failing to decode: **0**
- **re-encode is byte-identical over the full extent**
- opcodes present: `00` x108, `01` x14, `02` x84, `04` x2, `11` x120 (5 distinct)
- branch targets outside the pool: 0; not on an instruction boundary: 0
  (the corpus contains no branches, so control flow is straight-line per root)

### What the round-trip does and does not prove
OLD CLAIM (drafted earlier in this ticket): the exhaustive tiling independently
confirms **every** operand-width decision.

NEW EVIDENCE: this corpus uses only opcodes `00/01/02/04/11`, and those five
have **identical widths in both games**. Decoding it under LOGII's
`stack_be7_v1` therefore also tiles it exactly and round-trips byte-identically
(measured, not argued).

RESOLUTION: the round-trip proves the corpus is bounded, safely parsed and
losslessly re-encoded. It does **not** by itself discriminate the Buu branch
contract, because no branch opcode occurs in it. The branch contract rests on
the **handler disassembly** (`0x08003E47`, `0x08003E57`, `0x08003FC1`) - direct
CONFIRMED_ROM evidence - while the packaged-contract check is what binds the
right grammar to the right ROM. Buu's `0x12/0x13/0x1C` widths remain
unexercised by any supported corpus and would first be exercised by a family
that actually branches. Asserted by
`test_round_trip_alone_does_not_discriminate_the_grammars` so that no later
reader mistakes a passing round-trip for end-to-end validation of the encoding.

## References and semantics
- Opcode `02` appears only with secondary byte **27**, resolving through
  `0x08055098` slot 27 to native **`0x080007B7`** - a single shared native
  operation, invoked 84 times. Per the generic-shared-handler rule its gameplay
  meaning is **UNKNOWN** and it is exposed as a structural native reference only.
- Record `+0x02` holds sequential halfwords `0x0266..0x028D`. These fall inside
  the 1,534-entry text table, but a numeric operand matching a valid text index
  is **not** proof of a text reference. No path through the verified text pointer
  table and no consumer evidence was established, so this is recorded as
  **CANDIDATE, not `text_ref`**.
- No map, placement, placement-type, flag, item or enemy reference was proven
  from this corpus. No attachment is claimed.

## Corrections
None required. `0x08046AA4` remains the gcc `__call_via_rN` veneer; the
interpreter calls it as a veneer, consistent with the TOOLKIT-012 correction.
The TOOLKIT-012 `MapEntry[+0x2C]` content-stream finding is unaffected: this VM
corpus lies at `0x08720340`, outside that stream (`0x080728CC..0x0808E1E0`).

## Unsupported candidate families
The other 28 interpreter call sites take cursors from runtime objects or caller
arguments. Their scripts are reachable only at runtime, so they have **no
deterministic static entry enumeration** and are outside the supported corpus.
Bounding them is the narrow future question.

## Superseded in part by TOOLKIT-014
`docs/research/BUU_SCRIPT_OWNERSHIP.md` censused all 29 call sites and bounded a
second family, `item_use`, owned by the static item table `0x083BD2F8`. Three
statements above are narrowed by it; everything else on this page still holds.

1. **"Bounding them is the narrow future question."** One has now been bounded.
   26 call sites remain runtime-fed and unattributed.
2. **The branch contract.** This page correctly records that `static40` contains
   no branch, so Buu's `0x12/0x13/0x1C` widths rest on handler disassembly.
   `item_use` exercises `0x12` and `0x13` over 42 canonical instructions, and
   only the two-byte big-endian reading makes them real jumps rather than
   no-ops. **`0x12` and `0x13` are now corpus-backed as well as handler-derived.
   `0x1C` is still handler-derived only** - no supported corpus exercises it.
3. **The `0x0266..0x028D` CANDIDATE.** Still CANDIDATE, deliberately. TOOLKIT-014
   proved a text consumer for the *item* table's halfwords, which begin at
   `0x028E`, immediately after this range. Adjacency to a proven range is not a
   consumer, and no path from a `static40` record to the text table was found.

`static40`'s own measurements are unchanged: 40 records, 120 roots, 328
instructions, 548 bytes, 5 opcodes, no attachment.

## Addendum 2026-09-21 - a second script-controlled sprite channel, and the interpreter variables

Source: HUMAN-4-USAGE-CLOSURE-001 (recorded by HUMAN-4-RESEARCH-CAPTURE-001).
Read-only static work on the canonical image; no runtime capture, no code change.

### Native slot 78 - attached-actor construction (CONFIRMED_ROM)

Handler **`0x080013F4`**, pop 2:

```
pop1 (top)          -> r4
pop2                -> r5
alloc(0x0C) 0x0803D5B8
  obj +0x00 = 0x0804B2C8        ; relative class vtable   (0x08001418..0x0800141C)
  obj +0x04 = 0
  obj +0x08 = pop1              ; the sprite id           (0x0800141E)
r0 = r5; bl 0x080001C6
bl 0x0801936A                   ; register / queue
```

The class vtable `0x0804B2C8` is a **32-bit base-relative** table: each entry is
`method - table_base`, not an absolute pointer. Slot 1's entry at `0x0804B2CC` is
`0xFFFCD0CD`, and `0x0804B2C8 + 0xFFFCD0CD = 0x08018395`, i.e. the method at
**`0x08018394`**. Control for the convention: the map-object vtable TOOLKIT-025
recorded (`0x0804C484`) has `0xFFFC32EB` in slot 0, and
`0x0804C484 + 0xFFFC32EB = 0x0800F76F`. Absolute-pointer searches find neither,
which is why this table shape reads as "unreferenced" until the offset convention
is applied.

Method `0x08018394` reads the stored value back from **`[r0 + 0x08]`**, resolves it
through the sprite-id resolver **`0x08000158`** (`bl` at `0x080183FE`) and creates
the actor through **`0x0801111C`** (`bl` at `0x08018408`) - the same factory native
slot 53 uses. Its measured call list is
`0x08046AA2, 0x08011944, 0x08000158, 0x0801111C, 0x0801191A`.

**This is a second script-controlled sprite-id channel, distinct from slot 53
actor spawning, and a handler-body resolver scan does not see it**: slot 78's own
handler never calls `0x08000158`; the call happens later, in a vtable method.
Anything censusing sprite ids from handlers alone will under-count by this channel.

### Native slots 79 and 80 - recorded at their real verification level

* **Slot 79** (`0x08001440`) builds the **same 12-byte object with the top operand
  at `+0x08`** (`0x0800144C`, `0x0800146A`) but installs vtable **`0x0804DEA0`**.
  That class's slot 1 is method **`0x08018432`**, whose measured call list is
  `0x08046AA2, 0x08011944, 0x08009124, 0x080192BA, 0x0801142A` - it does **not**
  call `0x08000158`. Whether a slot-79 operand is a sprite id is therefore
  **NOT ESTABLISHED**, and is not claimed here.
* **Slot 80** (`0x0800148C`) does **not** perform that construction at all: it pops
  four operands and forwards the top one to `0x0805082C` (`r3`) while the deepest
  goes to `0x080001C6`, then registers through `0x0801936A`. Its object layout and
  any sprite role are **unverified**.
* **Correction to the two source reports.** HUMAN-4-USAGE-CLOSURE-001 described
  slots 79 and 80 as storing "their popped value at `+0x08` the same way". That is
  true of slot 79's *layout* only, and false of slot 80. The end-to-end verified
  channel is **slot 78**; the census below is an operand-level count over all
  three slots.

### Attached-actor census (operand level, complete 377-block corpus)

| Measure | Value |
|---|---|
| Uses of slots 78/79/80 | **25** |
| Top-popped operand literals | `1, 2, 3, 4, 5, 11, 12, 200, 252, 260, 303` |
| - from slots 78/79 | `1, 2, 3, 4, 5, 11, 12, 252, 260, 303` |
| - from slot 80 (role unverified) | `200` only |
| Variable-supplied, unresolved | 3 (`event_resource:0502` blocks 19/21/22) |
| Sprite **101** among the literals | **absent** |

### The twelve interpreter variables (indices 0..11)

The native getter slots read, and the paired table `0x08055478` above **writes**,
twelve interpreter variables. `0x08055478 = 0x08055098 + 0x3E0` = **slot 248**, so
`setter[index] = slot 248 + index`:

| Indices | Getter slots | Storage |
|---|---|---|
| 0..3 | 0..3 | `0x03001058[+0x00, +0x04, +0x08, +0x0C]` |
| 4..7 | 4..7 | the interpreter event object `[0x03001030]`, fields `+0x00, +0x04, +0x08, +0x0C` |
| 8..11 | 8..11 | `0x03001020[+0x00, +0x04, +0x08, +0x0C]` |
| 0..11 | setters | slots **248..259** |

The opcode table's rows `15..1A` ("one secondary-dispatch byte") read that byte as
the **variable index**: each handler calls `getter[index]`, mutates the top of
stack, and calls `setter[index]` - the increment/decrement variants.

Measured over the complete decoded script corpus:

* **Slots 248..259 have 0 uses.** No script assigns any of the twelve variables.
* The only variable-mutating opcode uses are **5**, all opcode **`0x15`**, on
  indices **1, 3, 6, 7** (index 1 twice).
* Fields `+0x00/+0x04/+0x08` of `[0x03001030]` are instead filled by the
  event-resource consumer family (`0x080030F8`, `0x08003126`, `0x08003164` storing
  popped operands), documented in `BUU_EVENT_RESOURCE.md`.

**Consequence, stated as a bound and not as a value:** the sprite operands of
**32** computed sites (29 native-slot-53 actor spawns + 3 attached-actor uses) are
reads of these variables, so they are engine/runtime supplied. Their runtime values
are **not inferred** and cannot currently be closed statically. No gameplay meaning
is assigned to any variable here.
