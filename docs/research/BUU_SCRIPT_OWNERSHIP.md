# TOOLKIT-014 Buu script ownership and attachment evidence

## Status
Selected family: the **`item_use`** family of Buu's Fury (USA rev 0, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`).

TOOLKIT-013 left one narrow question open: 28 of 29 interpreter call sites took
their script cursor from a runtime object or caller register, so no attachment
could be proven and the Buu branch contract rested on handler disassembly alone.
This ticket closes both. A **static ROM record now owns a script**, the resulting
corpus **exercises real branch opcodes**, and its **text references are proven
through the verified text pointer table** rather than asserted from a numeric
range.

Chain, end to end:

    item record 0x083BD2F8 + 52*index
      -> record +0x30 (script pointer)
      -> interpreter 0x08004038
      -> bounded 703-byte corpus, 23 roots, exact round-trip

## Prior knowledge audit
Consulted before fresh RE: TOOLKIT-013 `BUU_SCRIPT_VM.md` (interpreter, dispatch
table, 31 opcode slots, `static40`); TOOLKIT-004 `TEXT_FORMAT.md` (text pointer
table `0x0806BCE8`, 1,534 entries); TOOLKIT-007 `MAP_FORMAT.md`; TOOLKIT-008
placement format; TOOLKIT-009 `PLACEMENT_TYPES.md` (table `0x08711274`, stride
28, constructor `0x0800F68C`); TOOLKIT-011 free space; TOOLKIT-012
`COLLISION_FORMAT.md` including the `MapEntry[+0x2C]` content stream and the
`0x08046AA4` `__call_via_rN` correction; `SUBSYSTEM_MAP.md`; `AUTO_RE_<local-state-name>`.

Upstream `extern/buusfury` remains the stub recorded in TOOLKIT-013: no opcode
table, no script walker, no item structure. Nothing was transferred from it.
Arefu/Legacy remain LOGII-only leads and were not used. Every claim below is
re-derived from Buu code and Buu bytes.

## Census of all 29 interpreter call sites
Every Thumb `BL` whose target is `0x08004038`, with the instruction that last
defines `r1` (the script cursor) before the call. Method: enumerate BL pairs
ROM-wide with the shared decoder, locate each site's `push {..., lr}` prologue,
then disassemble forward and keep the final writer of `r1`.

| # | Call site | Enclosing proc | Cursor `r1` from | Source class |
|---|---|---|---|---|
| 1 | `0x080040DC` | `0x08004098` | `adds r1,r5` (allocated buffer) | runtime object |
| 2 | `0x080040EE` | `0x08004098` | `adds r1,r0,#3` where `r0=[r6]` | runtime object |
| 3 | `0x0800422E` | `0x0800421E` | `ldr r1,[r0,#4]` | caller argument |
| 4 | `0x08004246` | `0x0800423A` | `r1` is the incoming argument | caller register |
| 5 | `0x080047FE` | `0x08004784` | `adds r1,r0` | caller register |
| 6 | `0x0800737E` | `0x08007368` | `ldr r1,[r0,#0x10]` | runtime object |
| 7 | `0x080089C4` | `0x080089A0` | `ldr r1,[r0,#0x28]` | runtime object |
| 8 | `0x080089F4` | `0x080089D8` | `ldr r1,[r0,#0x24]` | runtime object |
| 9 | `0x08008A4E` | `0x08008A36` | `ldr r1,[r1,#0x0C]` | runtime object |
| 10 | `0x08008CE8` | `0x08008B30` | `adds r1,r7` | runtime object |
| 11 | `0x08008CFE` | `0x08008B30` | `ldr r1,[r0,#0x30]` | runtime object |
| 12 | `0x0800908C` | `0x08009030` | `adds r1,r5` | runtime object |
| 13 | `0x080090A0` | `0x08009030` | `ldr r1,[r0,#0x30]` | runtime object |
| 14 | `0x080091E0` | `0x080091B8` | `adds r1,r4` from `[r1,#0x34]` | runtime object |
| 15 | **`0x0800F67A`** | `0x0800F62C` | `ldr r1,[r4,#0x18]` | **unreferenced proc** |
| 16 | `0x08011F8C` | `0x08011F5A` | `adds r1,r7` | caller register |
| 17 | `0x080121BC` | `0x080121A8` | `adds r1,#8` | caller argument |
| 18 | `0x08012204` | `0x080121D8` | `adds r1,#8` | caller argument |
| 19 | `0x08012310` | `0x080122B4` | `adds r1,#8` | caller argument |
| 20 | `0x08013C5E` | `0x08013C02` | `ldr r1,[r1,#0x28]` | runtime object |
| 21 | `0x080141FA` | `0x08014188` | `ldr r1,[r4,#4]` | **static table** (`static40`) |
| 22 | `0x0801420A` | `0x08014188` | `ldr r1,[r4,#8]` | **static table** (`static40`) |
| 23 | `0x08014232` | `0x08014188` | `ldr r1,[r4,#0x0C]` | **static table** (`static40`) |
| 24 | `0x0801E15C` | `0x0801E14C` | `ldr r1,[r0,#0x30]` | **static record** (see below) |
| 25 | **`0x0801E182`** | `0x0801E164` | `ldr r1,[r0,#0x30]` | **static record - selected** |
| 26 | `0x08025A96` | `0x0802574C` | `ldr r1,[r0,#4]` | runtime object |
| 27 | `0x0803331E` | `0x08033308` | `ldr r1,[r0,#4]` | caller argument |
| 28 | `0x0803336C` | `0x08033360` | `r1` is the incoming argument | caller register |
| 29 | `0x0803339C` | `0x08033390` | `r1` is the incoming argument | caller register |

