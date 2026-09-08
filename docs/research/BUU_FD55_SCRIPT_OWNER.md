# TOOLKIT-016 second `0x0800FD55` variant ownership evidence

## Status: OWNERSHIP PROVEN, owned subset promoted

Profile `buus_fury_usa_rev0_01c1707f`, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

TOOLKIT-016 asked one question: **what stable static structure owns or addresses
the second `0x0800FD55` variant responsible for the 64 known references into the
`0x0800421F` script-record corpus?**

The answer is that there is **no second variant**. The record family has one
layout, and TOOLKIT-008 measured only its most common shape. Once the real
layout is read, the map table owns these records directly through the same
`MapEntry[+0x14]` array that already carries the supported placement corpus.

    MapEntry[+0x14] -> placement array -> placement record
      -> +0x14 behavior descriptor {handler, payload}
      -> handler 0x0800421F -> payload = script -> interpreter 0x08004038

**57 of the 64** referencing records are owned by **10 verified maps**, covering
**25 script roots / 202 instructions / 514 bytes**, exact round-trip, and all
three canonical `0x1C` backward branches fall inside the owned subset.

## The structural finding: the record is variable-length

TOOLKIT-008 recorded a fixed 32-byte record whose last three words are the
constants `{0x080555A0, 0x00000001, 0x080716EC}`. Measured against the 64
referencing records, those three words are not constants and not a tail:

    +0x00  factory_raw     0x0800FD55
    +0x04  flags_raw
    +0x08  type_raw
    +0x0C  position_raw
    +0x10  id_raw
    +0x14  behavior_ptr    -> 2-word descriptor {handler, payload}
    +0x18  child_count     n
    +0x1C  child_ptr[n]    n pointers -- the record ends after these

So the record size is `0x1C + 4 * n`, not a constant 32. The supported corpus
looked fixed-size only because **1,427 of 1,442 records carry `n == 1`**, which
makes `0x1C + 4` exactly 32 and freezes `+0x18`/`+0x1C` into apparent constants.

| Implied record size | Records |
|---|---|
| 32 (`n = 1`) | 1,427 |
| 36 (`n = 2`) | 7 |
| 40 (`n = 3`) | 6 |
| 44 (`n = 4`) | 2 |

**This is corroborated by the constructor, not inferred from the data alone.**
`0x0800FD54` is the factory wrapper; it calls `0x0800F68C`, which at
`0x0800F6D2` does `adds r1, #0x18` and calls `0x0800A93C`. TOOLKIT-015 already
disassembled `0x0800A93C`/`0x0800A95A` and found that it walks its argument as
`{count, ptr[count]}`. That is precisely this field pair. TOOLKIT-015 read the
right code and drew the wrong conclusion from it, because it was testing
`+0x18`/`+0x1C` against the corpus where `n` is always 1.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION - the record tail

**OLD CLAIM** (TOOLKIT-008, restated in TOOLKIT-015). The placement record is
32 bytes and ends in the constant tail `{0x080555A0, 0x00000001, 0x080716EC}`;
records not carrying that tail are "non-conforming" and excluded. TOOLKIT-015
additionally concluded from the constancy of `+0x18`/`+0x1C` that they are a
"shared vtable pointer pair" that "cannot select a per-placement script".

**NEW EVIDENCE.** Over all 1,442 map-reached records, `+0x18` is a count and
`+0x1C..` is a `count`-long pointer array, exactly as `0x0800A93C` consumes it.
15 records carry `n != 1`. Reading `+0x18` as a count and bounding each record
at `0x1C + 4n`, **zero** of the 1,442 record bodies runs into the next record,
and the 240 pointer arrays share **zero** slots. The apparent constants are an
artifact of `n == 1` dominating the corpus.

**RESOLUTION.** There is one record family with a variable-length child array,
not a conforming family plus a second variant. `+0x18`/`+0x1C` are `count` and
`child_ptr[0]`. The vtable-pair reading is **refuted**.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION - the 1,442-record walker

**OLD CLAIM** (TOOLKIT-015, recorded as a "hard lesson"). A hand-written walker
accepting any `0x0800FD55`-led word reached 1,442 placements against the
verified parser's 1,295; the extra 147 were "precisely the non-conforming
records TOOLKIT-008 refuses", and the rule drawn was that any re-derived walker
disagreeing with a verified corpus count is wrong until proven otherwise.

**NEW EVIDENCE.** Re-measured, the generalized walk reaches **1,442 distinct
records across 240 arrays**, and it is a strict superset of the verified corpus:
all **1,295** verified placements are reached, **zero** verified placements are
lost, **zero** records are claimed by two maps, and **zero** array slots
overlap. The 147 extra records are well-formed under the variable-length
layout - 57 carry a script handler, 24 carry handler `0x0800424F`, 66 carry the
same null handler as the supported corpus.

