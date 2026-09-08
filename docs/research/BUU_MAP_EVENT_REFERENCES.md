# Buu's Fury map-scene event references (TOOLKIT-018)

Verified against the canonical image `buus_fury_usa_rev0_01c1707f`,
SHA-256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
Every address below is a file offset or a GBA ROM address measured in that
image. Nothing here is transferred from upstream assertion.

TOOLKIT-018 asked which operands in the supported 25-root map-scene event
corpus are verified references to stable Webfoot game resources. The answer is
two confirmed structural reference classes and one refuted hypothesis.

## Scope

The corpus is the TOOLKIT-016 owned subset, unchanged:

| Measure | Value |
| --- | --- |
| placements | 57 |
| maps | 10 |
| distinct roots | 25 |
| basic blocks | 42 |
| instructions | 202 |
| unique bytes | 514 |
| operands | 247 |
| `0x1C` backward branches | 3 |

## Opcode census

Measured over the corpus, not over the VM's 31-slot dispatch table. Opcodes the
corpus does not contain were not investigated.

| Opcode | Name | Encoding | Count | Distinct operands | Semantics |
| --- | --- | --- | ---: | ---: | --- |
| `0x00` | `push_byte` | u8 | 41 | 17 | CONFIRMED_ROM |
| `0x01` | `push_signed_magnitude` | sm7 | 2 | 2 | CONFIRMED_ROM |
| `0x02` | `native_stack` | u8 | 74 | 27 | UNKNOWN |
| `0x03` | `native_pop` | u8 | 2 | 2 | UNKNOWN |
| `0x04` | `logical_and` | none | 1 | - | CONFIRMED_ROM |
| `0x07` | `add` | none | 5 | - | CONFIRMED_ROM |
| `0x08` | `subtract` | none | 6 | - | CONFIRMED_ROM |
| `0x0F` | `less` | none | 1 | - | CONFIRMED_ROM |
| `0x11` | `terminate` | none | 25 | - | CONFIRMED_ROM |
| `0x12` | `branch_forward` | be16 | 1 | 1 | CONFIRMED_ROM |
| `0x13` | `branch_if_zero` | be16 | 5 | 3 | CONFIRMED_ROM |
| `0x1B` | `transfer_to_alternate` | none | 3 | - | CONFIRMED_ROM |
| `0x1C` | `alternate_count_back` | be16 | 3 | 3 | CONFIRMED_ROM |
| `0x1D` | `push_many` | count_sm7 | 33 | 48 | CONFIRMED_ROM |

Fourteen opcodes, 202 instructions. The three `0x1C` occurrences are the
project's only canonical exercise of that opcode and remain unchanged.

## Investigated families

The ticket authorised at most three deep investigations. All three were spent.

### 1. `0x1D push_many` feeding `0x02 native_stack` slot 182