Sites 21-23 are the TOOLKIT-013 `static40` walker and were already supported.
Of the remaining 26, sites 24 and 25 are the only ones whose `r0` is proven to
be a **static ROM record** rather than a heap object.

### Selection rationale
Site 25 (`0x0801E182`, proc `0x0801E164`) was selected because its owner is
static, its enumeration is deterministic, and it was reachable without runtime
instrumentation. Site 15 was inspected first and **rejected**: proc `0x0800F62C`
has a plausible descriptor shape but **zero inbound references anywhere in the
ROM** - no `BL`, no aligned word, no unaligned word - so no owner can be proven
for it. That is recorded rather than glossed, because "looks like a descriptor"
is not evidence of ownership.

No runtime instrumentation was used. Static tracing settled ownership, so per
the ticket's own rule no probe was run.

## The static owner (CONFIRMED_ROM)
Proc `0x0801E164` reads `[r0+0x30]` and passes it to the interpreter:

    0x0801E168  ldrb r1,[r0]        ; owner record byte +0x00
    0x0801E16E  lsls r1,r1,#0x1E    ; isolate bit 1
    0x0801E170  lsrs r1,r1,#0x1F
    0x0801E176  beq  0x0801E18A     ; bit clear -> no script path
    0x0801E178  ldr  r1,[r0,#0x30]  ; the script cursor
    0x0801E182  bl   0x08004038     ; interpret it

Its two callers both form `r0` as `table + 52*index` over one static base:

    0x0800D742  movs r0,#0x34            ; 52
    0x0800D744  ldr  r1,=0x083BD2F8      ; literal at 0x0800D880
    0x0800D746  muls r0,r4,r0            ; r4 = index
    0x0800D748  adds r0,r0,r1
    0x0800D74E  bl   0x0801E164

    0x0800DDBE  movs r3,#0x34
    0x0800DDC2  ldr  r1,=0x083BD2F8      ; literal at 0x0800DE1C
    0x0800DDC4  muls r0,r3,r0            ; r0 = [r7+4], r7 = [r4+0x30]
    0x0800DDC6  adds r0,r0,r1
    0x0800DDFA  bl   0x0801E164

The second caller is an overlap/trigger handler: it compares four bounding-box
edges (`+0x34/+0x38/+0x3C/+0x40` against `[r6+0]/[r6+4]/[r6+8]/[r6+0x0C]`) and
only then runs the record's script. This is recorded structurally; **no role
name such as "on_pickup" or "on_use" is claimed**, because the consumer
semantics were not proven.

The same base is loaded from **twelve** independent literals across the ROM
(`0x0800D524`, `0x0800D880`, `0x0800DE1C`, `0x08016790`, `0x08016AA0`,
`0x0801E478`, `0x0801F7BC`, `0x0801FB50`, `0x0802BD48`, `0x08031C44`,
`0x080321B4`, `0x080325B4`), all with stride 52. An independent corroboration at
`0x0801E1FE` loads `table + 52*index + 0x30` and tests it against zero to set a
capability flag, confirming that `+0x30` is understood by the game itself as an
optional per-record script.

### Owner identity
The record is the game's **item** record: 83 records of 52 bytes at
`0x083BD2F8`, ending at `0x083BE3D4`. Record identity is established by its own
text, not by an upstream name - see the next section, where index `0x028E`
resolves to `"Miso Soup"` and `0x0291` to
`"A tasty, yet nutritious soup. Restores 20 hit points."`.

Attachments are therefore exposed at **item level**: `item:NNNN` to `event:...`.
There is no map, placement or placement-type attachment in this family, and none
is claimed. `MapEntry[+0x2C]` content-stream boundaries are untouched; this
corpus lies at `0x083BBBB0`, far outside that stream.

## Text references (CONFIRMED_ROM - promoted)
Each item record carries four halfwords at `+0x02`, `+0x04`, `+0x06`, `+0x08`.
These are **proven consumers**, not a numeric range match:

    0x0801F818  ldr  r1,=0x0806BCE8   ; the TOOLKIT-004 text pointer table
    ...
    0x0801F85E  ldrh r2,[r2,#2]       ; item record +0x02
    0x0801F860  lsls r2,r2,#2         ; * 4
    0x0801F862  ldr  r1,[r1,r2]       ; index the text pointer table

That is a real dereference through the verified table, which is exactly the
proof path TOOLKIT-013 required and could not supply for `static40`.

Measured: **all 83 records** have four in-range, decodable text indices
(332 references total). Spot-verified decodes: index `0x028E` gives
`"Miso Soup"`, `0x0290` gives `"Miso Soups"`, `0x0291` gives the description
string; `0x0292` gives `"Rice Ball"`; `0x03D2` gives `"Z. Exhibit #15"`. The
four slots are singular, singular, plural and description.

OLD CLAIM (TOOLKIT-013): sequential halfwords `0x0266..0x028D` in the `static40`
records fall inside the text table, recorded **CANDIDATE** because no consumer
was proven.

NEW EVIDENCE: a consumer for the *item* table's halfwords is now proven at
`0x0801F85E..0x0801F862` through `0x0806BCE8`. The item ids begin at `0x028E`,
immediately after the `static40` candidate range ends at `0x028D`.

RESOLUTION: **`item_use` text references are promoted to CONFIRMED_ROM.** The
`static40` values `0x0266..0x028D` **remain CANDIDATE**: adjacency to a proven
range is suggestive, not a consumer. They are a different table read by
different code, and no path from a `static40` record to the text table was
found. Promoting them on adjacency would be exactly the numeric-match error the
previous ticket refused to make.

## Corpus measurement and exhaustive ROUND_TRIP
- owner records: **83**; records owning a script: **23**; null `+0x30`: 60
- entry roots: **23**; distinct roots: 23 (no sharing)
- roots strictly ascending, all inside the pool
- pool extent: `0x083BBBB0..0x083BBE6F` = **703 unique physical bytes**
- basic blocks: **86**; instructions: **351**; terminators: **23**
- **decode coverage: 703 of 703 bytes; uncovered: 0**
- roots failing to decode: **0**
- **re-encode is byte-identical over the full extent**, enforced inside
  `load_scripts` rather than only in a test
- opcodes present: `00` x79, `01` x19, `02` x101, `03` x44, `07` x42,
  `11` x23, `12` x21, `13` x21, `1D` x1 (**9 distinct**)

The pool bound is measured, not assumed: 703 is the largest extent for which the
23 roots tile exhaustively with zero uncovered bytes. At 687 and 688 bytes the
decode raises `instruction outside extent`; at 704 and beyond a trailing byte is
left uncovered and the corpus is refused.

### Corpus identity kept separate from `static40`
The two families share the interpreter, the dispatch table and the opcode
specification, but they are enumerated from **different static owners** and
their pools do not touch. They are therefore declared as two families under one
profile, not merged. Merging would destroy the ownership distinction that makes
an attachment meaningful, and the profile loader now refuses two families whose
pools overlap.

## Branch opcodes: the contract gains canonical evidence
`static40` contains no branch opcode, so TOOLKIT-013 recorded honestly that the
Buu branch contract rested on handler disassembly alone. `item_use` contains
**42 branch instructions** - 21 `0x12` (forward) and 21 `0x13` (conditional
forward). Displacements range 9..13. No `0x1C` backward branch occurs, so the
loop opcode remains unexercised by any supported corpus and is still recorded as
handler-derived only.

Control flow reconstructs cleanly: **86 blocks, 84 edges, 0 edges to an unknown
block, 0 branch targets off an instruction boundary**, and no unreachable block.

### The measurement that discriminates the two grammars
Both grammars decode the corpus and both re-encode it byte-identically, so
round-trip alone does not discriminate - the same honest bound TOOLKIT-013
recorded. The discriminator is what the branches *mean*:

| | Buu `stack_be16_buu_v1` | LOGII `stack_be7_v1` |
|---|---|---|
| blocks | 86 | 65 |
| instructions | 351 | 393 |
| branches with displacement 0 | **0** | **42** |
| branches whose target is their own fallthrough | **0** | **42** |
| real jumps | **42** | **0** |

Under the LOGII reading every one of the 42 branches has displacement zero and
jumps to the instruction that already follows it - all 42 branches are no-ops,
and the second displacement byte is re-read as a spurious opcode. Worked example
at the first root, `0x083BBBB0 +004`:

    Buu   : op 13, two-byte BE displacement 12 -> target +016 (a real boundary)
    LOGII : op 13, one-byte displacement 0     -> target +006, then invents op 0C

OLD CLAIM (TOOLKIT-013): Buu's `0x12/0x13/0x1C` widths are unexercised by any
supported corpus; the branch contract is handler-derived only.

NEW EVIDENCE: `item_use` exercises `0x12` and `0x13` over 42 canonical
instructions, and only the Buu two-byte big-endian reading produces branches
that do anything.

RESOLUTION: the Buu **forward** branch contract (`0x12`, `0x13`) is now backed
by handler disassembly **and** canonical script bytes. `0x1C` remains
handler-derived only and is recorded as such.

## References and semantics
Native dispatch resolved structurally through secondary table `0x08055098`:

| Opcode | Secondary | Count | Native handler |
|---|---|---|---|
| `02` | 12 | 22 | `0x08000337` |
| `02` | 13 | 1 | `0x0800035D` |
| `02` | 14 | 20 | `0x080004BB` |
| `02` | 15 | 1 | `0x08000383` |
| `02` | 31 | 12 | `0x08000817` |
| `02` | 130 | 23 | `0x08000BB3` |
| `02` | 213 | 21 | `0x080029D9` |
| `02` | 242 | 1 | `0x08003A75` |
| `03` | 12 | 33 | `0x08000337` |
| `03` | 14 | 11 | `0x080004BB` |

Eight distinct native targets. Per the shared-handler rule their gameplay
meaning stays **UNKNOWN** and they are exposed as structural native references
only. No opcode is renamed to `heal`, `restore_hp`, `give_item` or anything
comparable: an item whose description says it restores hit points is not proof
that a particular native call is the one that does it.

`0x080007B7`, the single native target of the `static40` corpus, does **not**
occur here, and remains structurally known but semantically UNKNOWN.

## Corrections
1. Site 15 (`0x0800F67A`) was initially read as the strongest candidate because
   proc `0x0800F62C` sits immediately before the TOOLKIT-009 placement-type
   constructor `0x0800F68C` and reads a descriptor-shaped record. A reference
   search found **zero** inbound references of any kind, so no owner exists to
   attach to. Rejected on evidence, not preference.
2. During the census, capstone decoded the literal pool at
   `0x0800F624..0x0800F62A` as instructions. The words are `0x0804D174` and
   `0x03001BAC`; `0x0800F62C` is a genuine prologue preceded by its pool. This
   does not change any conclusion but is recorded so a later reader does not
   trust a linear disassembly across a literal pool.
3. No TOOLKIT-013 measurement was found to be wrong. `static40` is unchanged at
   40 records / 120 roots / 328 instructions / 548 bytes / 5 opcodes.

## Unsupported call sites
The 26 sites not in `static40` or `item_use` still take their cursor from a
runtime object or a caller register and have no deterministic static entry
enumeration. Site 24 (`0x0801E15C`) reads `+0x30` from a record of the same
shape and is very likely the same owner family reached by another path, but its
caller `0x0801E42E` forms `r0` indirectly and that was not chased: the ticket
budget is one family, and one was proven. Bounding the rest remains the narrow
future question.
