# TOOLKIT-015 map-scene Buu script ownership evidence

## Status: BLOCKED on ownership, with a new bounded script family measured

Profile `buus_fury_usa_rev0_01c1707f`, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

TOOLKIT-015 asked one question: **which stable Buu map-scene record owns or
selects script execution?** After the two deep investigations the ticket
allows, the honest answer is that **no map, placement or placement-type record
in the verified corpus owns a script**. Two candidate families were traced to
their static ends and both terminate short of a map-scene owner.

A genuinely new script family was measured on the way - the `0x0800421F`
content-stream family, 44 roots / 921 bytes / exact round-trip, and the **first
corpus in this project to exercise backward branch opcode `0x1C`**. It is
reported in full below but **not promoted to a project attachment**, because its
owner chain stops at records that the verified placement corpus excludes.

One narrow evidence promotion does follow from it: the three `0x1C` instructions
pass every structural check, so the **`0x1C` encoding and branch contract** is
promoted to canonical-ROM corroborated. That is a statement about the opcode, not
about the corpus - the family itself stays unsupported and unattached.

    map / placement / placement type  ->  (no static path found)
    0x0800FD55 variant record +0x14   ->  0x0800421F header +0x04
      -> interpreter 0x08004038 -> 44 roots, 921 bytes, ROUND_TRIP

## Prior knowledge audit
Read before any fresh probing: `BUU_SCRIPT_OWNERSHIP.md` (TOOLKIT-014 census of
all 29 interpreter call sites), `BUU_SCRIPT_VM.md` (TOOLKIT-013 interpreter and
opcode contract), `PLACEMENT_TYPES.md` (TOOLKIT-009 type table `0x08711274`,
stride 28, constructor `0x0800F68C`), `map_placements.py` (TOOLKIT-008 record
layout and the 1,295-placement ownership walk), `MAP_FORMAT.md`,
`COLLISION_FORMAT.md` (the `MapEntry[+0x2C]` content stream and the
`0x08046AA4` `__call_via_rN` correction), and the TOOLKIT-012 factory-tag
census, which already recorded `0x0800421F x140`.

No runtime instrumentation was used: both candidates were settled statically,
so per the ticket's own rule no probe was launched. Nothing was imported from
upstream projects.

## Candidate 1 - placement `+0x18` / `+0x1C` (REJECTED)

TOOLKIT-009 recorded placement `+0x18`/`+0x1C` as a CONFIRMED structural
attachment with UNKNOWN semantics: `0x0800F6D2` passes the address
`placement+0x18` to `0x0800A93C`, which retains it. That made it the most
promising placement-level script candidate on the board.

`0x0800A93C` allocates a 12-byte cursor object and stores the passed address at
its `+0x08`; `0x0800A95A` then walks `[+0x08]` as `{count, ptr[count]}` and
dispatches each entry through `bl 0x8046aa4` - a **vtable call**, not a script
cursor. The interpreter `0x08004038` is never reached on this path.

The decisive measurement is in the corpus rather than the code:
`map_placements.py` records, over all 1,295 verified placements, that `+0x18` is
the constant `0x00000001` and `+0x1C` the constant `0x080716EC`. A field that is
byte-identical on every record cannot select a per-placement script.
`0x080716EC` reads as `{0x0800A26F, 0x030019A4, 0x0800A9B1, 0x0800A9B5,
0x0800A9B9, ...}` - Thumb function pointers interleaved with an IWRAM data slot,
i.e. the shared dispatch structure those calls go through. It is a mixed
vtable-plus-state block, not a pure function-pointer table; only the entries
actually dispatched are claimed as code.

RESOLUTION: placement `+0x18`/`+0x1C` is a **shared vtable pointer pair**, not a
script attachment. Rejected on measured evidence.

## Candidate 2 - the `0x0800421F` content-stream family (script chain proven, owner missing)

### Why it was selected
TOOLKIT-014's census left 26 interpreter sites whose cursor comes from a runtime
object or caller register. Rather than chase them individually, each enclosing
proc was tested for **inbound Thumb-pointer references from the MapEntry
`+0x2C` content stream** (`0x080728CC..0x0808E1E0`). Exactly one proc answered:

| Census site | Enclosing proc | Inbound refs | Inside the `+0x2C` stream |
|---|---|---|---|
| 3 | `0x0800421E` | **140** | **140** |
| all 19 others | - | 0 | 0 |

That is a decisive selection signal, and it matches the TOOLKIT-012 factory-tag
census entry `0x0800421F x140`. No other unresolved site is referenced from map
content at all.