Slot 182 of the native dispatch table `0x08055098` holds `0x080030F9`, so the
handler entry is `0x080030F8`. It pops two stack values:

    0x080030F8  push  {r3, lr}
    0x080030FA  ldr   r1, [r0]            ; stack depth
    0x080030FC  ldr   r2, =0x03001030     ; runtime object holder
    ...
    0x0800310A  str   r1, [r3]            ; first pop  -> object field +0x00
    ...
    0x08003116  ldr   r0, [r0, #4]        ; second pop -> table index
    0x08003118  ldr   r1, =0x0879B704     ; <- the table
    0x0800311A  lsls  r0, r0, #2
    0x0800311C  ldr   r0, [r1, r0]        ; index it
    0x0800311E  ldr   r1, [r2]
    0x08003120  bl    0x08012588
    0x08003124  pop   {r3, pc}

The value that indexes the table is the one popped **last**, which is the value
pushed **first** by `push_many`. This ordering was read from the handler, not
assumed from operand position.

### 2. `0x01 push_signed_magnitude` feeding `0x02 native_stack` slot 29

Slot 29 holds `0x080007E7`, entry `0x080007E6`. It pops one value into `r1`,
loads a runtime object into `r0`, and calls `0x08004380`:

    0x08004380  asrs  r2, r1, #3      ; byte index  = operand >> 3
    0x08004382  adds  r0, r2, r0
    0x08004384  lsls  r3, r1, #0x1d
    0x08004386  adds  r0, #0x50
    0x08004388  ldrb  r2, [r0, #5]
    0x0800438A  lsrs  r3, r3, #0x1d   ; bit index   = operand & 7
    0x0800438C  movs  r1, #1
    0x0800438E  lsls  r1, r3
    0x08004390  orrs  r1, r2          ; SET the bit
    0x08004392  strb  r1, [r0, #5]
    0x08004394  bx    lr

`0x08004396` is the matching routine with `bics` in place of `orrs`, i.e. bit
clear. The corpus reaches only the `orrs` form, so only SET is claimed.

### 3. `0x02 native_stack` slot 216

Slot 216 holds `0x0800327F`, entry `0x0800327E`. It pops three values; the
first two are stored into the same `0x03001030` runtime object, and the third
and deepest indexes the same table `0x0879B704` through the identical
`lsls #2` / `ldr` sequence. This independently corroborates family 1.

## CONFIRMED: event -> event resource record

Table base `0x0879B704`, file offset `0x79B704`.

| Property | Value |
| --- | --- |
| entries | 522 |
| entry width | 4 bytes, absolute ROM pointer, little-endian |
| table extent | file `0x79B704`..`0x79BF2C` (2,088 bytes) |
| record pool | `0x0877C5A4`..`0x0879B704` (127,328 bytes) |
| ordering | strictly ascending, all word aligned |
| tiling | records tile the pool contiguously and exhaustively |
| inbound refs to base | exactly 2, both consumer literal pools (file `0x31C0`, `0x3444`) |

The pool ends exactly where the table begins, the same signature carried by
every other verified Webfoot table in this project. Records are variable size
(16 to 3,168 bytes; 61 records are the minimum 16). All 522 records begin with
a ROM pointer, 521 of which point back inside the pool.

The table bound is corroborated a second, independent way. The ascending-pointer
walk terminates at file `0x79BF2C`; Data Crystal's ROM map records `0x0879BF2C`
as the start of a separate compressed-text region, its pointer stored at
`0x7B5B64`. Both pointers were verified present in our own image. Two methods,
one boundary.

Record internals are **not** decoded. Records are composite: header pointers
followed by a region that resembles bytecode but does not tile as a script under
`stack_be16_buu_v1` from any offset. No gameplay meaning is assigned, so the
class is named structurally, `event_resource`, never "dialogue", "cutscene",
"quest" or "trigger".

Corpus coverage: 15 referencing instructions across 15 events on 4 maps (19,
21, 22 and 325), resolving to 4 distinct records (indices 393, 506, 508, 509),
all in range and all resolving inside the pool. Because events are shared,
those 15 events are reached by 47 placements; a reference query reports all of
them rather than the first.

## CONFIRMED: event -> save flag [SET]

Two references, operands 266 and 267, in events
`map:0240/placement:0000` and `map:0240/placement:0001`. Under the handler's
own arithmetic these are byte 33, bits 2 and 3.

Exposed as `save_flag:0266` and `save_flag:0267`. The access mode recorded is
SET only, because only `0x08004380` is reached. Read, clear and toggle are not
claimed. Individual flag meanings remain UNKNOWN; no flag is named for a quest,
boss, NPC or cutscene.

## REFUTED: event -> text

OLD CLAIM / HYPOTHESIS: the strongest map-scene event operands look like Buu
text IDs. Ten events on map 19 each run the identical three-instruction script
`push_many(2, 508|509, 388..397); native_stack(182); terminate`, with operand
values running consecutively 388, 389, 390, 391, 392 and 393, 394, 395, 396,
397 across sibling NPC placements while the other operand stays constant. That
is the exact shape of a per-NPC dialogue fan, and every value lies inside the
verified 0..1533 text-ID range. Operands 266 and 267 are likewise in range.

NEW EVIDENCE:

- The consumer indexes `0x0879B704`, not the verified text pointer table
  `0x0806BCE8`. The 388..397 values are not even the index; they are the
  runtime argument stored into the `0x03001030` object.
- Operands 266 and 267 reach a bitfield set operation, not a text lookup.
- None of the three consumer functions `0x080030F8`, `0x0800327E` or
  `0x08012588` carries a literal for the text table `0x0806BCE8`.
- No word in any of the 522 records references the text table base.
- Exactly three record words fall inside the text pool's numeric range, and all
  three are refuted individually: none is one of the 1,534 real string starts,
  and two (`0x0806021D`, `0x0806031D`) are odd aligned, which is impossible for
  a UTF-16LE string start.
- `0x08012588` is a generic constructor. It allocates 8 bytes, stores vtable
  `0x08049D18` and queues into `0x03002A58`. It is the same routine descriptor
  handler `0x0800424F` calls, i.e. a shared constructor, not a text consumer.

RESOLUTION: the text-reference hypothesis is **REFUTED** for the three
investigated map-scene candidate families. It is not left at CANDIDATE, and
regression tests pin the refutation so a future numeric coincidence cannot
revive it. The scope of this refutation is the investigated families of the
supported corpus; it is not a claim that no Buu map event anywhere references
text.

Consequently no `event -> text`, `placement -> text` or `map -> text` edge is
emitted for this family.

## Correction to the TOOLKIT-018 premise

OLD CLAIM: the ticket's section 7 directs reuse of the TOOLKIT-014 text proof,
requiring only that a map-scene operand reach the same consumer "in the same
argument position".

NEW EVIDENCE: TOOLKIT-014 proved an **item-record** to text reference, not a
script-operand one. At `0x0801F85E` the instruction `ldrh r2,[r2,#2]` reads the
item record's `+0x02` halfword, a field of a static data table, and no script
operand participates.

RESOLUTION: there is no script-operand argument position in that proof for a
map-scene operand to occupy, so section 7 is not applicable. TOOLKIT-014's
`item_use -> text` result is untouched and remains CONFIRMED.

## Reference states, kept distinct

| Family | Text state |
| --- | --- |
| `item_use` | CONFIRMED (TOOLKIT-014, unchanged) |
| `static40` `0x0266..0x028D` | CANDIDATE (TOOLKIT-013, unchanged) |
| map-scene investigated families | REFUTED (this ticket) |

## Vendor corroboration of the VM

The canonical image retains one Webfoot build path at file `0x00416A`,
`T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp`, adjacent to
interpreter `0x08004038`. The subsystem's own name is therefore
ByteCodeInterpreter, corroborating the TOOLKIT-013 identification from the
binary itself rather than from upstream claim.

Buu retains only this one path string; searches for `K:\Source`, `Dialog`,
`Trigger` and `SaveState` return zero hits. The richer sibling set documented
for Legacy of Goku II, including `ByteCodeFunctionList.cpp`, is not present in
Buu, so no Buu structure is named from it.

## Capability matrix

| Capability | Status |
| --- | --- |
| map -> placement | Supported |
| placement -> descriptor | Supported |
| descriptor -> map-scene event | Supported, 57-placement subset |
| map-scene event -> text | REFUTED for the three investigated candidate families |
| map-scene event -> event resource record | CONFIRMED |
| map-scene event -> save flag | CONFIRMED, SET access only |
| save-flag gameplay meaning | UNKNOWN |
| event resource record gameplay meaning | UNKNOWN |
| event resource record internals | Not decoded |
| semantic script WRITE | Absent |
| AUTHOR_NEW | Absent |
| script growth | Absent |

## Future lead, not investigated

Data Crystal records seven compressed-text pointers beginning `0x0879BF2C`,
stored at `0x7B5B64`..`0x7B5B7C`; all seven values were verified present in our
image. That region is outside the verified 1,534-entry UTF-16LE pool
(`0x5792C`..`0x6BCE6`). It was deliberately **not** investigated: the ticket's
three-family budget was spent, and it is recorded only as a lead. No TOOLKIT-018
claim depends on it, and it is not asserted to belong to this event family.

Data Crystal's `struct NPC` is a different structure from our verified
placement record. It has six fields led by a constant `0x08017DA3` header,
whereas the verified placement is `0x1C + 4n` led by `0x0800FD55` with the
behavior descriptor at `+0x14`. Its `dialogue` field is an unverified upstream
label on a different layout and is not evidence for this corpus.

## Operand identity is positional

An operand is identified by its position within its producer, never by matching
its value. The classifier originally located the selected operand with a
by-value lookup, which returns the first equal operand.

On this corpus the two rules agree everywhere: every selected index sits at
position 1 and is the first occurrence of its value, so the by-value lookup was
not producing wrong offsets. This is a latent fragility that was corrected, not
an observed defect - stated plainly because the distinction matters.

The rules do diverge on real data as soon as a duplicated operand is selected.
`block:0010` (map 21) pushes `(3, 506, 0, 0)`; its two zeros are both one byte
wide, so they occupy different offsets while decoding to the same value.
Selecting the trailing zero by position gives file `0x73B01`, whereas the
by-value lookup gives the first zero at `0x73B00`. A regression test drives the
classifier at that depth and asserts the exact offset, because a value
comparison alone cannot tell the two zeros apart.

## Method note

The values that looked most like text references were not text references. The
consecutive per-NPC fan, the constant sibling operand and the in-range numeric
values were all present, and all of it was circumstantial. Only following the
consumer settled it. Numeric resemblance to an existing resource namespace is
not reference evidence; this is the same discipline that kept `static40` from
being promoted on adjacency in TOOLKIT-014.
