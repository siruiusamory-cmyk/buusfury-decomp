# Buu's Fury static map collision: evidence and blocker

TOOLKIT-012 evidence. Every measurement here was taken against the canonical
Buu's Fury image (SHA-256 `940ad5f0...f059e`) by reading it in this ticket. No
count is inherited from a prior ticket's summary or from an upstream project.

**Outcome: BLOCKED at the evidence gate.** No bounded static collision family
with verified movement-blocking semantics was established. No codec was written.
Per ticket section 38, the premise was measured rather than forced, and the
strongest candidate was *refuted* rather than promoted.

## Sources consulted before any new reverse engineering

| Source | What it gave | What it did not |
| --- | --- | --- |
| `docs/research/MAP_FORMAT.md` (TOOLKIT-007) | The one CONFIRMED bounds structure `0x080755C0`; the typed/opaque slot split; `Collision = DISCOVERED` | Any collision representation; it records collision as explicitly undecoded |
| `docs/research/ENTITY_FORMAT.md` (TOOLKIT-008) | The `+0x14` placement chain, the 32-byte record layout, the `position_raw` axis refusal | Any blocking or walkability semantics |
| `docs/research/PLACEMENT_TYPES.md` (TOOLKIT-009) | Placement type selector chain into enemy stat records | Anything environmental |
| `docs/consumer-analysis.md` (ROM-011/012) | The registry population path `0x08012664`, the AABB query family `0x080126D4..0x080128F2`, and the ROM-012 runtime trace | A collision label; it states collision semantics remain unproven |
| `docs/reverse-engineering.md` | The nine MapEntry pointer words and the full pointer census | Any Category A collision confirmation |
| `docs/research/AUTO_RE_STATE.md` | The `FUN_0803B4FC` ray-march notes; the "point query" notes | A correct callee identity - see the correction below |
| `extern/buusfury` (pinned disassembly) | MapEntry table base/stride/count | Nothing on collision; `src/` holds only 3 unrelated files |
| `extern/DragonByteZ` | Upstream field names `items`/`objects`/`npcs` | Zero collision hits on a full-text grep |
| `extern/Legacy` (DBZKit) | Script VM opcodes 71 `SetCollisionRect` / 72 `ClearCollisionRect` | These are **Legacy of Goku** bytecode ops; LOG1 collision is out of scope per section 36, and no Buu equivalent exists |
| `extern/BuusFuryToolkit` | Extracted text only | No structural collision data |
| `extern/dbz-buus-fury-recomp` | `gbarecomp` infrastructure | Its "collision" hits are compiler data-range collisions, unrelated to game space |

Grep across all five upstreams for `collision|walkab|passab|blocking|solid|
terrain|obstacle` produced **no Buu static collision structure**. The upstream
names were treated as leads, and none survived.

## OLD CLAIM / NEW EVIDENCE / RESOLUTION: `0x08046AA4` is not a collision query

**OLD CLAIM.** `AUTO_RE_STATE.md` records, in five separate places (lines 910,
1022, 1291, 1461, 2090), a "point query `0x08046AA4`" / "`0x08046AA6`", and
describes `FUN_0803B4FC` as "a dual ray-march against map collision via
`FUN_08046AA4` (point query on `*param_2+0x54` room data)".

**NEW EVIDENCE.** Direct capstone disassembly of the canonical image:

```
08046AA0  bx r0
08046AA2  bx r1
08046AA4  bx r2
08046AA6  bx r3
08046AA8  bx r4
08046AAA  bx r5
08046AAC  bx r6
08046AAE  bx r7
```

This is the standard gcc `__call_via_rN` indirect-call thunk block. `0x08046AA4`
is not a function that queries anything; it is a **register-indirect jump**. The
real callee is whatever pointer was in `r2` at the moment of the call.
`docs/consumer-analysis.md:252` already had this right, naming
`0x08046AA2` "the Thumb `BX r1` veneer"; `AUTO_RE_STATE.md` did not.

**RESOLUTION.** Every note describing `0x08046AA4`/`0x08046AA6` as a point query
is describing a **virtual dispatch**, not a fixed collision routine. Re-reading
the actual call site at `0x0803B540`:

```
0803B540  ldr r1,[r4]        ; r1 = object's class/base struct
0803B542  adds r0, r4, #0    ; arg0 = the object
0803B544  ldr r2,[r1,#0x54]  ; r2 = self-relative offset stored at base+0x54
0803B546  adds r2, r2, r1    ; r2 = r1 + delta  -> the METHOD ADDRESS
0803B548  add r1, sp, #0x2c  ; arg1 = a point on the stack
0803B54A  bl  0x8046aa4      ; bx r2 = CALL THAT METHOD
0803B54E  cmp r0, #0         ; boolean result
```