**The two numbers name two different things, and both stay in use.** `1,442` is
the full placement-record census under the correct variable-length contract.
`1,295` is the size of the **legacy supported fixed-codec subset** - the records
the 32-byte codec in `map_placements.py` can currently read. Every historical
`1,295` in this project remains correct as that subset's size and must **not**
be rewritten to `1,442`:

| Figure | What it counts | Still valid |
|---:|---|---|
| 1,295 | legacy supported fixed-codec subset | yes, as a subset |
| 1,442 | full variable-length placement census | yes, as the census |
| 147 | census minus subset, truncated by the tail requirement | new |

**RESOLUTION.** The 1,442 walk was **correct**, and the disagreement was the
verified parser's tail requirement truncating 240 arrays early rather than the
walker over-collecting. The TOOLKIT-015 lesson is **narrowed**: a re-derived
walker disagreeing with a verified corpus must be reconciled, and the verified
corpus is not automatically the correct side of the disagreement. What made the
difference here is that the generalized walk is *bounded* - it terminates on a
non-`0x0800FD55` word, its arrays provably do not overlap, and its record bodies
provably do not collide - so it is checkable rather than merely larger.

Note this does **not** revive TOOLKIT-015's separate refuted claim that 57
records "prefix a map-reachable placement". That arithmetic-adjacency
hypothesis stays refuted; the ownership established here is by **pointer**, not
by adjacency, and the coincidence of the number 57 is unrelated.

## The behavior descriptor at `+0x14`

`+0x14` points at a 2-word descriptor `{handler, payload}`. Across all 1,442
map-reached records there are exactly **three** handlers, and each one is a
short Thumb routine that loads the descriptor's `+0x04`:

| Handler | Disassembly | Records | Maps | Meaning |
|---|---|---|---|---|
| `0x0800421D` | `bx lr` | 1,361 | 226 | no behavior - the null handler |
| `0x0800421F` | `ldr r1,[r0,#4]` ; `bl 0x08004038` | **57** | **10** | **interpret payload as script** |
| `0x0800424F` | `ldr r0,[r0,#4]` ; `bl 0x08012588` | 24 | 16 | other consumer, semantics UNKNOWN |

The supported corpus's "constant" `+0x14 = 0x080555A0` is simply the shared
address of the **null-handler descriptor** - `0x080555A0` holds `0x0800421D`,
and it has 1,442 inbound references, one per map-reached record. That count
matching the walk exactly is independent corroboration of the walk's extent.

This is what makes the ownership real rather than positional: a record does not
"contain" a script, it **names a handler**, and 57 records name the interpreter
trampoline. `0x0800421F` is not a factory tag for a separate record family - it
is a **function pointer**, the first word of a descriptor.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION - the `0x0800421F` "records"

**OLD CLAIM** (TOOLKIT-012 factory census, carried into TOOLKIT-015). The image
contains a family of 140 `0x0800421F` records, of which 64 are referenced from a
second `0x0800FD55` variant and 76 have no referrer.

**NEW EVIDENCE.** All 140 are 2-word behavior descriptors whose first word is
the Thumb pointer `0x0800421F` and whose second word is a script root. They are
not a factory-led record family; `0x0800421F` is the address of the trampoline
disassembled in TOOLKIT-015.

**RESOLUTION.** The "family" is a **descriptor kind**, and its 140 occurrences
are the descriptors that select script behavior. 64 are named by a placement
record's `+0x14`; the other 76 are named from elsewhere or unused, and remain
out of scope.

## Ownership result

Walking `MapEntry[+0x14]` under the corrected layout:

| Measurement | Value |
|---|---|
| Maps with a placement array | 240 |
| Records reached | 1,442 (all distinct) |
| Verified TOOLKIT-008 placements reached | **1,295 of 1,295** |
| Verified placements lost | **0** |
| Records claimed by two maps | **0** |
| Overlapping array slots | **0** |
| Record bodies colliding with the next record | **0** |
| Script-bearing records owned | **57** |
| Maps owning a script-bearing record | **10** |

Per-map ownership of the script-bearing subset:

| Map | Records | Distinct roots |
|---|---|---|
| 19 | 10 | 10 |
| 21 | 15 | 1 |
| 22 | 15 | 1 |
| 240 | 2 | 2 |
| 309 | 1 | 1 |
| 325 | 7 | 3 |
| 428 | 1 | 1 |
| 430 | 2 | 2 |
| 432 | 2 | 2 |
| 437 | 2 | 2 |

Maps 21 and 22 each point 15 records at a single shared root, which is why
sharing must be represented rather than flattened.

## The owned script subset