### The script chain (CONFIRMED_ROM)
`0x0800421E` is a pure trampoline - it takes a record and interprets its `+0x04`:

    0800421E  push {lr}
    08004220  ldr  r1,[r0,#4]      ; the script cursor
    08004224  sub  sp,#0x6c        ; VM working frame
    0800422E  bl   0x08004038      ; interpret it

All 140 records carry `+0x00 = 0x0800421F` and a `+0x04` pointer that always
points **backward** into the same content stream - the script is stored inline,
ahead of its header. The distance is **not** fixed: the commonest deltas are
-12 (14 records), -16 (10) and -20 (5), with a long tail out to -50,036, so the
header and its script are not a fixed-size pair and the header cannot be located
from the script by arithmetic. 44 distinct roots serve the 140 records, so
sharing is real and measured.

### Corpus measurement and exact ROUND_TRIP
Decoded with the existing `stack_be16_buu_v1` opcode set - no new VM:

- records: **140**; distinct script roots: **44** (real sharing, 140 -> 44)
- basic blocks: **69**; instructions: **358**
- byte extent: **921 unique bytes**, and the summed per-root extents equal 921,
  so **no two roots overlap**
- root extents range 5..239 bytes
- decode failures: **0**; uncovered bytes within each root's extent: **0**
- **re-encode is byte-identical for all 44 roots**
- opcodes present: `00` x72, `01` x10, `02` x140, `03` x2, `04` x3, `07` x5,
  `08` x6, `0B` x2, `0F` x1, `11` x44, `12` x1, `13` x9, `1B` x3, `1C` x3,
  `1D` x57 - **15 distinct**

### Branch coverage - `0x1C` is exercised for the first time
`static40` has no branch at all; `item_use` exercises `0x12` and `0x13` but no
`0x1C`, so TOOLKIT-014 correctly left the backward branch handler-derived only.
This corpus contains **`0x12` x1, `0x13` x9 and `0x1C` x3**.

`0x1C` is therefore **exercised by canonical bytes for the first time in this
project**, and the three instructions were put through the full structural
contract rather than merely counted.

### `0x1C` structural verification (all three instructions)
The rule under test is the handler-derived one implemented at
`tools/webfoot/formats/script_vm.py:147-159`: opcode 28 is declared `be16` with
flow `count_back` (`tools/webfoot/data/script_specs.py:49-50`) and branch base
`before_operand` (`tools/webfoot/data/script_specs.py:77`), so the target is
`(offset + 1) - displacement`. Every check below recomputes the target
independently of the decoder rather than trusting its output.

All three occur in root `0x08085 3E8` (extent 239 bytes, 10 blocks):

| Offset | Raw bytes | Displacement | Base | Target | Backward | In extent | Block head |
|---|---|---|---|---|---|---|---|
| 104 | `1c 00 52` | 82 (BE `0052`) | 105 | 23 | yes | yes | yes |
| 186 | `1c 00 38` | 56 (BE `0038`) | 187 | 131 | yes | yes | yes |
| 231 | `1c 00 18` | 24 (BE `0018`) | 232 | 208 | yes | yes | yes |

- **two-byte big-endian displacement**: each operand is 2 bytes and
  `value == (raw[1] << 8) | raw[2]` for all three
- **branch base**: `before_operand`, i.e. the byte after the opcode
- **subtraction**: independently recomputed `base - displacement` equals the
  decoder's target in all three cases
- **instruction boundaries**: every target is the first instruction of a real
  basic block, so all three are genuine loop heads
- **CFG coherence**: across the whole 44-root family, 37 edges, **0 edges to an
  unknown block**, and exactly 3 backward branches - the three above

OLD STATUS: `0x1C` backward-branch behavior supported only by handler
disassembly; no canonical corpus exercised it (TOOLKIT-013, restated in
TOOLKIT-014).

NEW EVIDENCE: three canonical Buu script instructions independently exercise the
same encoding - two-byte big-endian displacement, `before_operand` base,
subtraction - and every one resolves backward onto a valid instruction boundary
that is a basic-block head, with a coherent CFG.

RESOLUTION: the **`0x1C` opcode encoding and branch contract** is promoted to
**canonical-ROM corroborated**. Ownership governs whether a corpus can become a
toolkit capability; it does not govern whether canonical bytes can corroborate an
opcode's encoding, and these bytes do.

**Explicitly NOT promoted by this**: the owning corpus, its attachment status,
its gameplay semantics, and any native-handler meaning. The family remains
unsupported and undeclared.

### Where the ownership chain stops
Every static path from the map table was tested and all of them fail:

| Path tested | Result |
|---|---|
| `MapEntry` field == a record, all fields `+0x0C..+0x34` | **0** of 452 |
| `MapEntry` field -> array containing a record (2nd level) | **0** of 452 |
| `MapEntry[+0x2C]` stream walk, up to 2 hops | **0** of 452 |
| `MapEntry[+0x14]` placement-array walk | **0** of 452 |
| Verified placement immediately preceding a record | **0** of 1,295 |

The records *are* all inside the `+0x2C` content stream
(`0x08072D10..0x0808E0C4`), so they are map content by position - but position
inside a heterogeneous stream is not ownership, and nothing in the map table
addresses them.

Inbound references were then traced directly. 64 of the 140 records have exactly
one inbound word; **all 64 sit at offset `+0x14` of a record whose first word is
`0x0800FD55`** - the placement factory tag. That looked like placement
ownership, and it is not: in all 1,295 **verified** placements `+0x14` is the
constant `0x080555A0`. None of these 64 `0x0800FD55` bases is a verified
placement.

They are a **second `0x0800FD55` record variant** that shares the factory tag but
not the layout - exactly the non-conforming occurrences TOOLKIT-008 excluded
from the supported corpus. The remaining **76 records have no inbound reference
of any kind**.

Final accounting: 64 records owned by an unverified FD55 variant, 76 orphaned,
**0 reaching any verified map, placement or placement type**.

## Corrections

**OLD CLAIM (mid-investigation, this ticket).** 57 of the 140 records sit 8
bytes before a map-reachable placement across 10 maps, suggesting a
header-prefix ownership relationship.

**NEW EVIDENCE.** That number came from a hand-written placement walker that
accepted any `0x0800FD55`-led word and reached **1,442** placements. The
verified parser reaches **1,295**; the extra 147 are precisely the
non-conforming records TOOLKIT-008 refuses. Re-run against
`maps.placements()`, the count of verified placements preceded by a `0x0800421F`
header is **0 of 1,295**.

**RESOLUTION.** The header-prefix hypothesis is **refuted**. The lesson is
recorded rather than quietly dropped: a re-derived walker that disagrees with a
verified corpus count is wrong until proven otherwise, and every ownership claim
in this ticket is measured against `maps.placements()`, never against a local
re-walk.

A second correction: the record's `+0x08` word is `0x0800FD55` in 64 of 140
cases, which first read as "the header prefixes a placement". It does not - the
FD55 record's own `+0x14` points *back* at the header. The relationship is a
back-pointer inside one variant record, not a prefix.

## Capability matrix after TOOLKIT-015

| Capability | Status |
|---|---|
| Buu VM grammar (`stack_be16_buu_v1`) | CONFIRMED_ROM |
| `static40` corpus | ROUND_TRIP, no attachment |
| `item_use` corpus | ROUND_TRIP + item attachment + text refs |
| `0x0800421F` family | measured, ROUND_TRIP, **not promoted** (no owner) |
| map -> event | **UNRESOLVED** - no static path found |
| placement -> event | **REFUTED** for `+0x18`/`+0x1C`; none found |
| placement type -> event | **UNRESOLVED** - `+0x08` reaches a behavior-tree descriptor table at `0x0870F514`, not the script VM |
| event -> text | CONFIRMED_ROM for `item_use` only |
| branch `0x12` / `0x13` | canonical-corpus validated (TOOLKIT-014) |
| branch `0x1C` **encoding/contract** | **canonical-ROM corroborated** - 3 instructions, all structural checks pass |
| `0x1C` owning corpus / attachment / semantics | **NOT promoted** - the family stays unsupported |
| native semantics | UNKNOWN |
| script WRITE / AUTHOR_NEW | not attempted; free capacity remains 0 |

## Placement-type `+0x08` note (incidental, no scope expansion)
For completeness of the second investigation: placement type `+0x08` feeds
`0x0800AA9C`, which indexes a stride-8 table at `0x0870F514` pairing a vtable
with a descriptor in `0x086FDA00..`. Those descriptors are
`{vtable, count, child_ptr[count]}` and their methods (`0x08018F90`) recurse
over children - a **behavior-tree/state-machine structure**, not VM bytecode.
It never calls `0x08004038`. Recorded so a later ticket does not re-walk it
looking for scripts; nothing about it is promoted here.