So `+0x54` is a **virtual method slot** taking `(object, point*)` and returning a
boolean. It is not a pointer to "room data". This shape occurs at **57** call
sites ROM-wide (measured). The predicate is real and is used to guard movement,
but the data it consults is behind a virtual call, and the vtables involved
resolve to **IWRAM** (see below), not to static ROM tables.

This correction does not weaken any shipped capability: no toolkit code ever
depended on the old reading.

## Area content is one heterogeneous stream, not typed collision tables

Measured across all 452 MapEntry records, per-field ROM-pointer liveness:

| Field | Entries with a live ROM pointer |
| --- | ---: |
| `+0x10` | 222 |
| `+0x14` | 316 |
| `+0x18` | 53 |
| `+0x1C` | 12 |
| `+0x20` | 15 |
| `+0x24` | 3 |
| **`+0x2C`** | **452** |
| `+0x30` | 166 |
| `+0x34` | 1 |

`+0x2C` is the only field live on **every** map. Its 452 targets are **all
distinct** - zero maps share one. They span
`0x080728CC..0x0808E1E0`, **112,916 bytes**, ending exactly where the MapEntry
table begins at `0x0808E2E0`.

That span is a single contiguous, heterogeneous, factory-tagged descriptor
stream. A census of Thumb-code tag words inside it finds **40 distinct
factories**:

| Factory | Occurrences | Note |
| --- | ---: | --- |
| `0x0800FD55` | 1,559 | TOOLKIT-008's placement records live here |
| `0x08007387` | 271 | |
| `0x08017DA3` | 191 | |
| `0x0800742D` | 166 | the 20-byte rectangle family, below |
| `0x080077DF` | 154 | |
| `0x080111A9` | 148 | |
| `0x0800421F` | 140 | |
| `0x0800770D` | 131 | |
| `0x0800776D` | 122 | |
| `0x08007675` | 99 | CONFIRMED factory (AUTO_RE_STATE) |
| `0x0800774F` | 97 | |
| `0x0800A223` | 94 | |
| (28 more) | | each under 90 |

This is the structural reason no separate "collision table" was found: Buu does
not keep one. Spatial objects of every kind are interleaved records in one
per-map stream, distinguished only by their factory word.

## The candidate family, and why it was refused

The strongest candidate was the 20-byte family tagged `0x0800742D`, because it
contains the project's **only** CONFIRMED bounds structure (`0x080755C0`, reached
from MapEntry 39, halfwords `481, 121, 615, 271`).

Measured layout, stride `0x14`:

| Offset | Width | Content |
| ---: | ---: | --- |
| `+0x00` | 4 | factory `0x0800742D`, constant |
| `+0x04` | 4 | a subtype thunk (10 distinct values) |
| `+0x08` | 4 | two `s16` - `bound_a` |
| `+0x0C` | 4 | two `s16` - `bound_b` |
| `+0x10` | 4 | auxiliary pointer |

Corpus: **166** aligned occurrences, **152** well-formed, in **102** contiguous
runs (run lengths: 85 singletons, 9 pairs, 4 triples, 2 quads, one run of 12,
one of 17).

Three independent findings refuse this family as static map collision.

**1. No static map ownership.** Of the 102 run starts, **zero** are referenced
from the MapEntry table - not directly, and not at one or two further levels of
indirection (L1 array starts: 153, of which 0 have any inbound reference from
the table; L2 and L3 both empty). Ticket section 4 requires verified map
ownership; this family has none. It is reachable only by walking the `+0x2C`
stream, which is exactly what makes it *not* a separately-owned collision array.

**2. The subtype words are vtable getters returning IWRAM.** The 10 distinct
`+0x04` values are not constructors. Eight decode as
`ldr r0,[pc,#N] ; bx lr` - a getter that returns a literal:

| Subtype thunk | Returns |
| --- | --- |
| `0x080077DF` (x65) | `0x03001960` |
| `0x0800770D` (x32) | `0x03001938` |
| `0x0800774F` (x16) | `0x0300193C` |
| `0x0800775F` (x5) | `0x0300193C` |
| `0x0802266F` (x4) | `0x03002F4C` |
| `0x0800776D` (x1) | `0x0300195C` |
| `0x08007753` (x1) | `0x0300193C` |
| `0x08007759` (x1) | `0x0300193C` |

Every one is an **IWRAM** address. The class identity of these records is
constructed in RAM at load time; it is not a static ROM class table this toolkit
could own or validate.

**3. The one CONFIRMED rectangle is a transition, not a blocker.** `0x0300195C`
is the exact callback receiver that ROM-012 traced at runtime
(`docs/consumer-analysis.md:842`, `docs/reverse-engineering.md:334`). In that
capture the player entity `0x0202E4D0` entered bounds `x=[592,601), y=[136,241)`
on MapEntry 39, the filter accepted, the action executed - and the human
observer recorded that **entering it moved the player to the next area and
started dialogue**.

Ticket section 21 forbids treating transition rectangles as movement blockers.
The best-witnessed rectangle in this ROM is a transition. Promoting its family
to "collision" would be precisely the collapse the ticket prohibits.