Decoded with the existing `stack_be16_buu_v1` opcode set - **no new VM, no new
assembler, no new syntax**:

- owned records: **57**; distinct roots: **25** (real sharing, 57 -> 25)
- blocks: **42**; instructions: **202**
- byte extent: **514 unique bytes**; summed per-root extents also 514, so
  **no two owned roots overlap**
- decode failures **0**, uncovered bytes **0**
- **re-encode byte-identical for all 25 roots**
- 14 distinct opcodes: `00` x41, `01` x2, `02` x74, `03` x2, `04` x1, `07` x5,
  `08` x6, `0F` x1, `11` x25, `12` x1, `13` x5, `1B` x3, `1C` x3, `1D` x33

**All three canonical `0x1C` backward branches are inside the owned subset.**
The opcode's encoding contract was already promoted to canonical-ROM
corroborated by TOOLKIT-015 and is unchanged here; what is new is that the
corpus exercising it now has a proven owner, so the family carrying it can be
supported rather than merely measured.

### Unowned remainder, explicitly excluded

- **7** of the 64 referencing records are not reached from any map:
  `0807CDF4`, `0807FA1C`, `08081A04`, `08083DA4`, `0808DF58`, `0808E018`,
  `0808E0CC`.
- **76** descriptors have no `0x0800FD55` referrer at all.
- Together these account for **19** of the 44 roots.
- **Sharing across the boundary is zero**: no owned root is also referenced by
  an unowned descriptor, so the owned subset is a clean partition and promoting
  it cannot silently promote unowned bytes.

## Attachment level

Ownership is exposed at the level the ROM actually stores it:

    map -> placement record -> behavior descriptor -> event

It is **not** flattened to `map -> event`. The descriptor is a real addressable
object shared between records (maps 21 and 22 prove sharing), and the placement
record is what the map addresses.

## Capability matrix after TOOLKIT-016

| Capability | Status |
|---|---|
| Buu VM grammar (`stack_be16_buu_v1`) | CONFIRMED_ROM |
| Supported placement family (TOOLKIT-008) | ROUND_TRIP, **layout corrected to variable-length** |
| Placement record variable-length child array | CONFIRMED_ROM (constructor + corpus) |
| Behavior descriptor `+0x14` `{handler, payload}` | CONFIRMED_ROM, 3 handler kinds |
| `static40` corpus | ROUND_TRIP, no attachment (unchanged) |
| `item_use` corpus | ROUND_TRIP + item attachment + text refs (unchanged) |
| **map -> placement -> descriptor -> event** | **CONFIRMED_ROM, 57 records / 10 maps** |
| Owned script subset | **ROUND_TRIP, 25 roots / 514 bytes, promoted** |
| Unowned remainder (7 records, 76 descriptors, 19 roots) | measured, **not promoted** |
| Handler `0x0800424F` (24 records) | structural only, semantics UNKNOWN |
| branch `0x1C` encoding/contract | canonical-ROM corroborated (TOOLKIT-015), now inside an owned corpus |
| event -> text | CONFIRMED_ROM for `item_use` only; not claimed here |
| native handler semantics | UNKNOWN |
| script WRITE / AUTHOR_NEW | not attempted; free capacity remains 0 |

### What this does NOT provide

Ownership is **established** and the owned subset is **proven**. Neither phrase
means the toolkit exposes them through its normal path yet. Not delivered here:

- variable-length placement codec support in the supported path
- project extraction of all 1,442 records
- normal supported-path reading of the 57 owned records
- script WRITE, AUTHOR_NEW
- runtime destination-field proof through the constructor chain

The 57-record subset must not be described as "wired" or as normal production
support. The accurate wording is **ownership established / owned subset
proven**.

### Immediate implementation consequence

> The production placement codec must be changed to respect `0x1C + 4n` before
> the newly proven 57-record attachment subset can be exposed through the
> supported project path.

`tools/webfoot/formats/map_placements.py` still encodes a fixed 32-byte record
with `RECORD_TAIL`, which is now known incomplete: it reads the `n == 1` subset
and truncates the rest. **Deliberately not implemented in TOOLKIT-016** - the
contract is proven here, and wiring it is the next ticket's work.

### Constructor-chain limit

Ownership does **not** depend on completing:

    +0x14 -> 0x0800E754 -> 0x0800FD74 -> runtime destination field

The static proof is sufficient through: map walk -> placement record ->
descriptor -> handler/payload dichotomy -> script. The runtime destination field
is **unresolved** and is not invented here.

## Method note

No runtime instrumentation was used. The question was settled statically, so
per the ticket's own rule no probe was launched. Nothing was imported from
upstream projects. Every ownership number above is measured against
`maps.placements()` for the verified corpus and against a bounded walk whose
non-overlap is independently checked, never against an unchecked re-walk.