## No dense walkability grid exists behind any map pointer

A tile- or bitmask-based walkability grid would appear as a low-entropy byte
block hanging off a MapEntry pointer. Measured across every live pointer in
fields `+0x10`, `+0x14`, `+0x18`, `+0x1C`, `+0x20` and `+0x30` (784 live
pointers in total), the count of targets whose first 512 bytes are low-entropy
(at most 16 distinct byte values, modal byte at least 25%) is:

**0 - in every field.**

Sweeping the whole 8 MiB image for 512-byte blocks whose bytes are all `<= 0x0F`
and not constant finds only **10** such blocks, all in `0x08725600..0x08754600`,
inside the graphics region and not reachable from any map record.

There is therefore no evidence for a grid/bitmap walkability representation in
this ROM, and the ticket's opening framing ("walkable vs blocked areas",
"collision boundaries") is not satisfied by any static structure found.

## Debug strings

The image contains exactly **4** `T:\Source\...` debug strings, all inline
assert literals with no separate aligned reference:

| Address | String |
| --- | --- |
| `0x08004160` | `T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp` |
| `0x08004818` | `T:\Source\GameData.cpp` |
| `0x08008A5C` | `T:\Source\AreaEntry.cpp` |
| `0x08013BAC` | `T:\Source\CharacterData.cpp` |

`AreaEntry.cpp` confirms which subsystem owns the map-load code region, and is
consistent with the `+0x2C` stream being area content. **No collision-named
source file exists in the image.**

## Collision domains, kept separate

| Domain | Status after TOOLKIT-012 |
| --- | --- |
| Static map walkability / environmental blocking | **DISCOVERED** - no verified representation; this ticket's blocker |
| Spatial object rectangles (`0x0800742D`, 152 records) | **DISCOVERED** - bounded and measured, semantics unproven, no map ownership |
| Transition / contact rectangles | **DECODE** - unchanged from TOOLKIT-007; one instance runtime-confirmed as a transition |
| Placement records | **ROUND_TRIP + EDIT** - unchanged from TOOLKIT-008 |
| Actor-body collision | **DISCOVERED** - unchanged |
| Combat / melee AABB | **DISCOVERED** - P-003/P-006 evidence, not environmental |
| Projectile collision | **DISCOVERED** - untouched |
| The `+0x54` virtual point-query predicate | **DISCOVERED** - 57 call sites located; dispatches through IWRAM vtables, no static data owner identified |

## Capability matrix

| Target family | Rung | Note |
| --- | --- | --- |
| Static map collision family | **DISCOVERED** | none established; no codec written |
| Geometry decode | **NOT ESTABLISHED** | no verified collision record type |
| Coordinate semantics | **NOT ESTABLISHED** | no axis claim added; TOOLKIT-008's refusal stands |
| Collision WRITE | **NOT SUPPORTED** | nothing verified to write |
| Transition geometry | **DECODE** | unchanged from TOOLKIT-007 (89 edges, destinations UNKNOWN) |
| Placement bounds | **ROUND_TRIP + EDIT** | unchanged from TOOLKIT-008 |
| Combat AABB | **DISCOVERED** | unchanged; explicitly not merged into map collision |
| Runtime behavioral validation | **NOT PERFORMED** | no candidate reached the bar that would justify a probe |

## Preserved canonical corrections

Every count listed in ticket section 34 was left untouched. This ticket
contradicts none of them, adds no new spatial claim, and renames no field.

## Runtime validation

**Not performed, and this is stated explicitly.** Ticket section 9 permits fresh
runtime work only to unblock a narrow question about an otherwise-settled
structure. No candidate family reached that state: the blocker here is
*ownership and identity*, which a runtime probe of an unowned record could not
settle. No emulator was launched, and no save or state file was read or written.

## Unresolved collision questions

* What static data, if any, backs the `+0x54` virtual point-query predicate. The
  predicate is real and guards movement at 57 sites, but its data is reached
  through an IWRAM vtable built at load time.
* Whether environmental blocking in Buu is data-driven at all, or is a property
  of the tile/graphics layer rather than a separate structure.
* Which of the 40 stream factory families, if any, constructs a movement blocker.
  36 of them remain entirely uncharacterised.
* Whether the 152 rectangle records include blockers alongside transitions. Their
  10 subtypes resolve to 5 distinct IWRAM vtables; only one
  (`0x0300195C`) has any runtime evidence, and that evidence says "transition".

## What would unblock this

The smallest decisive next step is **not** more static scanning. It is to
identify, at runtime, which IWRAM vtable the `+0x54` predicate resolves to during
ordinary walking-into-a-wall, then walk that vtable back to the static record
that constructed it. That is a bounded runtime question, but it is fresh
reverse engineering of a kind TOOLKIT-012 explicitly forbids opening
(section 9: "Do not start a general collision RE campaign"), so it is recorded
here rather than attempted.
